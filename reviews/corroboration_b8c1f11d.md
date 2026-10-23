# R-b8c1f11d — Independent corroboration record (2026-10-23, session `arena/b8c1f11d-gold4`)

> **NO-HALLUCINATION RULE.** Every "live read" below is a value this session's own fetch displayed, quoted
> verbatim with the retrieval time (UTC). Where a value could not be re-read, that is stated — nothing is
> inferred, interpolated, or carried from another session's report. This review is **read-only by design**:
> it changes no data rows (they are actively owned by other sessions); it records what an independent
> re-read of the official sources shows, for human review.

**Method.** A fixed sample covering **all 10 sellers** plus the four Tier A legal sources and the Tier B
spot benchmark was re-opened with this session's own fetches between **2026-10-23 09:57 UTC and 10:20 UTC**.
Tree under review: `main @ 6256af9` (post PR #27/#28), with the merged PR #29/#31/#33/#34/#35 changes
(legal/source-text fixes by `d1586f6a` and `46691f83`) noted where they overlap this sample.

Legend: ✔ = live read matches the stored value exactly · ⚠ = live read differs (price moved or rendering variance) · ✖ = contradicts a claim made elsewhere.

## A. Tier A/B reference sources

| # | Source | What the project claims | My live read (2026-10-23 UTC) | Verdict |
|---|--------|-------------------------|-------------------------------|---------|
| A1 | [World Gold Council spot panel](https://www.gold.org/goldhub/data/gold-prices) | benchmark **$4,024.45/oz**, "Data as of 22 October, 2026" = $129.389072/g | Panel: **"USD /oz 4,024.45"**, "Data as of 22 October, 2026"; "Market Data: Provided by ICE Data Services" (09:57) | ✔ exact match |
| A2 | [16 CFR § 23.3](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-23/section-23.3) (eCFR, "up to date as of 10/21/2026") | Pass 12 correction: no 10K minimum for karat gold; 10K is only a **plating** fineness floor | § 23.3(c)(1) verbatim: *"for example, '14 Karat Gold,' '14 K. Gold,' '14 Kt. Gold,'* ***'9 Karat Gold,' or '9 Kt. Gold'****"*; the "not less than 10 karat fineness" text appears only in (c)(2) mechanical plating and (c)(3) electroplating (0.175 µm / 2.5 µm thresholds; 1/40th and 1/20th weight fractions). (c)(1) also: hollow-centre gold alloy *"should not be described or marked as … 'Solid 14 Kt. Gold.'"* (10:02) | ✔ corroborates the correction verbatim |
| A3 | [15 U.S.C. § 295](https://www.law.cornell.edu/uscode/text/15/295) | fineness tolerance **0.003** tested part (solder-free), **0.007** whole article incl. solder | Statute text: *"shall not be less by more than three one-thousandth parts …"* and *"…including all solder … shall not be less by more than three one-thousandth parts, in the case of a watchcase or flatware, or than seven one-thousandth parts, in the case of any other such article"* (10:02) | ✔ exact match |
| A4 | [FTC — Buying Platinum, Gold, and Silver Jewelry](https://consumer.ftc.gov/articles/buying-platinum-gold-and-silver-jewelry) | karat = parts of 24; karat mark must sit beside maker's/trademark; "solid gold" = not hollow; vermeil = sterling base; ≥1/20 threshold for fraction marking | Article verbatim: 18K = 18 parts gold + 6 parts other; 14K = 14 + 10; *"Near the karat quality mark, look for the name or the U.S. registered trademark… If you… don't see a trademark along with the karat mark, don't buy it."*; *"The phrase 'solid gold' means the gold item isn't hollow."*; *"If the layer of gold is less than 1/20… marking should state the fraction"*; vermeil = sterling coated/plated with gold (10:02) | ✔ exact match |

## B. Retailer rows (all 10 sellers sampled)

| Row | Stored value | My live read (2026-10-23 UTC) | Verdict |
|-----|--------------|-------------------------------|---------|
| [BN-22](https://www.bluenile.com/engagement-rings/design-your-own-ring/wide-band-solitaire-engagement-ring-in-14k-yellow-gold-5mm-item-203321) | $2,050 · 14K YG · 5.00mm · SKU 501580y14 · `COPY_INCONSISTENT_METAL` | Full product page served: "Wide Band Solitaire Engagement Ring in 14K Yellow Gold (5mm)", **$2,050 (Setting Price)**, Stock Number **501580y14**, Width **5.00mm**; Product Details copy still reads *"Bold and modern, this **platinum** solitaire setting…"* (09:57) | ✔ all stored values + the contradiction re-confirmed live. **✖ contradicts session `03c0c10f`'s board note that this URL returns a 404 page** — see discrepancy D-1 below |
| [AL-01](https://www.allurez.com/products/floral-solitaire-engagement-ring-14k-yellow-gold) | $585 · 14K YG · 3.58 g · style NG4426 · setting only | "**$585** 51% Savings / $1,194 Everyone Else"; "Setting only. Center stone sold separately."; Style number **NG4426**; "Approximate Metal Weight **3.58 grams**"; FREE 1-year limited warranty panel (10:05) | ✔ exact match (price, weight, SKU, karat, basis) |
| [MJ-01](https://mejuri.com/products/diamonds-team-ring?Material=Solid+Yellow+Gold+%2814k%29&Stone=Natural+Diamond) | $548 · 14K yellow gold variant · no gram weight | Exact variant URL served "Solid Yellow Gold (14k), Natural Diamond … **$548**"; specs: min carat 0.14 ct, SI–I, GHI, shank 1.6 mm — **no gram weight anywhere on the page**; 2-year warranty; 30-day free returns (10:08) | ✔ price + metal variant + blank weight all confirmed |
| [SR-03](https://www.sarraf.com/products/18k-Yellow-Gold-5mm-High-Polished-Traditional-Domed-Wedding-Band.html) | $871.00 · 18K Solid Gold · 6.70 g · SKU 18KY-LPBWB05 · stock 140139 | "Now: **US$871.00** -15% OFF (Was US$1,019.00)"; "Material: **18K Solid Gold**"; "Approximate Metal Weight: **6.70 grams**" (size-10 note in description); "SKU: **18KY-LPBWB05** Stock Number: **140139**" (10:09) | ✔ exact match |
| [BE-05](https://www.brilliantearth.com/Freesia-Hidden-Halo-Diamond-Ring-14K-Gold-BE1D3939-76789075/) | $1,190 USD (V2 snapshot, flagged `PRICE_V2_ONLY` + `PRICE_CURRENCY_LOCALIZED`) | Page loads (H1 "Freesia Hidden Halo Diamond Ring in 14K Yellow Gold"; Style **BE1D3939-14KY**; Metal 14K Yellow Gold; "Free 1-Year Resizing" badge) but the price renders to this fetcher as **"€1,350.00 (Setting Only)"** — Global-e Eurozone rendering (EUR/USD/CAD/AUD/GBP selector with a German flag) (10:07–10:12) | ⚠ stored USD price **not reproducible** from the live page for a Eurozone-routed fetch — the V2 provenance and both flags are correct as they stand. Not an error; do not "fix" the row from a EUR rendering |
| [AN-01](https://www.anjolee.com/rings/diamond-solitaire-engagement-rings/Six-Curved-Prongs-Solitaire-Diamond-Engagement-Ring.aspx) | $870.76 incl. lab-created 0.50 ct FG/VS centre · 2.90 g · 14K **white** gold | Product Details table verbatim: "Approx. Metal Weight: **2.90 Gr.**", "Center Diamond Color: **Lab Created FG**", "Center Diamond Clarity: **Lab Created VS**", Metal Type "**14K White Gold**", Ring Size 6.5; price displayed: **$870.76**; "All customized orders can be returned for full refund within 30 days of receipt." (10:10–10:12) | ✔ exact match incl. the two flags (`PRICE_INCLUDES_CENTRE_STONE`, `CENTRE_STONE_LAB_CREATED`) — the row's own `price_basis` ("not comparable with setting-only rows") is accurate |
| [RS-01](https://www.ross-simons.com/jewelry/rings/571221.html) | $400 · 14kt YG · 1.7 g · item 571221 | Served (after redirect to `ross-simons.com/products/571221`): "Women's 2mm 14kt Yellow Gold Band … **$400**"; sizes 5/6/7/8/9 in stock at $400.00 (5.5/6.5/7.5/8.5 sold out); Details: Metal **14kt Yellow Gold**, Gold Weight **1.7 grams**, Item **571221** (10:12) | ✔ values exact. ⚠ observation: stored URL now **301-redirects** to `/products/571221` — see R-06 |
| [CB-01](https://www.catbirdnyc.com/the-swan-solitaire-2475.html) | from $3,900 incl. GIA centre diamond · no weight | "The Swan Solitaire Diamond Engagement Ring … **from $3,900.00**" (10:14) | ✔ "from" price exactly as stored (`PRICE_IS_FROM_PRICE` correct) |
| [MN-01](https://mene.com/products/knot-ring-gold) | $1,465 (read 2026-10-22) · 24k · weight null (`NO_WEIGHT_PUBLISHED`) | Live price **$1,454** (10:15–10:18); "Menē transparently prices, sells, and buys-back our pure 24 karat jewelry by gram weight … The weight (measured in metric grams) represents the pure 24 karat gold … within each design. Weights can fluctuate by up to 0.5 grams per piece"; 7-day return/exchange blurb; "Crafted-on-Demand item" | ⚠ **PRICE MOVED −$11 (−0.75%) in ~15 hours** — stored value was accurate when read; Menē prices track metal value daily, so any snapshot goes stale fast (evidence FOR the freshness gate `03c0c10f` is building). The blank weight stays defensible for statically served content (per-item grams only appear behind the dynamic "Price breakdown" panel) — see R-05 |
| [VR-01](https://www.vrai.com/configure/setting-to-diamond/classic-4-prong-dome/round-brilliant-yellow-gold-40635875360861) | weight 2.86 g (this URL) · width `WIDTH_UNVERIFIED` · `SPEC_LISTED_PAVE_ON_PLAIN_BAND` · price only from listing card | Setting Details verbatim: "Metal: **18k Yellow Gold**", "Band width: **Standard**" (no numeric width), "Band depth: 1.6mm", "**Metal weight: 2.86g (Ring size 6)**", "**Pavé carat weight: 0.18ctw**" — while the selected configuration is "**Band: Plain band**"; Returns: 30 days, unworn, original packaging; no setting price in page text (10:19–10:20) | ✔ every stored value and all three flags re-confirmed live (Pass 10's width blanking is right: the only millimetre figure on the page is the *depth*) |

## C. Cross-session discrepancies and irregularities surfaced by this corroboration

| # | Item | Detail | Action for owners |
|---|------|--------|-------------------|
| D-1 | **BN-22 fetch-outcome variance** | `03c0c10f`'s board records this URL as serving Blue Nile's 404 page (09:53 UTC); this session was served the full 200 product page with all specs (09:57 UTC). Same URL, 4 minutes apart | Likely CDN/bot-gating variance between fetch services. Recommend the source-health checker (PR #26) record **redirect chain + served `<title>` + a content snippet**, not just a status classification, so a soft-404 served to one fetcher is distinguishable from a real dead link. The row's stored values are confirmed live |
| D-2 | **MN-01 price moved** | $1,465 (stored, 22 Oct) → $1,454 (live, 23 Oct 10:15 UTC), −0.75%. Menē sells by gram weight against daily metal value | Logged as a request for the data owner (`03c0c10f`, task 21 price-freshness): re-read MN-01/MN-02 before or after merge. This session does not edit the row |
| D-3 | **Pass-numbering collisions** | Two sessions published a "Pass 12" (`d1586f6a`, `03c0c10f`) and one a "Pass 14" (`04f1f10d`); there is no "Pass 13". This review is deliberately numbered **R-b8c1f11d** instead | Cosmetic-integrity: recommend the integration session deduplicate pass numbering in `data/verification_log.json` at close-out |
| D-4 | **RS-01 URL redirect** | stored `price_source_url` (`/jewelry/rings/571221.html`) 301-redirects to `/products/571221` | Benign; recommend noting the canonical URL in the row at the next owner edit. Link still resolves |
| D-5 | **Aggregate multiples include stone-inclusive rows** | See `reviews/repo_review_b8c1f11d.md` R-01 (recomputed by hand: published 14K max 4.73× and 18K max 6.65× are diamond-inclusive SR-05/SR-06) | Logged request to `scripts/compute.py` owner — corroborates the identical request already logged by `b2c018a8` |

## D. What this review deliberately did NOT do

- Did not edit any row, source, seller, spot, or script — edits belong to the owning sessions; everything above is a
  written record with verbatim quotes and links so any session can re-check in one click.
- Did not re-fetch the 49 rows outside the sample; a sample is a sample. Sellers are covered 10/10; rows 15/64
  (+4 reference sources).
- Did not verify seller reputation, complaints, or any physical property (hallmark, XRF). No such claim exists
  in the dataset (`hallmark_published: false` on all 64 rows — confirmed in `data/derived.json`).
- Did not treat any search-engine snippet as a source.

**Recompute cross-check.** Independently re-derived all 17 weighted rows from `weight_g`, `karat`, and the
benchmark (`$4,024.45/oz ÷ 31.1034768 g/oz = $129.389072/g`): pure-gold grams, gold value, and price ÷ gold
for every row match `data/derived.json` to within ±$0.02. 0 mismatches. Detail in
`reviews/repo_review_b8c1f11d.md` § Arithmetic audit.

*Reviewer: session `arena/b8c1f11d-gold4` · review id `R-b8c1f11d` · tree reviewed: main `6256af9`→`7f59a6c` · fetches 2026-10-23 09:57–10:20 UTC.*
