# VERIFICATION.md — line-by-line verification record

Generated 2026-10-22 23:33 UTC from `data/*.json` by `scripts/gen_verification.py`.

## Rule applied to every single value

> **No hallucination.** A value is recorded only if it was read from the official page linked in the same row and the fetch was made during this project (verification level **V1**). If a value could not be read from the official page it is **blank** and flagged `PRICE_UNVERIFIED` / `NO_WEIGHT_PUBLISHED` / `WEIGHT_UNVERIFIED` on the Flagged for Review page. Nothing is estimated, averaged, inferred from photos, or copied from a blog, marketplace, resale listing or price-comparison site. Derived values (gold grams, gold value, price ÷ gold) are arithmetic on published inputs and are re-computed independently by `scripts/audit.py` on every pass.

**Benchmark:** gold spot **$4,028.53/oz** as shown on the World Gold Council page for **21 October, 2026** (retrieved 2026-10-22) = **$129.5202/g**. Benchmark source: https://www.gold.org/goldhub/data/gold-prices


## Coverage summary

- Rows: **22**
- Prices read from the seller's page: **21**
- Gram weights published by the seller: **7** (therefore only these rows have a computable gold value)
- Rows with explicit *solid gold* wording: **5**
- Rows publishing a hallmark or maker's mark: **0** (the legal requirement is quoted in `data/methodology.json`)
- Rows carrying at least one flag: **22**

## Line-by-line verification — every row

| ID | Retailer | Ring | Karat | Price | Price source (fetched) | Weight | Weight source (fetched) | Gold value (derived) | Solid wording | Hallmark | Flags |
|---|---|---|---|---|---|---|---|---|---|---|---|
| AL-01 | Allurez | [Engraved Floral Solitaire Engagement Ring Setting](https://www.allurez.com/products/floral-solitaire-engagement-ring-14k-yellow-gold) | 14K | $585 | V1 · 2026-10-22 | 3.58 g | V1 | $270.48 | not stated | not published | WEIGHT_APPROXIMATE, SOLID_NOT_STATED, HALLMARK_NOT_PUBLISHED |
| AL-02 | Allurez | [Milgrain Trellis Solitaire Engagement Ring](https://www.allurez.com/products/milgrain-trellis-solitaire-engagement-ring-14k-yellow-gold) | 14K | $724 | V1 · 2026-10-22 | 3.40 g | V1 | $256.88 | not stated | not published | WEIGHT_APPROXIMATE, SOLID_NOT_STATED, HALLMARK_NOT_PUBLISHED |
| AL-03 | Allurez | [Split Shank Solitaire Engagement Ring](https://www.allurez.com/products/split-shank-solitaire-engagement-ring-14k-yellow-gold) | 14K | $848 | V1 · 2026-10-22 | 4.40 g | V1 | $332.44 | not stated | not published | WEIGHT_APPROXIMATE, SOLID_NOT_STATED, HALLMARK_NOT_PUBLISHED |
| AL-04 | Allurez | [Split Shank Solitaire Engagement Ring](https://www.allurez.com/products/split-shank-solitaire-engagement-ring-18k-yellow-gold) | 18K | $1,425 | V1 · 2026-10-22 | 5.30 g | V1 | $514.84 | not stated | not published | WEIGHT_APPROXIMATE, SOLID_NOT_STATED, HALLMARK_NOT_PUBLISHED |
| AN-01 | Anjolee | [Six Curved Prongs Solitaire Diamond Engagement Ring (MS354-A)](https://www.anjolee.com/rings/diamond-solitaire-engagement-rings/Six-Curved-Prongs-Solitaire-Diamond-Engagement-Ring.aspx) | 14K | $870.76 | V1 · 2026-10-22 | 2.90 g | V1 | $219.11 | not stated | not published | PRICE_INCLUDES_CENTRE_STONE, CENTRE_STONE_LAB_CREATED, SOLID_NOT_STATED, HALLMARK_NOT_PUBLISHED, WHITE_GOLD |
| BE-01 | Brilliant Earth | [Atelier Solitaire Ring (2 mm, claw-prong bypass)](https://www.brilliantearth.com/Atelier-Solitaire-Ring-14K-Gold-BE1D2444-76788321/) | 14K | $1,190 | V1 · 2026-10-22 | **blank** | — | — | not stated | not published | NO_WEIGHT_PUBLISHED, SOLID_NOT_STATED, HALLMARK_NOT_PUBLISHED |
| BE-02 | Brilliant Earth | [Atelier Solitaire Ring (2 mm, claw-prong bypass)](https://www.brilliantearth.com/Atelier-Solitaire-Ring-Gold-BE1D2444-42024993/) | 18K | $1,390 | V1 · 2026-10-22 | **blank** | — | — | not stated | not published | NO_WEIGHT_PUBLISHED, SOLID_NOT_STATED, HALLMARK_NOT_PUBLISHED |
| BN-01 | Blue Nile | [Petite Solitaire Engagement Ring](https://www.bluenile.com/engagement-rings/design-your-own-ring/petite-solitaire-engagement-ring-in-14k-yellow-gold-item-195639) | 14K | $1,000 | V1 · 2026-10-22 | **blank** | — | — | not stated | not published | NO_WEIGHT_PUBLISHED, SOLID_NOT_STATED, HALLMARK_NOT_PUBLISHED |
| BN-02 | Blue Nile | [Petite Solitaire Engagement Ring](https://www.bluenile.com/engagement-rings/design-your-own-ring/petite-solitaire-engagement-ring-in-18k-yellow-gold-item-195269) | 18K | $1,155 | V1 · 2026-10-22 | **blank** | — | — | not stated | not published | NO_WEIGHT_PUBLISHED, SOLID_NOT_STATED, HALLMARK_NOT_PUBLISHED |
| BN-03 | Blue Nile | [Classic Six-Prong Solitaire Engagement Ring](https://www.bluenile.com/engagement-rings/design-your-own-ring/classic-six-prong-solitaire-engagement-ring-in-14k-yellow-gold-item-203272) | 14K | $1,000 | V1 · 2026-10-22 | **blank** | — | — | not stated | not published | NO_WEIGHT_PUBLISHED, SOLID_NOT_STATED, HALLMARK_NOT_PUBLISHED |
| BN-04 | Blue Nile | [Classic Comfort Fit Solitaire Engagement Ring (2.5mm)](https://www.bluenile.com/engagement-rings/design-your-own-ring/classic-comfort-fit-solitaire-engagement-ring-in-14k-yellow-gold-25mm-item-203284) | 14K | $935 | V1 · 2026-10-22 | **blank** | — | — | not stated | not published | NO_WEIGHT_PUBLISHED, SOLID_NOT_STATED, HALLMARK_NOT_PUBLISHED, COPY_INCONSISTENT_METAL |
| BN-05 | Blue Nile | [Classic Comfort Fit Solitaire Engagement Ring (2.5mm)](https://www.bluenile.com/engagement-rings/design-your-own-ring/classic-comfort-fit-solitaire-engagement-ring-in-18k-yellow-gold-25mm-item-194941) | 18K | $1,310 | V1 · 2026-10-22 | **blank** | — | — | not stated | not published | NO_WEIGHT_PUBLISHED, SOLID_NOT_STATED, HALLMARK_NOT_PUBLISHED |
| BN-06 | Blue Nile | [Six-Prong Low Dome Comfort Fit Solitaire Engagement Ring (2mm)](https://www.bluenile.com/engagement-rings/design-your-own-ring/six-prong-low-dome-comfort-fit-solitaire-engagement-ring-in-18k-yellow-gold-2mm-item-195379) | 18K | $1,295 | V1 · 2026-10-22 | **blank** | — | — | not stated | not published | NO_WEIGHT_PUBLISHED, SOLID_NOT_STATED, HALLMARK_NOT_PUBLISHED |
| BN-07 | Blue Nile | [Classic Four Prong Solitaire Engagement Ring](https://www.bluenile.com/engagement-rings/design-your-own-ring/classic-four-prong-solitaire-engagement-ring-in-14k-yellow-gold-item-203257) | 14K | $870 | V1 · 2026-10-22 | **blank** | — | — | not stated | not published | NO_WEIGHT_PUBLISHED, SOLID_NOT_STATED, HALLMARK_NOT_PUBLISHED, MIXED_METAL_UNCLEAR |
| BN-08 | Blue Nile | [Riviera Pave Diamond Engagement Ring (1/6 ct. tw.)](https://www.bluenile.com/engagement-rings/design-your-own-ring/riviera-pave-diamond-engagement-ring-in-14k-yellow-gold-1-6-ct-tw-item-203512) | 14K | $1,500 | V1 · 2026-10-22 | **blank** | — | — | not stated | not published | NO_WEIGHT_PUBLISHED, SOLID_NOT_STATED, HALLMARK_NOT_PUBLISHED, COPY_INCONSISTENT_METAL |
| MJ-01 | Mejuri | [Diamonds Team Ring](https://mejuri.com/products/diamonds-team-ring) | 14K | $548 | V1 · 2026-10-22 | **blank** | — | — | stated: “Solid Yellow Gold (14k)” | not published | NO_WEIGHT_PUBLISHED, HALLMARK_NOT_PUBLISHED, NOT_MARKETED_AS_BRIDAL, PRICE_VARIANT_DEPENDENT |
| MJ-02 | Mejuri | [Diamonds Band](https://mejuri.com/products/diamonds-band) | 14K | $648 | V1 · 2026-10-22 | **blank** | — | — | stated: “Solid Yellow Gold (14k)” | not published | NO_WEIGHT_PUBLISHED, HALLMARK_NOT_PUBLISHED, NOT_MARKETED_AS_BRIDAL |
| MJ-03 | Mejuri | [Pave Diamond Slim Signet](https://mejuri.com/products/pave-diamond-slim-signet-ring) | 14K | $548 | V1 · 2026-10-22 | **blank** | — | — | stated: “Solid Yellow Gold (14k)” | not published | NO_WEIGHT_PUBLISHED, HALLMARK_NOT_PUBLISHED, NOT_MARKETED_AS_BRIDAL, ENGRAVING_NON_RETURNABLE, PRICE_VARIANT_DEPENDENT |
| MJ-04 | Mejuri | [Pave Diamond Thin Dome Ring](https://mejuri.com/products/pave-diamond-thin-dome-ring) | 14K | $798 | V1 · 2026-10-22 | **blank** | — | — | stated: “Solid Yellow Gold (14k)” | not published | NO_WEIGHT_PUBLISHED, HALLMARK_NOT_PUBLISHED, NOT_MARKETED_AS_BRIDAL |
| MJ-05 | Mejuri | [Ziggy Ring (Bezel Lab Grown Diamond Zig-Zag Ring)](https://mejuri.com/products/bezel-lab-grown-diamond-zig-zag-ring) | 14K | $598 | V1 · 2026-10-22 | **blank** | — | — | stated: “Solid Yellow Gold (14k)” | not published | NO_WEIGHT_PUBLISHED, HALLMARK_NOT_PUBLISHED, NOT_MARKETED_AS_BRIDAL, SCS_CERT_REQUIRED_FOR_RETURN, PRICE_IS_FROM_PRICE |
| VR-01 | VRAI | [The Classic Engagement Ring (4-prong dome, plain band)](https://www.vrai.com/configure/setting-to-diamond/classic-4-prong-dome/round-brilliant-yellow-gold-40635875360861) | 18K | $1,035 | V1 · 2026-10-22 | 2.86 g | V1 | $277.82 | not stated | not published | PRICE_IS_FROM_PRICE, PRICE_AND_WEIGHT_DIFFERENT_URLS, SOLID_NOT_STATED, HALLMARK_NOT_PUBLISHED, SPEC_LISTED_PAVE_ON_PLAIN_BAND |
| VR-02 | VRAI | [Signature 6 Prong Engagement Ring (plain band)](https://www.vrai.com/configure/setting-to-diamond/signature-6-prong/round-brilliant-yellow-gold-32891144798301) | 18K | **blank** | **not verified** | 2.84 g | V1 | $275.88 | not stated | not published | PRICE_UNVERIFIED, SOLID_NOT_STATED, HALLMARK_NOT_PUBLISHED, SPEC_LISTED_PAVE_ON_PLAIN_BAND |

## Derived arithmetic (re-computed and cross-checked by the audit)

| ID | Weight (g) | Fineness | Pure gold (g) | Spot $/g | Gold value | Legal-min value (stamp − 0.007) | Price | Price ÷ gold |
|---|---|---|---|---|---|---|---|---|
| AL-01 | 3.58 | 0.5833 | 2.088 | $129.5202 | $270.48 | $267.24 | $585 | 2.16× |
| AL-02 | 3.40 | 0.5833 | 1.983 | $129.5202 | $256.88 | $253.80 | $724 | 2.82× |
| AL-03 | 4.40 | 0.5833 | 2.567 | $129.5202 | $332.44 | $328.45 | $848 | 2.55× |
| AL-04 | 5.30 | 0.7500 | 3.975 | $129.5202 | $514.84 | $510.04 | $1,425 | 2.77× |
| AN-01 | 2.90 | 0.5833 | 1.692 | $129.5202 | $219.11 | $216.48 | $870.76 | 3.97× |
| VR-01 | 2.86 | 0.7500 | 2.145 | $129.5202 | $277.82 | $275.23 | $1,035 | 3.73× |
| VR-02 | 2.84 | 0.7500 | 2.130 | $129.5202 | $275.88 | $273.30 | **blank** | **blank**× |

## Karat pairs (same design, both karats sold by the same retailer)

| Pair | Retailer | Design | 14K → 18K price | Price gap | Gold-content gap | Multiple 14K → 18K |
|---|---|---|---|---|---|---|
| PAIR-AL-SPLIT | Allurez | [Split Shank Solitaire Engagement Ring](https://www.allurez.com/products/split-shank-solitaire-engagement-ring-14k-yellow-gold) ([AL-03](https://www.allurez.com/products/split-shank-solitaire-engagement-ring-14k-yellow-gold), [AL-04](https://www.allurez.com/products/split-shank-solitaire-engagement-ring-18k-yellow-gold)) | $848 → $1,425 | +68.0% | +54.9% | 2.55× → 2.77× |
| PAIR-BE-ATELIER | Brilliant Earth | [Atelier Solitaire Ring (2 mm, claw-prong bypass)](https://www.brilliantearth.com/Atelier-Solitaire-Ring-14K-Gold-BE1D2444-76788321/) ([BE-01](https://www.brilliantearth.com/Atelier-Solitaire-Ring-14K-Gold-BE1D2444-76788321/), [BE-02](https://www.brilliantearth.com/Atelier-Solitaire-Ring-Gold-BE1D2444-42024993/)) | $1,190 → $1,390 | +16.8% | **not computable** (no published weights) | **blank**× → **blank**× |
| PAIR-BN-COMFORT | Blue Nile | [Classic Comfort Fit Solitaire Engagement Ring (2.5mm)](https://www.bluenile.com/engagement-rings/design-your-own-ring/classic-comfort-fit-solitaire-engagement-ring-in-14k-yellow-gold-25mm-item-203284) ([BN-04](https://www.bluenile.com/engagement-rings/design-your-own-ring/classic-comfort-fit-solitaire-engagement-ring-in-14k-yellow-gold-25mm-item-203284), [BN-05](https://www.bluenile.com/engagement-rings/design-your-own-ring/classic-comfort-fit-solitaire-engagement-ring-in-18k-yellow-gold-25mm-item-194941)) | $935 → $1,310 | +40.1% | **not computable** (no published weights) | **blank**× → **blank**× |
| PAIR-BN-PETITE | Blue Nile | [Petite Solitaire Engagement Ring](https://www.bluenile.com/engagement-rings/design-your-own-ring/petite-solitaire-engagement-ring-in-14k-yellow-gold-item-195639) ([BN-01](https://www.bluenile.com/engagement-rings/design-your-own-ring/petite-solitaire-engagement-ring-in-14k-yellow-gold-item-195639), [BN-02](https://www.bluenile.com/engagement-rings/design-your-own-ring/petite-solitaire-engagement-ring-in-18k-yellow-gold-item-195269)) | $1,000 → $1,155 | +15.5% | **not computable** (no published weights) | **blank**× → **blank**× |

## Seller-level claims and the page that proves each one

| Seller | Return window | Contact captured | Resized rings returnable | Custom / engraved | Resize service | Warranty | Solid wording | Policy source |
|---|---|---|---|---|---|---|---|---|
| Blue Nile | 30 days | +1-800-242-2728 | no | excluded | One free resize up or down two sizes within 6 months if the design permits; eternity bands, tension rings, alternative-metal rings and some milgrain/ornate bands cannot be resized | Limited lifetime warranty on gold and platinum items with a purchase price of $1,000 or mo | not stated | [Return Policy - 30-day money back guarantee](https://www.bluenile.com/policies/returns) |
| Allurez | 30 days | +1-800-554-3509 | no | excluded | Not published as a free service; the included 1-year warranty covers free ring sizing | Free 1-year limited warranty included (2-year +$59, 10-year +$79, lifetime +$149 on the 14 | not stated | [Return Policy](https://www.allurez.com/pages/return-policy) |
| VRAI | 30 days | help@vrai.com | no | excluded | One complimentary resize up to one full US size; infinity and eternity bands cannot be resized | Lifetime warranty and annual shine are listed as included with the ring on the product pag | not stated | [Returns & Exchanges](https://www.vrai.com/returns-exchanges) |
| Mejuri | 30 days | **not captured** | not excluded | excluded | Not published as a standard free service on the captured returns page | Two-year warranty from the date of receipt for defects or issues resulting from workmanshi | stated | [Returns Terms & Conditions](https://mejuri.com/company/returns-terms) |
| Brilliant Earth | 30 days | 800.691.0952 | not excluded | no exclusion captured | Page badge reads "Free 1-Year Resizing" (Pass 5, 2026-10-22). The earlier capture of the same page described one complimentary resize within 60 days of purchase. The two captures disagree, so ask the seller which applies to your ring before ordering. | Free Lifetime Warranty (product page badge) | not stated | [Atelier Solitaire Ring in 18K Yellow Gold](https://www.brilliantearth.com/Atelier-Solitaire-Ring-Gold-BE1D2444-42024993/) |
| Anjolee | 30 days | 877-265-6533 | not excluded | no exclusion captured | Not captured on the page | Lifetime warranty (prong tightening, re-polishing, rhodium plating, cleaning) plus a one-y | not stated | [Six Curved Prongs Solitaire Diamond Engagement Ring (MS354-A)](https://www.anjolee.com/rings/diamond-solitaire-engagement-rings/Six-Curved-Prongs-Solitaire-Diamond-Engagement-Ring.aspx) |

## Source registry

| ID | Tier | Publisher | Document | Retrieved |
|---|---|---|---|---|
| ftc-gold-jewelry | A | U.S. Federal Trade Commission (consumer.ftc.gov) | [Buying Platinum, Gold, and Silver Jewelry](https://consumer.ftc.gov/articles/buying-platinum-gold-and-silver-jewelry) | 2026-10-22 |
| ecfr-16-23 | A | U.S. Federal Trade Commission / eCFR (National Archives) | [16 CFR Part 23 - Guides for the Jewelry, Precious Metals, and Pewter Industries](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-23) | 2026-10-22 |
| usc-15-295 | A | U.S. Code (Legal Information Institute, Cornell Law School) - 15 U.S.C. § 295 | [Standard of fineness of gold articles; deviation](https://www.law.cornell.edu/uscode/text/15/295) | 2026-10-22 |
| usc-15-ch8 | A | U.S. Code (Legal Information Institute) - 15 U.S.C. ch. 8 | [Falsely stamped gold or silver or goods manufactured therefrom (sections 291-300)](https://www.law.cornell.edu/uscode/text/15/chapter-8) | 2026-10-22 |
| wgc-gold-prices | B | World Gold Council (Goldhub) | [Gold spot prices & market history](https://www.gold.org/goldhub/data/gold-prices) | 2026-10-22 |
| lbma-prices | B | London Bullion Market Association | [LBMA Precious Metal Prices](https://www.lbma.org.uk/prices-and-data/precious-metal-prices) | 2026-10-22 |
| ftc-credit-cards | A | U.S. Federal Trade Commission (consumer.ftc.gov) | [Using Credit Cards and Disputing Charges](https://consumer.ftc.gov/articles/using-credit-cards-and-disputing-charges) | 2026-10-22 |
| bluenile-returns | C | Blue Nile | [Return Policy - 30-day money back guarantee](https://www.bluenile.com/policies/returns) | 2026-10-22 |
| allurez-returns | C | Allurez | [Return Policy](https://www.allurez.com/pages/return-policy) | 2026-10-22 |
| vrai-returns | C | VRAI | [Returns & Exchanges](https://www.vrai.com/returns-exchanges) | 2026-10-22 |
| mejuri-returns | C | Mejuri | [Returns Terms & Conditions](https://mejuri.com/company/returns-terms) | 2026-10-22 |
| brilliantearth-atelier | C | Brilliant Earth | [Atelier Solitaire Ring in 18K Yellow Gold](https://www.brilliantearth.com/Atelier-Solitaire-Ring-Gold-BE1D2444-42024993/) | 2026-10-22 |
| anjolee-ms354a | C | Anjolee | [Six Curved Prongs Solitaire Diamond Engagement Ring (MS354-A)](https://www.anjolee.com/rings/diamond-solitaire-engagement-rings/Six-Curved-Prongs-Solitaire-Diamond-Engagement-Ring.aspx) | 2026-10-22 |
| brilliantearth-atelier-14k | C | Brilliant Earth | [Atelier Solitaire Ring in 14K Yellow Gold](https://www.brilliantearth.com/Atelier-Solitaire-Ring-14K-Gold-BE1D2444-76788321/) | 2026-10-22 |

## Irregularities flagged for human review

1. **Blue Nile copy contradicts its own specification (BN-04).** The 14K Comfort Fit 2.5 mm description says the ring is “crafted in 18k yellow gold” while the specification block says 14K Yellow Gold. Page: https://www.bluenile.com/engagement-rings/design-your-own-ring/classic-comfort-fit-solitaire-engagement-ring-in-14k-yellow-gold-25mm-item-203284
2. **Blue Nile copy names the wrong metal colour (BN-08).** The Riviera Pavé 14K *yellow* gold page says the diamonds are “set in 14k white gold”. Page: https://www.bluenile.com/engagement-rings/design-your-own-ring/riviera-pave-diamond-engagement-ring-in-14k-yellow-gold-1-6-ct-tw-item-203512
3. **Mixed-metal ambiguity (BN-07).** The Classic Four Prong Solitaire is titled 14K Yellow Gold but the description mentions “platinum prongs”; if true, the ring is not all gold and any gold-weight calculation would overstate the gold content. Page: https://www.bluenile.com/engagement-rings/design-your-own-ring/classic-four-prong-solitaire-engagement-ring-in-14k-yellow-gold-item-203257
4. **No hallmark anywhere.** 0 of 20 rows publish the physical stamp or the maker's mark, so the hallmark requirement can only be checked in hand.
5. **Weights are approximate where they exist.** Allurez labels its number “Approximate Metal Weight”; VRAI publishes a size-6 metal weight. Neither is a measurement of the ring you will receive.
6. **Two search-snapshot-only values were deliberately NOT used:** an Anjolee “2.90 Gr.” weight and every Brilliant Earth price/weight. They appeared only in search-engine snapshots of the official pages and could not be re-read from the live page, so they are recorded as unverified rather than published.
7. **Reputation was not verified for any seller.** No independent review or complaints dataset was collected, so no reputation claim is made anywhere on the site.
8. **Seller contact gaps.** Mejuri's phone/email did not appear in the captured policy page; Brilliant Earth's email did not. Both are left blank rather than guessed.
9. **Structured data notes used prices from a listing card.** VRAI's “From $1,035” is a listing-level price, while its 2.86 g weight comes from the configuration page for the same design. Both are VRAI pages, but the pair is flagged `PRICE_AND_WEIGHT_DIFFERENT_URLS`.

## Unverified values published as blank

- **AL-01** (Allurez · Engraved Floral Solitaire Engagement Ring Setting): solid-gold wording not published on the captured page → https://www.allurez.com/products/floral-solitaire-engagement-ring-14k-yellow-gold
- **AL-02** (Allurez · Milgrain Trellis Solitaire Engagement Ring): solid-gold wording not published on the captured page → https://www.allurez.com/products/milgrain-trellis-solitaire-engagement-ring-14k-yellow-gold
- **AL-03** (Allurez · Split Shank Solitaire Engagement Ring): solid-gold wording not published on the captured page → https://www.allurez.com/products/split-shank-solitaire-engagement-ring-14k-yellow-gold
- **AL-04** (Allurez · Split Shank Solitaire Engagement Ring): solid-gold wording not published on the captured page → https://www.allurez.com/products/split-shank-solitaire-engagement-ring-18k-yellow-gold
- **AN-01** (Anjolee · Six Curved Prongs Solitaire Diamond Engagement Ring (MS354-A)): solid-gold wording not published on the captured page → https://www.anjolee.com/rings/diamond-solitaire-engagement-rings/Six-Curved-Prongs-Solitaire-Diamond-Engagement-Ring.aspx
- **BE-01** (Brilliant Earth · Atelier Solitaire Ring (2 mm, claw-prong bypass)): weight, solid-gold wording not published on the captured page → https://www.brilliantearth.com/Atelier-Solitaire-Ring-14K-Gold-BE1D2444-76788321/
- **BE-02** (Brilliant Earth · Atelier Solitaire Ring (2 mm, claw-prong bypass)): weight, solid-gold wording not published on the captured page → https://www.brilliantearth.com/Atelier-Solitaire-Ring-Gold-BE1D2444-42024993/
- **BN-01** (Blue Nile · Petite Solitaire Engagement Ring): weight, solid-gold wording not published on the captured page → https://www.bluenile.com/engagement-rings/design-your-own-ring/petite-solitaire-engagement-ring-in-14k-yellow-gold-item-195639
- **BN-02** (Blue Nile · Petite Solitaire Engagement Ring): weight, solid-gold wording not published on the captured page → https://www.bluenile.com/engagement-rings/design-your-own-ring/petite-solitaire-engagement-ring-in-18k-yellow-gold-item-195269
- **BN-03** (Blue Nile · Classic Six-Prong Solitaire Engagement Ring): weight, solid-gold wording not published on the captured page → https://www.bluenile.com/engagement-rings/design-your-own-ring/classic-six-prong-solitaire-engagement-ring-in-14k-yellow-gold-item-203272
- **BN-04** (Blue Nile · Classic Comfort Fit Solitaire Engagement Ring (2.5mm)): weight, solid-gold wording not published on the captured page → https://www.bluenile.com/engagement-rings/design-your-own-ring/classic-comfort-fit-solitaire-engagement-ring-in-14k-yellow-gold-25mm-item-203284
- **BN-05** (Blue Nile · Classic Comfort Fit Solitaire Engagement Ring (2.5mm)): weight, solid-gold wording not published on the captured page → https://www.bluenile.com/engagement-rings/design-your-own-ring/classic-comfort-fit-solitaire-engagement-ring-in-18k-yellow-gold-25mm-item-194941
- **BN-06** (Blue Nile · Six-Prong Low Dome Comfort Fit Solitaire Engagement Ring (2mm)): weight, solid-gold wording not published on the captured page → https://www.bluenile.com/engagement-rings/design-your-own-ring/six-prong-low-dome-comfort-fit-solitaire-engagement-ring-in-18k-yellow-gold-2mm-item-195379
- **BN-07** (Blue Nile · Classic Four Prong Solitaire Engagement Ring): weight, solid-gold wording not published on the captured page → https://www.bluenile.com/engagement-rings/design-your-own-ring/classic-four-prong-solitaire-engagement-ring-in-14k-yellow-gold-item-203257
- **BN-08** (Blue Nile · Riviera Pave Diamond Engagement Ring (1/6 ct. tw.)): weight, solid-gold wording not published on the captured page → https://www.bluenile.com/engagement-rings/design-your-own-ring/riviera-pave-diamond-engagement-ring-in-14k-yellow-gold-1-6-ct-tw-item-203512
- **MJ-01** (Mejuri · Diamonds Team Ring): weight not published on the captured page → https://mejuri.com/products/diamonds-team-ring
- **MJ-02** (Mejuri · Diamonds Band): weight not published on the captured page → https://mejuri.com/products/diamonds-band
- **MJ-03** (Mejuri · Pave Diamond Slim Signet): weight not published on the captured page → https://mejuri.com/products/pave-diamond-slim-signet-ring
- **MJ-04** (Mejuri · Pave Diamond Thin Dome Ring): weight not published on the captured page → https://mejuri.com/products/pave-diamond-thin-dome-ring
- **MJ-05** (Mejuri · Ziggy Ring (Bezel Lab Grown Diamond Zig-Zag Ring)): weight not published on the captured page → https://mejuri.com/products/bezel-lab-grown-diamond-zig-zag-ring
- **VR-01** (VRAI · The Classic Engagement Ring (4-prong dome, plain band)): solid-gold wording not published on the captured page → https://www.vrai.com/configure/setting-to-diamond/classic-4-prong-dome/round-brilliant-yellow-gold-40635875360861
- **VR-02** (VRAI · Signature 6 Prong Engagement Ring (plain band)): price, solid-gold wording not published on the captured page → https://www.vrai.com/configure/setting-to-diamond/signature-6-prong/round-brilliant-yellow-gold-32891144798301

## Integrity audit output (hallucination / security check)

```
GOLD4 integrity audit (hallucination / security check)
run_utc: 2026-10-22T23:33:03+00:00
dataset rows: 22 | sellers: 6 | sources: 14
spot benchmark: $4,028.53/oz (21 October, 2026) = $129.5202/g

RESULT: PASS  (59 passed, 0 warnings, 0 failures)

No warnings, no failures.

Checks performed: source registry + domain allow-list, banned-domain scan, HTTPS enforcement,
price/weight provenance, capture dates, blank-value flagging, karat/fineness consistency,
independent recomputation of every derived number, phantom-math detection (no weight => no value),
seller contact/return provenance, speculation-language scan, site link check,
per-row source-link requirement, and render-text sanity.
```

Re-run after every review pass:

```bash
python3 scripts/compute.py && python3 scripts/build_site.py && python3 scripts/audit.py
```

