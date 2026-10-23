# GOLD4 — gold engagement-ring verification desk

A small, auditable dataset of **solid-gold engagement rings** with retailer prices, published gram weights, computed gold content and every unverified value published as *blank* instead of guessed.

**Latest review pass:** 22 October 2026 — every row was re-opened on its own source page three times, by two independent sessions and once more against merged `main`. Pass 2 corrected Anjolee's weight and centre-stone origin; Pass 5 re-checked all rows again and added two Brilliant Earth rows; Pass 6 re-checked the merged site and found no discrepancy. Two Brilliant Earth rows (BE-01 14K, BE-02 18K yellow gold) were added because their setting price became readable on this pass; three new flags were raised for Mejuri variant pricing, Brilliant Earth resize wording and the gold-spot drift. Nothing was filled in to make a row look complete. See the [Verification log](https://karagemop466-tech.github.io/GOLD4/pages/log.html).

**Live site:** https://karagemop466-tech.github.io/GOLD4/

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
| `data/rings.json` | The dataset: 22 rings, each with price, weight, sources, verification level, re-verification date and flags |
| `data/sellers.json` | Seller-level facts: return window, exclusions, resize terms, warranty, contact |
| `data/sources.json` | The 14 registered sources with tier, retrieval date and what each one supports |
| `data/methodology.json` | Karat table, 15 U.S.C. § 295 tolerances, formulas, assumptions, verification levels |
| `data/gold_spot.json` | The gold benchmark: **$4,028.53/oz, data as of 21 Oct 2026** (World Gold Council, read 22 Oct 2026). The earlier same-day reading of $4,024.36/oz is kept in `prior_captures` |
| `data/derived.json` | Computed gold content / value / multiples (generated) |
| `data/verification_log.json` | The verification passes (0–6) rendered on the site's Log page |
| `VERIFICATION.md` | Line-by-line verification record (generated from the JSON) |
| `reports/audit_latest.txt` | Latest integrity-audit output |
| `COORDINATION.md` | Shared task board for the agent sessions working in this repo |
| `scripts/` | `compute.py`, `build_site.py`, `audit.py`, `gen_verification.py` |

## Reproduce / re-verify

```bash
python3 scripts/compute.py        # derived gold values from published inputs
python3 scripts/build_site.py     # regenerate the static site
python3 scripts/gen_verification.py
python3 scripts/audit.py          # hallucination + integrity audit; non-zero exit on failure
```

No third-party dependencies, no network access required to build. Python 3.10+.

## Independent re-verification passes on the same tree

The published tree was **not taken on trust**: it was re-fetched row by row three times on the same day — twice by two separate agent sessions before the merge, and once more against the merged `main` afterwards. Later sessions extended the tree rather than re-reading it: `arena/a0be79d4-gold4` added the Sarraf / Catbird / Menē rows and the root research suite, `arena/81b71aa5-gold4` added Ross-Simons and the 5-gate CI (Pass 8), and `arena/22b5b06c-gold4` (Pass 9, below) collected a fresh dataset from scratch and merged 17 new rows additively. All are recorded in `COORDINATION.md` and `data/verification_log.json`.

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

**Pass 9 — session `arena/22b5b06c-gold4`** (second independent collection, merged additively via PR #11)

- This session did **not** re-read the published rows; it collected a **fresh 19-candidate dataset from scratch** off official Blue Nile / James Allen / Brilliant Earth pages, then merged main's 47-row tree unchanged and added its rows on top (47 → 64). Because main had since assigned BE-03/BE-04 and BN-09…BN-12, its rows were **renumbered** to BE-05…BE-07 and BN-13…BN-26 (original ids preserved in `data/preserved/rings_candidates_22b5b06c.json`).
- 8 added rows were **live-fetched** (including BN-26, which was **sold out** — its price stays blank; an older $660 snapshot was deliberately *not* used), and 9 came from **dated snapshots of the same official pages** during a fetch-service outage, each corroborated by at least one further official read (schema.org JSON-LD where published). Those rows are flagged `PRICE_V2_ONLY` until a live re-fetch upgrades them.
- **Two duplicates resolved, not stacked:** its Atelier Solitaire 14K candidate was published BE-01 (same URL, same $1,190), and its "Classic Simple Solitaire" candidate (item-203348) turned out to be published **BN-10** — a live re-fetch at 23:58Z showed the *same stock number 502120y14*, width 2.40mm and $1,145 under a second official URL alias with a *different product name*. Both times the published row was kept and the independent corroboration **appended** to its record; the BN-10 naming variance is recorded, not resolved.
- **Two new Blue Nile contradictions:** BN-22's copy says "platinum solitaire setting" against a 14K Yellow Gold spec (`COPY_INCONSISTENT_METAL`), and BN-20 showed four sale prices ($772/$724/$730/$728) for one SKU across four official pages (`SALE_PRICE_VARIES_ACROSS_PAGES`).
- **Benchmark cross-check:** an independent live API reading of **$4,028.10/oz** (23:01:42 UTC) sits 0.01% from the WGC benchmark $4,028.53/oz; same-day Kitco/APMEX snapshots are recorded informationally in `data/gold_spot.json`. The benchmark itself was left untouched.
- Full pipeline re-run after integration, all five CI gates green: `audit.py` **PASS (128 checks, 9 informational warnings, 0 failures)**, `check_site.py` PASS (26 pages), `verify.py` 0 hard failures (64 records), `verify_a0be79d4.py` 0 hard failures, `audit_hallucinations.py` **PASS (875 checks, 0 failures)**.

Every re-read is recorded per row in `data/rings.json` (`reverified_utc`, `reverified_by`, `reverification`) and per seller in `data/sellers.json`, and summarised on the site's Log page.

## What the data currently shows

| Metric | Value |
|---|---|
| Rings tracked | 64 |
| Retailers with product rows | 10 (Blue Nile — including the James Allen line, Allurez, VRAI, Mejuri, Brilliant Earth, Anjolee, Sarraf, Catbird NYC, Menē, Ross-Simons) |
| Prices read from the retailer's own page | 62 of 64 (2 deliberately blank: VRAI VR-02 publishes no price; Blue Nile BN-26 was sold out at the live check) |
| Price provenance | 54 rows V1 (live page fetch) · 9 rows V2 (dated snapshot of the official page, each corroborated by ≥2 official reads, flagged `PRICE_V2_ONLY` pending live re-fetch) · 1 row with no published price (`U_unverified`) |
| Gram weights published by the retailer | 17 of 64 — only these rows have a computable gold value |
| Rows with explicit *solid gold* wording | 19 of 64 (Mejuri, Sarraf, Catbird NYC, Menē) |
| Rows publishing a hallmark / maker's mark | **0 of 64** — it can only be checked in your hand |
| Rows re-read from their own source page | all rows published through Pass 8 were re-read on 2026-10-22 by independent sessions; the 17 rows added by Pass 9 were each read from their official page at collection (8 live-fetched, 9 from dated official-page snapshots with corroboration) |
| Gold benchmark used | $4,028.53/oz = $129.5202/g, data as of 21 Oct 2026 (prior same-day capture $4,024.36/oz; an independent live reading of $4,028.10/oz at 23:01 UTC on 22 Oct plus same-day Kitco/APMEX snapshots are recorded informationally in `data/gold_spot.json` — derived arithmetic uses only the benchmark) |
| Flags raised for review | published on the Flagged page, with sources |

**Headline findings**

1. A stamp is a claim with a legal tolerance, not a measurement: under 15 U.S.C. § 295 an "18K" ring may be as low as 74.3% gold and a "14K" ring as low as 57.63%.
2. Most major retailers do not publish a gram weight, so their rings cannot be priced against their own gold. Only Allurez, VRAI, Anjolee, Sarraf and Ross-Simons did (17 of 64 rows). Anjolee's price includes a lab-created centre stone, so even that multiple is not a setting markup. Blue Nile and Brilliant Earth publish none at all.
3. The 18K premium is inconsistent: +15.5% (Blue Nile Petite Solitaire), +16.8% (Brilliant Earth Atelier), +16.8% (Brilliant Earth Freesia, added by Pass 9), +40.1% (Blue Nile Comfort Fit), +68.0% (Allurez Split Shank) — and for the one pair with both weights published, 54.9% of that premium is simply more gold.
4. Return windows all look like "30 days", but exclusions differ sharply (resized, engraved, custom). One seller (Anjolee) explicitly accepts returns on customised orders; another (Allurez) makes custom orders non-refundable.
5. Several retailer pages contradict their own specification blocks; each case is listed on the Flagged page. Pass 9 found two more on Blue Nile: a 14K yellow-gold page whose copy says "platinum solitaire setting" (BN-22), and one SKU showing four different sale prices across four official category pages (BN-20). It also recorded a naming variance: stock number 502120y14 is titled "Low Dome Comfort Fit Solitaire" on one official URL and "Classic Simple Solitaire" on its alias (BN-10's record).
6. James Allen now redirects into Blue Nile: jamesallen.com product URLs land on bluenile.com, which states "James Allen is Now Part of Blue Nile" (live-verified 2026-10-22, recorded on BN-26). "By James Allen" collection rings are Blue Nile listings and carry Blue Nile's policies.

## Sources

- **Tier A — government/regulator:** FTC consumer guidance on jewellery; 16 CFR Part 23 (§ 23.3); 15 U.S.C. § 295 and ch. 8; FTC credit-card dispute guidance.
- **Tier B — market benchmark:** World Gold Council gold spot; LBMA benchmark description.
- **Tier C — retailer's own site:** 20 product pages plus return-policy pages from Blue Nile, Allurez, VRAI, Mejuri, Brilliant Earth and Anjolee.

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

Five CI gates now run against the combined repository (`.github/workflows/pages.yml`), and all five must pass before a merge:

```bash
python3 scripts/audit.py               # Gate 1 — deep audit: allow-list, recomputation, speculation scan
python3 scripts/check_site.py          # Gate 2 — links + per-row source links + FTC/no-hallucination presence
python3 scripts/verify.py              # Gate 3 — schema-aware data audit, rewrites AUDIT.md
python3 scripts/verify_a0be79d4.py     # Gate 4 — 30-page XSS / 404 blocklist / Assay-Lab scanner
python3 scripts/audit_hallucinations.py # Gate 5 — gemstone-deduction, category-subpage & 875-check auditor
```

The earlier sessions' own records (including the note that their sandboxes had no outbound access, which is why their catalogs were empty) are preserved in `COORDINATION.md` and in the site's Log page.

## Limitations (stated, not hidden)

- The gold benchmark is a live quote. Two reads on the same day differed by 0.10%; the dataset stores the reading it actually saw and never silently refreshes it.
- Prices are a snapshot: 22 October 2026. Retail prices move; re-check the source link before buying.
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
