#!/usr/bin/env python3
"""Independent re-derivation audit (Pass 21 companion, session arena/91e9aba0-gold4).

WHY THIS IS SEPARATE FROM scripts/compute.py AND scripts/audit.py
-----------------------------------------------------------------
compute.py *produces* data/derived.json; audit.py re-checks it with the project's
own helpers. This script is a third implementation: it uses `decimal.Decimal`
binary-free arithmetic, reads the fineness table straight out of
data/methodology.json, and re-derives every weighted row, every karat/retailer/
category aggregate and every pair comparison from the stored inputs. It then
diffs its result against data/derived.json field by field.

It writes NOTHING to data/. It exits non-zero only on a real mismatch, so it can
be run as a gate. A mismatch is reported as a finding, never silently fixed.
"""
from __future__ import annotations

import json
import pathlib
import sys
from decimal import Decimal, getcontext, ROUND_HALF_UP

getcontext().prec = 40
ROOT = pathlib.Path(__file__).resolve().parents[2]
DATA = ROOT / "data"


def q(value: Decimal, places: int) -> Decimal:
    return value.quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP)


def load(name):
    with open(DATA / name, encoding="utf-8") as fh:
        return json.load(fh)


def main() -> int:
    rings = load("rings.json")["rows"]
    spot = load("gold_spot.json")
    method = load("methodology.json")
    derived = load("derived.json")

    oz_g = Decimal(str(spot["constants"]["troy_ounce_grams"]))
    usd_oz = Decimal(str(spot["benchmark"]["value_usd_per_oz"]))
    usd_g = usd_oz / oz_g

    fineness = {int(r["karat"]): Decimal(str(r["fineness"]))
                for r in method["karat_fineness"]["table"]}
    minimum = {int(k): Decimal(str(v)) for k, v in
               method["legal_allowable_deviation"]["minimum_fineness_if_stamped"].items()}

    checks = 0
    mismatches = []
    rounding_notes = []

    def is_aggregate(rid, field):
        """Aggregates are rounded from already-rounded 3-dp row multiples, so a
        half-way digit can legitimately land on either side. Row-level fields
        are not excused."""
        return (rid.startswith(("retailer:", "karat:", "category:"))
                or "*" == rid) and field.startswith("multiple_")

    def check(rid, field, mine, stored):
        nonlocal checks
        checks += 1
        if mine is None and stored is None:
            return
        if isinstance(mine, str) or isinstance(stored, str):
            if mine != stored:
                mismatches.append((rid, field, mine, stored))
            return
        if isinstance(mine, Decimal):
            mine = float(mine)
        if stored is None or mine is None:
            mismatches.append((rid, field, mine, stored))
            return
        if abs(float(mine) - float(stored)) > 1e-9:
            if is_aggregate(rid, field) and abs(float(mine) - float(stored)) <= 0.011:
                rounding_notes.append((rid, field, float(mine), float(stored)))
            else:
                mismatches.append((rid, field, mine, stored))

    d_rows = {r["id"]: r for r in derived["rows"]}
    if len(d_rows) != len(rings):
        mismatches.append(("*", "row_count", len(rings), len(d_rows)))

    my_rows = {}
    for row in rings:
        rid = row["id"]
        k = int(row["karat"])
        if k not in fineness:
            mismatches.append((rid, "karat_not_in_table", k, None))
            continue
        f = fineness[k]
        rec = {
            "fineness": q(f, 7),
            "gold_pct": q(f * 100, 4),
        }
        w = row.get("weight_g")
        p = row.get("price_usd")
        if w is not None:
            wd = Decimal(str(w))
            pure = wd * f
            value = pure * usd_g
            rec["pure_gold_g"] = q(pure, 4)
            rec["gold_value_usd"] = q(value, 2)
            rec["legal_min_gold_value_usd"] = q(wd * minimum[k] * usd_g, 2)
            if p is not None:
                rec["price_to_gold_multiple"] = q(Decimal(str(p)) / value, 3)
                rec["price_per_gold_gram_usd"] = q(Decimal(str(p)) / pure, 2)
            else:
                rec["price_to_gold_multiple"] = None
                rec["price_per_gold_gram_usd"] = None
        else:
            for key in ("pure_gold_g", "gold_value_usd", "legal_min_gold_value_usd",
                        "price_to_gold_multiple", "price_per_gold_gram_usd"):
                rec[key] = None
        rec["multiple_basis"] = ("includes_centre_stone"
                                 if "PRICE_INCLUDES_CENTRE_STONE" in row.get("flags", [])
                                 else "setting_metal_only")
        my_rows[rid] = rec
        stored = d_rows.get(rid)
        if stored is None:
            mismatches.append((rid, "missing_from_derived", True, False))
            continue
        for field, mine in rec.items():
            check(rid, field, mine, stored.get(field))

    # aggregates, recomputed from the raw rows
    stats = derived["stats"]

    def agg(pred):
        sel = [r for r in rings if pred(r)]
        with_price = [r for r in sel if r.get("price_usd") is not None]
        with_weight = [r for r in sel if r.get("weight_g") is not None]
        mults = [my_rows[r["id"]]["price_to_gold_multiple"] for r in sel
                 if my_rows[r["id"]]["price_to_gold_multiple"] is not None]
        return {
            "rows": len(sel),
            "prices_verified": len(with_price),
            "weights_published": len(with_weight),
            "multiple_min": q(min(mults), 2) if mults else None,
            "multiple_max": q(max(mults), 2) if mults else None,
            "multiple_avg": q(sum(mults) / Decimal(len(mults)), 2) if mults else None,
        }

    check("*", "total_rows", len(rings), stats["total_rows"])
    check("*", "rows_with_verified_price",
          sum(1 for r in rings if r.get("price_usd") is not None),
          stats["rows_with_verified_price"])
    check("*", "rows_with_published_weight",
          sum(1 for r in rings if r.get("weight_g") is not None),
          stats["rows_with_published_weight"])
    check("*", "rows_with_solid_gold_statement",
          sum(1 for r in rings if r.get("solid_gold_status") == "stated"),
          stats["rows_with_solid_gold_statement"])
    check("*", "rows_with_hallmark_published",
          sum(1 for r in rings if r.get("hallmark_published")), stats["rows_with_hallmark_published"])
    check("*", "rows_with_any_flag",
          sum(1 for r in rings if r.get("flags")), stats["rows_with_any_flag"])

    for k in sorted({int(r["karat"]) for r in rings}):
        mine = agg(lambda r, k=k: int(r["karat"]) == k)
        for field, val in mine.items():
            check(f"karat:{k}", field, val, stats["by_karat"].get(str(k), {}).get(field))
    for c in sorted({r["category"] for r in rings}):
        mine = agg(lambda r, c=c: r["category"] == c)
        for field, val in mine.items():
            check(f"category:{c}", field, val, stats["by_category"].get(c, {}).get(field))
    for s in sorted({r["retailer_id"] for r in rings}):
        mine = agg(lambda r, s=s: r["retailer_id"] == s)
        for field, val in mine.items():
            check(f"retailer:{s}", field, val, stats["by_retailer"].get(s, {}).get(field))

    # pairs: recompute the gaps
    pairs = {}
    for row in rings:
        if row.get("pair_id"):
            pairs.setdefault(row["pair_id"], []).append(row)
    stored_pairs = {p["pair_id"]: p for p in derived["pairs"]}
    checked_pairs = 0
    for pid, members in pairs.items():
        if len(members) != 2:
            continue
        members = sorted(members, key=lambda r: int(r["karat"]))
        lo, hi = members
        sp = stored_pairs.get(pid)
        if sp is None:
            mismatches.append((pid, "pair_missing", True, False))
            continue
        checked_pairs += 1
        lp, hp = lo.get("price_usd"), hi.get("price_usd")
        if lp and hp:
            check(pid, "price_gap_usd", q(Decimal(str(hp)) - Decimal(str(lp)), 2), sp.get("price_gap_usd"))
            check(pid, "price_gap_pct",
                  q((Decimal(str(hp)) / Decimal(str(lp)) - 1) * 100, 2), sp.get("price_gap_pct"))
        lw, hw = lo.get("weight_g"), hi.get("weight_g")
        if lw and hw:
            lo_pure = Decimal(str(lw)) * fineness[int(lo["karat"])]
            hi_pure = Decimal(str(hw)) * fineness[int(hi["karat"])]
            gpct = q((hi_pure / lo_pure - 1) * 100, 2)
            check(pid, "gold_gap_pct", gpct, sp.get("gold_gap_pct"))
            check(pid, "gold_value_gap_pct", gpct, sp.get("gold_value_gap_pct"))
            check(pid, "low_pure_gold_g", q(lo_pure, 3), sp.get("low_pure_gold_g"))
            check(pid, "high_pure_gold_g", q(hi_pure, 3), sp.get("high_pure_gold_g"))

    # spot block must match the benchmark file it claims to come from
    check("*", "spot.value_usd_per_oz",
          spot["benchmark"]["value_usd_per_oz"], derived["spot"]["value_usd_per_oz"])
    check("*", "spot.usd_per_gram", q(usd_g, 6), derived["spot"]["usd_per_gram"])

    weighted = sum(1 for r in rings if r.get("weight_g") is not None)
    print(f"independent Decimal re-derivation | {len(rings)} rows, {weighted} weighted, "
          f"{checked_pairs} karat pairs | {checks} field comparisons")
    print(f"benchmark in force: USD {usd_oz}/oz = USD {q(usd_g, 5)}/g ("
          f"{spot['benchmark']['price_date_as_shown_on_source']})")
    if rounding_notes:
        print(f"NOTE: {len(rounding_notes)} aggregate value(s) differ by one hundredth "
              f"(half-way rounding path, not a data error):")
        for n in rounding_notes:
            print(f"    {n[0]} {n[1]}: exact-decimal {n[2]} vs stored {n[3]}")
    if mismatches:
        print(f"FAIL: {len(mismatches)} mismatch(es)")
        for m in mismatches:
            print("   ", m)
        return 1
    print("PASS: every derived value, aggregate and pair gap re-derives to the stored figure")
    print("LIMIT: this proves internal arithmetic only. It cannot prove the store's price or the "
          "seller's weight is true; that needs the live page read in section 58/59.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
