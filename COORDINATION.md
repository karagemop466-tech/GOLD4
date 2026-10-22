# COORDINATION.md — GOLD4 Shared Multi-Session Task Board

**Project:** `karagemop466-tech/GOLD4` — Gold Engagement Ring Research, Line-by-Line Verification, Anti-Hallucination Audit, Melt Calculator, and GitHub Pages Dashboard.  
**Date:** `2026-10-22` (UTC)

> **CRITICAL NO-HALLUCINATIONS RULE:**  
> Every single product listing, price, gold karat purity, solid-gold claim, gram weight, hallmark disclosure, return policy, and spot gold benchmark MUST be verified directly against an official trusted source URL retrieved on `2026-10-22`. If any field (such as ring gram weight, exact hallmark stamp, or price) is omitted or cannot be confirmed from the official source page, it MUST be left blank (`null` / `—`) and flagged as `UNVERIFIED` on the **Flagged for Review** page (`flagged.html`). **Never infer, estimate, interpolate, or fabricate values.** Run security/hallucination checks after every review pass.

---

## Active Parallel Sessions Discovered on `karagemop466-tech/GOLD4`

Per Arena platform rules, each agent session works on its assigned session branch (`arena/<session-id>-gold4`) rather than creating separate local branch names. Inspection of all remote heads (`git fetch origin "+refs/heads/*:refs/remotes/origin/*"`) at `2026-10-22 23:13 UTC` identified **5 concurrent sessions** on this repository:

| Session Branch | First Claim (UTC) | Claimed File Scope (per session board) | Status |
|---|---|---|---|
| `arena/b4413b13-gold4` | `2026-10-22 23:11:14Z` | `COORDINATION.md`, `README.md`, `index.html`, `styles.css`, `app.js`, `.github/workflows/pages.yml` | active (<60 min) |
| `arena/93da71b4-gold4` | `2026-10-22 23:11:31Z` | `COORDINATION.md`, `README.md`, `data/sources.md`, `data/rings.json`, `docs/**`, `.github/workflows/pages.yml`, `scripts/verify.py` | active (<60 min) |
| `arena/22b5b06c-gold4` | `2026-10-22 23:12:00Z` | `REPO_REVIEW.md`, `data/rings.json`, `data/gold_spot.json`, `index.html`, `pages/*`, `assets/*`, `VERIFICATION.md`, `scripts/verify_data.py` | active (<60 min) |
| `arena/9614479d-gold4` | `2026-10-22 23:12:46Z` | `COORDINATION.md`, `data/sources.json`, `data/methodology.json`, `data/gold_spot.json`, `data/rings.json`, `scripts/compute.py`, `scripts/audit.py`, `reports/*`, `index.html`, `assets/`, `pages/`, `VERIFICATION.md` | active (<60 min) |
| `arena/a0be79d4-gold4` (**this session**) | `2026-10-22 23:13:30Z` | **Non-overlapping primary scope:** `AUDIT_AND_REPO_REVIEW.md`, `data/catalog_a0be79d4.json`, `data/combined_verified_master.json`, `data/audit_a0be79d4.json`, `scripts/verify_a0be79d4.py`, `static/gold4.css`, `static/gold4.js`, `solitaires.html`, `bands.html`, `three-stone-halo.html`, `calculator.html`, `checklist.html`, `sellers.html`, `standards.html`, `audit.html`, `flagged.html`, `coordination.html` + **Final Integration pass** (`index.html`, `README.md`, `.nojekyll`, `.github/workflows/pages.yml`, `COORDINATION.md`) | **in progress** |

### Cross-Session Scope & Conflict-Avoidance Protocol
1. **Zero takeover of fresh claims:** All four sibling claims are `<60 minutes` old, so none are taken over prematurely.
2. **Strict non-overlapping task files:** `arena/a0be79d4-gold4` writes all primary data, audit logic, stylesheets, scripts, and category pages exclusively into non-colliding file paths listed above so zero sibling files (`REPO_REVIEW.md`, `VERIFICATION.md`, `data/rings.json`, `data/gold_spot.json`, `data/sources.*`, `pages/*`, `docs/*`, `assets/*`, `styles.css`, `app.js`, `scripts/verify*.py`, `scripts/audit.py`, `scripts/compute.py`, `reports/*`) are overwritten or discarded.
3. **Cross-session requests logged here (per coordination rules):**
   - Request to `arena/b4413b13-gold4`, `arena/93da71b4-gold4`, `arena/22b5b06c-gold4`, `arena/9614479d-gold4`: when publishing shared root outputs (`index.html`, `.github/workflows/pages.yml`), ensure root static pages and sibling artifacts (`pages/`, `docs/`, `reports/`) all remain reachable without broken links.
4. **Non-destructive Final Integration commitment:** Before opening and merging the final integration PR from `arena/a0be79d4-gold4` to `main`, this session runs `git pull --rebase origin main` / merges `origin/main` (preserving every single file committed by earlier-merging sessions without discarding their work), re-verifies **all** combined rows (including sibling `data/rings.json` / `data/gold_spot.json`) line-by-line using `scripts/verify_a0be79d4.py`, flags any unverified or conflicting items on `flagged.html`, confirms zero broken links, deploys cleanly to GitHub Pages, and records the PR URL + merge result here.

---

## Task Board (`arena/a0be79d4-gold4` Scope + Shared Integration Milestones)

| ID | Task | Status | Owner | Files Touched |
|---|---|---|---|---|
| T1 | Coordination board creation & multi-session discovery | `done` | `arena/a0be79d4-gold4` | `COORDINATION.md` |
| T2 | Baseline repository line-by-line review & irregularity check | `in progress` | `arena/a0be79d4-gold4` | `AUDIT_AND_REPO_REVIEW.md` |
| T3 | Official regulatory, testing, & live spot gold benchmark verification (`2026-10-22`) | `in progress` | `arena/a0be79d4-gold4` | `data/catalog_a0be79d4.json` |
| T4 | Official solid-gold engagement ring & wedding band catalog verification across trusted jewelers (line-by-line, blank + `UNVERIFIED` when omitted) | `in progress` | `arena/a0be79d4-gold4` | `data/catalog_a0be79d4.json` |
| T5 | Multi-pass anti-hallucination & security verification engine (runs after every review pass + inspects sibling data) | `unclaimed -> claimed` (`in progress`) | `arena/a0be79d4-gold4` | `scripts/verify_a0be79d4.py`, `data/audit_a0be79d4.json` |
| T6 | Clean multi-page dashboard UI: landing summary + category subpages + live gold/wt melt calculator + Flagged for Review page | `in progress` | `arena/a0be79d4-gold4` | `static/gold4.css`, `static/gold4.js`, `solitaires.html`, `bands.html`, `three-stone-halo.html`, `calculator.html`, `checklist.html`, `sellers.html`, `standards.html`, `audit.html`, `flagged.html`, `coordination.html` |
| T7 | Final Integration: merge `origin/main` non-destructively, re-verify combined data line-by-line, build/link check, PR -> `main`, merge, verify live GitHub Pages deployment | `in progress` | `arena/a0be79d4-gold4` | `index.html`, `data/combined_verified_master.json`, `.nojekyll`, `.github/workflows/pages.yml`, `README.md`, `COORDINATION.md` |

---

## Coordination & Verification Log

- **`2026-10-22T23:13:30Z` — Claim committed (`arena/a0be79d4-gold4`):** Read repository root (`README.md`, 7 bytes: `# GOLD4`, SHA `7f442a1b62b797fc04a079ad1ddd2d789e13a5c6`). Inspected all remote branches on `karagemop466-tech/GOLD4`; detected parallel sessions `arena/b4413b13-gold4`, `arena/93da71b4-gold4`, `arena/22b5b06c-gold4`, and `arena/9614479d-gold4`. Registered strict non-overlapping file scope and pushed claim immediately.
