#!/usr/bin/env python3
"""Pass 12 — independent live re-verification, session arena/d1586f6a-gold4.

Every change below is backed by a page this session opened live on 2026-10-23.
No value is invented; where a page could not be read the value stays blank.

Sources actually opened in this pass (live fetch_page, 2026-10-23):
  A1 https://consumer.ftc.gov/articles/buying-platinum-gold-and-silver-jewelry
  A2 https://www.law.cornell.edu/uscode/text/15/295
  A3 https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-23/section-23.3
  A4 https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-23/section-23.4
  B1 https://www.gold.org/goldhub/data/gold-prices
  C1 https://www.allurez.com/products/floral-solitaire-engagement-ring-14k-yellow-gold   (AL-01)
  C2 https://www.sarraf.com/products/18k-Yellow-Gold-5mm-High-Polished-Traditional-Domed-Wedding-Band.html (SR-03)
  C3 https://www.sarraf.com/products/14k-yellow-gold-mens-solitaire-diamond-ring-1-2-ct.html (SR-05)
  C4 https://www.bluenile.com/engagement-rings/design-your-own-ring/woven-solitaire-engagement-ring-in-14k-yellow-gold-by-james-allen-item-310896 (BN-20)
  C5 https://mejuri.com/products/diamonds-team-ring (MJ-01)

Run from the repo root:  python3 scripts/session_d1586f6a/pass12_20261023.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
PASS_ID = "arena/d1586f6a-gold4 (Pass 12)"
TODAY = "2026-10-23"


def load(name: str) -> dict:
    with open(DATA / name, encoding="utf-8") as fh:
        return json.load(fh)


def save(name: str, obj: dict) -> None:
    with open(DATA / name, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


# ----------------------------------------------------------------- 1. gold spot
# Live WGC panel on 2026-10-23 read: "USD /oz 4,024.45", page date "22 October, 2026",
# chart line "Data as of 22 October, 2026", "Market Data: Provided by ICE Data Services".
NEW_OZ = 4024.45
OZ_G = 31.1034768
spot = load("gold_spot.json")
old_bench = dict(spot["benchmark"])
old_oz = float(old_bench["value_usd_per_oz"])

spot["benchmark"].update({
    "value_usd_per_oz": NEW_OZ,
    "price_date_as_shown_on_source": "22 October, 2026",
    "data_as_of_shown_on_source": "Data as of 22 October, 2026",
    "retrieved_utc": TODAY,
    "verification": "V1_direct_page_fetch",
    "what_the_source_page_shows": (
        "Gold spot price panel: 'USD /oz 4,024.45' on a page dated '22 October, 2026', "
        "with the chart footer 'Data as of 22 October, 2026' and 'Market Data: Provided by ICE Data Services'."
    ),
    "captured_utc": "2026-10-23T10:02Z",
})
spot["benchmark"]["notes"] = [
    "Pass 12 (2026-10-23): the live World Gold Council panel was re-read and now displays USD 4,024.45/oz with the date line 'Data as of 22 October, 2026'. This reading replaces the 21-October reading as the benchmark, so every derived value on the site is computed from a benchmark whose own source date moved forward by one day.",
    f"Difference from the previous benchmark (USD {old_oz:,.2f}/oz): {(NEW_OZ - old_oz) / old_oz * 100:+.2f}%. The change comes from the market data date advancing, not from any change in method.",
    "Spot is a live market quote; the figure recorded here is a dated reading, not a claim about today's price. Re-read the source before relying on it.",
    "The World Gold Council page states that the LBMA Gold Price is the key benchmark used throughout the gold market and that historical LBMA auction data was removed from the WGC site at the request of ICE Benchmark Administration (licensing).",
]
spot["constants"]["spot_usd_per_gram"] = round(NEW_OZ / OZ_G, 6)
spot["captured_utc"] = "2026-10-23T10:02Z"

prior = spot.setdefault("prior_captures", [])
prior.append({
    "value_usd_per_oz": old_oz,
    "price_date_as_shown_on_source": old_bench["price_date_as_shown_on_source"],
    "retrieved_utc": old_bench.get("retrieved_utc"),
    "verification": "V1_direct_page_fetch",
    "status": "superseded",
    "note": (
        "Benchmark used by Passes 2-11 (2026-10-22). Superseded in Pass 12 when the live WGC panel "
        f"showed a newer data date (22 October, 2026) at USD {NEW_OZ:,.2f}/oz. Kept for audit; no "
        "current calculation uses it."
    ),
})
spot["pass12_live_reading_2026_10_23"] = {
    "source_url": "https://www.gold.org/goldhub/data/gold-prices",
    "publisher": "World Gold Council (Goldhub)",
    "usd_per_troy_oz": NEW_OZ,
    "usd_per_gram_exact_computed": round(NEW_OZ / OZ_G, 6),
    "source_date_line_verbatim": "22 October, 2026",
    "source_data_as_of_verbatim": "Data as of 22 October, 2026",
    "retrieved_utc": TODAY,
    "prior_benchmark_usd_per_oz": old_oz,
    "delta_pct_vs_prior_benchmark": round((NEW_OZ - old_oz) / old_oz * 100, 4),
    "assessment": (
        "Read live on 2026-10-23. The panel is a live quote and moved 0.10% from the 21-October reading "
        "recorded on 2026-10-22. Recorded so the benchmark's own date is never mistaken for today's date."
    ),
}
save("gold_spot.json", spot)

# --------------------------------------------- 2. correct the 10-karat legal claim
# eCFR 16 CFR 23.3(c)(1) (read live 2026-10-23) gives "9 Karat Gold" as an ACCEPTABLE
# description; the 2018 revision removed the old 10K threshold for the word "gold".
# 10K survives only as the minimum fineness for PLATING (23.3(c)(2)-(3), 23.4(b)).
WRONG = ("lowest fine-gold content legally sellable as 'karat gold' in the U.S. under 16 CFR § 23.3.")
RIGHT = (
    "the usual lowest karat sold in the U.S. market, but NOT a legal minimum: the 2018 revision of "
    "16 CFR Part 23 removed the old 10-karat threshold, and 16 CFR 23.3(c)(1) itself gives "
    "'9 Karat Gold' as an acceptable description. 10-karat is a floor for plating fineness only "
    "(23.3(c)(2)-(3), 23.4(b))."
)
catalog = load("catalog_a0be79d4.json")
fixed = 0
for k in catalog["karat_reference"]:
    prof = k.get("durability_profile", "")
    if WRONG in prof:
        k["durability_profile"] = prof.replace(WRONG, RIGHT)
        fixed += 1
if fixed != 1:
    raise SystemExit(f"expected exactly 1 karat claim to correct, got {fixed}")

# --------------------------------------------- 3. publish the pass-12 findings
new_flags = [
    {
        "flag_id": "FLG-PASS12-01",
        "severity": "HIGH",
        "category": "Anti-Hallucination Correction (legal claim)",
        "item_ref": "standards.html — 14K karat table row (data/catalog_a0be79d4.json)",
        "title": "Incorrect Statement That 10K Is The Legal Minimum For 'Karat Gold' — Corrected Against 16 CFR 23.3(c)(1)",
        "detail": (
            "The site previously described 14K as the 'lowest fine-gold content legally sellable as karat gold in the "
            "U.S. under 16 CFR § 23.3'. That is wrong for the current rule. Read live on 2026-10-23, 16 CFR 23.3(c)(1) "
            "lists '9 Karat Gold' and '9 Kt. Gold' among acceptable descriptions, and the 2018 revision of the Guides "
            "removed the former 10-karat threshold for the word 'gold'. The 10-karat figure that remains in Part 23 is a "
            "minimum fineness for PLATING: gold plate / gold filled / gold electroplate under 23.3(c)(2)-(3) and vermeil "
            "under 23.4(b). The cell was rewritten to say exactly that, and no dataset row was affected (no 9K row exists)."
        ),
        "action": "Corrected in data/catalog_a0be79d4.json; the karat table now states the market practice, the removal of the 10K threshold and the surviving plating floor, each traceable to the eCFR text.",
        "source_url": "https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-23/section-23.3",
        "date": TODAY,
    },
    {
        "flag_id": "FLG-PASS12-02",
        "severity": "MEDIUM",
        "category": "Benchmark date drift",
        "item_ref": f"data/gold_spot.json — benchmark {old_oz:,.2f}/oz (21 October) → {NEW_OZ:,.2f}/oz (22 October)",
        "title": "Gold Benchmark Was One Data-Day Behind: WGC Panel Re-Read Live And Moved Forward One Day",
        "detail": (
            f"The stored benchmark was USD {old_oz:,.2f}/oz with the source's own date line '21 October, 2026', captured on "
            f"2026-10-22. Re-read live on 2026-10-23 the same panel shows USD {NEW_OZ:,.2f}/oz with 'Data as of 22 October, 2026' "
            f"— a {(NEW_OZ - old_oz) / old_oz * 100:+.2f}% move that is a change of market data date, not of method. Every derived "
            "melt value on the site is recomputed from the newer reading; the superseded reading is retained in prior_captures."
        ),
        "action": "Benchmark replaced with the fresh dated reading; prior reading kept for audit. Re-check the source date before quoting any melt value.",
        "source_url": "https://www.gold.org/goldhub/data/gold-prices",
        "date": TODAY,
    },
    {
        "flag_id": "FLG-PASS12-03",
        "severity": "MEDIUM",
        "category": "Variant-dependent price re-confirmed live",
        "item_ref": "MJ-01 Mejuri Diamonds Team Ring",
        "title": "Mejuri Price Still Depends On Which Variant The Page Opens On ($548 On The Solid White Gold 14k Variant)",
        "detail": (
            "Re-opened live on 2026-10-23, the Diamonds Team Ring page resolved to the 'Solid White Gold (14k), Natural Diamond' "
            "variant and displayed $548, while the stored row records the 14k yellow-gold material. The price figure itself was "
            "confirmed ($548), but the metal shown at that price was white gold, not the yellow gold recorded in the row. The "
            "row's price is therefore a variant-reading, not a metal-specific quote, and its gram weight is still not published."
        ),
        "action": "Price kept at $548 with PRICE_VARIANT_DEPENDENT retained and this confirmation appended to the row note. Do not treat $548 as a yellow-gold-only price; select the metal variant and re-read before buying.",
        "source_url": "https://mejuri.com/products/diamonds-team-ring",
        "date": TODAY,
    },
    {
        "flag_id": "FLG-PASS12-04",
        "severity": "HIGH",
        "category": "Still unverifiable online (unchanged policy)",
        "item_ref": "All 64 rows — hallmark and as-delivered weight",
        "title": "No Retailer Publishes A Hallmark Image Or Maker's Mark: The Karat Stamp Can Only Be Verified On Arrival",
        "detail": (
            "Re-checked on the live pages opened this pass: Allurez, Sarraf, Blue Nile and Mejuri publish karat in their metal "
            "field but none publishes a photograph or description of the physical stamp plus the maker's/registered trademark "
            "that 16 CFR 23.3 and the FTC consumer guidance require next to the karat mark. The FTC's own guidance is explicit: "
            "if the trademark is not next to the karat mark, do not buy. This cannot be settled from a web page, so hallmark_published "
            "stays false for every row and the check belongs in the on-arrival XRF step."
        ),
        "action": "Keep every hallmark cell UNVERIFIED; complete the stamp + trademark check and an XRF assay with an independent jeweller inside the return window.",
        "source_url": "https://consumer.ftc.gov/articles/buying-platinum-gold-and-silver-jewelry",
        "date": TODAY,
    },
]
catalog["flagged_items"].extend(new_flags)
# keep the 14K fine-gold statement out of any 'minimum legal' wording elsewhere
if "10K Minimum Legal Gold (US)" in json.dumps(catalog):
    for k in catalog["karat_reference"]:
        if k.get("label") == "10K Minimum Legal Gold (US)":
            k["label"] = "10K (common U.S. market minimum — not a legal floor since the 2018 Guides revision)"
save("catalog_a0be79d4.json", catalog)

# --------------------------------------------- 4. row-level re-verification notes
rings = load("rings.json")
VERIFIED = {
    "AL-01": ("price $585, 'Setting only. Center stone sold separately.', style number NG4426, metal 14k Yellow Gold and "
              "'Approximate Metal Weight 3.58 grams' all re-read and match this record."),
    "SR-03": ("price US$871.00 ('Now'), SKU 18KY-LPBWB05, stock 140139, '18K Solid Gold' and 'Approximate Metal Weight: "
              "6.70 grams' (page states the weight is for a size-10 ring) all re-read and match this record."),
    "SR-05": ("price US$2,858.00 ('Now'), SKU 9240-14ky, stock 145364, '14K Solid Gold', 'Approximate Metal Weight: 8.00 grams' "
              "and Diamond Weight 0.50 Ct all re-read and match this record; the price is stone-inclusive, as flagged."),
    "BN-20": ("price $965 '(Setting Price)' with no discount, Stock Number 505038y14, Metal 14K Yellow Gold and Width 1.80mm all "
              "re-read and match this record; the ended 22-October sale is confirmed absent from the live page."),
    "MJ-01": ("price $548 re-read, but the page opened on the 'Solid White Gold (14k), Natural Diamond' variant, not the 14k yellow "
              "gold recorded in this row; no gram weight is published on the page."),
}
touched = 0
for row in rings["rows"]:
    if row["id"] in VERIFIED:
        prev = row.get("reverification") or ""
        row["reverification"] = f"Pass 12 (2026-10-23): {VERIFIED[row['id']]}" + (f" Earlier: {prev}" if prev else "")
        row["reverified_utc"] = TODAY
        row["reverified_by"] = PASS_ID
        touched += 1
if touched != len(VERIFIED):
    raise SystemExit(f"expected {len(VERIFIED)} rows updated, got {touched}")
rings["reverified_utc"] = TODAY
rings["last_full_reverification_utc"] = rings.get("last_full_reverification_utc")
for row in rings["rows"]:
    if row["id"] == "MJ-01":
        row["flag_detail"] = (row.get("flag_detail") or "") + (
            " Pass 12 live re-read (2026-10-23): the page resolved to the Solid White Gold (14k) variant at $548, so the "
            "recorded price is variant-dependent and the metal shown at that price differed from this row's yellow-gold label."
        )
save("rings.json", rings)

# --------------------------------------------- 5. seller contact re-verified live
sellers = load("sellers.json")
for s in sellers["sellers"]:
    if s["id"] == "blue-nile":
        s["contact"]["pass12_live_check"] = {
            "retrieved_utc": TODAY,
            "verified_from": "https://www.bluenile.com/engagement-rings/design-your-own-ring/woven-solitaire-engagement-ring-in-14k-yellow-gold-by-james-allen-item-310896",
            "what_the_page_shows": "Contact panel lists '+1-800-242-2728', 'service@bluenile.com', a WhatsApp number and a Contact Us page link.",
            "phone_matches_record": True,
            "email_matches_record": True,
        }
sellers["reverified_utc"] = TODAY
save("sellers.json", sellers)

# --------------------------------------------- 6. append the pass to the log
log = load("verification_log.json")
log["passes"].append({
    "pass": "Pass 12 — independent live re-verification (session arena/d1586f6a-gold4)",
    "when_utc": "2026-10-23T10:05Z",
    "scope": (
        "Live re-open of the Tier A legal sources, the Tier B spot benchmark and a sample of retailer rows/policies, "
        "done from a fresh sandbox to test whether the stored claims still hold on the pages as served today."
    ),
    "checked": [
        "FTC 'Buying Platinum, Gold, and Silver Jewelry' (consumer.ftc.gov) — still live at the recorded URL. Re-confirmed verbatim: the karat mark must sit beside the name or U.S. registered trademark of the company standing behind the mark ('If you're thinking about buying a piece of gold jewelry but don't see a trademark along with the karat mark, don't buy it.'); 'solid gold' means the item is not hollow; vermeil is a sterling-silver base coated or plated with gold; gold filled / gold overlay / RGP are mechanically applied layers; the article also tells shoppers to look up complaints and get the return policy in writing. The checklist's items 2, 3, 5 and 7 are supported by this page.",
        "15 U.S.C. § 295 (law.cornell.edu) — text unchanged: actual fineness may not be less than the stamped fineness by more than three one-thousandths, and for the whole article including solder, seven one-thousandths (other than watchcases/flatware). This is the source of the 'a stamp is not proof' arithmetic used by the calculator's legal-minimum column.",
        "16 CFR 23.3 and 23.4 (ecfr.gov, title up to date as of 10/21/2026) — text read in full. 23.3(a) prohibits misrepresenting karat fineness; 23.3(c)(1) requires the karat designation immediately before the word gold and states hollow-centred articles 'should not be marked or described as solid'; 23.4(b) defines vermeil as sterling silver plated with gold of not less than 10 karat fineness and a minimum thickness equivalent to 2.5 microns.",
        "IRREGULARITY FOUND AND CORRECTED: the site's 14K karat row claimed 10K is the 'lowest fine-gold content legally sellable as karat gold under 16 CFR § 23.3'. That is not the current rule — 23.3(c)(1) itself lists '9 Karat Gold' as an acceptable description and the 2018 revision removed the old 10-karat threshold. The remaining 10-karat figures in Part 23 are plating-fineness floors (23.3(c)(2)-(3), 23.4(b)). The cell was corrected and the correction published as FLG-PASS12-01. No dataset row was affected.",
        "World Gold Council spot panel — re-read live. The stored benchmark carried the source's own date line '21 October, 2026' at $4,028.53/oz; today the same panel shows $4,024.45/oz with 'Data as of 22 October, 2026'. Benchmark advanced by one data day (-0.10%) and every derived melt value recomputed; prior reading kept in prior_captures. Published as FLG-PASS12-02.",
        "AL-01 Allurez — live page matches every stored field ($585, 'Setting only. Center stone sold separately.', NG4426, 14k Yellow Gold, 'Approximate Metal Weight 3.58 grams'). No solid-gold wording and no hallmark image on the page, as flagged.",
        "SR-03 Sarraf 18K 5mm domed band — live page matches ($871.00 Now, SKU 18KY-LPBWB05, stock 140139, 18K Solid Gold, 6.70 grams for a size-10 ring).",
        "SR-05 Sarraf 14K men's solitaire — live page matches ($2,858.00 Now, SKU 9240-14ky, stock 145364, 14K Solid Gold, 8.00 grams, 0.50 ct H/SI1 natural diamond). Stone-inclusive pricing flag stands.",
        "BN-20 Blue Nile Woven Solitaire — live page matches ($965 Setting Price, no discount, stock 505038y14, 14K Yellow Gold, 1.80mm). Confirms the Pass 11 resolution and that the 22-October sale has ended. Blue Nile's contact panel (+1-800-242-2728, service@bluenile.com) also re-read live.",
        "MJ-01 Mejuri Diamonds Team Ring — $548 re-read, BUT the page opened on the 'Solid White Gold (14k), Natural Diamond' variant while the row records yellow gold; gram weight still not published. PRICE_VARIANT_DEPENDENT re-confirmed and FLG-PASS12-03 published.",
        "Hallmark check on every live page opened this pass: none publishes the physical stamp plus maker's mark, so hallmark_published stays false for all 64 rows and the check stays on the on-arrival list (FLG-PASS12-04).",
    ],
    "not_verified_this_pass": [
        "The 59 rows not listed above were not re-opened in this pass; their last verification date remains 2026-10-22 and is recorded per row.",
        "Brilliant Earth BE-05/BE-06/BE-07 still carry V2 snapshot provenance; they were not re-fetched this pass.",
        "Seller reputation and independent complaint history remains unverified for every seller (no independent review corpus was consulted).",
        "Physical hallmark, XRF assay and as-delivered weight can only be established on the ring in hand.",
    ],
    "result": "PASS — 4 Tier A/B sources and 5 retailer pages re-read live; 1 incorrect legal claim found and corrected; 1 benchmark date drift found and refreshed; 2 confirmed-but-still-unresolved retailer irregularities re-published. No fabricated value was added.",
    "outcome": "All four corrections are published on the Flagged page with source links; every unconfirmable value remains blank.",
})
save("verification_log.json", log)

print(f"Pass 12 applied: spot {old_oz:,.2f} -> {NEW_OZ:,.2f}/oz; 1 legal claim corrected; "
      f"{len(new_flags)} flags published; {touched} rows re-verified.")
