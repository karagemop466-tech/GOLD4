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
| 1 | Repo review (baseline audit of existing files) | in progress | arena-22b5b06c-gold4 | REPO_REVIEW.md |
| 2 | Collect ring listings w/ prices from official retailer pages | unclaimed | — | data/rings.json |
| 3 | Collect current gold spot price from trusted source | unclaimed | — | data/gold_spot.json |
| 4 | Build GH Pages site (landing, categories, calculator, flagged page) | unclaimed | — | index.html, pages/*, assets/* |
| 5 | Verification pass: line-by-line re-check of every row vs source URL | unclaimed | — | VERIFICATION.md |
| 6 | Hallucination/security check script + run | unclaimed | — | scripts/verify_data.py, VERIFICATION.md |
| 7 | Integration: PR to main, merge, enable + confirm GH Pages deploy | unclaimed | — | COORDINATION.md |

## Claim log
- 2026-10-22 — arena-22b5b06c-gold4 claims Task 1 (repo review). Scope: REPO_REVIEW.md. Committing claim now.

## Notes
- No other sessions have claimed tasks at the time of writing (board was created fresh by this session).
- This session will claim subsequent tasks by updating this file and committing before starting each one.
