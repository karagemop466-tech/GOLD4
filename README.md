# GOLD — Gold engagement ring research

**NO HALLUCINATIONS (top rule):** no invented products, prices, spot quotes, weights, seller claims, or return terms. Every value needs an official-source link + retrieval date; unconfirmed fields stay blank and are flagged for review. Run the hallucination checks after every review: `python3 scripts/check_site.py && python3 scripts/verify.py`.

## Site (GitHub Pages, repo root + extended sub-site)
- `index.html` / `flagged.html` (by session arena/b4413b13) — dashboard, empty verified-candidate table, buyer checklist, gold-content calculator, FTC reference.
- `docs/` (by session arena/93da71b4) — extended dashboard: `docs/index.html` landing with NO-HALLUCINATIONS top summary, `checklist.html`, `rings.html` (8 official-retailer candidates, all price/weight/karat blank=UNVERIFIED), `calculator.html` (karat × grams × user-entered dated spot → pure-gold grams + melt value), `sellers.html`, `sources.html`, `flagged.html`, `verification.html`.
- Data: `data/rings.json` · Audits: `scripts/check_site.py`, `scripts/verify.py`, `AUDIT.md` · Coordination: `COORDINATION.md`.

## Evidence
FTC: https://consumer.ftc.gov/articles/buying-platinum-gold-and-silver-jewelry (retrieved 2026-10-22) explains karat marks and solid vs plated/vermeil/filled terminology. NIST SP 811 defines 1 troy oz = 31.1034768 g. LBMA/Kitco linked for spot (none published here — it would go stale). Formula: pure gold g = weight × karat/24; melt = pure g / 31.1034768 × spot. A 14K/18K stamp alone does not prove purity — reputable seller + hallmark & maker's mark + price-vs-melt sanity + independent XRF test after delivery.
