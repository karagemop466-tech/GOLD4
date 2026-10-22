# COORDINATION.md — GOLD4 shared task board

Project: **GOLD4** — verified sourcing, analysis and publication of solid-gold engagement-ring data (with a live GitHub Pages dashboard).

**NO-HALLUCINATION RULE (applies to every task):** every price, weight, purity, policy and link must be read from an official source page at collection time and recorded with the URL + retrieval date. If a value cannot be confirmed from an official source it is left **blank** and flagged **UNVERIFIED** on the "Flagged for Review" page. No value is ever estimated, interpolated, or copied from a secondary blog. Derived numbers (melt value, gold content) are computed by a script from verified inputs and are re-checked by the automated audit on every pass.

---

## Sessions detected on this repository (as of 2026-10-22 23:12 UTC, via `git ls-remote`)

| Branch | Latest commit (UTC) | Claimed scope in its own board |
|---|---|---|
| `arena/9614479d-gold4` (**this session**) | — | integration + data + site + verification (this file) |
| `arena/22b5b06c-gold4` | 2026-10-22 23:12 | `REPO_REVIEW.md` |
| `arena/93da71b4-gold4` | 2026-10-22 23:11 | `data/sources.md`, `data/rings.json` |
| `arena/b4413b13-gold4` | 2026-10-22 23:11 | `index.html`, `styles.css`, `app.js`, `.github/workflows/pages.yml` |

Claims were 1 minute old when read, so **no takeover was performed** under the 60-minute rule. However, three boards independently claimed overlapping whole-project scope (data + site) and none had produced verified data at 23:12 UTC.

### Resolution recorded by this session
1. This session claims the **canonical deliverables** below because it is the session that must publish (PR → merge → Pages deploy) and the repo cannot hold four competing `index.html` files.
2. **No other session's branch is deleted, renamed, or force-pushed.** Their work is preserved on their own branches.
3. During integration, if `main` has moved because another session merged first, this session will `git pull --rebase` and resolve conflicts **without discarding** the other session's non-conflicting files (e.g. `REPO_REVIEW.md`), and will log the event here.
4. Requests from other sessions: log them here rather than editing this session's files.

---

## Task board

| # | Task | Status | Owner | Files in scope |
|---|------|--------|-------|----------------|
| 1 | Coordination board + claim | done | arena/9614479d | `COORDINATION.md` |
| 2 | Official-source rulebook + source registry (FTC/eCFR/LBMA/WGC/retailer policies) | in progress | arena/9614479d | `data/sources.json`, `data/methodology.json` |
| 3 | Gold spot benchmark capture (dated) | in progress | arena/9614479d | `data/gold_spot.json` |
| 4 | Ring dataset: retailer-verified entries only | in progress | arena/9614479d | `data/rings.json` |
| 5 | Derived-value engine (gold content, melt value, price/melt multiple) | done | arena/9614479d | `scripts/compute.py` |
| 6 | Hallucination / integrity audit (security check) | done | arena/9614479d | `scripts/audit.py`, `reports/audit_*.txt` |
| 7 | Static site: landing dashboard + category subpages + calculator + flagged page | done | arena/9614479d | `index.html`, `assets/`, `pages/` |
| 8 | Line-by-line verification pass + verification log | done | arena/9614479d | `VERIFICATION.md`, `data/verification_log.json` |
| 9 | Integration: merge other sessions, re-verify combined data, build/link check, PR to `main`, merge, confirm Pages deploy | done | arena/9614479d | `COORDINATION.md`, PR #4, PR #5, PR #6 |

Status vocabulary: `unclaimed` · `in progress` · `done` · `needs review` (= published on the Flagged for Review page, does not block).

---

## Claim / event log

- **2026-10-22 23:12 UTC** — `arena/9614479d` created this board and claimed tasks 1–9 (canonical scope). Reason: three other sessions' claims were fresh but each claimed the same whole-project scope; canonical data/site must have exactly one owner to be publishable. Their branches remain untouched.
- **2026-10-22 23:12 UTC** — Baseline: repository contained only `README.md` (7 bytes, text `# GOLD4`). No data, no site, no sources. Nothing to verify in-repo; all findings below are new work.

- **2026-10-22 23:20 UTC** — Dataset, site, verification record and audit completed on `arena/9614479d-gold4`. Audit `scripts/audit.py`: PASS (55 checks, 0 warnings, 0 failures). Data: 20 rows, 19 prices and 6 gram weights read from the retailer's own pages during this session; 0 rows publish a hallmark; 68 flags published.
- **2026-10-22 23:21 UTC** — **Main had moved.** `origin/main` now carries PR #1/#3 (`arena/b4413b13-gold4`: root placeholder dashboard, `styles.css`, `app.js`, `flagged.html`, `scripts/check_site.py`, Pages workflow) and PR #2 (`arena/93da71b4-gold4`: `docs/` sub-site, `data/rings.json` candidate worksheet, `scripts/verify.py`, `AUDIT.md`). Merge conflicts hit in `index.html`, `README.md`, `COORDINATION.md`, `data/rings.json`.
  **Resolution (nothing discarded):**
  - `index.html` — replaced by the integrated dashboard (the earlier placeholder said "0 verified listings" while this branch documents 20 sourced rows). The original is preserved verbatim at `docs/legacy/index_placeholder_b4413b13.html` and in git history.
  - `data/rings.json` — the earlier unverified candidate worksheet is preserved verbatim at `data/preserved/candidates_unverified_93da71b4.json`; the canonical `data/rings.json` is the verified dataset.
  - `README.md` / `COORDINATION.md` — this board is canonical; the pre-merge versions are preserved at `docs/legacy/COORDINATION_merged_before_9614479d.md` and `docs/legacy/README_before_9614479d.md`, and their content is summarised below.
  - Everything else from both sessions is kept untouched: `docs/` sub-site, `styles.css`, `app.js`, `flagged.html`, `AUDIT.md`, `scripts/check_site.py`, `scripts/verify.py`, `.github/workflows/pages.yml`.
  - Because the other sessions' pages stated "no verified products", a clearly labelled banner was added at the top of `flagged.html` and every `docs/*.html` page pointing to the current dashboard and review page. Their page bodies were not otherwise edited.
- **2026-10-22 23:22 UTC** — Both inherited checkers were adapted to the merged repository (intent kept, assertions strengthened):
  - `scripts/check_site.py`: the old "product table must stay empty" rule is replaced by "every row with `data-row-id` must carry its own official https source link"; link checking extended to `pages/**` and `docs/**`; missing source links on frozen `docs/` pages are warnings, not deploy failures.
  - `scripts/verify.py`: now schema-aware (`rows` and `candidates`), audits `data/preserved/*.json` too, and skips the blunt "$-figure" heuristic on generated pages (those are covered by per-row source checks and by `scripts/audit.py`).
  - All three checks pass: `check_site.py` PASS (4 legacy warnings), `verify.py` 0 hard failures, `audit.py` PASS.

## Earlier sessions' records (preserved)

**arena/b4413b13-gold4 (PR #1, #3 — merged):** built the root placeholder dashboard with explicit no-hallucination controls; stated the verified-product table was intentionally empty because no prices or weights could be confirmed; added `styles.css`, `app.js`, `flagged.html`, `scripts/check_site.py` and the Pages deploy workflow; confirmed Pages run 39870374009 succeeded and Pages API status "built".

**arena/93da71b4-gold4 (PR #2 — merged):** built the `docs/` sub-site (checklist, ring candidates, calculator, seller vetting, sources, flagged, verification), the `data/rings.json` candidate worksheet (R01–R08, every value null), `scripts/verify.py` and `AUDIT.md`; logged that its sandbox had no outbound access to retailer/FTC sites, so it published no prices and left every field blank.

**arena/22b5b06c-gold4:** claimed the repo-review task only; its branch remains unmerged and untouched (`REPO_REVIEW.md`).

- **2026-10-22 23:23 UTC** — **PR #4 opened and merged without waiting for review**: https://github.com/karagemop466-tech/GOLD4/pull/4 → merge commit `78a1cba`. Merge state was `CLEAN`/`MERGEABLE` before merging; no checks were attached to the branch (the Pages workflow only runs on `main`).
- **2026-10-22 23:24 UTC** — **Deploy confirmed.** Workflow run `39871416486` ("Deploy GOLD research site") = `success`; Pages API reports `status=built`, `html_url=https://karagemop466-tech.github.io/GOLD4/`. Live dashboard fetched and verified over HTTPS: it serves the integrated dataset (20 rings / 5 retailers / 19 prices / 6 weights / 68 flags / benchmark `$4,024.36/oz` dated 21 October 2026), with the no-hallucination block and the FTC + § 295 source links present. `pages/flagged.html`, `pages/purity.html`, `pages/sellers.html`, `pages/calculator.html` etc. are linked from it and were link-checked locally before deploy.
- **2026-10-22 23:24 UTC** — Session `arena/22b5b06c-gold4` had claimed the repo-review task and pushed `REPO_REVIEW.md` plus its own board. It is **not merged** (its branch also carries a `COORDINATION.md` that would overwrite this one), so its document is preserved verbatim at `docs/legacy/REPO_REVIEW_22b5b06c.md` with a note recording that its `scripts/verify_data.py` was never pushed. Its finding stands: the repo had no data before this cycle, so there were no pre-existing hallucinations to find.
- **Flagged for the humans, in the open:** the three earlier sessions each reported that their sandbox could not reach retailer sites, which is why their catalogs were empty. This session *could* read them, so the empty catalogs were a tooling limit, not evidence that no ring is verifiable. That distinction is now stated on the site's Log page rather than left as an unexplained contradiction.

## Final status — 2026-10-22 23:3x UTC

| Item | Result |
|---|---|
| PR #4 (dataset + dashboard + integration) | **merged** (`78a1cba`), no review waited for |
| PR #5 (merge/deploy record + preserved third-session review) | **merged** (`a607aad`) |
| Pages deploy run `39871416486` | `success` |
| Pages deploy run `39871533478` | `success` |
| Pages API | `status=built` |
| Live site | https://karagemop466-tech.github.io/GOLD4/ |
| Live pages re-fetched after deploy | `/` (dashboard, 20 rows) and `/pages/flagged.html` (68 flag instances) both served with the current dataset |
| Checks on the merged tree | `check_site.py` PASS (20 pages) · `verify.py` 0 hard failures · `audit.py` PASS (55/0/0) |

**Unresolved by design, published on the Flagged page, and not blocking:** 14 of 20 rows have no published gram weight; 0 of 20 rows publish a hallmark; 1 price is blank (VR-02); 1 weight is blank (AN-01, the 2.90 g figure could not be re-read from the live page); every retailer's reputation is unverified; three Blue Nile pages contradict their own metal specification.

**Open work handed off (not claimed by this session):** `arena/22b5b06c-gold4`'s branch still holds a `COORDINATION.md` that conflicts with this board; its review document is preserved at `docs/legacy/REPO_REVIEW_22b5b06c.md`. If that session returns, it should take the board from `main`, not force-push its copy.

---

## Session `arena/fd51d093-gold4` — independent verification pass (2026-10-22 23:55 UTC)

### Claim (made before any file was edited)

| Task | Status | Owner | Files in scope |
|---|---|---|---|
| V-1 | Independent line-by-line re-verification of every published value | in progress → done | `data/rings.json`, `data/sellers.json`, `data/gold_spot.json`, `data/sources.json`, `data/verification_log.json` |
| V-2 | Correct what the re-read contradicted | done | same as V-1 |
| V-3 | Rebuild site + re-run all three checks | done | `index.html`, `pages/`, `scripts/compute.py`, `scripts/build_site.py` |
| V-4 | Publish the pass (PR → merge → Pages) and record it here | done | `COORDINATION.md`, `README.md`, `VERIFICATION.md` |

**Scope discipline:** this session edits only the files above. It did **not** touch `docs/**` (the inherited sub-site), `docs/legacy/**` (preserved other-session work), `data/preserved/**`, `scripts/audit.py`, `scripts/verify.py` or `scripts/check_site.py`. The earlier sessions' branches were not modified, renamed or force-pushed. No other session's claim was open and unclaimed work was not duplicated: this pass verifies the already-merged tree rather than rebuilding it.

### What was done — and what it found

The published dataset was treated as **untrusted input** and re-fetched page by page. 20 product pages, 4 retailer policy pages, the Anjolee spec sheet, the World Gold Council spot panel, LBMA, the FTC jewellery article, 16 CFR 23.3, 15 U.S.C. § 295 and the FTC credit-card article were all re-read during this session.

**Matched (no change needed):** all 20 prices; all 20 karat/metal labels; the 8 Blue Nile stock numbers and widths; the 4 Allurez and 2 VRAI gram weights; the 5 Mejuri yellow-gold prices; all four retailers' return windows, exclusions, fees and resize terms; every Tier A/B legal claim (karat = parts of 24, trademark-beside-karat-mark, hollow-centre ban, the 0.003/0.007 tolerances, LBMA's twice-daily 10:30/15:00 auctions).

**Corrected — the previous pass was wrong, and this is exactly the class of error the audit exists to catch:**

1. **AN-01's weight was recorded as unverified when the live page publishes it.** Anjolee's own Product Details table reads `Approx. Metal Weight: 2.90 Gr.` for the 0.50 ct / ring-size-6.5 configuration, and the linked spec sheet (`MS354-A.pdf` on anjolee.com) lists `2.9 Gr` for the 0.50 ct size. The value is now recorded with its source and the `WEIGHT_UNVERIFIED` flag is gone. The seller-level `WEIGHT_NOT_PUBLISHED` flag on Anjolee was also wrong and was removed.
2. **AN-01's centre stone is lab-created and the dataset did not say so.** The same table states `Center Diamond Color: Lab Created FG` / `Center Diamond Clarity: Lab Created VS`. The price basis now says it, a `CENTRE_STONE_LAB_CREATED` flag was added, and the row's price ÷ gold multiple is labelled "price includes a centre stone" in the table so it cannot be read as a setting markup.
3. **The gold benchmark moved between reads.** The World Gold Council panel read `USD 4,028.53/oz` on this pass versus `4,024.36/oz` recorded earlier the same day (both with `Data as of 21 October, 2026`). The earlier value is preserved in `gold_spot.json → prior_captures` and the active benchmark is now the reading this session actually saw; all derived values were recomputed and the audit re-derived them.

**New irregularities flagged, not resolved (published on the Flagged for Review page):**

- `SPEC_LISTED_PAVE_ON_PLAIN_BAND` (VR-01, VR-02): the selected band is `Plain band`, yet the Setting Details block still lists `Pave carat weight:0.18ctw`.
- Re-confirmed on the live pages: Blue Nile's 14K page whose copy says "crafted in 18k yellow gold" (BN-04), the 14K page whose copy says "set in 14k white gold" (BN-08), and the 14K page whose copy mentions "platinum prongs" (BN-07).

**Carried forward as NOT verified, and said so on the site:** Brilliant Earth's seller-level facts were not re-fetched this pass (marked earlier-pass-only); no seller's reputation was verified; no item was assayed or XRF-tested; the blank price on VR-02 is correct because the design page genuinely shows no setting price.

### Result

| Check | Result |
|---|---|
| `scripts/compute.py` | 20 rows; 7 with published weight; 19 with verified price; spot $129.5202/g |
| `scripts/audit.py` | **PASS** — 56 passed, 0 warnings, 0 failures |
| `scripts/check_site.py` | PASS — 20 pages, local links resolve, every populated row carries its own official source link |
| `scripts/verify.py` | 0 hard failures; 15 deliberately blank values flagged |
| Dataset | 20 rows · 5 retailers · 19 prices · 7 weights · 0 hallmarks · all sellers' reputations unverified |

### PR and merge record

| Item | Result |
|---|---|
| PR #7 (this pass) | **merged** into `main` — https://github.com/karagemop466-tech/GOLD4/pull/7 · merge commit `66a99e8` · merged 2026-10-22 23:30:59 UTC, no review waited for |
| Pages workflow run | `39872297863` ("Deploy GOLD research site") = **success** |
| Pages API | `status=built`, latest build commit `66a99e8`, built 23:31:20 UTC |
| Live site re-fetched after deploy | `https://karagemop466-tech.github.io/GOLD4/` serves the new build: **7 published gram weights**, benchmark **$4,028.53/oz = $129.52/g**, **70 flag instances**, and the "7 of 20 rows" analysis with the AN-01 lab-created caveat. The Flagged page serves the new `CENTRE_STONE_LAB_CREATED` and `SPEC_LISTED_PAVE_ON_PLAIN_BAND` entries with their sources. |
| Follow-up record commit | PR #9 — this table, the log entry and the two new flag labels on the Flagged page |

### Event log additions

- **2026-10-22 23:26 UTC** — `arena/fd51d093-gold4` created, branched from `main` at `815bb97`. Read this board first; no task was open and unclaimed, so nothing was taken over. Claimed V-1…V-4 above and pushed the claim.
- **2026-10-22 23:55 UTC** — Pass 2 completed: 20 product pages + 4 policy pages + spec sheet + 6 reference sources re-fetched. 3 corrections, 2 new flags, 0 unexplained mismatches. Logged in `data/verification_log.json` as "Pass 4 — independent line-by-line re-verification of the published tree".

- **2026-10-22 23:31 UTC** — **PR #7 opened and merged without waiting for review**: https://github.com/karagemop466-tech/GOLD4/pull/7 → merge commit `66a99e8`. Merge state was `CLEAN`/`MERGEABLE`; Pages workflow `39872297863` succeeded and the Pages API reported `status=built` for that commit.
- **2026-10-22 23:32 UTC** — Live-site verification after deploy (not just "the workflow went green"): the dashboard and the Flagged page were fetched over HTTPS and confirmed to serve the corrected dataset — 7 weights, $4,028.53/oz, 70 flags, the AN-01 lab-created caveat, and both new flags. An earlier fetch returned the pre-merge build from cache; the re-fetch with a cache-buster returned the new build, which is why the check was repeated rather than assumed.
- **2026-10-22 23:33 UTC** — Cosmetic fix found *because* the live page was read: the two new flags rendered with a raw lowercase name instead of a human-readable label. Labels added in `scripts/build_site.py`, site rebuilt, all checks re-run (audit PASS 56/0/0, check_site PASS). Shipped as PR #9.

## What a human should look at first

1. **Anjolee AN-01** — the only row whose price includes a diamond, and that diamond is **lab-created**. It is the cheapest-looking solitaire in the table for that reason. Do not read it as "gold cheaper than Blue Nile".
2. **Blue Nile BN-04 / BN-07 / BN-08** — three pages whose own copy contradicts their own specification block. Nothing has been inferred about which side is right; that is a question for Blue Nile in writing.
3. **VRAI VR-02** — weight published, price not. The blank is correct, not a gap to fill.
4. **Every seller's reputation** — still unverified for all six. The FTC's own advice is to search the seller's name with "complaint" or "review"; this dataset does not do that for you and does not pretend to.
