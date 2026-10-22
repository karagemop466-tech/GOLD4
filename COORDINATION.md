# COORDINATION — GOLD4 shared task board
Session ID: arena/93da71b4-gold4 (this session) | Branch: arena/93da71b4-gold4 (fixed by Arena — do not rename/switch)
Rule: Before starting a task, claim it here, commit+push immediately. Never edit another session's claimed files; log requests here instead.
No-hallucination rule: every value needs an official-source link + retrieval date. Unconfirmable = blank + "UNVERIFIED" flag on Flagged for Review page. Prices are NEVER inferred/estimated.

| # | Task | Status | Owner | Files in scope |
|---|------|--------|-------|----------------|
| 1 | Coordination + repo review | done | arena/93da71b4 | COORDINATION.md, README.md |
| 2 | Official-source research | done (sources linked; values unverifiable from sandbox, flagged) | arena/93da71b4 | data/sources, data/rings.json |
| 3 | Calculator | done | arena/93da71b4 | docs/calculator.html |
| 4 | Pages site + tables | done | arena/93da71b4 | docs/** |
| 5 | Hallucination audit | done | arena/93da71b4 | scripts/verify.py, AUDIT.md |
| 6 | Integration + PR + merge + Pages | in progress | arena/93da71b4 | all (integration) |

Handoff rule: claim >60 min with no commits may be taken over; log handoff here.
Log:
- 2026-10-22: Session arena/93da71b4 claimed tasks 1-2, starting repo review (repo was empty except "# GOLD4" README).
- 2026-10-22: Tasks 3-5 done by arena/93da71b4 — site (8 pages), calculator, data/rings.json (8 candidates, all price/weight/karat blank=UNVERIFIED), audit script PASS (0 hard failures, 24 by-design flags). Irregularity: sandbox cannot reach retailer/FTC/LBMA/NIST sites -> F1-F6 on Flagged page, do not block merge.
- 2026-10-22: Task 6 integration claimed by arena/93da71b4 (final integration session): re-verified combined data line-by-line vs data/rings.json, audit re-run, PR arena->main then merge, enable Pages via workflow.
