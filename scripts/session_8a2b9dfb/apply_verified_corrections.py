#!/usr/bin/env python3
"""Idempotent, narrowly scoped correction with first-hand evidence provenance.

Only MN-01/MN-02 solid-wording metadata/labels/flags and BE-05 price provenance change.
No price amount, metal, weight, product URL or other row is changed. Source
observations were read during this session; this script does not fetch or infer.
"""
from copy import deepcopy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "data/rings.json"
REVIEW = "readiness_review_8a2b9dfb"


def main():
    raw = PATH.read_text(encoding="utf-8")
    doc = json.loads(raw)
    changed = []
    for row in doc["rows"]:
        titles = {"MN-01": "Knot Ring", "MN-02": "Etruscan Sun Band"}
        if row.get(REVIEW):
            if row["id"] in titles and row["product_name"] != titles[row["id"]]:
                row[REVIEW]["prior_descriptive_product_name"] = row["product_name"]
                row[REVIEW]["fields_reviewed"].append("product_name")
                row["product_name"] = titles[row["id"]]
                changed.append(row["id"] + " (remove unsupported solid wording from descriptive label)")
            continue
        if row["id"] in {"MN-01", "MN-02"}:
            row[REVIEW] = {
                "review_date_utc": "2026-10-23", "fields_reviewed": ["solid_gold_statement", "solid_gold_status", "product_name"],
                "prior_descriptive_product_name": row["product_name"],
                "source_url": row["url"], "source_chunks_reviewed": [0],
                "prior_solid_gold_statement": row.get("solid_gold_statement"),
                "prior_solid_gold_status": row.get("solid_gold_status"),
                "note": "The recorded wording Pure 24k Gold sold by weight with Certificate of Authenticity does not explicitly say solid. Withhold solid-wording credit rather than infer construction from purity, a certificate or a product name. The reviewed product block identifies 24k Gold and Crafted-on-Demand; this is not a claim about every part of the website and not a physical-construction finding. Price/weight captures and source-health evidence are unchanged. See R8-SOLID-01 and the dated official-source observation record.",
            }
            row["product_name"] = titles[row["id"]]
            row["solid_gold_statement"] = None
            row["solid_gold_status"] = "not_stated"
            if "SOLID_NOT_STATED" not in row["flags"]:
                row["flags"].append("SOLID_NOT_STATED")
            changed.append(row["id"])
        elif row["id"] == "BE-05":
            assert row["price_usd"] == 1190.0, "Never silently replace a different price"
            row[REVIEW] = {
                "review_date_utc": "2026-10-23", "fields_reviewed": ["price_verification", "price_captured_utc", "price_basis"],
                "source_url": row["price_source_url"], "source_chunks_reviewed": [0, 2, 3, 4, 5],
                "price_evidence_chunk": 4,
                "prior_price_observation": {key: deepcopy(row.get(key)) for key in (
                    "price_usd", "price_basis", "price_captured_utc", "price_verification", "price_source_url")},
                "observed_currency": "USD", "observed_setting_price_usd": 1190.0,
                "note": "First-hand official-page read before midnight UTC on 23 October: currency selector USD; Freesia Hidden Halo Diamond Ring in 14K Yellow Gold; $1,190 (Setting Only); BE1D3939-14KY. This corroborates the unchanged setting amount and upgrades V2 to V1. No ring size or centre diamond was selected, so it is not a final configured-ring or checkout quote. Weight stays blank. Prior EUR/localization observations and the historical runner's 403 remain intact; browser and runner outcomes differ.",
            }
            row["price_verification"] = "V1_direct_page_fetch"
            row["price_captured_utc"] = "2026-10-23"
            row["price_basis"] = "USD $1,190 (Setting Only), first-hand official-page read 2026-10-23; ring size/centre diamond unselected. Not a final configured-ring or checkout quote."
            row["flags"] = [flag for flag in row["flags"] if flag != "PRICE_V2_ONLY"]
            row["reverification"] = row.get("reverification", "") + " R8 (2026-10-23, arena/8a2b9dfb-gold4): first-hand official product chunk 4 finally rendered USD and $1,190 (Setting Only), style BE1D3939-14KY, 14K Yellow Gold. V2 upgraded to V1 without changing the amount. Selected ring size/centre diamond and gram weight remain unconfirmed. Historical currency-localization and runner-403 evidence preserved."
            changed.append(row["id"])
    if changed:
        # Match the canonical file's existing one-space indentation / ASCII style.
        PATH.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("Verified corrections applied: " + (", ".join(changed) if changed else "already applied (no change)"))


if __name__ == "__main__":
    main()
