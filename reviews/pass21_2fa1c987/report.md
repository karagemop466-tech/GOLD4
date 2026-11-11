# Pass 21 companion — non-canonical surface audit, prose hallucination scan & dead-link re-read

**Session:** `arena/2fa1c987-gold4` · **Branch:** `arena/2fa1c987-gold4` · **Read window:** 2026-11-11 08:05Z–08:26Z
**Board claim:** written and pushed *before* any file in scope was edited (`COORDINATION.md`, session section).

## Why this pass exists

Six other sessions were working this repository at the same minute this one started. All six were working the
**canonical** surfaces — `data/**`, `index.html`, `pages/**`, the gold benchmark, the gates. Nobody had claimed the
**non-canonical** surfaces: the eight root pages written by `scripts/generate_site.py`, the six `categories/**` pages,
the frozen `docs/**` sub-site, `assets/**`, `static/**`, and the long prose documents.

Those pages are still published to GitHub Pages and a reader can reach them. A number that has drifted there is a live
hallucination risk even when `data/` is perfect — and today is **2026-11-11**, nineteen days after the stored evidence,
which makes prose drift *more* likely, not less.

Scope discipline: this session wrote **nothing** into `data/**`, `index.html`, `pages/**`, `docs/**`, `categories/**`,
`assets/**`, README, AUDIT or VERIFICATION. Where a finding belongs to a file another session owns, it is logged as a
**request**, not edited.

## Read path (stated first, because it bounds every claim)

This sandbox has no general outbound internet from `bash`. It has a **browser-rendered page reader**. Every live value
below was read through that reader during the window above. Nothing is quoted from memory, nothing is inferred, and a
page that would not render produced **no claim at all**. Per-read clock times are not captured by the reader, so each
entry records the date, not a second-level time.

## 1. Machine audit of the non-canonical surfaces

Two new scanners, both in `scripts/session_2fa1c987/` and both read-only:

| Scanner | What it does | Result before fix | Result after fix |
|---|---|---|---|
| `scan_prose.py` | reconciles every money / per-oz / per-gram / gram / multiple / count token on 34 non-canonical files against every number stored in `data/**` | **1 416** claims · 1 413 traceable · 2 dated-historical · **1 untraceable** | **1 507** claims · 1 503 traceable · 3 dated-historical · **1 untraceable** |
| `check_superseded.py` | finds readings that `data/gold_spot.json` marks `status: superseded` but a page presents as current | **10 findings** | **3 findings** |

Raw output: `prose_scan.json`, `prose_scan_after.json`, `superseded_scan.json`, `superseded_scan_after.json` (this folder).

A note on method, because it matters: the first draft of `check_superseded.py` excluded any line containing the word
"cross-check", and that **silently swallowed the real finding** — the legacy pages print the benchmark inside a ribbon
whose label begins `CROSS-CHECK QUOTES · 2026-10-22 (benchmark: WGC $4,024.45/oz, 22 Oct)`. The exclusion is now by
*value* (Kitco / JM Bullion / BullionVault quotes read from `data/`), never by keyword. A scanner that hides its own
finding is worse than no scanner, so this is recorded rather than quietly corrected.

## 2. Live readings taken today

| Target | URL | What the page printed | Stored | Verdict |
|---|---|---|---|---|
| Gold benchmark | [gold.org/goldhub/data/gold-prices](https://www.gold.org/goldhub/data/gold-prices) | **USD 4,059.49/oz**, "Data as of **10 November, 2026**", ICE Data Services | $3,996.31/oz, "22 October, 2026" | **+1.58 %** — recorded, **not applied** (benchmark file is owned by `arena/d5947c03-gold4`) |
| AN-01 | [anjolee.com … Six-Curved-Prongs …](https://www.anjolee.com/rings/diamond-solitaire-engagement-rings/Six-Curved-Prongs-Solitaire-Diamond-Engagement-Ring.aspx) | `Price:$870.76`, MS354-A, 14K White Gold, 0.50 ct FG/VS, size 6.5 | $870.76 (2026-10-22) | **exact match** — first corroboration on a second read path; the page was previously recorded as unreadable |
| BE-07 | [brilliantearth.com Fleur Solitaire](https://www.brilliantearth.com/Fleur-Solitaire-Ring-14K-Gold-BE1574-76785943/) | `fleur solitaire-$1,350`, currency selector shows **USD** | $1,350 (2026-10-23) | **exact match, in USD** — the page was previously `SOURCE_BOT_BLOCKED` |
| VR-01 | [vrai.com classic-4-prong-dome](https://www.vrai.com/configure/setting-to-diamond/classic-4-prong-dome/round-brilliant-yellow-gold-40635875360861) | 18k Yellow Gold, 1.0 ct I-J VS+, plain band | metal 18k, price $1,035, 2.86 g | **metal matches; price not returned** → no price claim |
| BN-09 · BN-10 · BN-11 · BN-12 | four bluenile.com URLs | "We're sorry, the page you're looking for cannot be found." | flagged `SOURCE_URL_DEAD` | **all four still dead** (soft 404 — HTTP 200 with 404 copy), 19 days on |

## 3. Findings

| # | Severity | Finding | Where | Disposition |
|---|---|---|---|---|
| **F-2F-01** | **HIGH** | Eight published pages presented a **superseded** gold benchmark as the benchmark in force: `CROSS-CHECK QUOTES · 2026-10-22 (benchmark: WGC $4,024.45/oz, 22 Oct)`. `data/gold_spot.json` keeps $4,024.45 in `prior_captures[2]` with `status: superseded`; the active benchmark is **$3,996.31/oz**. Confirmed live on the public site today. The "Zero Invented Data" policy bullet repeated it: "the gold benchmark driving every derived value is … **$4,024.45/oz**". | `dashboard.html`, `solitaires.html`, `three-stone-halo.html`, `bands.html`, `checklist.html`, `standards.html`, `audit.html`, `coordination.html` | **FIXED** — value now derived from `data/gold_spot.json` at build time, with the WGC source link and both dates |
| **F-2F-02** | MEDIUM | The same ribbon claimed "**5** Automated Audit Gates Passing ✓". `.github/workflows/pages.yml` runs **nine gates / twelve command invocations**. | same eight pages | **FIXED** — gate count and invocation count are now counted from `pages.yml` at build time |
| **F-2F-03** | MEDIUM | The hero read "With **live** fine gold trading at $4,024.60/oz … on 2026-10-22" — a 20-day-old captured quote described as live. | `dashboard.html` | **FIXED** — reworded as a dated cross-check, with the benchmark in force named beside it |
| **F-2F-04** | LOW | The melt calculator shipped **pre-filled placeholder results** (`$650.20`, `1.34× melt (+$220.80 over raw gold)`, zone `1.02×–1.65×`) rendered in the results panel with no label and no source. If the script does not run, a reader sees numbers that look computed. The `+$220.80` figure is the single value this session's scanner could not trace to `data/**`. | `dashboard.html` (and every page using the widget) | **FIXED** — the panel is now explicitly headed "Pre-filled example only … not a quote, a valuation or a measured result for any listed ring" |
| **F-2F-05** | INFO | BN-09, BN-10, BN-11, BN-12 all still serve Blue Nile's own 404 copy. | `data/rings.json` rows | **confirmed, no change** — logged as a request for the `data/rings.json` owner |
| **F-2F-06** | INFO | AN-01's stored **$870.76** corroborated exactly today. | `data/rings.json` AN-01 | **logged as a request** — the `SOURCE_PRICE_NOT_MACHINE_READABLE` flag now has a contradicting read |
| **F-2F-07** | INFO | BE-07's stored **$1,350** corroborated exactly today, in **USD**. | `data/rings.json` BE-07 | **logged as a request** — bears on the `PRICE_CURRENCY_LOCALIZED` flag |
| **F-2F-08** | INFO | VR-01: metal confirmed; price not returned. Separately, the stored price **$1,035** (captured from a *different* URL, already flagged `PRICE_AND_WEIGHT_DIFFERENT_URLS`) is the same figure this page prints today for a **different product** ("Half Pave Band … $1,035") in its recommendations strip. | `data/rings.json` VR-01 | **flagged for review — no claim made.** It may be coincidence; the reviewer is told so |
| **F-2F-09** | INFO | WGC panel today: **$4,059.49/oz**, "Data as of 10 November, 2026" — **+1.58 %** vs the stored benchmark. | `data/gold_spot.json` | **recorded, not applied.** Independently agrees with PR #60's reading |
| **F-2F-10** | INFO | `README.md` lines 144 and 164 remain flagged by the new superseded scanner; both are historical pass narratives, not current claims. | `README.md` | **false positive — documented, no action** |
| **F-2F-11** | INFO | `categories/calculator.html` still offers "World Gold Council (2026-10-21): **$4,024.36**" as a selectable spot source. It is honestly dated in its own label, but it is a superseded reading and three weeks stale. | `categories/calculator.html` | **logged as a request** — not edited (honestly labelled, out of the claimed fix scope) |

## 4. What was changed

Two file groups, both unowned by any live session at the time the extension was claimed (verified with
`git diff --name-only b34ae17` against all six live branch heads):

1. **`scripts/generate_site.py`** — added `load_spot_facts()` (reads `data/gold_spot.json`) and `gate_counts()`
   (counts the gate steps and command lines in `.github/workflows/pages.yml`); replaced the hardcoded ribbon,
   gate count, hero wording, policy bullet, KPI labels and calculator example label with derived values.
   Applied by the idempotent, documented patch script `scripts/session_2fa1c987/apply_fix.py`.
2. **The eight root pages it regenerates** — rebuilt by `python3 scripts/generate_site.py`.

**No** ring price, weight, karat, URL, seller-policy text, benchmark value or other session's evidence file was
touched. `data/**` was read, never written.

## 5. Verification

All nine gates / twelve command invocations re-run on the edited tree — **12/12 PASS**
(full log: `reports/pass21_2fa1c987_gates.txt`):

| Gate | Result |
|---|---|
| G1 `audit.py` | PASS — 132 checks, 0 warnings, 0 failures |
| G2 `check_site.py` | PASS — 30 pages, local links resolve, every populated row carries an official source link |
| G3 `verify.py` | PASS — 64 records, 0 hard failures |
| G4 `verify_a0be79d4.py` | PASS — 40 pages, 0 hard failures |
| G5 `audit_hallucinations.py` | PASS — 1 183 checks, 0 warnings, 0 failures |
| G6a / G6b citations | PASS — self-test rejects the known-bad citation; 110 references clean |
| G7 `audit_freshness.py` | PASS — 295 checks, 4 known warnings, 0 failures |
| G8 `test_assurance.py` | PASS — 8/8 |
| G9a readiness tests | PASS — 22/22 |
| G9b calculator runtime | PASS — 10/10 (hypothetical fixtures) |
| G9c `readiness.py --check` | PASS |

Post-fix scanner state: superseded-benchmark findings **10 → 3**, of which 2 are historical-prose false positives
(F-2F-10) and 1 is an honestly-dated dropdown option (F-2F-11). Untraceable numeric claims: **1** (F-2F-04's
placeholder, now labelled an example).

## 6. Limits of this pass — read these before trusting it

- **This is a spot-check, not a sweep.** Seven live product URLs were re-read today. The other **57 rows keep their
  22–23 October 2026 capture dates** and were not re-opened by this session.
- A **soft 404** (HTTP 200 with 404 copy) is what Blue Nile serves; an automated status-code check alone would call
  those pages alive. They are not.
- The scanners reconcile numbers **against stored evidence**. Stored evidence can itself be stale: today's WGC panel is
  +1.58 % from the stored benchmark, so a page that perfectly matches `data/` can still be 19 days behind the market.
- **Passing gates are not proof.** The eight legacy pages passed every gate *while* printing a superseded benchmark,
  because no gate compares a rendered legacy number against `data/gold_spot.json`. That hole is what
  `check_superseded.py` now closes, and it is offered to the final integration as a candidate Gate 10.
- Corroboration of a stored price today does **not** authenticate a ring. It only says the page still prints that
  number.

**Standing rule, restated: after every review, look for hallucinations again — source link, capture date, read path,
and whether anything was inferred rather than read.**
