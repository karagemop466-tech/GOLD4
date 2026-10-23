# COORDINATION.md — Shared Task Board

Project: GOLD4 — Gold Engagement Ring research, verification, and GitHub Pages site.
Session ID convention: each working session records its ID below. Claims must be committed and pushed immediately.

**Active session:** `arena-22b5b06c-gold4` (branch `arena/22b5b06c-gold4`, per Arena session policy this session does all work on its fixed branch rather than `session-<id>/<task>` branches; this is logged here as the coordination record).

## Ground rules (from project owner)
- NO HALLUCINATIONS. Every price/value must be read directly from an official source page at collection time, with the URL recorded. If a value cannot be confirmed from an official source, leave it blank and flag it as UNVERIFIED. Never infer or fill in values.
- Verification passes run after every review; hallucination checks are run and flagged.
- "needs review" status = published on the Flagged for Review page; does not block.
- Shared outputs (combined table data, site index/nav) are finalized by the integration session after all tasks are done.

## Task board

| # | Task | Status | Owner (session) | Files touched |
|---|------|--------|-----------------|---------------|
| 1 | Repo review (baseline audit of existing files) | done | arena-22b5b06c-gold4 | REPO_REVIEW.md |
| 2 | Collect ring listings w/ prices from official retailer pages | done (19 rows; 10 rows Level B flagged for live re-check due to fetch outage) | arena-22b5b06c-gold4 | data/rings.json |
| 3 | Collect current gold spot price from trusted source | done (single source; cross-check flagged pending) | arena-22b5b06c-gold4 | data/gold_spot.json |
| 4 | Build GH Pages site (landing, categories, calculator, flagged page) | done | arena-22b5b06c-gold4 | index.html, pages/*, assets/*, scripts/build_site.py |
| 5 | Verification pass: line-by-line re-check of every row vs source URL | done (Pass 1–3 logged; Level B re-check pending fetch-service recovery) | arena-22b5b06c-gold4 | VERIFICATION.md |
| 6 | Hallucination/security check script + run | done (PASS_WITH_WARNINGS: 0 errors, 33 flags published) | arena-22b5b06c-gold4 | scripts/verify_data.py, reports/verification_report.json |
| 7 | Integration: PR to main, merge, enable + confirm GH Pages deploy | in progress | arena-22b5b06c-gold4 | COORDINATION.md |

## Completion records (sources & verification)
- Task 1: sources = local git inspection (commit 7f442a1). Irregularities: none pre-existing (empty repo). Logged in REPO_REVIEW.md.
- Task 2: sources = live fetches of bluenile.com product/category pages (23:13–23:19Z) and dated official-page snapshots for 10 rows (flagged). All URLs on each row in data/rings.json. Verification = scripts/verify_data.py PASS (0 errors). Irregularities: James Allen merged into Blue Nile (official notice); one style sold out → price left blank; retailer pages publish no gram weights → all weight cells blank+flagged.
- Task 3: source = https://api.gold-api.com/price/XAU fetched ~23:17Z: $4,028.10/oz, source-reported update 2026-10-22T23:01:42Z. Cross-check (Kitco/LBMA) pending due to fetch outage → flagged.
- Task 4: site built by scripts/build_site.py from data/ only; check_links.py: 0 broken local links (305 checked).
- Task 5/6: full line-by-line log in VERIFICATION.md; machine report in reports/verification_report.json; 33 flags published on pages/flagged.html.

## Claim log (continued)
- 2026-10-22 23:30Z — arena-22b5b06c-gold4 claims Tasks 2–7 (no other session activity on the board; scopes are this session's files only).

## Notes
- No other sessions have claimed tasks at the time of writing (board was created fresh by this session).
- This session will claim subsequent tasks by updating this file and committing before starting each one.
- 2026-10-22 23:20–23:30Z — fetch-service outage (page-fetch proxy returning signature errors). Level B rows recorded from dated official snapshots instead; all flagged for live re-confirmation on pages/flagged.html. Retries ongoing this session.
