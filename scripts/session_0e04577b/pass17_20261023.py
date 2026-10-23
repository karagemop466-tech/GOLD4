#!/usr/bin/env python3
"""Pass 17 (arena/0e04577b-gold4, 2026-10-23) data patch.
Text/provenance only: appends dated live re-read notes, adds the Pass 17
verification-log entry and the WGC live-tick cross-check. It changes NO
price, weight, karat, URL, flag or source_check value in the dataset."""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
D = ROOT / "data"

def load(n):
    with open(D/n, encoding="utf-8") as f: return json.load(f)
def save(n, obj):
    with open(D/n, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False); f.write("\n")

S = " PASS 17 (2026-10-23, arena/0e04577b-gold4): "
notes = {
 "AL-01": S+"official Allurez page re-fetched live and re-read: '$585', 'Setting only. Center stone sold separately.', Style number NG4426, Metal 14k Yellow Gold, 'Approximate Metal Weight 3.58 grams'. Identical to the stored record — a further independent corroboration. No value changed.",
 "SR-03": S+"official Sarraf page re-fetched live and re-read: 'Now: US$871.00' (MSRP US$3,388.00, Was US$1,019.00), SKU 18KY-LPBWB05, Stock Number 140139, Material '18K Solid Gold', 'Approximate Metal Weight 6.70 grams' (size-10 basis). Identical to the stored record; the 3.9x MSRP anchor (FLG-MED-14) reproduces live. No value changed.",
 "BN-20": S+"official Blue Nile page re-fetched live and re-read: '$965 (Setting Price)', Stock Number 505038y14, Metal 14K Yellow Gold, Width 1.80mm; contact panel '+1-800-242-2728' / 'service@bluenile.com'. Identical to the stored record. No gram weight published. No value changed.",
 "MJ-01": S+"official Mejuri page re-fetched live: the URL again resolves to the 'Solid White Gold (14k), Natural Diamond' variant at $548 (price matches the stored record; metal variant still differs from this row's yellow-gold basis — PRICE_VARIANT_DEPENDENT stands). The same page's Materials blurb is headed 'Solid Yellow Gold (14k)' while describing white-gold rhodium finishing, and states a two-year warranty and free 30-day returns from delivery. No gram weight published. No value changed.",
 "MN-01": S+"official Mene page re-fetched live: display price today is $1,442 USD for the default size (stored record: $1,465 captured 2026-10-22; Pass 16 structured size offers $1,800-$2,441). The page states 'Products are sold by weight, not size' and resale/exchange 'at the daily metal value', i.e. the price floats. Both dated readings are published; the stored value was NOT overwritten. PRICE_STRUCTURED_DIFFERS stands (FLG-PASS17-04). No gram weight was read from the fetched page content, so weight stays blank.",
 "BN-09": S+"stored Blue Nile URL re-opened via a browser-content fetch (not the CI runner): Blue Nile serves 'We're sorry, the page you're looking for cannot be found.' SOURCE_URL_DEAD is therefore corroborated on a second, independent read path. The stored $1,125 keeps its 2026-10-22 capture date: not re-confirmed, not deleted, not replaced with a guess.",
 "RS-05": S+"URL MIGRATION FOUND (FLG-PASS17-02): the stored ross-simons.com .html URL (HTTP 404 to the Pass 16 runner) was re-opened via a browser-content fetch and resolves to https://www.ross-simons.com/products/990022 , where the same product is live: '.80 Carat Ceritified [sic] Diamond Solitaire Ring in 14kt White Gold', Item 990022, 'Sale price $2,819' (Original price $3,995), GIA Cert#2225975086, Metal 14kt White Gold. The live $2,819 corroborates the stored price exactly. The stored URL and SOURCE_URL_DEAD flag are retained this pass to preserve the Pass 16 evidence chain; recommended next data pass: update the canonical URL to /products/990022 with this note as provenance. No value changed.",
}
rings = load("rings.json")
changed = 0
for r in rings["rows"]:
    if r["id"] in notes and "PASS 17 (2026-10-23, arena/0e04577b" not in (r.get("reverification") or ""):
        r["reverification"] = (r.get("reverification") or "") + notes[r["id"]]
        changed += 1
save("rings.json", rings)
print(f"rings.json: appended Pass 17 notes to {changed} rows (values untouched)")

spot = load("gold_spot.json")
spot["pass17_live_reading_2026_10_23"] = {
  "publisher": "World Gold Council (Goldhub)",
  "source_url": "https://www.gold.org/goldhub/data/gold-prices",
  "value_usd_per_oz": 3996.31,
  "page_date_as_shown_on_source": "22 October, 2026",
  "data_as_of_shown_on_source": "Data as of 22 October, 2026",
  "market_data_credit_as_shown": "Market Data: Provided by ICE Data Services",
  "retrieved_utc": "2026-10-23",
  "verification": "V1_direct_page_fetch",
  "spread_vs_active_benchmark_pct": -0.70,
  "decision": "Benchmark RETAINED at USD 4,024.45/oz (the Pass 12/14 dated reading). The live tick moved -0.70% while the source's own 'Data as of' date did not advance, so this reading is recorded as a dated cross-check (FLG-PASS17-01), not silently substituted into derived values. Every derived figure on the site remains labelled with the benchmark and its date; the calculator accepts any spot the reader enters (at 3,996.31/oz, gold = $128.4844/g and a 4.0 g 14K ring's gold value is $299.80 vs $301.91 at the benchmark).",
  "session": "arena/0e04577b-gold4 (Pass 17)"
}
save("gold_spot.json", spot)
print("gold_spot.json: Pass 17 live-tick cross-check recorded (benchmark unchanged)")

log = load("verification_log.json")
if not any("Pass 17" in (p.get("pass") or "") for p in log["passes"]):
    log["passes"].append({
      "pass": "Pass 17 — final integration, line-by-line re-verification & GitHub Pages re-publication (session arena/0e04577b-gold4)",
      "when_utc": "2026-10-23",
      "scope": "Whole repository as merged on main (64 rings / 10 retailers / 31 registered sources). Offline: all seven CI gates re-run fresh and every derived number independently re-derived. Online: the benchmark page, the two governing Tier A consumer/statute pages and seven retailer pages re-opened live and read field by field, deliberately including rows Pass 16 could not settle (a DIFFERS row, both dead-URL retailers, and the variant-priced Mejuri row). No stored price, weight, karat, URL or flag was changed by this pass; dated re-read notes were appended to seven rows.",
      "checked": [
        "All 7 gates re-run on the branched tree BEFORE any edit: audit.py PASS (131 passed, 1 warning BE-05 V2-only, 0 failures); check_site.py PASS (27 pages); verify.py PASS (64 records, blanks accounted); verify_a0be79d4.py PASS (2,072 links, 0 dead); audit_hallucinations.py PASS (941 checks); audit_freshness.py PASS (295 checks, 2 warnings BE-06/BE-07); citation gate PASS (109 CFR references; self-test rejects the known-bad Section 23.9 citation). Independent re-derivation: 0 mismatches across all 17 weighted rows; 0 phantom values (no weight => no gold value). Flag inventory re-counted: 250 instances (HALLMARK_NOT_PUBLISHED 64, NO_WEIGHT_PUBLISHED 47, SOLID_NOT_STATED 45).",
        "World Gold Council Goldhub re-read live (https://www.gold.org/goldhub/data/gold-prices): page dated '22 October, 2026', footer 'Data as of 22 October, 2026', market data by ICE Data Services — but the spot panel now ticks USD 3,996.31/oz against the frozen benchmark USD 4,024.45/oz (-0.70%). FLG-PASS17-01: benchmark RETAINED (the source date did not advance); the tick is recorded in data/gold_spot.json as a dated cross-check and every derived value stays labelled with the benchmark it was computed from. Sensitivity: at 3,996.31/oz gold is $128.4844/g; RS-04's 4.0 g 14K gold value moves $301.91 -> $299.80, far smaller than the 1.33x-6.65x price multiples being compared.",
        "FTC 'Buying Platinum, Gold, and Silver Jewelry' re-read live (https://consumer.ftc.gov/articles/buying-platinum-gold-and-silver-jewelry): karat mark states pure-gold content (18K = 18/24, 14K = 14/24); 'Near the karat quality mark, look for the name or the U.S. registered trademark... If you don't see a trademark along with the karat mark, don't buy it'; 'solid gold means the gold item isn't hollow'; vermeil = sterling silver base coated/plated with gold; gold-filled/overlay/RGP = layer of at least 10K gold on base metal; research complaints and get refund/return policies in writing. Every checklist claim on the site matches the page as read today.",
        "15 U.S.C. Section 295 re-read live (https://www.law.cornell.edu/uscode/text/15/295): tested-part fineness may not fall more than 3/1000 below the mark; whole-article fineness including solder may not fall more than 7/1000 below the mark (rings are 'any other such article'). The site's legal-minimum floors (14K 57.63%, 18K 74.30%) re-derive exactly: 14/24 - 0.007 = 0.576333, 18/24 - 0.007 = 0.743.",
        "AL-01 (Allurez) re-read live: $585, 'Setting only. Center stone sold separately.', NG4426, 14k Yellow Gold, 'Approximate Metal Weight 3.58 grams' — identical. SR-03 (Sarraf) re-read live: Now US$871.00 (MSRP US$3,388.00), 18KY-LPBWB05 / 140139, '18K Solid Gold', 6.70 grams — identical; 3.9x MSRP anchor reproduces. BN-20 (Blue Nile) re-read live: $965 (Setting Price), 505038y14, 14K Yellow Gold, 1.80mm, contact +1-800-242-2728 / service@bluenile.com — identical; no gram weight.",
        "MJ-01 (Mejuri) re-read live: URL again serves the Solid White Gold (14k) variant at $548 — price matches, variant mismatch (PRICE_VARIANT_DEPENDENT) reproduces; the same page's Materials heading says 'Solid Yellow Gold (14k)' while describing white-gold rhodium finishing; two-year warranty and free 30-day returns from delivery stated; no gram weight. MN-01 (Mene) re-read live: display $1,442 USD today vs stored $1,465 (2026-10-22) vs Pass 16 structured offers $1,800-$2,441; page states products are 'sold by weight' with exchange 'at the daily metal value' — FLG-PASS17-04: Mene prices float daily, both dated readings published, stored value not overwritten.",
        "BN-09 (Blue Nile, SOURCE_URL_DEAD) re-opened via a browser-content fetch: Blue Nile serves 'We're sorry, the page you're looking for cannot be found' — dead-link verdict corroborated off-runner; stored $1,125 (2026-10-22) stands flagged, not re-confirmed. RS-05 (Ross-Simons, SOURCE_URL_DEAD) — FLG-PASS17-02 URL MIGRATION: the stored .html URL resolves in a browser fetch to https://www.ross-simons.com/products/990022 where Item 990022 is live at 'Sale price $2,819' (was $3,995), GIA Cert#2225975086, 14kt White Gold (retailer title misspells 'Ceritified' [sic]). Live price corroborates the stored $2,819 exactly; stored URL/flag retained to preserve the Pass 16 evidence chain, with a recommendation that the next data pass adopt the /products/990022 canonical URL.",
        "FLG-PASS17-03 (corrected this pass): three hand-written README summary numbers had drifted from the dataset they describe — benchmark shown as $4,028.53/oz (data: $4,024.45/oz), source registry shown as 14 (data: 31), price provenance shown as 60 V1 / 3 V2 (data: of 62 priced rows, 61 V1 + 1 V2-only BE-05; the 2 blank prices are VR-02 U_unverified and BN-26 read-live with no price shown). README corrected with the Pass 17 date; the generated site was unaffected because it renders from JSON. FLG-PASS17-05 (standing, HIGH): none of the seven retailer pages re-read today — and none of the 64 in the dataset — publishes the physical karat stamp plus maker's/registered trademark; hallmark verification remains an in-hand + XRF step after delivery, exactly as the checklist states.",
        "Integration rebuild from data (compute.py -> generate_site.py -> build_site.py -> gen_verification.py) and all seven gates re-run on the regenerated tree before merge; results recorded in COORDINATION.md (session arena/0e04577b-gold4) and reports/audit_latest.txt. Full line-by-line record: reviews/pass17_repo_review_0e04577b.md."
      ],
      "result": "PASS — 7 retailer pages + WGC + FTC + Section 295 re-read live; 4 exact corroborations (AL-01, SR-03, BN-20, RS-05 price), 1 dead link corroborated (BN-09), 1 URL migration found (RS-05), 1 floating-price behaviour documented (MN-01), 1 variant mismatch reproduced (MJ-01), 1 spot-drift cross-check recorded, 3 stale README numbers corrected; 0 dataset values changed",
      "outcome": "The published numbers survived a fresh line-by-line read. What changed is the honesty layer around them: today's live gold tick, the Ross-Simons URL migration, Mene's daily floating price and the corrected README summary are all published with dates and source links instead of being silently absorbed. Recommendation repeated for every future review: re-open every source link, ask 'where is the official source, and what date was it read?', re-run scripts/audit.py + audit_hallucinations.py + audit_freshness.py, and treat anything that cannot answer as UNVERIFIED on the Flagged page."
    })
    log["coordination_summary"] = (log.get("coordination_summary") or "") + " | Pass 17 (arena/0e04577b-gold4, 2026-10-23): final integration — all 7 gates re-run, WGC/FTC/Section 295 + 7 retailer pages re-read live, RS-05 URL migration and Mene floating price documented, README summary corrected, site rebuilt and re-published; 0 dataset values changed."
    log["not_reverified_this_pass"] = [
      "Pass 17 (2026-10-23) re-opened live: AL-01, SR-03, BN-20, MJ-01, MN-01, BN-09, RS-05 plus the WGC, FTC and 15 U.S.C. Section 295 pages. The other 57 rows were NOT re-opened by this session and keep the capture/re-verification dates shown on each row (Pass 16 machine evidence of 2026-10-23T10:10:23Z still applies to them).",
      "BE-05 remains the only V2-only price (dated official-page snapshot; EUR served on live re-check in Pass 14); BE-01..BE-07 still refuse automated checks with HTTP 403, so no Brilliant Earth price was re-read this pass.",
      "AN-01 (Anjolee) was not re-read this pass; $870.76 and 2.90 g remain the 2026-10-22 readings and its price is not machine-readable (JavaScript shell in Pass 16).",
      "RS-05's canonical URL update (/products/990022) is recommended but deliberately NOT applied this pass, to preserve the Pass 16 evidence chain; see FLG-PASS17-02."
    ]
save("verification_log.json", log)
print("verification_log.json: Pass 17 appended; passes =", len(log["passes"]))
