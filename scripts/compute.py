#!/usr/bin/env python3
"""Compute derived gold values for every dataset row.

All inputs are read from data/*.json. Nothing is estimated: a derived value is
produced only when the retailer published the underlying weight, and the row is
otherwise left empty and flagged.

Output: data/derived.json  (consumed by scripts/build_site.py and audited by
scripts/audit.py, which recomputes everything independently).
"""
from __future__ import annotations

import json
import pathlib
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def load(name: str) -> dict:
    with open(DATA / name, encoding="utf-8") as fh:
        return json.load(fh)


def main() -> None:
    rings = load("rings.json")
    spot = load("gold_spot.json")
    method = load("methodology.json")

    oz_g = float(spot["constants"]["troy_ounce_grams"])
    usd_oz = float(spot["benchmark"]["value_usd_per_oz"])
    usd_g = usd_oz / oz_g

    fineness = {int(k): float(v) for k, v in
                ((r["karat"], r["fineness"]) for r in method["karat_fineness"]["table"])}
    min_fineness = {int(k): float(v) for k, v in
                    method["legal_allowable_deviation"]["minimum_fineness_if_stamped"].items()}

    rows = []
    for row in rings["rows"]:
        k = int(row["karat"])
        out = dict(row)
        out["fineness"] = round(fineness[k], 7)
        out["gold_pct"] = round(fineness[k] * 100, 4)

        if row.get("weight_g") is not None:
            w = float(row["weight_g"])
            pure = w * fineness[k]
            out["pure_gold_g"] = round(pure, 4)
            out["gold_value_usd"] = round(pure * usd_g, 2)
            out["legal_min_gold_value_usd"] = round(w * min_fineness[k] * usd_g, 2)
            if row.get("price_usd") is not None and "PRICE_INCLUDES_CENTRE_STONE" not in (row.get("flags") or []):
                p = float(row["price_usd"])
                out["price_to_gold_multiple"] = round(p / (pure * usd_g), 3)
                out["price_per_gold_gram_usd"] = round(p / pure, 2)
            else:
                # A price that includes a centre diamond is not comparable with
                # setting-only prices (PRICE_INCLUDES_CENTRE_STONE), so no
                # price-to-gold multiple is published for that row. The gold
                # content/value above describe the metal only and still stand.
                out["price_to_gold_multiple"] = None
                out["price_per_gold_gram_usd"] = None
        else:
            out["pure_gold_g"] = None
            out["gold_value_usd"] = None
            out["legal_min_gold_value_usd"] = None
            out["price_to_gold_multiple"] = None
            out["price_per_gold_gram_usd"] = None
        # Make it explicit when a price is not setting-only, so a price/gold
        # multiple is never read as a metal markup on its own.
        out["multiple_basis"] = ("includes_centre_stone"
                                 if "PRICE_INCLUDES_CENTRE_STONE" in row.get("flags", [])
                                 else "setting_metal_only")
        rows.append(out)

    # pair analysis: same design, different karat
    pairs = {}
    for r in rows:
        pid = r.get("pair_id")
        if pid:
            pairs.setdefault(pid, []).append(r)

    pair_out = []
    for pid, members in pairs.items():
        members = sorted(members, key=lambda r: r["karat"])
        if len(members) != 2:
            continue
        low, high = members[0], members[1]
        rec = {
            "pair_id": pid,
            "retailer": low["retailer"],
            "design": low["product_name"],
            "low_id": low["id"], "high_id": high["id"],
            "low_karat": low["karat"], "high_karat": high["karat"],
            "low_price": low["price_usd"], "high_price": high["price_usd"],
            "low_weight_g": low["weight_g"], "high_weight_g": high["weight_g"],
            "price_gap_usd": None, "price_gap_pct": None,
            "gold_gap_pct": None, "gold_value_gap_pct": None,
            "low_multiple": low["price_to_gold_multiple"], "high_multiple": high["price_to_gold_multiple"],
        }
        if rec["low_price"] and rec["high_price"]:
            rec["price_gap_usd"] = round(rec["high_price"] - rec["low_price"], 2)
            rec["price_gap_pct"] = round((rec["high_price"] / rec["low_price"] - 1) * 100, 2)
        if rec["low_weight_g"] and rec["high_weight_g"]:
            lo_pure = rec["low_weight_g"] * fineness[low["karat"]]
            hi_pure = rec["high_weight_g"] * fineness[high["karat"]]
            rec["low_pure_gold_g"] = round(lo_pure, 3)
            rec["high_pure_gold_g"] = round(hi_pure, 3)
            rec["gold_gap_pct"] = round((hi_pure / lo_pure - 1) * 100, 2)
            rec["gold_value_gap_pct"] = rec["gold_gap_pct"]  # same spot price
        pair_out.append(rec)

    def bucket(pred):
        sel = [r for r in rows if pred(r)]
        with_price = [r for r in sel if r.get("price_usd") is not None]
        with_weight = [r for r in sel if r.get("weight_g") is not None]
        mults = [r["price_to_gold_multiple"] for r in sel if r.get("price_to_gold_multiple")]
        return {
            "rows": len(sel),
            "prices_verified": len(with_price),
            "weights_published": len(with_weight),
            "multiple_min": round(min(mults), 2) if mults else None,
            "multiple_max": round(max(mults), 2) if mults else None,
            "multiple_avg": round(sum(mults) / len(mults), 2) if mults else None,
        }

    stats = {
        "total_rows": len(rows),
        "rows_with_verified_price": sum(1 for r in rows if r.get("price_usd") is not None),
        "rows_with_published_weight": sum(1 for r in rows if r.get("weight_g") is not None),
        "rows_with_solid_gold_statement": sum(1 for r in rows if r.get("solid_gold_status") == "stated"),
        "rows_with_hallmark_published": sum(1 for r in rows if r.get("hallmark_published")),
        "rows_with_any_flag": sum(1 for r in rows if r.get("flags")),
        "by_karat": {str(k): bucket(lambda r, k=k: int(r["karat"]) == k) for k in sorted({int(r["karat"]) for r in rows})},
        "by_category": {c: bucket(lambda r, c=c: r["category"] == c) for c in sorted({r["category"] for r in rows})},
        "by_retailer": {s: bucket(lambda r, s=s: r["retailer_id"] == s) for s in sorted({r["retailer_id"] for r in rows})},
    }

    derived = {
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "spot": {
            "value_usd_per_oz": usd_oz,
            "usd_per_gram": round(usd_g, 6),
            "price_date": spot["benchmark"]["price_date_as_shown_on_source"],
            "captured_utc": spot["benchmark"]["retrieved_utc"],
            "source_url": spot["benchmark"]["source_url"],
        },
        "constants": {
            "troy_ounce_grams": oz_g,
            "fineness": {str(k): round(v, 7) for k, v in sorted(fineness.items())},
            "min_fineness_if_stamped": {str(k): v for k, v in sorted(min_fineness.items())},
        },
        "rows": rows,
        "pairs": pair_out,
        "stats": stats,
    }

    with open(DATA / "derived.json", "w", encoding="utf-8") as fh:
        json.dump(derived, fh, indent=2, ensure_ascii=False)

    print(f"computed {len(rows)} rows; {stats['rows_with_published_weight']} with published weight; "
          f"{stats['rows_with_verified_price']} with verified price; spot ${usd_g:,.4f}/g")


if __name__ == "__main__":
    main()
