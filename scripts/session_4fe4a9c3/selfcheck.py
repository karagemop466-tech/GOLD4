#!/usr/bin/env python3
"""Hallucination self-check for the 2026-11-11 re-read (session 4fe4a9c3) — independent of scripts/session_4fe4a9c3/apply_reread.py.

For every row it asks one question: does the price now stored in data/rings.json
appear, as printed text, in the raw evidence captured on 2026-11-11? It reads the
raw runner artifact and the hand-read verbatim strings directly and does not use
the reconciliation file, so an error in the apply script cannot hide here.

Also checks: blank rows really have no price, weights and URLs are unchanged
against main@b34ae17, every superseded price is in price_history, and every
derived gold value re-derives from the benchmark. Exit 1 on any failure.
"""
from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
BASE = "b34ae17fc474e02539dc40c1b0f41ad9d952ced3"


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def amounts(text: str) -> set[float]:
    out = set()
    for mm in re.finditer(r"(?<![\d.])(\d{1,3}(?:,\d{3})+|\d+)(\.\d+)?(?![\d,])", text):
        try:
            out.add(round(float((mm.group(1) + (mm.group(2) or "")).replace(",", "")), 2))
        except ValueError:
            pass
    return out


def main() -> int:
    rings = load("data/rings.json")["rows"]
    runner = {r["key"]: r for r in load("reports/live_source_check_20261111T080309Z.json")["results"]}
    hand = {h["id"]: h for h in load("reviews/reread-4fe4a9c3/hand_reads.json")["rows"]}
    spot = load("data/gold_spot.json")
    derived = {r["id"]: r for r in load("data/derived.json")["rows"]}
    method = load("data/methodology.json")
    base = {r["id"]: r for r in json.loads(subprocess.run(["git", "show", f"{BASE}:data/rings.json"], cwd=ROOT, capture_output=True, text=True, check=True).stdout)["rows"]}
    fails, checks = [], 0

    def check(cond: bool, msg: str) -> None:
        nonlocal checks
        checks += 1
        if not cond:
            fails.append(msg)

    for r in rings:
        rid, p = r["id"], r.get("price_usd")
        rec = runner[rid]
        # only the fields that hold page-printed prices and weights, so byte counts or timings cannot match by accident
        raw = json.dumps([rec.get("price_snippets"), rec.get("structured_prices"), rec.get("weight_snippets")], ensure_ascii=False)
        seen = amounts(raw)
        if rid in hand:
            seen |= amounts(" ".join(hand[rid].get("verbatim", [])))
        dated_today = r.get("price_captured_utc") == "2026-11-11"
        if p is not None and dated_today:
            check(round(float(p), 2) in seen, f"{rid}: stored price {p} dated 2026-11-11 is not printed anywhere in that day's raw evidence")
            if r.get("list_price_usd"):
                check(round(float(r["list_price_usd"]), 2) in seen, f"{rid}: list price {r['list_price_usd']} not in that day's raw evidence")
        if p is None:
            check("PRICE_UNVERIFIED" in r["flags"], f"{rid}: blank price without PRICE_UNVERIFIED")
        if p is not None and not dated_today:
            check("PRICE_NOT_REREAD_2026_11_11" in r["flags"], f"{rid}: price keeps an October date without the not-re-read flag")
        check(r.get("weight_g") == base[rid].get("weight_g"), f"{rid}: weight changed against main")
        check(r["url"] == base[rid]["url"], f"{rid}: URL changed against main")
        check(r["karat"] == base[rid]["karat"], f"{rid}: karat changed against main")
        old = base[rid].get("price_usd")
        if old is not None and old != p:
            check(any(h.get("price_usd") == old for h in r.get("price_history", [])), f"{rid}: superseded price {old} missing from price_history")
        if r.get("weight_reread_utc") == "2026-11-11":
            check(round(float(r["weight_g"]), 2) in seen, f"{rid}: weight marked re-read but {r['weight_g']} is not in that day's raw evidence")

    oz = spot["constants"]["troy_ounce_grams"]
    val = spot["benchmark"]["value_usd_per_oz"]
    check(abs(val - load("reviews/reread-4fe4a9c3/hand_reads.json")["benchmark"]["value_usd_per_oz"]) < 1e-9, "benchmark differs from the hand-read record")
    check(f"{val:,.2f}" in " ".join(load("reviews/reread-4fe4a9c3/hand_reads.json")["benchmark"]["verbatim"]), "benchmark figure not in the verbatim strings")
    fin = {int(t["karat"]): float(t["fineness"]) for t in method["karat_fineness"]["table"]}
    for r in rings:
        d = derived[r["id"]]
        if r.get("weight_g") is not None:
            gv = round(r["weight_g"] * fin[int(r["karat"])] * val / oz, 2)
            check(abs(gv - d["gold_value_usd"]) < 0.011, f"{r['id']}: gold value {d['gold_value_usd']} does not re-derive ({gv})")
            if r.get("price_usd") is not None:
                mult = round(r["price_usd"] / (r["weight_g"] * fin[int(r["karat"])] * val / oz), 3)
                check(abs(mult - d["price_to_gold_multiple"]) < 0.0011, f"{r['id']}: multiple does not re-derive")
        else:
            check(not d.get("gold_value_usd"), f"{r['id']}: gold value shown without a published weight")

    for f in fails:
        print("[FAIL]", f)
    print(f"RESULT: {'PASS' if not fails else 'FAIL'} — {checks} checks, {len(fails)} failures")
    print("This check proves each price dated 2026-11-11 was printed in that day's evidence. It cannot prove the evidence matches what a shopper sees now.")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
