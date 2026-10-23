# Pass 17 — Repo review, line-by-line re-verification & final integration

**Session:** `arena/0e04577b-gold4` · **Date:** 2026-10-23 · **Live site:** https://karagemop466-tech.github.io/GOLD4/

## ⚠ NO HALLUCINATIONS — the rule this review was run under

> Every price, weight, karat, policy and link below was read from the **official page linked beside it**. If a value could not be read from an official source it is shown **blank** and flagged `UNVERIFIED` — never estimated, averaged, converted between currencies, inferred from photographs, or copied from a blog, marketplace, resale listing or price-comparison site. Derived numbers (pure gold, gold value, price ÷ gold) are labelled *derived*, state their formula and benchmark, and were independently re-derived in this pass. **Re-run the hallucination/security gates after every review** (`scripts/audit.py`, `scripts/audit_hallucinations.py`, `scripts/audit_freshness.py`, `scripts/check_site.py`, `scripts/verify.py`, `scripts/verify_a0be79d4.py`, citation gate) and ask of every row: *where is the official source, and what date was it read?* Anything that cannot answer belongs on [Flagged for Review](https://karagemop466-tech.github.io/GOLD4/pages/flagged.html), not in a price cell.

**What this pass did.** (1) Re-ran all seven numbered CI gates on the branched `main` *before* editing anything — all passed; independently re-derived every weighted row (0 mismatches, 0 phantom values). (2) Re-opened live: the World Gold Council benchmark page, the FTC gold-jewelry guidance, 15 U.S.C. § 295, and seven retailer pages chosen to stress-test the weakest evidence (a `DIFFERS` row, both dead-URL retailers, the variant-priced Mejuri row, plus three `CONFIRMED` anchors). (3) Corrected three drifted README summary numbers with dated notes. (4) Rebuilt the site from data and re-ran every gate. **No stored price, weight, karat, URL or flag was changed.** Claim, task board and close-out: [`COORDINATION.md`](../COORDINATION.md) (Pass 17, session `arena/0e04577b-gold4`).

---

## 1. Gold benchmark & calculator basis (verify before you compare any price)

| Item | Value | Source (official) | Read |
|---|---|---|---|
| Frozen benchmark used for **every** derived figure on the site | **$4,024.45 / troy oz = $129.3891 / g** | [World Gold Council — Gold spot prices](https://www.gold.org/goldhub/data/gold-prices) — page dated "22 October, 2026", footer "Data as of 22 October, 2026", market data by ICE Data Services | Benchmark captured 2026-10-23 (Passes 12/14); page re-read live 2026-10-23 (Pass 17) |
| Live tick on the same page at Pass 17 re-read | **$3,996.31 / oz = $128.4844 / g** (−0.70% vs benchmark) | Same WGC page, same "Data as of 22 October, 2026" date line | 2026-10-23 — recorded as a dated cross-check in `data/gold_spot.json` (`pass17_live_reading_2026_10_23`); **not** substituted into derived values (FLG-PASS17-01) |
| Troy ounce | 31.1034768 g | Definition (480 grains); see the exact-conversion note in `data/gold_spot.json` | — |

**Formulas (also in `data/methodology.json`, enforced by `scripts/audit.py`):**

- Fineness = karat ÷ 24 (10K = 41.667%, 14K = 58.333%, 18K = 75.000%, 24K = 100%).
- Pure gold (g) = ring weight (g) × fineness.
- Gold value (USD) = pure gold (g) × (spot $/oz ÷ 31.1034768).
- Legal-minimum gold value = weight × (fineness − 0.007) × $/g — the whole-article tolerance in [15 U.S.C. § 295](https://www.law.cornell.edu/uscode/text/15/295) (re-read live 2026-10-23: tested part ≤3/1000 below the mark; whole article incl. solder ≤7/1000 below). So a ring stamped 14K may lawfully assay at 57.63% and one stamped 18K at 74.30% — **a stamp is a claim with a tolerance, not a measurement**.
- Price ÷ gold multiple = asking price ÷ gold value. The site calculator does exactly this arithmetic in your browser (no network call): [Calculator](https://karagemop466-tech.github.io/GOLD4/pages/calculator.html).

**Worked examples (derived — check them yourself):**

1. *Benchmark check:* 4.0 g of 14K @ $4,024.45/oz → pure gold 2.333 g → **$301.91** (legal-min $298.28). This reproduces row RS-04's published gold value to the cent.
2. *Drift sensitivity:* the same ring at today's live tick $3,996.31/oz → **$299.80**. A −0.70% spot move matters far less than the 1.33×–6.65× price multiples below — but enter the day's spot in the calculator before buying.
3. *The karat trap (both rows publish weights):* RS-02 is **18K but only 0.7 g** = 0.525 g pure gold ($67.93); RS-01 is **14K and 1.7 g** = 0.992 g pure gold ($128.31). The higher-karat ring contains **47% less gold**. Karat without grams tells you almost nothing about gold value — which is why the 47 rows with no published weight stay blank instead of being guessed.

---

## 2. The buying checklist, answered with evidence (each claim ↔ official source)

| # | Checklist item | What the official source says | What this dataset shows | Where to verify |
|---|---|---|---|---|
| 1 | **Gold purity** — confirm 10K/14K/18K | [FTC](https://consumer.ftc.gov/articles/buying-platinum-gold-and-silver-jewelry): the karat mark states pure-gold content (18K = 18/24, 14K = 14/24). Re-read live 2026-10-23 | 64 rows: 42×14K, 18×18K, 2×10K, 2×24K (Menē). Higher karat = higher gold fraction, **not** necessarily more gold (see RS-01 vs RS-02) | [Purity page](https://karagemop466-tech.github.io/GOLD4/pages/purity.html) |
| 2 | **Solid gold** — must say so; reject plated / vermeil / filled / overlay / gold-tone | [FTC](https://consumer.ftc.gov/articles/buying-platinum-gold-and-silver-jewelry): "solid gold means the gold item isn't hollow"; vermeil = sterling-silver base plated with gold; filled/overlay/RGP = ≥10K layer on base metal | Only **19 of 64** rows carry explicit solid-gold wording; 45 are flagged `SOLID_NOT_STATED` (absence of the words is published, not assumed away) | [Flagged](https://karagemop466-tech.github.io/GOLD4/pages/flagged.html) |
| 3 | **Hallmark** — karat stamp **plus** maker's / registered trademark | [FTC](https://consumer.ftc.gov/articles/buying-platinum-gold-and-silver-jewelry): "Near the karat quality mark, look for the name or the U.S. registered trademark… If you don't see a trademark along with the karat mark, don't buy it." | **0 of 64** product pages publish the physical stamp + trademark (re-confirmed on all 7 pages re-read this pass — FLG-PASS17-05). This check can only be done in hand | [Methodology](https://karagemop466-tech.github.io/GOLD4/pages/methodology.html) |
| 4 | **Weight in grams** — a legitimate seller can provide it | Dataset policy (`data/methodology.json`): no published grams ⇒ blank, never estimated | **17 of 64** publish a gram weight (Allurez 4, Sarraf 6, Ross-Simons 4, VRAI 2, Anjolee 1). Blue Nile, Brilliant Earth, Mejuri, Catbird and Menē publish none in this dataset — their gold content is *unknowable from the listing* | [Calculator](https://karagemop466-tech.github.io/GOLD4/pages/calculator.html) |
| 5 | **Seller reputation** — independent reviews/complaints + real contact details | [FTC](https://consumer.ftc.gov/articles/buying-platinum-gold-and-silver-jewelry): search the seller's name + "complaint"/"review"; get policies in writing | Contact routes are captured per seller (e.g. Blue Nile +1-800-242-2728 / service@bluenile.com, re-read live this pass). **Reputation scores are deliberately NOT published** — no independent review data was collected under official-source rules, so that field stays empty and flagged rather than scraped | [Sellers](https://karagemop466-tech.github.io/GOLD4/pages/sellers.html) |
| 6 | **Price vs gold value** — unusually cheap is a red flag | Arithmetic above at the dated benchmark | Across the 16 rows with both price and weight: **1.33×–6.65×**. Plain Sarraf bands sit at the floor (1.33×–1.50×); rows whose price includes a centre stone (AN-01, SR-05, SR-06) are *not* setting markups and are labelled as such | §4 table below |
| 7 | **Return policy** — incl. resized/custom exclusions | Each seller's own returns page (registered in `data/sources.json`) | Windows: 30 days (8 sellers), 20 days (Catbird), **7 days (Menē)**. Resized/engraved/custom items are excluded by most sellers — **do not resize or wear the ring before independent verification, or you may void the return** | [Sellers](https://karagemop466-tech.github.io/GOLD4/pages/sellers.html) |
| 8 | **Payment** — prefer a credit card | [FTC — Using Credit Cards and Disputing Charges](https://consumer.ftc.gov/articles/using-credit-cards-and-disputing-charges); [CFPB FCBA guidance](https://www.consumerfinance.gov/ask-cfpb/how-do-i-dispute-a-charge-on-my-credit-card-bill-en-61/); [15 U.S.C. § 1666](https://www.law.cornell.edu/uscode/text/15/1666) (all registered Tier A) | Guidance only — the dataset records no payment data | [Methodology](https://karagemop466-tech.github.io/GOLD4/pages/methodology.html) |
| 9 | **Documentation** — keep listing, receipt, purity claims | — | Every row preserves its source URL + capture date; dead links are kept and flagged rather than deleted, so the claim as captured remains auditable | [Sources](https://karagemop466-tech.github.io/GOLD4/pages/sources.html) |
| 10 | **On arrival** — independent jeweler; **XRF** or equivalent; don't trust the stamp alone | GIA Lab Notes registered as Tier B ([XRF chemical analysis](https://www.gia.edu/gems-gemology/winter-2024-chemical-analysis)); § 295 tolerances above | Nothing in an online listing can substitute for this step: 0/64 hallmarks published, 47/64 weights unpublished, and § 295 allows below-stamp fineness | [Checklist page](https://karagemop466-tech.github.io/GOLD4/pages/calculator.html) |
| 11 | **If the seller won't allow independent verification / return — don't buy** | Follows from items 3, 7 and 10 | Menē's 7-day window is the tightest in the dataset: schedule the jeweler/XRF appointment *before* ordering | [Sellers](https://karagemop466-tech.github.io/GOLD4/pages/sellers.html) |

**The key point, restated with this pass's evidence:** a 14K/18K stamp by itself proves nothing — US law ([§ 295](https://www.law.cornell.edu/uscode/text/15/295)) expressly permits fineness below the stamp, no retailer in this dataset publishes the stamp, and most don't publish the weight. Reputable seller + proper markings checked in hand + price sanity-checked against grams + independent XRF after delivery (inside the return window, before resizing/wearing) is the only complete chain.

---

## 3. Pass 17 live re-reads (2026-10-23) — what each official page actually showed

| Row / source | Official page | Stored value (capture date) | Read live this pass | Verdict |
|---|---|---|---|---|
| Benchmark | [gold.org/goldhub/data/gold-prices](https://www.gold.org/goldhub/data/gold-prices) | $4,024.45/oz, "Data as of 22 Oct 2026" (2026-10-23) | $3,996.31/oz; page date and "Data as of" still 22 Oct 2026; ICE Data Services credit present | **Drift −0.70% recorded; benchmark retained** (FLG-PASS17-01) |
| FTC guidance (Tier A) | [consumer.ftc.gov](https://consumer.ftc.gov/articles/buying-platinum-gold-and-silver-jewelry) | Checklist rules in `data/methodology.json` | Karat/trademark, solid ≠ hollow, vermeil/filled definitions, complaint search, written policies — all as cited | **Match** |
| 15 U.S.C. § 295 (Tier A) | [law.cornell.edu](https://www.law.cornell.edu/uscode/text/15/295) | 3/1000 tested part; 7/1000 whole article | Statute text states exactly that | **Match** (14K floor 57.63%, 18K floor 74.30% re-derived) |
| AL-01 | [allurez.com](https://www.allurez.com/products/floral-solitaire-engagement-ring-14k-yellow-gold) | $585 · 14K · 3.58 g (2026-10-22) | $585; "Setting only"; NG4426; 14k Yellow Gold; "Approximate Metal Weight 3.58 grams" | **Exact match** |
| SR-03 | [sarraf.com](https://www.sarraf.com/products/18k-Yellow-Gold-5mm-High-Polished-Traditional-Domed-Wedding-Band.html) | $871 · 18K · 6.70 g (2026-10-22) | Now US$871.00 (MSRP $3,388, Was $1,019); 18KY-LPBWB05/140139; "18K Solid Gold"; 6.70 g (size-10) | **Exact match**; 3.9× MSRP anchor reproduces |
| BN-20 | [bluenile.com](https://www.bluenile.com/engagement-rings/design-your-own-ring/woven-solitaire-engagement-ring-in-14k-yellow-gold-by-james-allen-item-310896) | $965 · 14K · no weight (2026-10-23) | "$965 (Setting Price)"; 505038y14; 14K Yellow Gold; 1.80 mm; +1-800-242-2728 / service@bluenile.com | **Exact match** |
| MJ-01 | [mejuri.com](https://mejuri.com/products/diamonds-team-ring) | $548 · 14K · no weight (2026-10-22) | $548 on the **Solid White Gold (14k)** variant; Materials heading on the same page reads "Solid Yellow Gold (14k)" while describing white-gold rhodium finish; 2-year warranty; free 30-day returns from delivery; no grams | **Price match; variant mismatch reproduces** (flag stands) |
| MN-01 | [mene.com](https://mene.com/products/knot-ring-gold) | $1,465 · 24K · no weight (2026-10-22) | **$1,442 USD** (default size); "Products are sold by weight, not size"; exchange "at the daily metal value" | **Floats daily — both dated readings published, stored value kept** (FLG-PASS17-04) |
| BN-09 | [bluenile.com](https://www.bluenile.com/engagement-rings/design-your-own-ring/classic-four-prong-solitaire-engagement-ring-in-18k-yellow-gold-item-500000y) | $1,125 (2026-10-22), `SOURCE_URL_DEAD` | "We're sorry, the page you're looking for cannot be found." | **Dead corroborated off-runner**; value stands flagged, not re-confirmed |
| RS-05 | [ross-simons.com](https://www.ross-simons.com/0.80-carat-gia-ceritified-solitaire-diamond-engagement-ring-in-14kt-white-gold-990022.html) → resolves to [ross-simons.com/products/990022](https://www.ross-simons.com/products/990022) | $2,819 (2026-10-22), `SOURCE_URL_DEAD` | Item 990022 live: "Sale price $2,819" (was $3,995); GIA Cert#2225975086; 14kt White Gold; retailer title misspells "Ceritified" *[sic]* | **URL migration found; price corroborated exactly** (FLG-PASS17-02). Stored URL/flag retained pending a provenance-noted URL update |

*Not re-opened this pass (values keep their row capture dates; Pass 16 machine evidence of 2026-10-23T10:10:23Z still applies): the other 57 rows, including all Brilliant Earth rows (HTTP 403 to automated checks — no claim made) and AN-01 (JavaScript shell — price not machine-readable).*

**Gate results re-run fresh this pass (before edits, then again on the rebuilt tree — see `COORDINATION.md` close-out):** Gate 1 `audit.py` PASS 131 / 1 warning (BE-05 V2-only) / 0 failures · Gate 2 `check_site.py` PASS 27 pages · Gate 3 `verify.py` PASS 64 records · Gate 4 `verify_a0be79d4.py` PASS (2,072 links, 0 dead) · Gate 5 `audit_hallucinations.py` PASS 941 checks · Gate 6 citations PASS (109 CFR refs; self-test rejects the known-bad citation) · Gate 7 `audit_freshness.py` PASS 295 checks / 2 warnings (BE-06, BE-07). Dataset state: **64 rings · 10 retailers · 62 dated prices (61 V1 + 1 V2-only) · 17 published weights · 19 explicit "solid gold" wordings · 0 hallmarks · 250 flag instances**, all published on [Flagged for Review](https://karagemop466-tech.github.io/GOLD4/pages/flagged.html) and [Freshness](https://karagemop466-tech.github.io/GOLD4/pages/freshness.html).

---

## 4. Rings that can be priced against their own gold (17 publish a weight; 16 also publish a price)

Sorted by price ÷ gold value at the frozen benchmark ($4,024.45/oz). *Derived columns are arithmetic on the published price/weight beside them — re-derive before relying on them.* `includes_centre_stone` rows are **not** comparable to setting-only multiples: part of the price buys a diamond (AN-01's centre stone is lab-created per Anjolee's own table — see its row on the site). VR-02 publishes a weight (2.84 g, 18K ⇒ 2.13 g pure gold ⇒ $275.60 derived) but **no price**, so it has no multiple and its price cell stays blank.

| Rank | ID | Retailer | Purity | Weight | Pure gold | Gold value | Legal-min gold value (§295) | Price | Price ÷ gold | Basis |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | SR-04 | Sarraf | 18K | 11.1 g | 8.325 g | $1,077.16 | $1,067.11 | $1,436 | 1.333× | setting_metal_only |
| 2 | SR-03 | Sarraf | 18K | 6.7 g | 5.025 g | $650.18 | $644.11 | $871 | 1.34× | setting_metal_only |
| 3 | SR-01 | Sarraf | 10K | 4.8 g | 2.0 g | $258.78 | $254.43 | $352 | 1.36× | setting_metal_only |
| 4 | SR-02 | Sarraf | 14K | 9.4 g | 5.4833 g | $709.48 | $700.97 | $1,063 | 1.498× | setting_metal_only |
| 5 | AL-01 | Allurez | 14K | 3.58 g | 2.0883 g | $270.21 | $266.97 | $585 | 2.165× | setting_metal_only |
| 6 | AL-03 | Allurez | 14K | 4.4 g | 2.5667 g | $332.10 | $328.11 | $848 | 2.553× | setting_metal_only |
| 7 | AL-04 | Allurez | 18K | 5.3 g | 3.975 g | $514.32 | $509.52 | $1,425 | 2.771× | setting_metal_only |
| 8 | AL-02 | Allurez | 14K | 3.4 g | 1.9833 g | $256.62 | $253.54 | $724 | 2.821× | setting_metal_only |
| 9 | RS-01 | Ross-Simons | 14K | 1.7 g | 0.9917 g | $128.31 | $126.77 | $400 | 3.117× | setting_metal_only |
| 10 | RS-02 | Ross-Simons | 18K | 0.7 g | 0.525 g | $67.93 | $67.30 | $249 | 3.666× | setting_metal_only |
| 11 | VR-01 | VRAI | 18K | 2.86 g | 2.145 g | $277.54 | $274.95 | $1,035 | 3.729× | setting_metal_only |
| 12 | RS-03 | Ross-Simons | 14K | 2.1 g | 1.225 g | $158.50 | $156.60 | $595 | 3.754× | setting_metal_only |
| 13 | RS-04 | Ross-Simons | 14K | 4.0 g | 2.3333 g | $301.91 | $298.28 | $1,195 | 3.958× | setting_metal_only |
| 14 | AN-01 | Anjolee | 14K | 2.9 g | 1.6917 g | $218.88 | $216.26 | $870.76 | 3.978× | includes_centre_stone |
| 15 | SR-05 | Sarraf | 14K | 8.0 g | 4.6667 g | $603.82 | $596.57 | $2,858 | 4.733× | includes_centre_stone |
| 16 | SR-06 | Sarraf | 18K | 6.3 g | 4.725 g | $611.36 | $605.66 | $4,068 | 6.654× | includes_centre_stone |

**Reading this table honestly:** the Sarraf plain bands (SR-01…SR-04, 1.33×–1.50×) are the dataset's melt-value floor — simple bands with published weights and explicit "Solid Gold" wording. They are bands, not diamond settings, so they benchmark *gold value*, not setting craftsmanship. Allurez settings (2.17×–2.82×) are the cheapest *settings* that can be gold-checked at all. Everything from Blue Nile, Brilliant Earth, Mejuri and Catbird is absent from this table for one reason only: **no gram weight is published**, so no multiple exists — ask the seller for the weight in writing before buying, and treat a refusal as the checklist's stop signal.

**The 18K premium (same design, only karat changed — recomputed from stored prices this pass):** Blue Nile Petite Solitaire $1,000 → $1,155 (**+15.5%**); Brilliant Earth Atelier $1,190 → $1,390 (**+16.8%**); Blue Nile Comfort Fit $935 → $1,310 (**+40.1%**); Allurez Split Shank $848 → $1,425 (**+68.0%**). Only the Allurez pair publishes both weights (4.4 g → 5.3 g), so only there can "more gold" be separated from margin. Premiums this inconsistent cannot be gold content alone.

---

## 5. Full list — all 64 rings (every row carries its official source link; blanks are deliberate)

Prices are **as captured on the date shown** from the linked official page — open the link and confirm before buying; prices change without notice (Menē's change daily). Categories: solitaire 35 · pavé/accent 15 · band 14 (site subpages: [Solitaires](https://karagemop466-tech.github.io/GOLD4/pages/solitaire.html) · [Pavé](https://karagemop466-tech.github.io/GOLD4/pages/pave.html) · [Bands](https://karagemop466-tech.github.io/GOLD4/pages/band.html)).

| ID | Retailer | Ring — official product page (source) | Purity | Price as captured | Date captured | Weight | Pure gold (derived) | Gold value (derived) | Price ÷ gold (derived) | Pass 16 live state |
|---|---|---|---|---|---|---|---|---|---|---|
| AL-01 | Allurez | [Engraved Floral Solitaire Engagement Ring Setting](https://www.allurez.com/products/floral-solitaire-engagement-ring-14k-yellow-gold) | 14K | $585 | 2026-10-22 | 3.58 g | 2.0883 g | $270.21 | 2.165× | CONFIRMED |
| AL-02 | Allurez | [Milgrain Trellis Solitaire Engagement Ring](https://www.allurez.com/products/milgrain-trellis-solitaire-engagement-ring-14k-yellow-gold) | 14K | $724 | 2026-10-22 | 3.4 g | 1.9833 g | $256.62 | 2.821× | CONFIRMED |
| AL-03 | Allurez | [Split Shank Solitaire Engagement Ring](https://www.allurez.com/products/split-shank-solitaire-engagement-ring-14k-yellow-gold) | 14K | $848 | 2026-10-22 | 4.4 g | 2.5667 g | $332.10 | 2.553× | CONFIRMED |
| AL-04 | Allurez | [Split Shank Solitaire Engagement Ring](https://www.allurez.com/products/split-shank-solitaire-engagement-ring-18k-yellow-gold) | 18K | $1,425 | 2026-10-22 | 5.3 g | 3.975 g | $514.32 | 2.771× | CONFIRMED |
| AN-01 | Anjolee | [Six Curved Prongs Solitaire Diamond Engagement Ring (MS354-A)](https://www.anjolee.com/rings/diamond-solitaire-engagement-rings/Six-Curved-Prongs-Solitaire-Diamond-Engagement-Ring.aspx) | 14K | $870.76 | 2026-10-22 | 2.9 g | 1.6917 g | $218.88 | 3.978× | NOT_MACHINE_READABLE |
| BE-01 | Brilliant Earth | [Atelier Solitaire Ring (2 mm, claw-prong bypass)](https://www.brilliantearth.com/Atelier-Solitaire-Ring-14K-Gold-BE1D2444-76788321/) | 14K | $1,190 | 2026-10-22 | — blank — | — | — | — | SOURCE_NOT_REACHED |
| BE-02 | Brilliant Earth | [Atelier Solitaire Ring (2 mm, claw-prong bypass)](https://www.brilliantearth.com/Atelier-Solitaire-Ring-Gold-BE1D2444-42024993/) | 18K | $1,390 | 2026-10-22 | — blank — | — | — | — | SOURCE_NOT_REACHED |
| BN-01 | Blue Nile | [Petite Solitaire Engagement Ring](https://www.bluenile.com/engagement-rings/design-your-own-ring/petite-solitaire-engagement-ring-in-14k-yellow-gold-item-195639) | 14K | $1,000 | 2026-10-22 | — blank — | — | — | — | CONFIRMED |
| BN-02 | Blue Nile | [Petite Solitaire Engagement Ring](https://www.bluenile.com/engagement-rings/design-your-own-ring/petite-solitaire-engagement-ring-in-18k-yellow-gold-item-195269) | 18K | $1,155 | 2026-10-22 | — blank — | — | — | — | CONFIRMED |
| BN-03 | Blue Nile | [Classic Six-Prong Solitaire Engagement Ring](https://www.bluenile.com/engagement-rings/design-your-own-ring/classic-six-prong-solitaire-engagement-ring-in-14k-yellow-gold-item-203272) | 14K | $1,000 | 2026-10-22 | — blank — | — | — | — | CONFIRMED |
| BN-04 | Blue Nile | [Classic Comfort Fit Solitaire Engagement Ring (2.5mm)](https://www.bluenile.com/engagement-rings/design-your-own-ring/classic-comfort-fit-solitaire-engagement-ring-in-14k-yellow-gold-25mm-item-203284) | 14K | $935 | 2026-10-22 | — blank — | — | — | — | CONFIRMED |
| BN-05 | Blue Nile | [Classic Comfort Fit Solitaire Engagement Ring (2.5mm)](https://www.bluenile.com/engagement-rings/design-your-own-ring/classic-comfort-fit-solitaire-engagement-ring-in-18k-yellow-gold-25mm-item-194941) | 18K | $1,310 | 2026-10-22 | — blank — | — | — | — | CONFIRMED |
| BN-06 | Blue Nile | [Six-Prong Low Dome Comfort Fit Solitaire Engagement Ring (2mm)](https://www.bluenile.com/engagement-rings/design-your-own-ring/six-prong-low-dome-comfort-fit-solitaire-engagement-ring-in-18k-yellow-gold-2mm-item-195379) | 18K | $1,295 | 2026-10-22 | — blank — | — | — | — | CONFIRMED |
| BN-07 | Blue Nile | [Classic Four Prong Solitaire Engagement Ring](https://www.bluenile.com/engagement-rings/design-your-own-ring/classic-four-prong-solitaire-engagement-ring-in-14k-yellow-gold-item-203257) | 14K | $870 | 2026-10-22 | — blank — | — | — | — | CONFIRMED |
| BN-08 | Blue Nile | [Riviera Pave Diamond Engagement Ring (1/6 ct. tw.)](https://www.bluenile.com/engagement-rings/design-your-own-ring/riviera-pave-diamond-engagement-ring-in-14k-yellow-gold-1-6-ct-tw-item-203512) | 14K | $1,500 | 2026-10-22 | — blank — | — | — | — | CONFIRMED |
| MJ-01 | Mejuri | [Diamonds Team Ring](https://mejuri.com/products/diamonds-team-ring) | 14K | $548 | 2026-10-22 | — blank — | — | — | — | CONFIRMED |
| MJ-02 | Mejuri | [Diamonds Band](https://mejuri.com/products/diamonds-band) | 14K | $648 | 2026-10-22 | — blank — | — | — | — | CONFIRMED |
| MJ-03 | Mejuri | [Pave Diamond Slim Signet](https://mejuri.com/products/pave-diamond-slim-signet-ring) | 14K | $548 | 2026-10-22 | — blank — | — | — | — | CONFIRMED |
| MJ-04 | Mejuri | [Pave Diamond Thin Dome Ring](https://mejuri.com/products/pave-diamond-thin-dome-ring) | 14K | $798 | 2026-10-22 | — blank — | — | — | — | CONFIRMED |
| MJ-05 | Mejuri | [Ziggy Ring (Bezel Lab Grown Diamond Zig-Zag Ring)](https://mejuri.com/products/bezel-lab-grown-diamond-zig-zag-ring) | 14K | $598 | 2026-10-22 | — blank — | — | — | — | CONFIRMED |
| VR-01 | VRAI | [The Classic Engagement Ring (4-prong dome, plain band)](https://www.vrai.com/configure/setting-to-diamond/classic-4-prong-dome/round-brilliant-yellow-gold-40635875360861) | 18K | $1,035 | 2026-10-22 | 2.86 g | 2.145 g | $277.54 | 3.729× | DIFFERS |
| VR-02 | VRAI | [Signature 6 Prong Engagement Ring (plain band)](https://www.vrai.com/configure/setting-to-diamond/signature-6-prong/round-brilliant-yellow-gold-32891144798301) | 18K | — blank (UNVERIFIED) — | 2026-10-22 | 2.84 g | 2.13 g | $275.60 | — | NO_STORED_PRICE |
| BE-03 | Brilliant Earth | [Six-Prong Petite Comfort Fit 1.5mm Solitaire Setting (18K Shank + 14K White Gold Prongs)](https://www.brilliantearth.com/Six-Prong-Petite-Comfort-Fit-1.5mm-Solitaire-Ring-Gold-BE1199H6-1912137/) | 18K | $850 | 2026-10-22 | — blank — | — | — | — | SOURCE_NOT_REACHED |
| SR-01 | Sarraf | [10k White Gold 5mm High Polished Traditional Domed Wedding Band](https://www.sarraf.com/products/10k-White-Gold-5mm-High-Polished-Traditional-Domed-Wedding-Band.html) | 10K | $352 | 2026-10-22 | 4.8 g | 2.0 g | $258.78 | 1.36× | CONFIRMED |
| SR-02 | Sarraf | [14k Yellow Gold 6mm High Polished Comfort Fit Heavy Wedding Band](https://www.sarraf.com/products/14k-gold-6mm-high-polished-comfort-fit-wedding-band.html) | 14K | $1,063 | 2026-10-22 | 9.4 g | 5.4833 g | $709.48 | 1.498× | CONFIRMED |
| SR-03 | Sarraf | [18k Yellow Gold 5mm High Polished Traditional Domed Wedding Band](https://www.sarraf.com/products/18k-Yellow-Gold-5mm-High-Polished-Traditional-Domed-Wedding-Band.html) | 18K | $871 | 2026-10-22 | 6.7 g | 5.025 g | $650.18 | 1.34× | CONFIRMED |
| SR-04 | Sarraf | [18K Yellow Gold 6mm High Polished Flat Comfort Fit Heavy Band](https://www.sarraf.com/products/18K-Gold-6mm-High-Polished-Flat-Comfort-Fit-Wedding-Band.html) | 18K | $1,436 | 2026-10-22 | 11.1 g | 8.325 g | $1,077.16 | 1.333× | CONFIRMED |
| SR-05 | Sarraf | [14k Yellow Gold Men's Solitaire Natural Diamond Ring (0.50 ct H/SI1)](https://www.sarraf.com/products/14k-yellow-gold-mens-solitaire-diamond-ring-1-2-ct.html) | 14K | $2,858 | 2026-10-22 | 8.0 g | 4.6667 g | $603.82 | 4.733× | CONFIRMED |
| SR-06 | Sarraf | [18k Yellow Gold Men's Solitaire Natural Diamond Ring (0.74 ct J/SI1)](https://www.sarraf.com/products/18k-yellow-gold-mens-solitaire-diamond-ring-3-4-ct.html) | 18K | $4,068 | 2026-10-22 | 6.3 g | 4.725 g | $611.36 | 6.654× | CONFIRMED |
| SR-07 | Sarraf | [14k Gold 1/2 Ctw Natural Diamond Solitaire Engagement Ring (G/SI1)](https://www.sarraf.com/products/14k-gold-1-2-ctw-diamond-solitaire-engagement-diamond-ring.html) | 14K | $2,183 | 2026-10-22 | — blank — | — | — | — | CONFIRMED |
| SR-08 | Sarraf | [18k Yellow Gold 1/2 Carat Round Diamond Solitaire Engagement Ring](https://www.sarraf.com/products/18k-yellow-gold-1-2-carat-round-diamond-solitaire-engagement-ring.html) | 18K | $2,461 | 2026-10-22 | — blank — | — | — | — | CONFIRMED |
| CB-01 | Catbird NYC | [The Swan Solitaire Diamond Engagement Ring (1.0mm Recycled 14K Band)](https://www.catbirdnyc.com/the-swan-solitaire-2475.html) | 14K | $3,900 | 2026-10-22 | — blank — | — | — | — | CONFIRMED |
| CB-02 | Catbird NYC | [Grand Painter's Solid 14k Yellow Gold Band](https://www.catbirdnyc.com/grand-painters-ring.html) | 14K | $313.50 | 2026-10-22 | — blank — | — | — | — | CONFIRMED |
| MN-01 | Menē | [Menē 24k Pure Solid Gold Knot Ring](https://mene.com/products/knot-ring-gold) | 24K | $1,465 | 2026-10-22 | — blank — | — | — | — | DIFFERS |
| MN-02 | Menē | [Menē 24k Pure Solid Gold Etruscan Sun Band (4.5mm)](https://mene.com/products/etruscan-sun-band-gold) | 24K | $1,730 | 2026-10-22 | — blank — | — | — | — | DIFFERS |
| BN-09 | Blue Nile | [Classic Four-Prong Solitaire Engagement Ring (Platinum Prongs)](https://www.bluenile.com/engagement-rings/design-your-own-ring/classic-four-prong-solitaire-engagement-ring-in-18k-yellow-gold-item-500000y) | 18K | $1,125 | 2026-10-22 | — blank — | — | — | — | SOURCE_NOT_REACHED |
| BN-10 | Blue Nile | [Low Dome Comfort Fit Solitaire Engagement Ring](https://www.bluenile.com/engagement-rings/design-your-own-ring/low-dome-comfort-fit-solitaire-engagement-ring-in-14k-yellow-gold-item-502120y14) | 14K | $1,145 | 2026-10-22 | — blank — | — | — | — | SOURCE_NOT_REACHED |
| BN-11 | Blue Nile | [French Pavé Diamond Engagement Ring (1/20 ct. tw.)](https://www.bluenile.com/engagement-rings/design-your-own-ring/french-pave-diamond-engagement-ring-in-18k-yellow-gold-1-20-ct-tw-item-502520y) | 18K | $1,805 | 2026-10-22 | — blank — | — | — | — | SOURCE_NOT_REACHED |
| BN-12 | Blue Nile | [Tapered Baguette Diamond Engagement Ring (1/6 ct. tw.)](https://www.bluenile.com/engagement-rings/design-your-own-ring/tapered-baguette-diamond-engagement-ring-in-18k-yellow-gold-1-6-ct-tw-item-501670y) | 18K | $2,515 | 2026-10-22 | — blank — | — | — | — | SOURCE_NOT_REACHED |
| BN-13 | Blue Nile | [Solitaire Engagement Ring With Pavé Basket In 14K Yellow Gold By James Allen](https://www.bluenile.com/engagement-rings/design-your-own-ring/solitaire-engagement-ring-with-pave-basket-in-14k-yellow-gold-by-james-allen-item-311230) | 14K | $2,260 | 2026-10-22 | — blank — | — | — | — | CONFIRMED |
| BN-14 | Blue Nile | [Solitaire Engagement Ring With Intricate Basket In 14K Yellow Gold By James Allen](https://www.bluenile.com/engagement-rings/design-your-own-ring/solitaire-engagement-ring-with-intricate-basket-in-14k-yellow-gold-by-james-allen-item-315036) | 14K | $1,385 | 2026-10-22 | — blank — | — | — | — | CONFIRMED |
| BN-15 | Blue Nile | [East West Knife Edge Cathedral Solitaire Engagement Ring In 14K Yellow Gold By James Allen](https://www.bluenile.com/engagement-rings/design-your-own-ring/east-west-knife-edge-cathedral-solitaire-engagement-ring-in-14k-yellow-gold-by-james-allen-item-311246) | 14K | $975 | 2026-10-22 | — blank — | — | — | — | CONFIRMED |
| BN-16 | Blue Nile | [Pavé Diamond Halo Engagement Ring In 14K Yellow Gold (Oval) By James Allen](https://www.bluenile.com/engagement-rings/design-your-own-ring/pave-diamond-halo-engagement-ring-in-14k-yellow-gold-oval-by-james-allen-item-311127) | 14K | $1,565 | 2026-10-22 | — blank — | — | — | — | CONFIRMED |
| BN-17 | Blue Nile | [Pavé Diamond Halo Engagement Ring In 14K Yellow Gold (Pear) By James Allen](https://www.bluenile.com/engagement-rings/design-your-own-ring/pave-diamond-halo-engagement-ring-in-14k-yellow-gold-pear-by-james-allen-item-311121) | 14K | $1,555 | 2026-10-22 | — blank — | — | — | — | CONFIRMED |
| BN-18 | Blue Nile | [Petite Hidden Halo Solitaire Plus Diamond Engagement Ring in 14k Yellow Gold](https://www.bluenile.com/engagement-rings/design-your-own-ring/petite-hidden-halo-solitaire-plus-diamond-engagement-ring-in-14k-yellow-gold-item-192506) | 14K | $1,255 | 2026-10-22 | — blank — | — | — | — | CONFIRMED |
| BN-19 | Blue Nile | [Bow-Tie Engagement Ring With Channel Set Round Diamonds In 14K Yellow Gold By James Allen](https://www.bluenile.com/engagement-rings/design-your-own-ring/bow-tie-engagement-ring-with-channel-set-round-diamonds-in-14k-yellow-gold-by-james-allen-item-304294) | 14K | $2,350 | 2026-10-22 | — blank — | — | — | — | CONFIRMED |
| BN-20 | Blue Nile | [Woven Solitaire Engagement Ring In 14K Yellow Gold By James Allen](https://www.bluenile.com/engagement-rings/design-your-own-ring/woven-solitaire-engagement-ring-in-14k-yellow-gold-by-james-allen-item-310896) | 14K | $965 | 2026-10-23 | — blank — | — | — | — | CONFIRMED |
| BN-21 | Blue Nile | [Knife Edge Solitaire Engagement Ring in 14k Yellow Gold](https://www.bluenile.com/engagement-rings/design-your-own-ring/knife-edge-solitaire-engagement-ring-in-14k-yellow-gold-item-192261) | 14K | $1,290 | 2026-10-23 | — blank — | — | — | — | CONFIRMED |
| BN-22 | Blue Nile | [Wide Band Solitaire Engagement Ring in 14K Yellow Gold (5mm)](https://www.bluenile.com/engagement-rings/design-your-own-ring/wide-band-solitaire-engagement-ring-in-14k-yellow-gold-5mm-item-203321) | 14K | $2,050 | 2026-10-23 | — blank — | — | — | — | CONFIRMED |
| BN-23 | Blue Nile | [Emerald Cut Diamond Engagement Ring in 14K Yellow Gold (1 ct. tw.)](https://www.bluenile.com/engagement-rings/design-your-own-ring/emerald-cut-diamond-engagement-ring-in-14k-yellow-gold-1-ct-tw-item-203303) | 14K | $5,190 | 2026-10-23 | — blank — | — | — | — | CONFIRMED |
| BN-24 | Blue Nile | [Classic Simple Solitaire Engagement Ring in 14k White Gold](https://www.bluenile.com/engagement-rings/design-your-own-ring/classic-simple-solitaire-engagement-ring-in-14k-white-gold-item-195730) | 14K | $1,145 | 2026-10-23 | — blank — | — | — | — | CONFIRMED |
| BN-25 | Blue Nile | [Pavé Contour Diamond Engagement Ring In 14K White Gold By James Allen](https://www.bluenile.com/engagement-rings/design-your-own-ring/pave-contour-diamond-engagement-ring-in-14k-white-gold-by-james-allen-item-315661) | 14K | $2,210 | 2026-10-23 | — blank — | — | — | — | CONFIRMED |
| BN-26 | Blue Nile | [Comfort Fit Solitaire Engagement Ring In 14K Yellow Gold (James Allen style 17740y14)](https://www.bluenile.com/engagement-rings/design-your-own-ring/14k-yellow-gold-15mm-comfort-fit-engagement-ring-item-41515) | 14K | — blank (UNVERIFIED) — | 2026-10-22 | — blank — | — | — | — | NO_STORED_PRICE |
| BE-04 | Brilliant Earth | [Fairmined Hollis Knife Edge Solitaire Engagement Ring](https://www.brilliantearth.com/Fairmined-Hollis-Knife-Edge-Solitaire-Engagement-Ring-Gold-BE1FM0126/) | 18K | $1,090 | 2026-10-22 | — blank — | — | — | — | SOURCE_NOT_REACHED |
| BE-05 | Brilliant Earth | [Freesia Hidden Halo Diamond Ring](https://www.brilliantearth.com/Freesia-Hidden-Halo-Diamond-Ring-14K-Gold-BE1D3939-76789075/) | 14K | $1,190 | 2026-10-22 | — blank — | — | — | — | SOURCE_NOT_REACHED |
| BE-06 | Brilliant Earth | [Freesia Hidden Halo Diamond Ring](https://www.brilliantearth.com/Freesia-Hidden-Halo-Diamond-Ring-Gold-BE1D3939-19424930/) | 18K | $1,390 | 2026-10-23 | — blank — | — | — | — | SOURCE_NOT_REACHED |
| BE-07 | Brilliant Earth | [Fleur Solitaire Ring](https://www.brilliantearth.com/Fleur-Solitaire-Ring-14K-Gold-BE1574-76785943/) | 14K | $1,350 | 2026-10-23 | — blank — | — | — | — | SOURCE_NOT_REACHED |
| RS-01 | Ross-Simons | [14kt Yellow Gold 2mm Wedding Band](https://www.ross-simons.com/jewelry/rings/571221.html) | 14K | $400 | 2026-10-22 | 1.7 g | 0.9917 g | $128.31 | 3.117× | CONFIRMED |
| RS-02 | Ross-Simons | [Italian 18kt Yellow Gold 2mm Wedding Band](https://www.ross-simons.com/jewelry/rings/985230.html) | 18K | $249 | 2026-10-22 | 0.7 g | 0.525 g | $67.93 | 3.666× | CONFIRMED |
| RS-03 | Ross-Simons | [14kt Yellow Gold 3mm Comfort-Fit Wedding Band](https://www.ross-simons.com/jewelry/rings/820263.html) | 14K | $595 | 2026-10-22 | 2.1 g | 1.225 g | $158.50 | 3.754× | CONFIRMED |
| RS-04 | Ross-Simons | [14kt Yellow Gold 4mm Flat Wedding Band Ring](https://www.ross-simons.com/jewelry/rings/823796.html) | 14K | $1,195 | 2026-10-22 | 4.0 g | 2.3333 g | $301.91 | 3.958× | CONFIRMED |
| RS-05 | Ross-Simons | [0.80 Carat GIA Certified Solitaire Diamond Engagement Ring](https://www.ross-simons.com/0.80-carat-gia-ceritified-solitaire-diamond-engagement-ring-in-14kt-white-gold-990022.html) | 14K | $2,819 | 2026-10-22 | — blank — | — | — | — | SOURCE_NOT_REACHED |
| MJ-06 | Mejuri | [Pavé Diamond Slim Eternity Band](https://mejuri.com/us/en/products/diamond-eternity-band?Material=14k+Yellow+Gold&Stone=Natural+Diamond) | 14K | $1,100 | 2026-10-22 | — blank — | — | — | — | DIFFERS |
| MJ-07 | Mejuri | [Diamonds Line Ring](https://mejuri.com/us/en/products/diamonds-line-ring) | 10K | $348 | 2026-10-22 | — blank — | — | — | — | CONFIRMED |

---

## 6. Sellers at a glance (full clauses + sources on the Sellers page)

| Seller | Official site | Return window (as captured) | Key exclusions to check before buying (summary — read the seller page) |
|---|---|---|---|
| Blue Nile | https://www.bluenile.com/ | 30 days | Personalized jewellery; Custom orders; Engraved items |
| Allurez | https://www.allurez.com/ | 30 days | Engraved items; Custom-made orders (non-refundable and non-cancellable); Design Your Own engagement rings (exchange only, same or higher value, not for loose diamonds) |
| VRAI | https://www.vrai.com/ | 30 days | Modified or resized rings; Custom-designed items; Engraved items and engraving/finishing fees |
| Mejuri | https://mejuri.com/ | 30 days | Engraved and monogrammed products (not eligible at any time); Final sale items; Gift cards |
| Brilliant Earth | https://www.brilliantearth.com/ | 30 days | Resized, repaired, modified, or previously exchanged items are non-returnable (per /30-Day-Returns/); Custom-designed items are non-returnable; Engraved rings incur a $40 engraving removal fee on return (engraved gemstones non-returnable) |
| Anjolee | https://www.anjolee.com/ | 30 days | — see seller record — |
| Sarraf | https://www.sarraf.com/ | 30 days | Used, worn, or altered items; Third-party resizing or repair immediately voids Lifetime Warranty; Special/custom orders non-refundable |
| Catbird NYC | https://www.catbirdnyc.com/ | 20 days | Engraved items (final sale); Special orders and custom rings (final sale); All international sales (final sale) |
| Menē | https://mene.com/ | 7 days | Items missing original Certificate of Authenticity or packaging; Worn, altered, or damaged items |
| Ross-Simons | https://www.ross-simons.com/ | 30 days | Items resized, altered, damaged, or worked on by an outside jeweler; Custom or personalized/engraved items; Final sale items |

Return windows look uniform ("30 days") until the exclusions are read: resized, engraved and custom items are final-sale at most sellers in this dataset. **Order of operations that preserves your rights:** pay by credit card → keep the listing/receipt/purity claims → inspect stamp + trademark on arrival → independent jeweler weight + XRF purity test → *only then* wear/resize/engrave. Menē buyers have **7 days** for all of that.

---

## 7. Irregularities published for review (none blocks publication; all need your eyes)

| ID | Severity | Finding | Source | Status |
|---|---|---|---|---|
| FLG-PASS17-01 | Medium | Live WGC tick $3,996.31/oz vs frozen benchmark $4,024.45/oz under the *same* "Data as of 22 October, 2026" date line (−0.70%). Derived values remain benchmark-labelled; benchmark not silently swapped | [gold.org](https://www.gold.org/goldhub/data/gold-prices) | Recorded in `data/gold_spot.json`; re-check spot in the calculator on purchase day |
| FLG-PASS17-02 | Medium | RS-05 stored Ross-Simons `.html` URL 404s to automation, but the product (Item 990022) is live at `/products/990022` at the *same* $2,819. Stored URL + `SOURCE_URL_DEAD` retained this pass to preserve the Pass 16 evidence chain | [ross-simons.com/products/990022](https://www.ross-simons.com/products/990022) | **Needs review:** approve updating the canonical URL with this note as provenance |
| FLG-PASS17-03 | Low — **corrected** | README summary had drifted from the data: benchmark $4,028.53 (data: $4,024.45), sources 14 (data: 31), provenance 60 V1/3 V2 (data: 61 V1 priced + 1 V2). Generated site was unaffected (renders from JSON) | `data/*.json` recount this pass | Fixed with dated corrections; lesson logged — hand-written prose drifts, generated tables don't |
| FLG-PASS17-04 | Medium | Menē prices float with daily metal value and size/weight: MN-01 $1,465 (2026-10-22) vs $1,442 displayed 2026-10-23 vs $1,800–$2,441 structured size offers (Pass 16). Any Menē figure is a same-day reading only | [mene.com](https://mene.com/products/knot-ring-gold) | Both readings published; stored value not overwritten; `PRICE_STRUCTURED_DIFFERS` stands |
| FLG-PASS17-05 | High — standing | **0 of 64** pages (including all 7 re-read this pass) publish the karat stamp + maker's/registered trademark the FTC says to look for. `hallmark_published` stays `false` everywhere | [FTC](https://consumer.ftc.gov/articles/buying-platinum-gold-and-silver-jewelry) | Unresolvable online — in-hand inspection + XRF on arrival |

Standing items from earlier passes remain published on [Flagged for Review](https://karagemop466-tech.github.io/GOLD4/pages/flagged.html) and [Freshness](https://karagemop466-tech.github.io/GOLD4/pages/freshness.html): 45 prices re-confirmed by the pages' own structured data; 4 `PRICE_STRUCTURED_DIFFERS` (VR-01, MN-01, MN-02, MJ-06 — both numbers shown); 5 `SOURCE_URL_DEAD` (BN-09…BN-12, RS-05 — see FLG-PASS17-02 for RS-05); 7 Brilliant Earth `SOURCE_BOT_BLOCKED` (no price claim); 1 not-machine-readable (AN-01); BE-05 the last `PRICE_V2_ONLY`; 47 missing gram weights; 45 missing "solid gold" wordings; retailer copy-vs-spec contradictions itemised per row.

## 8. How to re-verify everything here (recommended after every review)

```bash
python3 scripts/compute.py             # derived values from published inputs only
python3 scripts/generate_site.py       # secondary Assay Lab catalogue
python3 scripts/build_site.py          # canonical dashboard + pages/ (owns index.html — run last)
python3 scripts/gen_verification.py    # VERIFICATION.md from the same JSON
python3 scripts/audit.py               # Gate 1 — integrity / hallucination audit
python3 scripts/check_site.py          # Gate 2 — links, source-per-row, no-hallucination banner
python3 scripts/verify.py              # Gate 3 — schema + blank-value accounting
python3 scripts/verify_a0be79d4.py     # Gate 4 — XSS / dead-link scanner
python3 scripts/audit_hallucinations.py           # Gate 5 — phantom-math auditor
python3 scripts/session_46691f83/verify_citations.py --self-test  # Gate 6a
python3 scripts/session_46691f83/verify_citations.py              # Gate 6b
python3 scripts/audit_freshness.py     # Gate 7 — live-evidence freshness
```

Then re-open the source link on any row you care about and compare the number with your own eyes. If the page no longer shows it, the correct action is a flag with today's date — **not** a new number from anywhere else. That is the whole method of this project, and Pass 17 changed no value that failed it.
