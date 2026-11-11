# Pass 21 — session `arena/d5947c03-gold4`

**Date:** 2026-11-11, evidence window ~07:59–08:20Z · **Branch:** `arena/d5947c03-gold4`
**Evidence:** [`observations.json`](observations.json) (machine-readable) · [`gates.txt`](gates.txt) / [`gates.json`](gates.json) (gate output)

> **No hallucinations.** Every value on this pass is either read from the official page linked beside
> it, computed by `scripts/compute.py` from published inputs, or left blank and flagged. Where a page
> printed a different number from the stored one, both numbers are published and nothing was
> overwritten. See [`observations.json`](observations.json) — nothing in it comes from memory.

---

## 1. What this pass did before touching a file

1. Read the board (`COORDINATION.md`): every prior pass merged and closed; no live claims; the last
   activity was 2026-10-24. No stale claim needed taking over.
2. Ran **all nine gates (twelve invocations)** on the unedited tree: **12/12 PASS** (Gate 7 passes with
   4 warnings — the three known Brilliant Earth 403-review warnings BE-05/06/07 plus a newly-present
   *age* warning: the stored runner evidence is 18 days old. The age warning is left visible).
3. Wrote the claim to `COORDINATION.md` and pushed it (**commit `47e48b9`**) **before** any scoped edit.
4. Reason for this pass: today is 2026-11-11 — 19 days after the stored benchmark's source date. The
   user's standing brief requires current prices, so the official benchmark source was re-read first.

**Branch note.** Arena pins this session to `arena/d5947c03-gold4`; the board's `session-<id>/<task>`
convention cannot be followed here. No other branch was created, modified or force-pushed.

## 2. Read paths available in this sandbox — stated, not assumed

| Path | Available? | What it was used for |
|---|---|---|
| Shell + internet to retailer sites | **No** — only GitHub, npm and PyPI hosts are reachable; `curl` to a retailer fails at TLS (`SSL_ERROR_SYSCALL`) | nothing |
| GitHub Actions (`workflow_dispatch`) | attempted post-push as a read-only evidence run; uploads an artifact | see note in observations.json / publish record |
| GitHub Actions run logs / artifacts | **No** — `results-receiver.actions.githubusercontent.com` is unreachable | nothing |
| This session's browser-rendered page reader | **Yes** | all reads below |

Consequence, said plainly: **no runner evidence was collected or inspected by this pass.** The last
inspected runner sweep remains 2026-10-23T20:23:21Z. Nothing was applied from any run artifact.

## 3. The benchmark move (the one data change)

| What | Before | After |
|---|---|---|
| WGC Goldhub panel value | $3,996.31/oz | **$4,059.49/oz** |
| Panel date line | "Data as of 22 October, 2026" | **"Data as of 10 November, 2026"** (page headed "10 November, 2026") |
| Per-gram constant | $128.48435/g | **$130.515634/g** (recomputed by `compute.py`, re-checked by `audit.py`) |
| Delta | — | **+1.58%** |
| Cross-check (same morning) | — | BullionVault "Current Gold Price" line: **$4,058.82/oz · $130.49/g** at 11 November 2026, 03:02:20 (GMT-05:00) — **−0.017%** vs the new benchmark |
| Superseded benchmark | — | preserved verbatim in `prior_captures`; nothing deleted |

Criterion, stated so the rule is checkable: the benchmark moves only when the panel's own **data date
advances** (Pass 12 precedent) or the move is material (Pass 18, −0.70%). Intraday ticks on an unchanged
source date (Passes 17/19/20) are recorded as cross-checks and never substituted. Here the source date
advanced 22 Oct → 10 Nov 2026 and the move was +1.58% — a move under the intraday-retain policy would be
wrong in both respects.

## 4. Readings (2026-11-11, all official sources)

| Ref | Row / page | Verdict | Stored | Page printed |
|---|---|---|---|---|
| R01 | gold benchmark (WGC) | **moved on advanced source date** | $3,996.31/oz @ 2026-10-23 | **$4,059.49/oz**, "Data as of 10 November, 2026" |
| X01 | BullionVault (cross-check) | corroborates | — | $4,058.82/oz · $130.49/g · 11 Nov 2026 03:02:20 GMT-05:00 |
| L01 | 15 U.S.C. § 295 (LII) | **match** | 0.003 / 0.007 duty | section prints exactly that; "concurrent and not alternative" |
| L02 | eCFR 16 CFR Part 23 | **match** | § 23.0–23.28 | Title 16 up to date as of 11/09/2026; last amended 10/30/2026; § 23.3/§ 23.4 present |
| L03 | FTC buying-jewelry guidance | **match** | checklist claims | karat = x/24; trademark beside karat mark; solid = not hollow; 1/20 overlay threshold; vermeil note |
| R02 | AL-01 (Allurez) | **match** | $585 · 3.58 g | `$585`, "Approximate Metal Weight 3.58 grams", NG4426, setting only |
| R03 | SR-03 (Sarraf) | **match** | $871 · 6.70 g | `Now: US$871.00`, "18K Solid Gold", "6.70 grams" (size-10 basis stated), 18KY-LPBWB05 |
| R04 | MN-01 (Menē) | **differs** (−0.68%) | $1,465 | **$1,455** — identical floating-price behaviour (Passes 17/19/20 read $1,442; daily metal-value pricing). Nothing overwritten |
| R05 | RS-02 (Ross-Simons) | **differs, conditional** | $249 · 0.7 g | 20% promo: "Original price $249", **"Sale price $199.20"**, sizes 5–10 in stock; 0.7 g / 18kt reproduce exactly. Nothing overwritten |
| R06 | BN-09 (Blue Nile) | **dead link, confirmed again** | $1,125 | "We're sorry, the page you're looking for cannot be found." |

**Coverage:** 5 of 64 product rows re-read live, of which **2 fully corroborate** (AL-01, SR-03) and 2 differ
in a way the dataset already predicts (floating price, sale state). **59 rows were not re-read this pass**
and keep their 2026-10-22/23 capture dates. No row's price, weight, karat, URL or flag was overwritten.

## 5. Calculator re-derivation at the new benchmark (hand check)

| Row | Weight | Fineness | Pure gold | Gold value @ $130.515634/g | Price ÷ gold value |
|---|---|---|---|---|---|
| AL-01 | 3.58 g | 14/24 | 2.0883 g | **$272.56** | 2.15× |
| SR-03 | 6.70 g | 18/24 | 5.0250 g | **$655.84** | 1.33× |

Both match what `scripts/compute.py` regenerated in `data/derived.json` and what `scripts/audit.py`
re-derives on every run (gate 1). Phantom-math rule intact: rows without a published weight get no gold
value, not a number.

## 6. Irregularities found and how they are handled

| ID | Finding | Handling |
|---|---|---|
| FLG-PASS21-01 | Stored benchmark 19 days behind its own source, +1.58% | **Fixed** (benchmark moved; old reading preserved; all derived values recomputed) |
| FLG-PASS21-02 | RS-02 is selling at $199.20 under a 20% promotion | **Published, not overwritten** — stored $249 (original price) retained with sale state noted in evidence |
| FLG-PASS21-03 | MN-01 now $1,455 vs stored $1,465 | **Published, not overwritten** — fourth independent floating-price read; register still shows current exact quote as blank |
| FLG-PASS21-04 | Gate 7 gained an age warning (evidence 18 days old) | **Left visible**; not suppressed or edited away; the online re-check remains the runner's job |
| FLG-PASS21-05 | RS-02's row URL (`/jewelry/rings/985230.html`) now **redirects** to `/products/985230` and title matches; metal/weight unchanged | **URL left unchanged** (redirect resolves; not a 404); noted for the next data-owned pass |

## 7. Security / hallucination scan posture

- All twelve gate invocations re-run after every edit class (see §8); no gate output was edited, weakened or skipped.
- Every populated table row still carries an official HTTPS source link — enforced by gates 2, 4 and 5.
- Front-page NO HALLUCINATIONS summary, the Flagged for Review page and the blank-current-price register are unchanged in force.
- No new hallucination class was found in this pass's edits; **the standing recommendation is repeated, as it is after every review: look again for hallucinations — source link, date, read path, and whether anything was inferred.**

## 8. Gate results

See [`gates.json`](gates.json) (machine-readable) and [`gates.txt`](gates.txt) (verbatim output). The same
suite is wired into `.github/workflows/pages.yml` and runs on the PR and on every push to `main`.

## 9. Not verified this pass (explicit)

- 59 of 64 rows not re-read; their values remain 2026-10-22/23 dated readings, not current quotes.
- Kitco and JM Bullion cross-checks not re-read (only BullionVault was). No number was carried over from memory.
- Brilliant Earth rows (403 to automation) unchanged.
- The live-source runner's artifact is not inspectable from this session; nothing from it was applied.
- Hallmarks, maker's marks and measured purity remain unverifiable without the ring in hand (XRF or equivalent required).
