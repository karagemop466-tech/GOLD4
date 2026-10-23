# GOLD4 — gold engagement-ring verification desk

A small, auditable dataset of **solid-gold engagement rings** with retailer prices, published gram weights, computed gold content and every unverified value published as *blank* instead of guessed.

**Latest review pass — Pass 20 (23 October 2026, 23:43–23:45Z): independent hand re-verification, and an honest coverage statement.** This session re-opened **11 of the 64 product rows plus the gold benchmark** with its own browser-rendered reader — a different read path from the runner sweeps of Passes 15–18 — and published every result, including the ones that did not go its way:

- **Five rows corroborated exactly** (price *and*, where published, weight): AL-01 `$585` / `3.58 g`, SR-03 `$871` / `6.70 g` ("18K Solid Gold"), SR-05 `$2,858` / `8.00 g` ("14K Solid Gold"), RS-02 `$249` / `0.7 g` (18kt), RS-05 `$2,819` (Item 990022, still live at the URL corrected in Pass 18).
- **One row still differs:** Menē MN-01 prints `$1,442` against the stored `$1,465` (−1.57%) — the **third** independent read of the same gap. Both numbers stay published; nothing was overwritten.
- **One row confirmed for the wrong variant:** Mejuri MJ-01's stored URL renders **white** gold, so the `$548` reading corroborates the white-gold variant, not the stored yellow-gold one.
- **One dead link confirmed by hand:** BN-09 serves Blue Nile's own "page cannot be found" copy.
- **Three pages only partly readable:** BE-07 (loaded, title still 14K yellow gold, price unreadable), AN-01 (JavaScript shell, as before), VR-01 (2.86 g confirmed but it is the seller's *ring-size-6* figure while size 5 was selected; the plain-band/pavé spec conflict persists). No price claim is made for these three.
- **54 rows were not re-read this pass** and keep their 22 October 2026 capture dates. The site says so on the Pass 20 page rather than implying a full sweep.

New irregularity found and published: **RS-05 is priced as a clearance item** ("CLEARANCE 29% Off", `$3,995` → `$2,819`) while Ross-Simons' 30-day return policy excludes **"Final sale items"**, and the page never says *final sale* — so its returnability must be confirmed in writing before paying (new row flag `CLEARANCE_RETURN_TERMS_UNCLEAR`). The gold panel printed **`$3,995.47/oz`** on the same source date line as the stored `$3,996.31` benchmark (−0.021%, an intraday tick); the benchmark was **retained**, the reading recorded. The stale, unmerged PR #47 (`arena/bc872fef-gold4`, no commits for three hours) was taken over under the board's handover rule; its one still-valuable fix — citing Sarraf's **dedicated** returns and warranty pages instead of a product page — was re-verified from the pages themselves and adopted, with a new `sarraf-warranty` source registered. Documentation drift was repaired: this README advertised *seven* CI gates when the pipeline runs **eight** (nine invocations) and introduced a Pass 15 section as "latest". Full record: [Pass 20 page](https://karagemop466-tech.github.io/GOLD4/pages/pass20.html) · [`reviews/pass20/report.md`](reviews/pass20/report.md) · raw evidence [`reviews/pass20/observations.json`](reviews/pass20/observations.json). **The standing recommendation stands: after every review, look for hallucinations again — source link, date, read path, and whether anything was inferred.**

**Pass 18 (23 October 2026):** — every ring URL and every registered source was re-opened from a GitHub runner with open internet, each page's own structured price compared with the stored value, and the winner of each comparison published rather than applied. Nothing in `data/` was overwritten to make a row look current; where a page and the stored value disagree, both numbers are shown and the row is flagged. The gold benchmark was re-read in a browser-rendered fetch and **moved to $3,996.31/oz (−0.70% on the 10:02Z reading)** — corroborated within four minutes by Kitco and BullionVault — so every derived gold value was recomputed at $128.48435/g. This pass also added capture of each page's own *availability* markup, which settled the one open question: BN-26 publishes `availability=SoldOut` beside an `$858` price meta, so its blank price is confirmed correct rather than merely uncaptured. It also **fixed the one dead link that could be fixed**: RS-05's 404 was a catalogue migration, and the product is live at `https://www.ross-simons.com/products/990022` (Item 990022, same **$2,819**, sizes 5–8 in stock) — found by the concurrent Pass 17 and independently confirmed here by a browser-rendered read. Its URL was corrected; its price and capture date were not touched. Four Blue Nile URLs (BN-09…BN-12) remain dead. Finally it repaired documentation drift: the README's file table still quoted the **superseded** 21-October benchmark ($4,028.53/oz) and "14 registered sources", and advertised five CI gates when the pipeline runs seven.

**Pass 17 (23 October 2026), final integration — merged from `arena/0e04577b-gold4`.** The merged tree (64 rings / 10 retailers / 31 registered sources) was re-verified line by line: all CI gates in `.github/workflows/pages.yml` (Gates 1–7, Gate 6 split into 6a/6b) re-ran clean, every derived gold value was independently re-derived with **0 mismatches**, and the benchmark page, the FTC gold-jewelry guidance, 15 U.S.C. § 295 and seven retailer pages were re-opened live. Four prices corroborated exactly (AL-01, SR-03, BN-20, RS-05); BN-09's dead link was corroborated off-runner; **RS-05's product was found alive at Ross-Simons' migrated URL** (`/products/990022`, same $2,819 — FLG-PASS17-02); Menē's daily floating price was documented without overwriting the stored reading (FLG-PASS17-04); the live WGC tick (**$3,996.31/oz**, page still dated 22 October 2026, −0.70% vs the frozen benchmark) was recorded as a dated cross-check rather than silently substituted (FLG-PASS17-01); and three drifted summary numbers in this README were corrected (FLG-PASS17-03). **No dataset value changed.** Full record: [`reviews/pass17_repo_review_0e04577b.md`](reviews/pass17_repo_review_0e04577b.md) and the [Verification log](https://karagemop466-tech.github.io/GOLD4/pages/log.html).

**Pass 14 (23 October 2026):** the World Gold Council spot panel was re-read and had moved to **$4,024.45/oz, "Data as of 22 October, 2026"** (from $4,028.53 at 21 October), so every derived gold value was recomputed at the new rate; the last three `PRICE_V2_ONLY` rows were re-fetched live and two of them (BE-06 $1,390, BE-07 $1,350) upgraded to first-hand verification, while BE-05 served **EUR** instead of USD and therefore stayed flagged rather than being converted; four weighted rows (AL-01, RS-01, RS-02, SR-01) were re-read live and matched exactly. Two new irregularities were published: Brilliant Earth's per-page currency localization (FLG-HIGH-13) and Sarraf's 3.9x "MSRP" anchor (FLG-MED-14). Gate 1 warnings fell 3 → 1; all CI gates then in place passed.

**Previous pass:** 22 October 2026 — every row was re-opened on its own source page three times, by two independent sessions and once more against merged `main`. Pass 2 corrected Anjolee's weight and centre-stone origin; Pass 5 re-checked all rows again and added two Brilliant Earth rows; Pass 6 re-checked the merged site and found no discrepancy. Two Brilliant Earth rows (BE-01 14K, BE-02 18K yellow gold) were added because their setting price became readable on this pass; three new flags were raised for Mejuri variant pricing, Brilliant Earth resize wording and the gold-spot drift. Nothing was filled in to make a row look complete. See the [Verification log](https://karagemop466-tech.github.io/GOLD4/pages/log.html).

**Live site:** https://karagemop466-tech.github.io/GOLD4/

**Pass 15 (2026-10-23) — the first *online* audit in this project (historical record; this table is what that pass saw).** Every one of the 64 ring URLs and all 28 sources registered at that time (32 today) was re-opened from a GitHub runner with open internet, and each page's own schema.org / price-meta offer was compared with the stored value:

| Result | Count | What it means |
|---|---|---|
| Prices re-confirmed by the page itself | **45** | the page's own structured data prints exactly the stored amount |
| Prices the page now prints differently | **4** | VR-01, MN-01, MN-02, MJ-06 — both numbers published, nothing overwritten |
| Source URLs that now return 404 | **5** | BN-09, BN-10, BN-11, BN-12, RS-05 — flagged `SOURCE_URL_DEAD` |
| Sources that refuse automated checks (403) | **7** | all Brilliant Earth — no price claim made, flagged `SOURCE_BOT_BLOCKED` |
| JavaScript-only pages (price unreadable) | **1** | AN-01 (Anjolee) |

See the **[Freshness page](https://karagemop466-tech.github.io/GOLD4/pages/freshness.html)** for the line-by-line table. No stored value was changed by that check: a dead link or a blocked page never becomes a guessed price.

---

## ⚠ No hallucination rule (read before trusting anything here)

> **Every price, weight, karat, policy and link in this repository was read from the official page linked beside it, during this project.**
> If a value could not be read from an official source it is **left blank** and flagged as `UNVERIFIED` on the [Flagged for Review](https://karagemop466-tech.github.io/GOLD4/pages/flagged.html) page.
> Nothing is estimated, averaged, inferred from photographs, or copied from a blog, marketplace, resale listing or price-comparison site.
> Derived numbers (gold grams, gold value, price ÷ gold) are arithmetic on published inputs at a frozen, dated spot price — and an automated audit re-derives every one of them on every pass.

This rule is repeated at the top of every page of the site, and enforced by `scripts/audit.py`, which fails the build on a missing source, a non-official domain, a blank value without a flag, or a derived number that does not re-derive from its inputs.

When reviewing anything in this repo, **ask of each value: where is the official source, and what date was it read?** If the answer is missing, the value does not belong here.

---

## What is in the repository

| Path | What it is |
|---|---|
| `index.html`, `pages/*.html` | The published dashboard and its subpages (generated — do not hand-edit) |
| `assets/style.css`, `assets/app.js` | Styling and the client-side gold calculator / table filter |
| `data/rings.json` | The dataset: 64 rings, each with price, weight, sources, verification level, re-verification date and flags |
| `data/sellers.json` | Seller-level facts: return window, exclusions, resize terms, warranty, contact |
| `data/sources.json` | The 32 registered sources (law/regulator, market benchmark and each retailer's own policy pages) with tier, retrieval date and what each one supports |
| `data/methodology.json` | Karat table, 15 U.S.C. § 295 tolerances, formulas, assumptions, verification levels |
| `data/gold_spot.json` | The gold benchmark in force: **$3,996.31/oz** = **$128.48435/g**, read from the World Gold Council Goldhub panel on **23 Oct 2026 at 20:23Z** (the panel's own "Data as of" line reads 22 October, 2026). Corroborated within four minutes by Kitco ($3,996.30), BullionVault ($3,996.62) and JM Bullion's gold ask ($4,010.61). Every earlier reading is kept in `prior_captures` / `secondary_reference` — superseded values are never deleted |
| `data/derived.json` | Computed gold content / value / multiples (generated) |
| `data/verification_log.json` | Every verification pass, 0 through 18 (20 entries including Pass 12b), rendered on the site's Log page |
| `VERIFICATION.md` | Line-by-line verification record (generated from the JSON) |
| `reports/audit_latest.txt` | Latest integrity-audit output |
| `reports/live_source_check_*.json` | Raw live evidence: per-URL HTTP status, page title and the price strings the page printed |
| `data/source_health.json` | Per-row reconciliation of that evidence (source state + price verdict) |
| `COORDINATION.md` | Shared task board for the agent sessions working in this repo |
| `scripts/` | `compute.py`, `build_site.py`, `audit.py`, `gen_verification.py` |

## Reproduce / re-verify

```bash
python3 scripts/compute.py            # derived gold values from published inputs
python3 scripts/generate_site.py      # Assay Lab section (secondary 22-item catalogue)
python3 scripts/build_site.py         # canonical dashboard + pages/ (run last: it owns index.html)
python3 scripts/gen_verification.py   # regenerates VERIFICATION.md from the log
python3 scripts/audit.py              # gate 1 — integrity / hallucination audit
python3 scripts/check_site.py         # gate 2 — links, source link per row, no-hallucination banner
python3 scripts/verify.py             # gate 3 — schema + blank-value accounting
python3 scripts/verify_a0be79d4.py    # gate 4 — XSS, dead-link and 404 blocklist scanner
python3 scripts/audit_hallucinations.py  # gate 5 — phantom-math / unsourced-value auditor
python3 scripts/audit_freshness.py    # gate 6 — live-evidence freshness & source-health
```

### The online half of the audit (needs internet)

`scripts/live_source_check.py` makes read-only GETs to every official URL in the dataset, restricted to the host allow-list in `data/sources.json`, and writes an evidence artifact (HTTP status, soft-404 detection, page title, and the raw price strings the page prints) to `reports/`. It never writes a value into the dataset. `scripts/build_source_health.py` reconciles that artifact into `data/source_health.json`, and `scripts/apply_source_health.py` stamps each row with a `source_check` block plus review flags. The whole chain runs in CI (`.github/workflows/live-source-check.yml`) and commits its evidence back to the branch.

**Rule for the reconciliation:** `CONFIRMED` requires the page's own structured data to print exactly the stored USD amount. A 404, a 403 or a JavaScript-only shell produces *no claim at all*. A different number is reported, never silently adopted.

No third-party dependencies, no network access required to build. Python 3.10+.

## Four independent re-verification passes on the same tree

The published tree was **not taken on trust**: it was re-fetched row by row several times on the same day — by separate agent sessions before and after the merges (below).

**Pass 2 — session `arena/fd51d093-gold4`**

- **All 20 prices matched** the page on re-read, as did all karat/metal labels, the eight Blue Nile stock numbers and widths, and the four Allurez and two VRAI gram weights.
- **One correction:** AN-01's weight **is** published — `Approx. Metal Weight: 2.90 Gr.` in Anjolee's own Product Details table. The earlier "weight unreadable" flag was wrong and was withdrawn.
- **One material correction:** that same table says the centre diamond is **lab-created** (`Lab Created FG` / `Lab Created VS`), so the price cannot be compared with setting-only prices.
- **Two new flags:** VRAI's plain-band pages print `Pave carat weight:0.18ctw` in the spec block (`SPEC_LISTED_PAVE_ON_PLAIN_BAND`).
- **Benchmark re-read:** the World Gold Council panel showed **$4,028.53/oz** versus $4,024.36/oz earlier the same day. Both readings are recorded; derived values use the one this pass saw.

**Pass 5 — session `arena/e04b126a-gold4`** (this branch)

- All 20 rows re-opened **again**; every price, weight, SKU and width still matched. Anjolee's Product Details table was re-read independently and confirmed the 2.90 g weight and the lab-created centre stone.
- **Two new rows:** Brilliant Earth's Atelier Solitaire price, previously unreadable, is now displayed — **$1,190 (14K)** and **$1,390 (18K)** setting-only — so BE-01 and BE-02 were added. Neither page publishes a gram weight, so both weights stay blank.
- **New flags:** Brilliant Earth's resize wording differs between captures (`Free 1-Year Resizing` vs "one complimentary resize within 60 days"); Mejuri's product URLs open on a different colourway from the row (`PRICE_VARIANT_DEPENDENT`, and MJ-05 is a "From" price); VRAI's listing card points at a different configuration id from the row that carries the weight.
- Mejuri's two-year warranty is published on its product pages, so that blank seller field was filled from the page.

**Pass 6 — session `arena/e04b126a-gold4`, run against merged `main`** (commit `e7f4d36`)

- Deliberately run **after** the merge, so what was checked is the published site rather than a working copy.
- **All 22 rows re-opened on their own pages. Every price, weight, karat and stock number reproduced exactly** — nothing changed, because nothing was wrong.
- All four returns pages re-read in full; every quoted clause (windows, RMA, the $150 and $300 missing-document fees, the free-resize rules, VRAI's $300/$50 recycling fees, Mejuri's SCS-certificate rule) matched.
- The World Gold Council panel was read a **third** time and still showed **USD 4,028.53/oz, data as of 21 October 2026** — so the benchmark was left alone rather than refreshed to a number the page never printed.
- 16 CFR 23.3 was re-read in full: (b)(1)–(9) and (c)(1) confirm the karat-qualification and hollow-centre/"not solid" rules, (c)(2) sets the 1/40 overlay and 1/20 gold-filled thresholds at ≥10K, and footnote 32 restates the National Stamping Act tolerances, corroborating 15 U.S.C. § 295 from a second official page.
- **Two limits re-confirmed, not papered over:** Brilliant Earth's `/returns/` page again served only navigation and footer text, so its 30-day window could not be re-displayed and stays flagged; and no VRAI configuration page exposes a setting price in page text, so a VRAI price is only as good as its listing card until it is in the cart.

Every re-read is recorded per row in `data/rings.json` (`reverified_utc`, `reverified_by`, `reverification`) and per seller in `data/sellers.json`, and summarised on the site's Log page.

**Pass 7 — session `arena/1372cb32-gold4`, run concurrently and then merged** (this branch)

- Ran its own row-by-row re-fetch before it saw the passes above, and **independently reached the same two findings**: the Anjolee Product Details table publishes `Approx. Metal Weight: 2.90 Gr.`, and both VRAI plain-band pages list `Pavé carat weight: 0.18ctw` in their spec block. Two sessions finding the same behaviour on separate fetches is corroboration, not duplication.
- All prices, weights, SKUs and widths of the then-published 20 rows matched exactly; all seller policies and all Tier A/B sources matched their registry entries.
- **After merging `main` (PRs #7–#15) it re-checked the two new Brilliant Earth rows:** the 18K Atelier row re-confirmed exactly (**$1,390**, `BE1D2444-18KY`); the 14K page served a **EUR** rendering ("1,350.00 EUR (Setting Only)") to this session — Brilliant Earth prices are currency-localized — so its USD $1,190 is kept from the same-day USD capture and flagged `PRICE_CURRENCY_LOCALIZED` on both BE rows for manual re-check in USD.
- **Two unique outputs kept:** every Mejuri `price_source_url` now points at the exact product-variant URL where the price is displayed (the collection page was one click away from where the value was read), and `data/methodology.json` now states the derivation basis of the 15 U.S.C. § 295 floors (karat ÷ 24 basis vs the 585‰ millesimal convention — 57.63% vs 57.8% floor for a 14K stamp), published on the Flagged page rather than left implicit.
- Merge resolution: when `main` moved mid-pass, every merged file from PRs #7–#15 was kept as-is and this session's overlapping pre-merge edits were superseded — nothing from another session was discarded. The full record is in `COORDINATION.md`.

**Pass 9 — session `arena/22b5b06c-gold4`** (second independent collection, merged additively via PR #11)

- This session did **not** re-read the published rows; it collected a **fresh 19-candidate dataset from scratch** off official Blue Nile / James Allen / Brilliant Earth pages, then merged main's 47-row tree unchanged and added its rows on top (47 → 64). Because main had since assigned BE-03/BE-04 and BN-09…BN-12, its rows were **renumbered** to BE-05…BE-07 and BN-13…BN-26 (original ids preserved in `data/preserved/rings_candidates_22b5b06c.json`).
- 8 added rows were **live-fetched** (including BN-26, which was **sold out** — its price stays blank; an older $660 snapshot was deliberately *not* used), and 9 came from **dated snapshots of the same official pages** during a fetch-service outage, each corroborated by at least one further official read (schema.org JSON-LD where published). Those rows are flagged `PRICE_V2_ONLY` until a live re-fetch upgrades them; the three Brilliant Earth rows also carry Pass 7's `PRICE_CURRENCY_LOCALIZED` flag (their snapshots displayed US-dollar figures).
- **Two duplicates resolved, not stacked:** its Atelier Solitaire 14K candidate was published BE-01 (same URL, same $1,190), and its "Classic Simple Solitaire" candidate (item-203348) turned out to be published **BN-10** — a live re-fetch at 23:58Z showed the *same stock number 502120y14*, width 2.40mm and $1,145 under a second official URL alias with a *different product name*. Both times the published row was kept and the independent corroboration **appended** to its record; the BN-10 naming variance is recorded, not resolved.
- **Two new Blue Nile contradictions:** BN-22's copy says "platinum solitaire setting" against a 14K Yellow Gold spec (`COPY_INCONSISTENT_METAL`), and BN-20 showed four sale prices ($772/$724/$730/$728) for one SKU across four official pages (`SALE_PRICE_VARIES_ACROSS_PAGES`).
- **Benchmark cross-check:** an independent live API reading of **$4,028.10/oz** (23:01:42 UTC) sits 0.01% from the WGC benchmark $4,028.53/oz; same-day Kitco/APMEX snapshots are recorded informationally in `data/gold_spot.json`. The benchmark itself was left untouched.
- Full pipeline re-run after integration, all five CI gates green: `audit.py` **PASS (128 checks, 9 informational warnings, 0 failures)**, `check_site.py` PASS (26 pages), `verify.py` 0 hard failures (64 records), `verify_a0be79d4.py` 0 hard failures, `audit_hallucinations.py` **PASS (0 failures)**.

**Pass 11 — same session, post-merge** (live re-fetch of the V2 rows, 2026-10-23 00:20–00:35 UTC)

- The fetch-service outage cleared briefly: **6 of the 9 `PRICE_V2_ONLY` rows were re-fetched live and upgraded to V1** (BN-20…BN-25). Every stock number, metal and width re-read exactly.
- **Two prices corrected to current live values:** BN-20 $772 → **$965** and BN-25 $1,657 → **$2,210** — both 22 Oct sales had *ended* and the live pages showed the undiscounted setting prices. This is the volatility the `SALE_PRICE_VARIES_ACROSS_PAGES` flag warned about, observed in real time.
- BN-22's "platinum solitaire setting" copy contradiction was **confirmed on the live page**, not just the snapshot.
- The three Brilliant Earth rows (BE-05/06/07) could **not** be completed — the outage returned mid-page — so they keep `PRICE_V2_ONLY` (and `PRICE_CURRENCY_LOCALIZED`) and stay listed on the Flagged page until a live read confirms them. `audit.py` warnings fell 9 → 3 accordingly.

## What the data currently shows

| Metric | Value |
|---|---|
| Rings tracked | 64 |
| Retailers with product rows | 10 (Blue Nile — including the James Allen line, Allurez, VRAI, Mejuri, Brilliant Earth, Anjolee, Ross-Simons, Sarraf, Catbird, Mene) |
| Prices read from the retailer's own page | 62 of 64 (2 deliberately blank: VRAI VR-02 publishes no price; Blue Nile BN-26 was sold out at the live check) |
| Price provenance | 62 rows V1 (read from the retailer's own page) · 1 row V2 (BE-05 — a dated snapshot of the official page, corroborated by ≥2 official reads, flagged `PRICE_V2_ONLY`; BE-06 and BE-07 were upgraded to V1 in Pass 14) · 1 row with no published price (`U_unverified`, BN-26 — sold out at capture) |
| Gram weights published by the retailer | 17 of 64 — only these rows have a computable gold value |
| Rows with explicit *solid gold* wording | 19 of 64 |
| Rows publishing a hallmark / maker's mark | **0 of 64** — it can only be checked in your hand |
| Rows re-read from their own source page | the original 20 rows were re-read by up to four independent sessions on 2026-10-22; the 17 rows added by Pass 9 were each read from their official page at collection (8 live-fetched, 9 from dated official-page snapshots with corroboration); every row carries its re-verification record |
| Gold benchmark used | **$3,996.31/oz = $128.48435/g**, read 23 Oct 2026 at 20:23Z (panel's "Data as of" line: 22 October 2026). The 10:02Z reading of $4,024.45 is preserved in `prior_captures`; the same-day Kitco/BullionVault/JM Bullion cross-checks are recorded informationally in `data/gold_spot.json` — the benchmark itself was independently re-read by a second session at ~20:19Z (same $3,996.31) and by Pass 17 as a cross-check before this refresh; derived arithmetic uses only the benchmark |
| Flags raised for review | published on the Flagged page, with sources |

**Headline findings**

1. A stamp is a claim with a legal tolerance, not a measurement: under 15 U.S.C. § 295 an "18K" ring may be as low as 74.3% gold and a "14K" ring as low as 57.63%.
2. Most major retailers do not publish a gram weight, so their rings cannot be priced against their own gold. Only Allurez, VRAI, Anjolee, Sarraf and Ross-Simons did (17 of 64 rows). Anjolee's price includes a lab-created centre stone, so even that multiple is not a setting markup. Blue Nile and Brilliant Earth publish none at all.
3. The 18K premium is inconsistent: +15.5% (Blue Nile Petite Solitaire), +16.8% (Brilliant Earth Atelier), +16.8% (Brilliant Earth Freesia, added by Pass 9), +40.1% (Blue Nile Comfort Fit), +68.0% (Allurez Split Shank) — and for the one pair with both weights published, 54.9% of that premium is simply more gold.
4. Return windows all look like "30 days", but exclusions differ sharply (resized, engraved, custom). One seller (Anjolee) explicitly accepts returns on customised orders; another (Allurez) makes custom orders non-refundable.
5. Several retailer pages contradict their own specification blocks; each case is listed on the Flagged page. Pass 9 found two more on Blue Nile: a 14K yellow-gold page whose copy says "platinum solitaire setting" (BN-22 — **confirmed on the live page** at the 2026-10-23 re-fetch), and one SKU showing four different sale prices across four official category pages (BN-20 — at the live re-fetch the sale had *ended* and the page showed $965 undiscounted; the live price is the recorded one). It also recorded a naming variance: stock number 502120y14 is titled "Low Dome Comfort Fit Solitaire" on one official URL and "Classic Simple Solitaire" on its alias (BN-10's record).
6. James Allen now redirects into Blue Nile: jamesallen.com product URLs land on bluenile.com, which states "James Allen is Now Part of Blue Nile" (live-verified 2026-10-22, recorded on BN-26). "By James Allen" collection rings are Blue Nile listings and carry Blue Nile's policies.

## Sources

- **Tier A — government/regulator:** FTC consumer guidance on jewellery; 16 CFR Part 23 (§ 23.3); 15 U.S.C. § 295 and ch. 8; FTC credit-card dispute guidance.
- **Tier B — market benchmark:** World Gold Council gold spot; LBMA benchmark description.
- **Tier C — retailer's own site:** 64 product pages across all 10 retailers (Blue Nile, Allurez, VRAI, Mejuri, Brilliant Earth, Anjolee, Ross-Simons, Sarraf, Catbird, Menē) plus each retailer's own returns/exchanges and warranty pages.

The full registry, with what each source supports, is in `data/sources.json` and on the site's Sources page.

---

## Parallel sessions and preserved artifacts

Several agent sessions worked in this repository. `main` already contained two of their merges when this session integrated. **Nothing was deleted**: their work is either kept in place or preserved verbatim under `docs/legacy/` and `data/preserved/`.

| Artifact | Origin | Status |
|---|---|---|
| `docs/**` sub-site (checklist, candidates, calculator, sellers, sources, flagged, verification) | session `arena/93da71b4-gold4` (PR #2) | Kept unmodified except for a banner marking it as a pre-data snapshot; still published under `/docs/` |
| `data/preserved/candidates_unverified_93da71b4.json` | same session | Preserved worksheet (R01–R08, all values null by design); **not** the canonical dataset |
| `styles.css`, `app.js`, `flagged.html`, `scripts/check_site.py`, `.github/workflows/pages.yml` | session `arena/b4413b13-gold4` (PR #1, #3) | Kept; `flagged.html` carries a "superseded" banner, the checker was extended for the populated catalog |
| `scripts/verify.py`, `AUDIT.md` | session `arena/93da71b4-gold4` | Kept and made schema-aware; still runs and still fails on an unsourced value |
| `docs/legacy/index_placeholder_b4413b13.html` | session `arena/b4413b13-gold4` | Original root dashboard, preserved after the integrated dashboard replaced it |
| `docs/legacy/COORDINATION_merged_before_9614479d.md`, `docs/legacy/README_before_9614479d.md` | pre-merge state of `main` | Preserved for audit |
| `data/preserved/rings_candidates_22b5b06c.json`, `data/preserved/gold_spot_capture_22b5b06c.json` | session `arena/22b5b06c-gold4` (PR #11) | Its independent 19-candidate working dataset (with its original ids) and live spot capture, preserved verbatim; 17 candidates were converted into the canonical schema as BE-05…BE-07 / BN-13…BN-26 and 2 duplicates were folded into corroboration notes on BE-01 and BN-10 |
| `docs/legacy/REPO_REVIEW_22b5b06c.md`, `docs/legacy/VERIFICATION_22b5b06c.md`, `docs/legacy/COORDINATION_22b5b06c.md`, `docs/legacy/README_22b5b06c.md` | same session | Its baseline repo review (annotated), line-by-line verification log, task board and README, preserved as written |
| `scripts/session_22b5b06c/`, `scripts/merge_rows_22b5b06c.py` | same session | Its standalone checkers and the idempotent converter that documents exactly how each added row was sourced — the audit trail of the Pass 9 integration |

**Eight** CI gates run against the combined repository (`.github/workflows/pages.yml`) as nine invocations — Gate 6 is split into a self-test (6a) and the real check (6b) — and every one must pass before a merge:

```bash
python3 scripts/audit.py                # Gate 1 — deep audit: allow-list, recomputation, speculation scan
python3 scripts/check_site.py           # Gate 2 — links + per-row source links + FTC/no-hallucination presence
python3 scripts/verify.py               # Gate 3 — schema-aware data audit, rewrites AUDIT.md
python3 scripts/verify_a0be79d4.py      # Gate 4 — multi-page XSS / 404 blocklist / Assay-Lab scanner
python3 scripts/audit_hallucinations.py # Gate 5 — gemstone-deduction, category-subpage & deep hallucination auditor
python3 scripts/session_46691f83/verify_citations.py --self-test   # Gate 6 — proves the citation gate still bites
python3 scripts/session_46691f83/verify_citations.py              # Gate 6 — CFR citation vs official section heading
python3 scripts/audit_freshness.py                                # Gate 7 — live evidence present, recent and applied to every row
python3 scripts/test_assurance.py                                 # Gate 8 — conservative currency parsing + blank current-price register
```

`scripts/run_gates_pass20.py` runs all nine invocations in one go and writes `reviews/pass20/gates.json`; that is the record quoted on the Pass 20 page.

The earlier sessions' own records (including the note that their sandboxes had no outbound access, which is why their catalogs were empty) are preserved in `COORDINATION.md` and in the site's Log page.

## Limitations (stated, not hidden)

- The gold benchmark is a live quote. Four reads on 2026-10-23 gave $4,024.45 (10:02Z), $3,996.31 (20:23Z), $3,995.47 (Pass 20, 23:43–23:45Z) and earlier $4,028.53 — a 0.80% spread across the day. The dataset stores the reading it actually saw, with its timestamp, and never silently refreshes it. **Policy applied in Pass 20:** an intraday tick on an unchanged source date (here −0.021%) is recorded as a cross-check rather than substituted into the benchmark, so derived values are re-derived only when the source's own data date moves or the move is material.
- Prices are a snapshot, not a feed: each row carries its own capture date (22–23 October 2026). Retail prices move; re-check the source link before buying.
- Weights are the seller's own numbers, sometimes labelled "approximate", and are quoted for a single ring size.
- Gold value is melt-value arithmetic, not an appraisal and not a resale offer.
- Reputation was **not** verified for any seller; no review or complaint data was collected.
- No XRF or assay result exists for any item — that is the point of the on-arrival step in the checklist.
- Brilliant Earth: the Atelier Solitaire setting price was readable on the 2026-10-22 pass ($1,190 in 14K, $1,390 in 18K yellow gold), so two rows now carry a price. No gram weight is published for either, so their gold value stays blank. The page badge read "Free 1-Year Resizing" on the re-read where the earlier capture described one complimentary resize within 60 days — flagged, not silently overwritten.
- Reputation data is still absent for every seller: no review or complaint source was collected, and none is implied.

## Coordination

Several agent sessions have worked in this repository. The shared task board, claims, hand-offs and the integration record live in [`COORDINATION.md`](COORDINATION.md), and the published summary is on the site's Log page. Shared output files (`index.html`, `pages/`, `data/`) are owned by the integration session; other sessions' branches were left untouched.

## Disclaimer

Research, not financial, legal or gemmological advice. Independently verify any ring — purity, weight and hallmark — with a qualified jeweller before relying on it.
