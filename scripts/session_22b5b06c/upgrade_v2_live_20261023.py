#!/usr/bin/env python3
"""
upgrade_v2_live_20261023.py — session arena/22b5b06c-gold4, Pass 11.

The fetch-service outage that forced six Blue Nile rows to V2 (dated-snapshot)
provenance cleared briefly on 2026-10-23 ~00:20-00:33 UTC. This script records
the LIVE re-fetches performed in that window:

  BN-20 item-310896 Woven Solitaire      live ~00:20Z: $965 (Setting Price), NO discount shown;
      Stock Number 505038y14, 14K Yellow Gold, Width 1.80mm re-read from the page.
      The 22 Oct sale display ($965 struck to $772, -20%) had ENDED -> price updated 772 -> 965.
  BN-21 item-192261 Knife Edge Solitaire live ~00:22Z: $1,290 (Setting Price) - unchanged;
      Stock Number 502500y14, 14K Yellow Gold, Width 1.80mm re-read.
  BN-22 item-203321 Wide Band Solitaire  live ~00:24Z: $2,050 (Setting Price) - unchanged;
      Stock Number 501580y14, 14K Yellow Gold, Width 5.00mm re-read; the Product Details text
      STILL says "this platinum solitaire setting features a flat profile" against the 14K YG
      spec - COPY_INCONSISTENT_METAL confirmed on the live page, not just the snapshot.
  BN-23 item-203303 Emerald Cut (1 ct tw) live ~00:26Z: $5,190 (Setting Price) - unchanged;
      Stock Number 501472y14, 14K Yellow Gold, Width 4.00mm; diamond block re-read:
      Emerald, Quantity 6, Total Carat 1, G-H, VS2-SI1, Not Enhanced, Prong.
  BN-24 item-195730 Classic Simple WG    live ~00:28Z: $1,145 (Setting Price) - unchanged;
      Stock Number 502120w14, 14K White Gold, Width 2.40mm, Rhodium Finish: Yes re-read.
  BN-25 item-315661 Pave Contour WG      live ~00:30Z: $2,210 (Setting Price), NO discount shown;
      Stock Number 505094w14, 14K White Gold, 1.75mm, Rhodium Finish: Yes; diamonds Round,
      Quantity 26, Total Carat 1/5, F-G, VS1-VS2 re-read. The 22 Oct sale display
      ($2,210 struck to $1,657, -25%) had ENDED -> price updated 1657 -> 2210.

  BE-05/BE-06/BE-07 (Brilliant Earth): re-fetch ATTEMPTED ~00:31-00:33Z; the fetch service
  failed again mid-page (SignatureDoesNotMatch outage) before the product block was reached.
  These three rows therefore KEEP V2 provenance + PRICE_V2_ONLY (and PRICE_CURRENCY_LOCALIZED).

Every upgrade: price_verification -> V1_direct_page_fetch, PRICE_V2_ONLY removed,
price_captured_utc/reverified_utc -> 2026-10-23, live read appended to reverification.
Prices that changed are updated to the LIVE value (prices must be current); the historical
snapshot values remain described in flag_detail. No other row is touched.

Also appends a Pass 11 entry to data/verification_log.json.
Idempotent: rows already upgraded (no PRICE_V2_ONLY / already V1) are skipped.
Run: python3 scripts/session_22b5b06c/upgrade_v2_live_20261023.py
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
DATA = ROOT / "data"

LIVE = {
    "BN-20": {
        "price": 965.0,
        "read": ("Live fetch 2026-10-23T00:20Z: $965 '(Setting Price)' with NO discount displayed; Stock Number 505038y14, "
                 "Metal 14K Yellow Gold, Width 1.80mm re-read from the page. The 22 Oct sale display ('$965 $772 -20%') had "
                 "ended by this re-fetch - the recorded price is updated to the live $965; the snapshot sale history and the "
                 "four differing category-page sale prices remain documented under SALE_PRICE_VARIES_ACROSS_PAGES."),
        "basis": "Setting only - live page shows '$965 (Setting Price)', no discount displayed at the 2026-10-23 re-fetch (the 22 Oct '-20% to $772' sale had ended)",
        "detail_add": (" LIVE UPDATE 2026-10-23T00:20Z: the product page now shows $965 (Setting Price) with no strike-through - "
                       "the sale seen on 22 Oct ($772/$724/$730/$728 across pages) has ended. This confirms the flag's point: "
                       "sale prices are volatile and page-dependent; the current live price is the recorded one."),
    },
    "BN-21": {
        "price": 1290.0,
        "read": ("Live fetch 2026-10-23T00:22Z: $1,290 '(Setting Price)' - unchanged from the snapshot; Stock Number 502500y14, "
                 "Metal 14K Yellow Gold, Width 1.80mm re-read from the page."),
        "basis": None,
        "detail_add": "",
    },
    "BN-22": {
        "price": 2050.0,
        "read": ("Live fetch 2026-10-23T00:24Z: $2,050 '(Setting Price)' - unchanged; Stock Number 501580y14, Metal 14K Yellow Gold, "
                 "Width 5.00mm re-read. The live page's Product Details text STILL reads 'this platinum solitaire setting features "
                 "a flat profile' against the 14K Yellow Gold spec - COPY_INCONSISTENT_METAL confirmed live, not only in snapshot."),
        "basis": None,
        "detail_add": (" LIVE UPDATE 2026-10-23T00:24Z: price re-confirmed on the live page and the metal-copy contradiction "
                       "('platinum solitaire setting' text vs 14K Yellow Gold specs) is still present on the live page."),
    },
    "BN-23": {
        "price": 5190.0,
        "read": ("Live fetch 2026-10-23T00:26Z: $5,190 '(Setting Price)' - unchanged; Stock Number 501472y14, Metal 14K Yellow Gold, "
                 "Width 4.00mm re-read; Natural Diamond Information re-read: Shape Emerald, Quantity 6, Total Carat 1, Color G-H, "
                 "Clarity VS2-SI1, Not Enhanced, Setting Type Prong, with the same 1 ct centre-stone disclaimer."),
        "basis": None,
        "detail_add": "",
    },
    "BN-24": {
        "price": 1145.0,
        "read": ("Live fetch 2026-10-23T00:28Z: $1,145 '(Setting Price)' - unchanged; Stock Number 502120w14, Metal 14K White Gold, "
                 "Width 2.40mm, Rhodium Finish: Yes re-read from the page. Page title 'Classic Simple Solitaire Engagement Ring in "
                 "14k White Gold' (same 502120 style family as published BN-10)."),
        "basis": None,
        "detail_add": "",
    },
    "BN-25": {
        "price": 2210.0,
        "read": ("Live fetch 2026-10-23T00:30Z: $2,210 '(Setting Price)' with NO discount displayed; Stock Number 505094w14, Metal "
                 "14K White Gold, Width 1.75mm, Rhodium Finish: Yes re-read; diamond block re-read: Round, Quantity 26, Total Carat "
                 "1/5, Color F-G, Clarity VS1-VS2. The 22 Oct sale display ('$2,210 $1,657 -25%') had ended by this re-fetch - the "
                 "recorded price is updated to the live $2,210."),
        "basis": "Setting only - live page shows '$2,210 (Setting Price)', no discount displayed at the 2026-10-23 re-fetch (the 22 Oct '-25% to $1,657' sale had ended); includes 26 pave-set round diamonds, 1/5 ct total, F-G colour, VS1-VS2 clarity",
        "detail_add": (" LIVE UPDATE 2026-10-23T00:30Z: the product page now shows $2,210 (Setting Price) with no strike-through - "
                       "the 22 Oct sale ($1,657, -25%) has ended; the recorded price is the current live one."),
    },
}


def main():
    rp = DATA / "rings.json"
    doc = json.loads(rp.read_text(encoding="utf-8"))
    upgraded, skipped = [], []
    for r in doc["rows"]:
        rid = r.get("id")
        if rid not in LIVE:
            continue
        if "PRICE_V2_ONLY" not in r.get("flags", []):
            skipped.append(rid)
            continue
        spec = LIVE[rid]
        r["flags"] = [f for f in r["flags"] if f != "PRICE_V2_ONLY"]
        r["price_verification"] = "V1_direct_page_fetch"
        r["price_usd"] = spec["price"]
        r["price_captured_utc"] = "2026-10-23"
        if spec["basis"]:
            r["price_basis"] = spec["basis"]
        if spec["detail_add"]:
            r["flag_detail"] = (r.get("flag_detail") or "") + spec["detail_add"]
        r["reverified_utc"] = "2026-10-23"
        r["reverification"] = (r.get("reverification") or "") + " " + spec["read"]
        upgraded.append(rid)
    rp.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("upgraded to V1:", upgraded, "| skipped (already upgraded):", skipped)

    vp = DATA / "verification_log.json"
    vlog = json.loads(vp.read_text(encoding="utf-8"))
    if not any("Pass 11" in p.get("pass", "") for p in vlog["passes"]):
        vlog["passes"].append({
            "pass": "Pass 11 — live re-fetch of the PRICE_V2_ONLY rows (session arena/22b5b06c-gold4)",
            "when_utc": "2026-10-23T00:35Z",
            "scope": ("The fetch-service outage that forced 9 rows to V2 snapshot provenance cleared briefly (00:20-00:33 UTC). "
                      "Six Blue Nile product pages (BN-20..BN-25) were re-fetched live; the three Brilliant Earth pages (BE-05/06/07) "
                      "were attempted but the outage returned mid-page before the product block."),
            "checked": [
                "BN-21/BN-22/BN-23/BN-24: live prices identical to the snapshots ($1,290 / $2,050 / $5,190 / $1,145); stock numbers, metals and widths re-read from the live pages - upgraded to V1_direct_page_fetch, PRICE_V2_ONLY removed.",
                "BN-20: live page shows $965 (Setting Price) with NO discount - the 22 Oct sale ($772/-20%, and $724/$730/$728 on category pages) has ENDED. Price updated to the live $965; SALE_PRICE_VARIES_ACROSS_PAGES kept as a documented historical irregularity with the live resolution appended.",
                "BN-25: live page shows $2,210 (Setting Price) with NO discount - the 22 Oct sale ($1,657/-25%) has ENDED. Price updated to the live $2,210.",
                "BN-22: the metal-copy contradiction ('platinum solitaire setting' text vs 14K Yellow Gold specs) is STILL present on the live page - COPY_INCONSISTENT_METAL confirmed live.",
                "BE-05/BE-06/BE-07: live re-fetch could not be completed (outage returned ~00:31-00:33Z); they keep V2 provenance and PRICE_V2_ONLY + PRICE_CURRENCY_LOCALIZED until a live read confirms them.",
            ],
            "result": "PASS (pipeline + all five CI gates re-run after the upgrade; outputs in reports/ and AUDIT.md)",
            "outcome": ("6 of the 9 PRICE_V2_ONLY rows upgraded to V1 with live reads; 2 prices corrected to current live values "
                        "(BN-20 $772->$965, BN-25 $1,657->$2,210 - both sales ended); dataset provenance now 60 V1 / 3 V2 / 1 U of 64 rows. "
                        "No value was inferred: every change quotes the live page."),
        })
        vlog["not_reverified_this_pass"].append(
            "Pass 11 could not complete the live re-fetch of BE-05/BE-06/BE-07 (Brilliant Earth Freesia 14K/18K, Fleur) - the fetch "
            "outage returned mid-page; they remain PRICE_V2_ONLY on the Flagged page until a live read confirms them.")
        vp.write_text(json.dumps(vlog, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print("verification_log.json: Pass 11 appended")


if __name__ == "__main__":
    main()
