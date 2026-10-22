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

## Three independent re-verification passes on the same tree

The published tree was **not taken on trust**: it was re-fetched row by row three times on the same day — twice by two separate agent sessions before the merge, and once more against the merged `main` afterwards.

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

## What the data currently shows

| Metric | Value |
|---|---|
| Rings tracked | 22 |
| Retailers with product rows | 6 (Blue Nile, Allurez, VRAI, Mejuri, Brilliant Earth, Anjolee) |
| Prices read from the retailer's own page | 21 of 22 (1 deliberately blank) |
| Gram weights published by the retailer | 7 of 22 — only these rows have a computable gold value |
| Rows with explicit *solid gold* wording | 5 of 22 (all Mejuri) |
| Rows publishing a hallmark / maker's mark | **0 of 22** — it can only be checked in your hand |
| Rows re-read from their own source page | 22 of 22, on 2026-10-22 (twice, by two independent sessions) |
| Gold benchmark used | $4,028.53/oz = $129.5202/g, data as of 21 Oct 2026 |
| Gold benchmark used | $4,024.36/oz = $129.3862/g, 21 Oct 2026 |
| Flags raised for review | published on the Flagged page, with sources |

**Headline findings**

1. A stamp is a claim with a legal tolerance, not a measurement: under 15 U.S.C. § 295 an "18K" ring may be as low as 74.3% gold and a "14K" ring as low as 57.63%.
2. Most major retailers do not publish a gram weight, so their rings cannot be priced against their own gold. Only Allurez, VRAI and Anjolee did. Anjolee's price includes a lab-created centre stone, so even that multiple is not a setting markup.
3. The 18K premium is inconsistent: +15.5% (Blue Nile Petite Solitaire), +16.8% (Brilliant Earth Atelier), +40.1% (Blue Nile Comfort Fit), +68.0% (Allurez Split Shank) — and for the one pair with both weights published, 54.9% of that premium is simply more gold.
4. Return windows all look like "30 days", but exclusions differ sharply (resized, engraved, custom). One seller (Anjolee) explicitly accepts returns on customised orders; another (Allurez) makes custom orders non-refundable.
5. Several retailer pages contradict their own specification blocks; each case is listed on the Flagged page.

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

Three checkers now run against the combined repository, and all three must pass before a merge:

```bash
python3 scripts/check_site.py   # links + per-row source links + FTC/no-hallucination presence
python3 scripts/verify.py       # schema-aware data audit, rewrites AUDIT.md
python3 scripts/audit.py        # deep audit: allow-list, recomputation, speculation scan
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
