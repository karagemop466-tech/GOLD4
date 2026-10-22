# Coordination board

Session identifier: `arena/b4413b13-gold4` (Arena did not expose a separate session ID).

| Task | Status | Owner | File scope |
|---|---|---|---|
| Review repository and build gold-ring research dashboard with explicit no-hallucination controls | done | arena/b4413b13-gold4 | COORDINATION.md, README.md, index.html, styles.css, app.js, flagged.html, scripts/check_site.py, .github/workflows/pages.yml |

## Verification log

- Repository started with only a seven-character README and no existing task board or product data. No other tasks/sessions were recorded, so no conflict detected.
- Product prices, products, seller claims, ring weights, and gold spot quotes are intentionally not fabricated or prefilled. Values require source links; unknowns stay blank and are flagged.
- Primary reference: FTC consumer guidance, https://consumer.ftc.gov/articles/buying-platinum-gold-and-silver-jewelry (retrieved 2026-10-22). Confirms karat quality mark, distinction between solid/hollow and plated/filled/overlay/vermeil terminology.
- All site content is a checklist/calculator/template, not a verified product catalog. Independent inspection and return-policy recommendations are presented as user safety checks, not claims that a particular seller/product passed.
- Implemented root-level static dashboard, Flagged for Review page, theoretical fine-gold content calculator, FTC-linked checklist, and GitHub Pages Actions deployment workflow. Added `scripts/check_site.py` as an offline regression gate against broken local links, missing source links, accidental product rows, and removal of the no-hallucination warning.
- Verification run: `python3 scripts/check_site.py` passed; `git diff --check` passed; Python HTML parser passed for both pages. The checker explicitly does not claim to verify source availability/product authenticity/live prices.

## Irregularities / limitations

- No official product listings, current gold-price source, or product data were present in the repository. Accordingly the verified-product table is empty. No current market price is asserted.
- This session's branch is fixed by Arena policy; separate per-task branches/worktrees and other-session coordination cannot be performed here. Changes are scoped to this branch.
- GitHub Pages publishing and PR/merge require repository permissions and a deploy configuration check; do not represent the site as published until confirmed.
