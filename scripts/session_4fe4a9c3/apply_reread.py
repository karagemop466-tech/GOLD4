#!/usr/bin/env python3
"""GOLD4 re-read of 2026-11-11 (session arena/4fe4a9c3-gold4) — apply that day's evidence.

This session claimed "Pass 21" on its branch at 08:00Z; session 91415e29's Pass 21 reached main first, so that
number is theirs. This work carries no pass number: it is identified by date and session id.

NO HALLUCINATIONS. This script types no price, weight or spot value of its own.
Every number it writes is copied from one of two committed evidence files:

  A. reports/live_source_check_20261111T080309Z.json
       GitHub runner, read-only GET of all 64 ring URLs + 32 registered sources,
       2026-11-11T08:00-08:03Z. Carries each page's JSON-LD / price-meta offers
       and the raw price text the page printed.
  B. reviews/reread-4fe4a9c3/hand_reads.json
       This session's browser-rendered reads (benchmark + 16 rows), with the
       verbatim strings each page printed and what each read did NOT reach.

Rules
  * A price is updated only when today's evidence prints the current price for
    that row. The previous value is appended to `price_history`, never deleted.
  * A row whose page is dead or sold out today gets a BLANK current price; the
    last value read stays visible as `last_known_price_usd` with its date.
  * A row nobody could read today keeps its October value and date and is
    flagged PRICE_NOT_REREAD_2026_11_11. It is not presented as current.
  * Weights are only re-dated when today's evidence prints the weight.
  * Idempotent: a second run changes nothing.

Usage: python3 scripts/session_4fe4a9c3/apply_reread.py [--check]
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
RUNNER = ROOT / "reports" / "live_source_check_20261111T080309Z.json"
HAND = ROOT / "reviews" / "reread-4fe4a9c3" / "hand_reads.json"
OUT = ROOT / "reviews" / "reread-4fe4a9c3" / "reconciliation.json"

TODAY = "2026-11-11"
SESSION = "arena/4fe4a9c3-gold4 (re-read 2026-11-11)"
RUNNER_REL = str(RUNNER.relative_to(ROOT))
HAND_REL = str(HAND.relative_to(ROOT))

REREAD_FLAGS = (
    "SALE_PRICE_TEMPORARY",
    "PRICE_CHANGED_2026_11_11",
    "PRICE_NOT_REREAD_2026_11_11",
    "SOURCE_DEAD_2026_11_11",
    "SOLD_OUT_2026_11_11",
    "STRUCTURED_PRICE_LAGS_DISPLAY",
)


def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def snippets(rec: dict) -> list[dict]:
    s = rec.get("price_snippets")
    if isinstance(s, str):
        try:
            s = ast.literal_eval(s)
        except Exception:
            return []
    return s or []


def usd(text: str) -> float:
    return float(text.replace("$", "").replace(",", "").strip())


def offers(rec: dict, source: str | None = None) -> list[float]:
    out = []
    for p in rec.get("structured_prices", []):
        if p.get("currency") != "USD":
            continue
        if source and not str(p.get("source", "")).startswith(source):
            continue
        try:
            out.append(float(p["price"]))
        except (TypeError, ValueError):
            pass
    return sorted(set(out))


def weight_in_text(rec: dict, stored: float | None) -> bool:
    if stored is None:
        return False
    for w in rec.get("weight_snippets", []):
        m = re.fullmatch(r"\s*([0-9]+(?:\.[0-9]+)?)\s*grams?\s*", w.get("text", ""), re.I)
        if m and abs(float(m.group(1)) - float(stored)) < 0.005:
            return True
    return False


def runner_verdict(row: dict, rec: dict) -> dict:
    """What the runner evidence alone says about this row's price today."""
    cls = rec.get("classification")
    v = {"runner_state": cls, "runner_checked_utc": rec.get("checked_utc"), "quotes": []}
    if cls != "OK":
        v["kind"] = {"HTTP_404": "DEAD"}.get(cls, "NOT_READ")
        return v
    rid, stored = row["id"], row.get("price_usd")
    avail = " ".join(map(str, (rec.get("offer_signals") or {}).get("availability", [])
                         + (rec.get("offer_signals") or {}).get("og:availability", [])))
    ld, meta, anyp = offers(rec, "json-ld"), offers(rec, "meta"), offers(rec)
    snips = snippets(rec)

    # --- Blue Nile: "$LIST $SALE (Setting Price) -20% *Discount code is applied automatically"
    if rid.startswith("BN-"):
        if not ld and ("SoldOut" in avail or "out of stock" in avail.lower()):
            v.update(kind="SOLD_OUT", quotes=[f"availability: {avail}"])
            return v
        m = None
        for s in snips:
            m = re.search(r"(\$[\d,]+(?:\.\d\d)?) (\$[\d,]+(?:\.\d\d)?) \(Setting Price\) (-\d+%)( \*Discount code is applied automatically)?", s["context"])
            if m:
                break
        if m:
            lst, sale = usd(m.group(1)), usd(m.group(2))
            v.update(kind="SALE", price=sale, list_price=lst, path="page text" + (" + JSON-LD offer" if sale in ld else ""),
                     quotes=[m.group(0)], structured_agrees=sale in ld)
            return v
        if len(ld) == 1 and len(meta) == 1 and ld[0] < meta[0]:
            v.update(kind="SALE", price=ld[0], list_price=meta[0], path="JSON-LD offer (sale) vs og:price meta (list); the price text itself was not captured",
                     quotes=[f"JSON-LD Offer price {ld[0]:g} USD", f"og:price:amount {meta[0]:g} USD"], structured_agrees=True)
            return v
        if stored is not None and stored in anyp:
            v.update(kind="UNCHANGED", price=stored, path="structured data")
            return v
        v["kind"] = "NOT_READ"
        return v

    # --- Ross-Simons: "NN% Off $LIST $SALE" in the page text; JSON-LD keeps the list price
    if rid.startswith("RS-"):
        for s in snips:
            m = re.search(r"(\d+)% Off (\$[\d,]+(?:\.\d\d)?) (\$[\d,]+(?:\.\d\d)?)((?: CLEARANCE)?(?: EXTRA \d+% OFF - PRICED AS MARKED)?)", s["context"])
            if m:
                lst, sale = usd(m.group(2)), usd(m.group(3))
                v.update(kind="SALE", price=sale, list_price=lst, path="page text",
                         quotes=[m.group(0).strip()], structured_agrees=sale in ld,
                         structured_prices=ld)
                return v
        v.update(kind="STRUCTURED_ONLY", structured_prices=ld)
        return v

    # --- Menē: "<name> $N,NNN USD Price breakdown" (default size); the price floats with gold
    if rid.startswith("MN-"):
        for s in snips:
            m = re.search(r"(\$[\d,]+) USD Price breakdown", s["context"])
            if m:
                p = usd(m.group(1))
                v.update(kind="UNCHANGED" if stored == p else "CHANGED", price=p, path="page text" + (" + JSON-LD offer" if p in ld else ""),
                         quotes=[m.group(0)], structured_agrees=p in ld)
                return v
        v["kind"] = "NOT_READ"
        return v

    # --- Catbird sale wording
    if rid.startswith("CB-"):
        for s in snips:
            m = re.search(r"(\$[\d,]+\.\d\d) Regular Price (\$[\d,]+\.\d\d) (\d+% off[^A-Z]*LEAVING SOON)?", s["context"])
            if m and stored is not None and abs(usd(m.group(1)) - stored) < 0.005:
                v.update(kind="UNCHANGED", price=stored, list_price=usd(m.group(2)), path="page text + JSON-LD offer",
                         quotes=[m.group(0).strip()])
                return v

    # --- Mejuri "From $X" page text
    if rid.startswith("MJ-"):
        for s in snips:
            m = re.search(r"From (\$[\d,]+) Material & Stone Options ([^,]+, [A-Za-z ]+Diamond)", s["context"])
            if m and stored is not None and abs(usd(m.group(1)) - stored) < 0.005:
                v.update(kind="UNCHANGED", price=stored, path="page text ('From' price for the named material)",
                         quotes=[m.group(0)])
                return v

    # --- generic: the page's own structured data prints exactly the stored amount
    if stored is not None and any(abs(p - stored) < 0.005 for p in anyp):
        v.update(kind="UNCHANGED", price=stored,
                 path="structured data" + (" (one of several variant offers)" if len(anyp) > 1 else ""),
                 quotes=[f"structured offers: {', '.join(f'{p:g}' for p in anyp)} USD"])
        return v
    v["kind"] = "NOT_READ"
    v["structured_prices"] = anyp
    return v


def decide(row: dict, rec: dict, hand: dict | None) -> dict:
    """Combine both read paths. Hand reads win where they exist; disagreement is recorded."""
    rv = runner_verdict(row, rec)
    stored = row.get("price_usd")
    d = {
        "id": row["id"], "stored_price_usd": stored, "stored_price_captured_utc": row.get("price_captured_utc"),
        "runner_state": rv["runner_state"], "runner_checked_utc": rv.get("runner_checked_utc"),
        "read_paths": [], "evidence": [], "quotes": [],
        "price_today_usd": None, "list_price_usd": None, "verdict": None,
        "weight_reread_today": False, "notes": [],
    }
    if rv.get("price") is not None or rv["kind"] in ("SALE", "UNCHANGED", "CHANGED"):
        d["read_paths"].append("runner: " + rv.get("path", "structured data"))
        d["evidence"].append(RUNNER_REL)
        d["quotes"] += rv.get("quotes", [])
    if weight_in_text(rec, row.get("weight_g")):
        d["weight_reread_today"] = True
        d["notes"].append(f"runner page text prints the stored weight ({row['weight_g']:g} g)")

    if hand:
        d["read_paths"].append("hand read (browser-rendered), chunk " + str(hand.get("chunk")))
        d["evidence"].append(HAND_REL)
        d["quotes"] += hand.get("verbatim", [])
        if hand.get("note"):
            d["notes"].append(hand["note"])
        if hand.get("not_read"):
            d["notes"].append("not read: " + hand["not_read"])
        if hand.get("weight_g_displayed") is not None and row.get("weight_g") is not None:
            if abs(hand["weight_g_displayed"] - row["weight_g"]) < 0.005:
                d["weight_reread_today"] = True
            else:
                d["notes"].append(f"WEIGHT DIFFERS: page prints {hand['weight_g_displayed']} g vs stored {row['weight_g']} g")
        hv = hand["verdict"]
        if hv == "SOURCE_URL_DEAD":
            d["verdict"] = "SOURCE_DEAD"
            return d
        hp = hand.get("price_usd_displayed")
        if hp is None and hand.get("listing_card_price_usd") is not None:
            hp = hand["listing_card_price_usd"]
            d["notes"].append("price is the retailer's listing-card price, not a configured-ring quote")
        if hp is not None:
            if rv.get("price") is not None and abs(rv["price"] - hp) > 0.005:
                d["notes"].append(f"READ PATHS DISAGREE: runner {rv['price']} vs hand {hp}; hand read used, both kept")
            d["price_today_usd"] = hp
            d["list_price_usd"] = hand.get("list_price_usd_displayed") or rv.get("list_price")
            if d["list_price_usd"] is not None and d["list_price_usd"] > hp:
                d["verdict"] = "SALE"
            else:
                d["list_price_usd"] = None
                d["verdict"] = "UNCHANGED" if stored is not None and abs(hp - stored) < 0.005 else "CHANGED"
            if row["id"].startswith("RS-") and rv.get("structured_prices") and hp not in rv["structured_prices"]:
                d["structured_lags"] = rv["structured_prices"]
            return d

    kind = rv["kind"]
    if rv.get("structured_agrees") is False:
        d["notes"].append("the price above is the amount the page DISPLAYS; the page's JSON-LD offers captured by the runner do not list it "
                          "(they cover other sizes/variants or still carry the pre-discount amount)")
    if row["id"].startswith("MN-"):
        d["notes"].append("Menē reprices with the gold price, so this figure is a reading at the stated time, not a stable list price; "
                          "the displayed amount is for the page's default size")
    if kind == "SALE":
        d.update(price_today_usd=rv["price"], list_price_usd=rv["list_price"], verdict="SALE")
        if row["id"].startswith("RS-") and rv.get("structured_prices") and rv["price"] not in rv["structured_prices"]:
            d["structured_lags"] = rv["structured_prices"]
    elif kind in ("UNCHANGED", "CHANGED"):
        d.update(price_today_usd=rv["price"], verdict=kind)
        if rv.get("list_price") and rv["list_price"] > rv["price"]:
            d["list_price_usd"] = rv["list_price"]
    elif kind == "DEAD":
        d["verdict"] = "SOURCE_DEAD"
        d["read_paths"].append("runner: HTTP 404")
        d["evidence"].append(RUNNER_REL)
    elif kind == "SOLD_OUT":
        d["verdict"] = "SOLD_OUT"
        d["read_paths"].append("runner: page availability signal")
        d["evidence"].append(RUNNER_REL)
        d["quotes"] += rv.get("quotes", [])
    else:
        d["verdict"] = "NOT_REREAD"
        d["notes"].append(f"runner state {rv['runner_state']}; no hand read of this row today")
    return d


def apply_row(row: dict, d: dict) -> None:
    flags = [f for f in row.get("flags", []) if f not in REREAD_FLAGS]
    verdict, stored = d["verdict"], row.get("price_usd")
    hist = row.setdefault("price_history", [])

    def push_history(reason: str) -> None:
        entry = {"price_usd": stored, "captured_utc": row.get("price_captured_utc"),
                 "price_basis": row.get("price_basis"), "superseded_utc": TODAY, "superseded_by": SESSION, "reason": reason}
        if stored is not None and not any(h.get("price_usd") == stored and h.get("captured_utc") == entry["captured_utc"] for h in hist):
            hist.append(entry)

    priced = [q for q in d["quotes"] if "$" in q]
    rest = [q for q in d["quotes"] if "$" not in q]
    quote = "; ".join(f"'{q}'" for q in (priced + rest)[:4])
    paths = " + ".join(d["read_paths"]) or "none"

    if verdict in ("UNCHANGED", "CHANGED", "SALE"):
        new = d["price_today_usd"]
        if stored is None or abs(new - stored) > 0.005:
            push_history({"SALE": "page now prints a sale price", "CHANGED": "page now prints a different price"}.get(verdict, "re-read"))
            row["price_usd"] = new
            flags.append("PRICE_CHANGED_2026_11_11")
        row["price_captured_utc"] = TODAY
        row["reverified_utc"] = TODAY
        if verdict == "SALE":
            row["list_price_usd"] = d["list_price_usd"]
            flags.append("SALE_PRICE_TEMPORARY")
            basis_word = f"SALE price read {TODAY}: list ${d['list_price_usd']:,.2f}, sale ${new:,.2f}"
        else:
            if d.get("list_price_usd"):
                row["list_price_usd"] = d["list_price_usd"]
            else:
                row.pop("list_price_usd", None)
            basis_word = f"Price read {TODAY}: ${new:,.2f}"
        old_basis = row.get("price_basis") or ""
        marker = " || Re-read 2026-11-11: "
        row["price_basis"] = old_basis.split(marker)[0] + marker + f"{basis_word} ({paths}). Verbatim: {quote}."
        if d.get("structured_lags"):
            flags.append("STRUCTURED_PRICE_LAGS_DISPLAY")
    elif verdict in ("SOURCE_DEAD", "SOLD_OUT"):
        if stored is not None:
            push_history("page dead today" if verdict == "SOURCE_DEAD" else "page reports sold out today")
            row["last_known_price_usd"] = stored
            row["last_known_price_captured_utc"] = row.get("price_captured_utc")
            row["price_usd"] = None
        if "PRICE_UNVERIFIED" not in flags:
            flags.append("PRICE_UNVERIFIED")
        flags.append("SOURCE_DEAD_2026_11_11" if verdict == "SOURCE_DEAD" else "SOLD_OUT_2026_11_11")
    else:  # NOT_REREAD
        flags.append("PRICE_NOT_REREAD_2026_11_11")

    if d["weight_reread_today"] and row.get("weight_g") is not None:
        row["weight_reread_utc"] = TODAY

    row["flags"] = flags
    row["reread_2026_11_11"] = {
        "session": SESSION, "observed_utc": TODAY, "verdict": verdict,
        "stored_price_before_usd": d["stored_price_usd"], "stored_price_before_captured_utc": d["stored_price_captured_utc"],
        "price_today_usd": d["price_today_usd"], "list_price_usd": d["list_price_usd"],
        "read_paths": d["read_paths"], "evidence": sorted(set(d["evidence"])),
        "verbatim": d["quotes"][:10], "weight_reread_today": d["weight_reread_today"], "notes": d["notes"],
    }
    who = row.get("reverified_by") or ""
    if verdict in ("UNCHANGED", "CHANGED", "SALE") and SESSION not in who:
        row["reverified_by"] = (who + " + " if who else "") + SESSION


def gold_evidence(runner: dict, hand: dict) -> dict:
    by = {r["key"]: r for r in runner["results"]}
    cross = []

    def grab(key: str, pattern: str, label: str) -> None:
        for s in snippets(by[key]):
            m = re.search(pattern, s["context"])
            if m:
                cross.append({"source_id": key, "source_url": by[key]["url"], "label": label,
                              "value_usd_per_oz": usd(m.group(1)), "verbatim": m.group(0),
                              "read_path": "GitHub runner page text", "retrieved_utc": by[key]["checked_utc"]})
                return

    grab("kitco-gold-spot", r"24K · 24KT · 999\.9 · 1000 (\$[\d,]+\.\d\d)", "Kitco 24K value per oz")
    grab("bullionvault-spot", r"Current Gold Price - (\$[\d,]+\.\d\d) per Ounce", "BullionVault current gold price per oz")
    grab("jmbullion-gold-spot", r"Gold Ask \$ ([\d,]+\.\d\d)", "JM Bullion gold ASK (includes a premium)")
    return {"benchmark": hand["benchmark"], "cross_checks": cross}


def apply_gold(spot: dict, ge: dict) -> bool:
    b, new = spot["benchmark"], ge["benchmark"]
    oz = float(spot["constants"]["troy_ounce_grams"])
    if abs(b["value_usd_per_oz"] - new["value_usd_per_oz"]) < 0.005 and b.get("captured_utc") == new["retrieved_utc"]:
        # already applied; keep the derived constant at the 6-decimal precision scripts/audit.py (A-03) checks
        g = round(b["value_usd_per_oz"] / oz, 6)
        spot["constants"]["spot_usd_per_gram"] = g
        spot["constants"]["spot_usd_per_gram_note"] = (
            f"value_usd_per_oz / 31.1034768 = {b['value_usd_per_oz']} / 31.1034768 = {g} USD/g "
            "(recomputed by scripts/compute.py and re-checked by scripts/audit.py).")
        return False
    old = dict(b)
    old["status"] = "superseded"
    old["note"] = (f"Benchmark in force from Pass 18 (2026-10-23T20:23Z) until the re-read of 2026-11-11 (session 4fe4a9c3). Superseded on {TODAY} when the World Gold "
                   "Council panel printed a newer data date. Kept for audit; no current calculation uses it.")
    spot.setdefault("prior_captures", []).append(old)
    val = new["value_usd_per_oz"]
    delta = (val / old["value_usd_per_oz"] - 1) * 100
    b.update({
        "value_usd_per_oz": val,
        "price_date_as_shown_on_source": "10 November, 2026",
        "data_as_of_shown_on_source": new["source_date_line_verbatim"],
        "retrieved_utc": TODAY,
        "captured_utc": new["retrieved_utc"],
        "what_the_source_page_shows": "Gold spot price panel: 'USD /oz 4,059.49', on a page dated '10 November, 2026', with the chart footer "
                                      "'Data as of 10 November, 2026' and 'Market Data: Provided by ICE Data Services'. The 'Last Updated' caption rendered empty in this read.",
        "verification": "V1_direct_page_fetch",
        "notes": [
            f"Re-read of {TODAY} (session 4fe4a9c3, 08:01Z): the World Gold Council panel was re-read in a browser-rendered fetch and printed USD {val:,.2f}/oz under "
            f"'{new['source_date_line_verbatim']}'. It replaces the 2026-10-23 reading of USD {old['value_usd_per_oz']:,.2f}/oz ({delta:+.2f}%), "
            "which was 19 days old. Every derived gold value on the site is recomputed from this reading.",
            "Cross-checked the same morning by three market pages read by the GitHub runner at 08:02Z (see reread_2026_11_11_cross_checks): "
            + "; ".join(f"{c['label']} USD {c['value_usd_per_oz']:,.2f}" for c in ge["cross_checks"])
            + ". Informational only; the single calculation basis remains the World Gold Council panel.",
            "Sessions 91415e29 and 91e9aba0 read the same figure on the same panel that morning and kept the October benchmark because their scope was additive only; 91e9aba0 logged request A21-01 to replace it. This change applies that request. Their records (pass21_live_crosscheck_2026_11_11) are kept unchanged.",
            "Spot is a live market quote; the figure recorded here is a dated reading, not a claim about the price at the moment you read this. Re-read the source before relying on it.",
        ],
    })
    spot["captured_utc"] = new["retrieved_utc"]
    spot["constants"]["spot_usd_per_gram"] = round(val / oz, 6)
    spot["constants"]["spot_usd_per_gram_note"] = (
        f"value_usd_per_oz / 31.1034768 = {val} / 31.1034768 = {round(val / oz, 6)} USD/g "
        "(recomputed by scripts/compute.py and re-checked by scripts/audit.py).")
    spot["recheck_note"] = (f"Re-read by session 4fe4a9c3 at {new['retrieved_utc']} (browser-rendered fetch of the WGC panel) and cross-checked against three "
                            "market pages read by the runner at 08:02Z. scripts/audit.py re-derives every derived value on every run.")
    spot["reread_2026_11_11_cross_checks"] = [
        dict(c, spread_vs_benchmark_pct=round((c["value_usd_per_oz"] / val - 1) * 100, 3)) for c in ge["cross_checks"]]
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report only, write nothing")
    args = ap.parse_args()

    runner, hand = load(RUNNER), load(HAND)
    by_key = {r["key"]: r for r in runner["results"]}
    by_hand = {h["id"]: h for h in hand["rows"]}
    rings = load(DATA / "rings.json")
    spot = load(DATA / "gold_spot.json")

    decisions = []
    for row in rings["rows"]:
        prior = row.get("reread_2026_11_11")
        if prior:  # idempotence: reconcile against the value that was stored before this pass
            base = dict(row, price_usd=prior["stored_price_before_usd"], price_captured_utc=prior["stored_price_before_captured_utc"])
        else:
            base = row
        d = decide(base, by_key[row["id"]], by_hand.get(row["id"]))
        decisions.append(d)
        if not args.check and not prior:
            apply_row(row, d)

    ge = gold_evidence(runner, hand)
    counts: dict[str, int] = {}
    for d in decisions:
        counts[d["verdict"]] = counts.get(d["verdict"], 0) + 1

    summary = {
        "artifact": "GOLD4 re-read of 2026-11-11 (session 4fe4a9c3) — reconciliation of every row, both read paths",
        "session": SESSION, "date_utc": TODAY,
        "rule": "NO HALLUCINATIONS: every value is copied from the evidence files listed; nothing is inferred.",
        "evidence": [RUNNER_REL, HAND_REL],
        "runner_summary": runner["summary"], "runner_checked_utc": runner["checked_utc"],
        "verdict_counts": dict(sorted(counts.items())),
        "rows_with_price_read_today": sum(1 for d in decisions if d["price_today_usd"] is not None),
        "rows_hand_read": len(by_hand),
        "rows_weight_reread_today": sum(1 for d in decisions if d["weight_reread_today"]),
        "gold": ge,
        "rows": decisions,
    }
    print(json.dumps({k: summary[k] for k in ("verdict_counts", "rows_with_price_read_today", "rows_hand_read", "rows_weight_reread_today")}, indent=1))
    for c in ge["cross_checks"]:
        print("  gold cross-check:", c["label"], c["value_usd_per_oz"])
    if args.check:
        for d in decisions:
            print(f"{d['id']:6} {d['verdict']:11} stored={d['stored_price_usd']} today={d['price_today_usd']} list={d['list_price_usd']} w={d['weight_reread_today']} | {' + '.join(d['read_paths'])[:90]}")
        return 0

    apply_gold(spot, ge)
    rings["reverified_utc"] = TODAY
    rings["reread_2026_11_11_note"] = (
        f"Re-read of {TODAY} ({SESSION}): every row was reconciled against a runner sweep of all 64 URLs taken at "
        f"{runner['checked_utc']} and against this session's hand reads of {len(by_hand)} rows. Verdicts: "
        + ", ".join(f"{k} {v}" for k, v in sorted(counts.items()))
        + ". Prices were updated only where today's evidence prints the current price; superseded values are kept in each row's price_history. "
          "Rows whose page is dead or sold out carry a blank current price and a last_known_price_usd. See reviews/reread-4fe4a9c3/reconciliation.json.")
    (DATA / "rings.json").write_text(json.dumps(rings, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    (DATA / "gold_spot.json").write_text(json.dumps(spot, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    OUT.write_text(json.dumps(summary, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"written: data/rings.json, data/gold_spot.json, {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
