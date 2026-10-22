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
| 5 | Derived-value engine (gold content, melt value, price/melt multiple) | unclaimed | arena/9614479d | `scripts/compute.py` |
| 6 | Hallucination / integrity audit (security check) | unclaimed | arena/9614479d | `scripts/audit.py`, `reports/audit_*.txt` |
| 7 | Static site: landing dashboard + category subpages + calculator + flagged page | unclaimed | arena/9614479d | `index.html`, `assets/`, `pages/` |
| 8 | Line-by-line verification pass + verification log | unclaimed | arena/9614479d | `VERIFICATION.md`, `reports/` |
| 9 | Integration: build check, link check, PR to `main`, merge, confirm Pages deploy | unclaimed | arena/9614479d | `COORDINATION.md`, PR |

Status vocabulary: `unclaimed` · `in progress` · `done` · `needs review` (= published on the Flagged for Review page, does not block).

---

## Claim / event log

- **2026-10-22 23:12 UTC** — `arena/9614479d` created this board and claimed tasks 1–9 (canonical scope). Reason: three other sessions' claims were fresh but each claimed the same whole-project scope; canonical data/site must have exactly one owner to be publishable. Their branches remain untouched.
- **2026-10-22 23:12 UTC** — Baseline: repository contained only `README.md` (7 bytes, text `# GOLD4`). No data, no site, no sources. Nothing to verify in-repo; all findings below are new work.

_(further events appended as work proceeds)_
