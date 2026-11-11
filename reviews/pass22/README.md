# Pass 22 — raw live evidence (placeholder)

`evidence/` is written by `.github/workflows/pass22-live-sweep.yml`, which runs
`scripts/live_source_check.py` on a GitHub runner with open internet and commits
the raw artifact back to this branch **unchanged**.

Rules for anything in this directory:

- It is **evidence**, not a dataset change. No value is applied from it by the
  workflow.
- A page that returns 403/404 or a JavaScript shell yields **no** statement about
  a price.
- A price the page prints differently is reported as a disagreement and is
  published as such; the stored value is not silently rewritten.

The reviewed findings, the reconciliation and the applied decisions live in
`../report.md` and `../observations.json`, written by the reviewing session.
