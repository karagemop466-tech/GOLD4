# GOLD — Gold engagement ring research

A source-first static dashboard for organizing gold engagement-ring candidates. The central rule is **no hallucinations**: no invented products, prices, spot quotes, weights, seller claims, or return terms. Unconfirmed fields remain blank and are flagged for review.

## Site

- `index.html` — dashboard, empty verified-candidate table, buyer checklist, gold-content calculator, and primary reference.
- `flagged.html` — research gaps and limitations.
- `styles.css`, `app.js` — presentation and browser-only calculator.

The gold-content formula is ring weight × karat ÷ 24. It is a theoretical fine-gold equivalent only, not an assay or valuation. Optional value calculation requires a separately verified price per gram and does not account for workmanship, gemstones, fees, or resale spreads.

## Evidence and verification

FTC consumer guidance is linked in the dashboard and review page: [Buying Platinum, Gold, and Silver Jewelry](https://consumer.ftc.gov/articles/buying-platinum-gold-and-silver-jewelry). It explains karat quality marks and gold terminology; it does not verify a particular product or retailer. No product listings or current prices were available to verify in the repository, so the product catalog is intentionally empty. Review date recorded: 2026-10-22.

Before adding a product row, record the dated official listing URL and only populate fields directly confirmed there. Flag absent, unclear, or conflicting evidence. Keep independent-review, official-listing, and physical-purity verification claims distinct. Recheck every row and link for hallucinations before publishing updates.

## GitHub Pages

The site is plain static HTML and can be served from the repository root. No build tools or third-party runtime dependencies are required. Publishing must be enabled in repository Pages settings (Deploy from a branch: `main`, `/ (root)`) unless an administrator configures a workflow. A pushed branch alone does not establish that GitHub Pages is live.
