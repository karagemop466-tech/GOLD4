#!/usr/bin/env python3
"""Apply the 2026-10-23 verification pass (session arena/46691f83-gold4).

Only changes that were confirmed against a live official page in
scripts/session_46691f83/live_evidence_20261023.json are applied here:

  1. data/gold_spot.json  - add the 2026-10-23 World Gold Council capture.
                            The 2026-10-22 reading is moved into prior_captures,
                            never deleted.
  2. data/sources.json    - fix the dead NIST Handbook 44 URL, correct the
                            NIST SP 811 "exact" conversion claim, add the two
                            government sources the site cites but never
                            registered (15 U.S.C. 297, 12 CFR 1026.13), and
                            stamp today's re-verification on the Tier A set.
  3. data/catalog_a0be79d4.json + scripts/build_dataset.py
                          - correct the 16 CFR 23.9 -> 23.10 citation error and
                            re-attribute the FCBA 90-day limit to 12 CFR
                            1026.13 instead of the CFPB FAQ page.
  4. data/rings.json      - append today's re-read to the four rows that were
                            re-opened live; no numeric value is changed.

Nothing is estimated. Every edit is keyed to a URL in the evidence file.
"""
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
TROY = 31.1034768
TODAY = "2026-10-23"
NOW = "2026-10-23T10:05Z"


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def save(name, obj):
    (DATA / name).write_text(json.dumps(obj, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- gold spot
spot = load("gold_spot.json")
old_bench = dict(spot["benchmark"])
new_value = 4024.45
spot["captured_utc"] = NOW
spot["benchmark"] = {
    "id": "wgc-gold-spot-usd",
    "name": "Gold spot price, USD per troy ounce",
    "value_usd_per_oz": new_value,
    "quote_currency": "USD",
    "quote_unit": "troy ounce",
    "price_date_as_shown_on_source": "22 October, 2026",
    "data_as_of_shown_on_source": "Data as of 22 October, 2026",
    "retrieved_utc": TODAY,
    "publisher": "World Gold Council (Goldhub)",
    "publisher_type": "industry benchmark body (market data supplied by ICE Data Services)",
    "source_url": "https://www.gold.org/goldhub/data/gold-prices",
    "what_the_source_page_shows": "Gold Spot price panel: 'USD /oz 4,024.45' with the 'Last Updated' label, on a dataset page dated 'Data as of 22 October, 2026' and captioned 'Market Data: Provided by ICE Data Services'.",
    "verification": "V1_direct_page_fetch",
    "notes": [
        "Pass 14 capture, taken 2026-10-23T~09:58Z. The page's own date line reads 22 October 2026, one day behind the retrieval date; the source date is recorded exactly as shown and is never advanced by this project.",
        "The previous benchmark (USD 4,028.53/oz, source date line 21 October 2026, captured 2026-10-22) is preserved in prior_captures. The move is -0.10%.",
        "Every derived value in this repository is recomputed from this single benchmark by scripts/compute.py; scripts/audit.py independently re-derives all of them on every run.",
    ],
    "captured_utc": NOW,
}
old_bench["status"] = "superseded"
old_bench["superseded_by_utc"] = NOW
old_bench["superseded_note"] = (
    "Pass 14 (2026-10-23) adopted the newer World Gold Council reading (USD 4,024.45/oz, "
    "source date line 22 October 2026). This 2026-10-22 capture is kept unchanged for audit; "
    "it is no longer the calculation basis."
)
spot.setdefault("prior_captures", []).insert(0, old_bench)
spot["constants"]["spot_usd_per_gram"] = round(new_value / TROY, 6)
spot["constants"]["spot_usd_per_gram_note"] = (
    f"value_usd_per_oz / 31.1034768 = {new_value} / 31.1034768 = {round(new_value / TROY, 6)} USD/g. Recomputed by scripts/compute.py."
)
spot["recheck_note"] = (
    "Re-read on 2026-10-23 (Pass 14). Any derived value in this repository can be recomputed in one line "
    "from value_usd_per_oz and 31.1034768 g/oz; scripts/audit.py re-derives all of them on every run."
)
spot["reverification_2026_10_23"] = {
    "source_url": "https://www.gold.org/goldhub/data/gold-prices",
    "value_usd_per_oz": new_value,
    "date_line_on_page": "Data as of 22 October, 2026",
    "retrieved_utc": TODAY,
    "verification": "V1_direct_page_fetch",
    "note": "The World Gold Council panel is the single calculation basis for this project. Same-day Kitco/JM Bullion cross-checks captured on 2026-10-22 remain in the file as evidence of agreement at that time; they are not the basis.",
}
save("gold_spot.json", spot)
print(f"gold_spot.json: benchmark {old_bench['value_usd_per_oz']} -> {new_value} USD/oz; prior captures: {len(spot['prior_captures'])}")


# ---------------------------------------------------------------- sources
src = load("sources.json")
by_id = {s["id"]: s for s in src["sources"]}

# 1. Dead NIST Handbook 44 URL -> live current-edition page, corrected title/supports.
hb = by_id["nist-hb44-2026"]
hb["url"] = "https://www.nist.gov/pml/owm/nist-handbook-44-current-edition"
hb["title"] = "NIST Handbook 44 — Current Edition (2026): Specifications, Tolerances, and Other Technical Requirements for Weighing and Measuring Devices"
hb["retrieved_utc"] = TODAY
hb["reverified_utc"] = TODAY
hb["supports"] = [
    "The live 2026 Handbook 44 index page was read; it links every section (1.10 General Code, 2.20 Scales, 2.21 … 2.25, Section 3 device codes) as DOCX/PDF.",
    "The index page itself does NOT print a troy-ounce or metric-carat conversion factor, so no numeric factor is attributed to it by this project.",
]
hb["correction_2026_10_23"] = (
    "The previously registered URL https://www.nist.gov/pml/owm/metric-publications/nist-handbook-44 was re-opened on "
    "2026-10-23 and returned NIST's own 'Page not found' (error 404). It also carried the invented-looking subtitle "
    "'Appendix C: Units of Mass for Precious Metals & Metric Carat', which is not what the page says. Both were replaced."
)
hb["previous_urls"] = ["https://www.nist.gov/pml/owm/metric-publications/nist-handbook-44"]

# 2. NIST SP 811 - the 31.1034768 g figure is not an exact NIST table value.
sp = by_id["nist-sp811-pml"]
sp["reverified_utc"] = TODAY
sp["supports"] = [
    "'carat, metric → gram' is listed as 2.0 E-01 in bold (= exact) in Appendix B.8, i.e. 0.200 g exactly.",
    "'ounce (troy or apothecary) → gram' is listed as 3.110 348 E+01 and is NOT bold, i.e. 31.10348 g rounded, not an exact table value.",
]
sp["correction_2026_10_23"] = (
    "This project uses 31.1034768 g per troy ounce, which is the 480-grain definition (480 × 64.79891 mg) and agrees with "
    "NIST's rounded table entry. It must not be quoted as 'NIST's exact conversion factor'. The earlier supports text did "
    "exactly that and has been corrected; the constant itself is unchanged and still exact by definition."
)
sp["verified_subpage"] = {
    "url": "https://www.nist.gov/physical-measurement-laboratory/nist-guide-si-appendix-b8",
    "title": "NIST Guide to the SI, Appendix B.8: Factors for Units Listed Alphabetically",
    "retrieved_utc": TODAY,
}

# 3. Two government sources the site cites but never registered.
src["sources"].append({
    "id": "usc-15-297",
    "tier": "A",
    "publisher": "U.S. Code (Legal Information Institute, Cornell Law School) - 15 U.S.C. § 297",
    "title": "15 U.S.C. § 297 — Stamping plated articles",
    "url": "https://www.law.cornell.edu/uscode/text/15/297",
    "retrieved_utc": TODAY,
    "verification": "V1_direct_page_fetch",
    "supports": [
        "Subsection (b): a person applying a quality mark to a gold or silver article must also apply a trademark registered in the U.S. (or their name), in lettering at least as large as the quality mark and as close as possible to it.",
        "Subsection (a): plated articles must not be stamped 'sterling' or 'coin'.",
    ],
    "why_added": "standards.html cited 15 U.S.C. § 297 for the hallmark-plus-trademark rule, but no sources.json entry existed, so the citation had no registry backing. Added after reading the section on 2026-10-23.",
})
src["sources"].append({
    "id": "ecfr-12-1026-13",
    "tier": "A",
    "publisher": "Consumer Financial Protection Bureau / eCFR (National Archives) - Regulation Z",
    "title": "12 CFR § 1026.13 — Billing error resolution",
    "url": "https://www.ecfr.gov/current/title-12/chapter-X/part-1026/subpart-B/section-1026.13",
    "retrieved_utc": TODAY,
    "verification": "V1_direct_page_fetch",
    "supports": [
        "(b)(1): the billing-error notice must reach the creditor no later than 60 days after the first periodic statement reflecting the error.",
        "(c)(1): written acknowledgment within 30 days of receiving the notice.",
        "(c)(2): resolution within 2 complete billing cycles and in no event later than 90 days.",
    ],
    "why_added": "The 60-day / 30-day figures are on the CFPB consumer page, but the 2-billing-cycle / 90-day outer limit is not. That limit is in this section, so it is now cited to the section itself.",
})

for sid in ("ftc-gold-jewelry", "ecfr-16-23", "usc-15-295", "cfpb-fcba-en61"):
    s = by_id[sid]
    s["reverified_utc"] = TODAY
    s["reverification"] = {
        "ftc-gold-jewelry": "Re-read 2026-10-23: karat-out-of-24 definition, quality-mark-plus-trademark rule, 'solid gold' = not hollow, and the plated/filled/overlay/RGP/electroplate/vermeil definitions all still present.",
        "ecfr-16-23": "Re-read 2026-10-23: eCFR shows title 16 up to date as of 10/21/2026; § 23.3, § 23.4, § 23.7, § 23.8, § 23.10 headings and text confirmed. § 23.9 is pewter content, not quality marks.",
        "usc-15-295": "Re-read 2026-10-23: three one-thousandth parts tolerance for the part assayed, seven one-thousandth parts for the whole article including solder.",
        "cfpb-fcba-en61": "Re-read 2026-10-23: 60 calendar days for the written billing-error notice and 30 days for the acknowledgment. Page reviewed APR 15, 2024.",
    }[sid]

save("sources.json", src)
print("sources.json:", len(src["sources"]), "sources")


# ---------------------------------------------------------------- catalog
cat = load("catalog_a0be79d4.json")
fixed = 0
for std in cat["standards_sources"]:
    if std["id"] == "STD-ECFR-16CFR23":
        std["citation"] = "16 CFR Part 23 (incl. § 23.3 Gold, § 23.4 Vermeil, § 23.7 Rhodium, § 23.8 Multi-Metal, § 23.10 Quality Marks)"
        std["key_takeaways"] = [
            "16 CFR § 23.3: unqualified 'Gold' is reserved for 24-karat metal; the karat designation must immediately precede the word Gold; hollow articles must not be described as 'solid'.",
            "16 CFR § 23.4: 'vermeil' requires a sterling-silver base (>=925/1000) coated with >=10K gold at least 2.5 microns thick — never solid gold.",
            "16 CFR § 23.7 & § 23.8: a rhodium surface layer must be disclosed, and multi-precious-metal products must list the metals in order of relative weight.",
            "16 CFR § 23.10 (with 15 U.S.C. § 297): a quality mark must be accompanied by the manufacturer's or dealer's registered trademark or name.",
        ]
        std["retrieved_date"] = TODAY
        std["correction_2026_10_23"] = "The trademark rule was cited to § 23.9, which is the pewter section. It is § 23.10 ('Additional guidance for the use of quality marks'). Corrected after reading both sections on the eCFR page."
        fixed += 1
    if std["id"] == "STD-CFPB-FCBA":
        std["key_takeaways"] = [
            "The CFPB page states: send a written billing-error notice within 60 calendar days after the charge appears on your statement; the card company then has 30 days to confirm receipt in writing.",
            "12 CFR § 1026.13(c)(2) — not the CFPB FAQ page — sets the outer resolution limit: two complete billing cycles, and in no case later than 90 days after the notice.",
            "Project guidance (not a CFPB statement): pay with a credit card rather than wire transfer, a peer-to-peer app, crypto or a debit card, because only the credit-card route carries the statutory billing-error dispute right.",
        ]
        std["retrieved_date"] = TODAY
        std["correction_2026_10_23"] = "The 90-day / two-billing-cycle limit was paraphrased as if the CFPB FAQ page said it; that page does not. It is now attributed to 12 CFR 1026.13(c)(2), and the card-only advice is labelled as this project's guidance."
        fixed += 1
cat["meta"]["calculation_basis_2026_10_23"] = (
    "The melt figures in this catalog are the session-a0be79d4 cross-check columns computed from the two 2026-10-22 "
    "Kitco/JM Bullion quotes. The canonical calculation basis for the repository is data/gold_spot.json (World Gold "
    "Council), re-captured on 2026-10-23 at USD 4,024.45/oz. The two bases differ by 0.004% (4,024.45 vs 4,024.60), "
    "so no displayed melt value is materially affected; both are published rather than harmonised silently."
)
save("catalog_a0be79d4.json", cat)
print("catalog: corrected", fixed, "standard entries")


# ---------------------------------------------------------------- rings
rings = load("rings.json")
notes = {
    "AL-01": "Pass 14 (2026-10-23): page re-opened live. $585, 'Setting only. Center stone sold separately.', NG4426, 14k Yellow Gold and 'Approximate Metal Weight 3.58 grams' all re-read and unchanged.",
    "SR-01": "Pass 14 (2026-10-23): page re-opened live. US$352.00 (-15% off US$412.00), SKU 10KW-LPBWB05, 'Material: 10K Solid Gold', 'Approximate Metal Weight: 4.80 grams' all re-read and unchanged.",
    "RS-01": "Pass 14 (2026-10-23): page re-opened live (the /jewelry/rings/571221.html URL now resolves to /products/571221). $400, Item 571221, 'Gold Weight 1.7 grams' all re-read and unchanged.",
    "MJ-01": "Pass 14 (2026-10-23): page re-opened live and landed on the Solid White Gold (14k) / Natural Diamond variant at $548. Price matches this row but the variant differs from the recorded yellow-gold basis, so PRICE_VARIANT_DEPENDENT stands and the yellow-gold figure is not re-confirmed today.",
}
touched = 0
for row in rings["rows"]:
    if row["id"] in notes:
        prev = row.get("reverification", "").strip()
        row["reverification"] = (prev + " | " if prev else "") + notes[row["id"]]
        row["reverified_utc"] = TODAY
        row["reverified_by"] = (row.get("reverified_by", "") + " + arena/46691f83-gold4 (Pass 14)").strip(" +")
        touched += 1
rings["last_full_reverification_utc"] = TODAY
rings["pass_14_note"] = (
    "Pass 14 (2026-10-23) re-opened 5 of the 64 rows live: AL-01, SR-01, RS-01 and MJ-01 were re-confirmed (MJ-01 on a "
    "different metal variant) and AN-01 loaded but its Product Details table was not reached. The other 59 rows keep their "
    "2026-10-22 captures; they are not claimed as re-verified today. See data/verification_log.json."
)
save("rings.json", rings)
print("rings.json: rows re-read today:", touched)


# ---------------------------------------------------------------- generator source
gen = ROOT / "scripts" / "build_dataset.py"
text = gen.read_text(encoding="utf-8")
before = text
text = text.replace(
    '"citation": "16 CFR §§ 23.1–23.18 (incl. § 23.3 Gold, § 23.4 Vermeil, § 23.7 Rhodium, § 23.8 Multi-Metal, § 23.9 Quality Marks)",',
    '"citation": "16 CFR Part 23 (incl. § 23.3 Gold, § 23.4 Vermeil, § 23.7 Rhodium, § 23.8 Multi-Metal, § 23.10 Quality Marks)",')
text = text.replace(
    '"16 CFR § 23.9 & 15 U.S.C. § 297 (National Stamping Act): Every quality stamp must be accompanied by the registered manufacturer/seller trademark.",',
    '"16 CFR § 23.10 & 15 U.S.C. § 297 (National Stamping Act): Every quality stamp must be accompanied by the registered manufacturer/seller trademark.",')
if text != before:
    gen.write_text(text, encoding="utf-8")
    print("build_dataset.py: citation strings corrected")
else:
    raise SystemExit("build_dataset.py: expected strings not found - aborting so the fix is not silently skipped")
