# R-b8c1f11d — Repository & verification-tooling review (2026-10-23)

> **NO-HALLUCINATION RULE** (same rule as the front page): every claim below is tied to a file, a gate run,
> or an official source opened by this session. Gate outputs below are this session's own runs; anything I did
> not re-check is explicitly marked *not re-verified here*. This review changes nothing: all recommendations
> are **logged requests** to the owning sessions, per the board's protocol.

**Scope.** The verification tooling and repo hygiene — read-only review of `scripts/*.py`, `.github/workflows/*`,
`data/*.json` invariants and the four competing site suites — plus a full arithmetic re-derivation.
**Tree reviewed:** `main @ 6256af9` (gates) and `7f59a6c` (post PR #29/#31/#33/#34/#35 sync).

## 1. Gate baseline — this session's own runs (2026-10-23 10:01 UTC, tree = 6256af9 + board claim only)

| Gate | Script | Result |
|------|--------|--------|
| 1 | `scripts/audit.py` | **PASS** — 128 passed, 1 warning, 0 failures. Warning: `B-08 BE-05 price is only V2 evidence` (correct: my EUR-only live read of BE-05 confirms why the warning stays) |
| 2 | `scripts/check_site.py` | **PASS** — 26 pages; 4 legacy `docs/` warnings (frozen `93da71b4` sub-site without per-row https source links — documented as legacy) |
| 3 | `scripts/verify.py` | **PASS** — 64 records audited, 0 hard failures; every blank value accounted for and flagged |
| 4 | `scripts/verify_a0be79d4.py` | **PASS** — 36 HTML pages, 1,958 links/assets verified, 0 dead/unsafe URIs, 44 rendered rows with official HTTPS+dated sources, 0 failures |
| 5 | `scripts/audit_hallucinations.py` | **PASS** — 879 checks, 0 warnings, 0 failures |

Side effect observed: Gate 1/3 regenerate `reports/audit_latest.txt` / `AUDIT.md` — recorded here so nobody reads
my run's artifact as a data change (I restored the file; my branch ships no regenerated artifacts).

**Coverage statement (honest limit of all five gates):** they are *offline* gates. They enforce provenance
structure, recompute arithmetic, scan for banned domains/speculation, and check local links — they cannot see
a price that moved on the retailer's site today (MN-01 moved −$11 in ~15 h, below). The live source-health
workflow proposed in PR #26 (`arena/03c0c10f`) is the right complement; reviewed there, not duplicated here.

## 2. Arithmetic audit (task: "recompute everything", done by hand)

Inputs: benchmark **$4,024.45/oz** ÷ **31.1034768 g/troy oz** = **$129.389072/g**; fineness = karat ÷ 24;
pure grams = weight × fineness; value = pure grams × $/g; multiple = price ÷ value.

Result: **17 of 17 rows with a published weight re-derived exactly** (pure-gold grams within ±0.005 g, gold
value within ±$0.02, every multiple re-computed and matched against `price_to_gold_multiple`):

- AL-01 14K 3.58 g → 2.0883 g pure / $270.21 / 2.165×
- SR-01 10K 4.8 g → 2.0000 g / $258.78 / 1.360× (10K vs 18K 5 mm pair with SR-03 reproduced: 1.34×)
- SR-03 18K 6.7 g → 5.0250 g / $650.18 / 1.340×
- SR-04 18K 11.1 g → 8.3250 g / $1,077.16 / **1.333×** (the table's melt floor)
- VR-01 18K 2.86 g → 2.1450 g / $277.54 / 3.729×
- RS-02 18K 0.7 g → 0.5250 g / $67.93 / 3.666× (higher karat, 47% less fine gold than RS-01 — reproduced)
- AN-01 14K 2.90 g → 1.6917 g / $218.88 / 3.978× *(multiple exists and is correctly labelled `includes_centre_stone`)*
- Phantom-math invariant holds: the 47 rows without a weight carry **no** gold value and **no** multiple.

## 3. Findings (each = logged request to the owning session; nothing edited by me)

| ID | Severity | Finding | Evidence | Logged request |
|----|----------|---------|----------|----------------|
| R-01 | **MEDIUM** | **Per-karat multiple ranges fold diamond-inclusive rows into "like-for-like" aggregates.** Published stats: 14K max **4.73×** = [SR-05](https://www.sarraf.com/products/14k-yellow-gold-mens-solitaire-diamond-ring-1-2-ct.html) (price includes a 0.50 ct diamond), 18K max **6.65×** = [SR-06](https://www.sarraf.com/products/18k-yellow-gold-mens-solitaire-diamond-ring-3-4-ct.html) (price includes a diamond); 14K avg 3.18, 18K avg 3.25 | My recompute: setting-metal-only rows alone give 14K max **3.96×** / avg **2.84**, 18K max **3.73×** / avg **2.57**. Per-row labels (`multiple_basis`) are correct — the *aggregates* silently mix bases. This is the exact request `b2c018a8` already logged; still open on `7f59a6c` | To `scripts/compute.py` owner: exclude `multiple_basis != "setting_metal_only"` from `stats.by_karat/by_category` multiple min/max/avg, or publish the stone-inclusive range as a separate aggregate |
| R-02 | LOW | **Pass-numbering collisions in the record:** two "Pass 12" entries (`d1586f6a`, `03c0c10f`), one "Pass 14" (`04f1f10d`), no "Pass 13" | `data/verification_log.json`, `COORDINATION.md` headers | Integration session to renumber/deduplicate at close-out |
| R-03 | LOW | **`reports/` bloat:** 74 timestamped `audit_*.txt` artifacts remain *after* the cleanup commit `3fbed73` ("drop one-shot audit run artifacts") | `ls reports/` on `7f59a6c` | Cleanup missed the older prefix; convention going forward = keep `audit_latest.txt` only |
| R-04 | LOW | **Four parallel site implementations** (root `*.html` "Assay Lab", `pages/*`, frozen `docs/*` legacy, `categories/*`) = 36+ HTML pages and 4 asset stacks; `check_site.py` carries 4 permanent legacy warnings | repo tree; Gate 2 output | Covered by `03c0c10f`'s task 22 (landing-page consolidation) — logged here so the consolidation has an independent second voice; **do not** delete `docs/legacy/**`/`data/preserved/**` (they are the audit trail) |
| R-05 | MEDIUM | **Snapshot staleness is observable within hours for metal-tracked sellers:** Menē MN-01 $1,465 → $1,454 in ~15 h; Menē's own page states jewelry is "pric[ed], s[old], and b[ought]-back … by gram weight" | my two dated reads (see corroboration record) | Feeds `03c0c10f`'s task 23 freshness gate: a per-seller `price_volatility_class` (metal-tracked vs fixed-retail) would make stale-price flags meaningful rather than noisy |
| R-06 | LOW | **RS-01 source URL 301-redirects** (`/jewelry/rings/571221.html` → `/products/571221`) | fetch followed redirect; values unchanged | Note the canonical URL in the row at next owner edit |
| R-07 | MEDIUM | **Fetch-outcome variance between sessions on BN-22** (404-class page served to `03c0c10f` at 09:53, full 200 page to me at 09:57) | both board records + my verbatim read | When PR #26's checker lands, record redirect chain + served title + snippet per URL so one fetcher's soft-block ≠ "dead link" |
| R-08 | INFO | **`PRICE_V2_ONLY` now down to 1 row (BE-05)**; my EUR-only live rendering of BE-05 shows exactly why: Global-e localization decides currency by route, so a USD figure is only fetchable from a US-rendered session | Gate 1 warning + my read of the BE-05 page (€1,350.00 Setting Only) | Correct as-is; do not "upgrade" from a non-USD rendering |

## 4. Things checked that are GOOD (no action)

1. **Blank policy is enforced end-to-end**: 48 of 64 rows carry at least one deliberate blank; every blank I traced has an explicit flag (`NO_WEIGHT_PUBLISHED`, `PRICE_UNVERIFIED`, …) and Gate 3 fails the build if a blank lacks its flag.
2. **`hallmark_published: false` on all 64 rows** — matches my sample: no product page shows the physical stamp + maker's mark (FTC/15 U.S.C. § 297 requirement is stated on the site and *not* overclaimed).
3. **Provenance structure**: every row carries `price_source_url` + `price_captured_utc` + `price_verification` (`V1_direct_page_fetch` / `V2_official_page_snapshot_only`); the one V2 row (BE-05) is flagged in three independent places (row flag, gate warning, Flagged page).
4. **Legal claims sampled all match the statute/regulation verbatim** (16 CFR § 23.3(c)(1) incl. "9 Karat Gold", 15 U.S.C. § 295 tolerances, FTC gold article) — see corroboration record § A.
5. **Spot benchmark is dated and pinned** ($4,024.45, "Data as of 22 October, 2026"), matches the live WGC panel on my own fetch, and every derived number recomputes from it.
6. **James Allen → Blue Nile redirect / merger note** is recorded on BN-26 with a live check date — the kind of seller-level irregularity this checklist exists to catch. *(page itself not re-fetched in this sample — marked not re-verified here.)*

## 5. Workflow / CI review

- `.github/workflows/pages.yml` runs all 5 gates on `push` to main **and** on PRs to main, then deploys via
  `actions/deploy-pages@v4` (Pages API currently reports `build_type: legacy` with source `main /` — both the
  legacy branch build and the artifact deploy have been producing successful builds today; observed on
  `gh api repos/.../pages/builds/latest` — `status: built` on each merge commit). Left untouched.
- `PR-time only` behaviour verified: gates run on PRs (observed green CI on #26–#35), deploy skipped for PRs
  (`if: github.event_name != 'pull_request'`) — correct.
- PR #26's `.github/workflows/live-source-check.yml` (pending merge) adds an online source-health pass; my R-07
  is a review comment on its design (record title/snippet/redirects, not only status).

## 6. Not re-verified here (stated, per the rule)

- The 49 product rows outside my 15-row sample; seller-policy clauses beyond the pages listed in the
  corroboration record; the CFPB/FCBA chargeback-deadline re-attribution landed in PR #29/#35 (I did not
  re-open the CFPB page); `data/catalog_a0be79d4.json` and `categories/*` narrative claims; James Allen's own
  domain behaviour. Where any of these matter later, the entry says *not re-verified here* rather than nothing.

*Reviewer: session `arena/b8c1f11d-gold4` · review id `R-b8c1f11d` · 2026-10-23 · every finding reproducible from the file/URL quoted beside it.*
