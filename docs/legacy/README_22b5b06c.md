# GOLD4 — Gold Engagement Ring Research Dashboard

🚫 **NO HALLUCINATIONS:** every price/spec in this repo was read directly from an official retailer source page (Blue Nile, James Allen→Blue Nile, Brilliant Earth) or an official price API, and is stored with its source URL and UTC verification timestamp. Values that could not be confirmed are left **blank** and flagged — never guessed. See [VERIFICATION.md](VERIFICATION.md) and the site's **Flagged for Review** page.

**Live site (GitHub Pages):** https://karagemop466-tech.github.io/GOLD4/

## What's here
| Path | Purpose |
|------|---------|
| `index.html`, `pages/` | Static dashboard site (landing, category tables, calculator, sellers, checklist, methodology, flagged) |
| `data/rings.json` | All ring entries with source URLs, prices, timestamps, verification levels, flags |
| `data/gold_spot.json` | Verified gold spot snapshot (source + timestamps) |
| `scripts/verify_data.py` | Automated anti-hallucination / schema / consistency checks |
| `scripts/build_site.py` | Regenerates the whole site from `data/` (no hand-typed numbers in HTML) |
| `scripts/check_links.py` | Local link-integrity check before publish |
| `reports/verification_report.json` | Latest machine-readable check results |
| [VERIFICATION.md](VERIFICATION.md) | Line-by-line verification log |
| [REPO_REVIEW.md](REPO_REVIEW.md) | Baseline repo audit |
| [COORDINATION.md](COORDINATION.md) | Multi-session task board & claims |

## Buying checklist (short form)
Confirm karat · insist on **solid gold** (not plated/vermeil/gold-filled) · hallmark + maker's mark · weight in grams · seller reputation & real contacts · price vs gold content (unusually cheap = red flag) · return policy (incl. resized/custom exclusions) · pay by credit card · keep documentation · independent jeweler + **XRF test** on arrival · if the seller blocks verification/returns — don't buy. Full checklist on the site.

## Re-verify anytime
```bash
python3 scripts/verify_data.py   # anti-hallucination checks
python3 scripts/build_site.py    # rebuild site from data
python3 scripts/check_links.py   # link integrity
```

Data collected 2026-10-22 (UTC). Prices are point-in-time — always re-check the seller's live page before buying.
