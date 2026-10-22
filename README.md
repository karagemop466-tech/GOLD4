# GOLD4 — Verified Solid Gold Engagement Ring Research, Assay & Melt-Value Desk

- **Live GitHub Pages Application:** <https://karagemop466-tech.github.io/GOLD4/>
- **Verification Date:** `2026-10-22` (UTC)
- **Zero-Hallucination Policy:** **NO HALLUCINATIONS.** Every single price, karat purity, metal gram weight, live spot gold benchmark (`Kitco $4,024.60/oz = $129.39/g` & `JM Bullion $4,039.76/oz = $129.88/g`), return window, and statutory/gemological citation in this repository was verified line by line from live-fetched official primary sources (`HTTP 200 OK` on `2026-10-22`). Any unconfirmable or internally conflicting field is strictly left blank (`null` / `—`) and flagged `UNVERIFIED` on [`flagged.html`](https://karagemop466-tech.github.io/GOLD4/flagged.html). **Always check for hallucinations and re-run all three verification scripts after every edit or review.**

---

## Published Multi-Page Architecture

| Page | Purpose |
|---|---|
| [`index.html`](index.html) | Front-page Executive Summary, prominent **Zero-Hallucination Pledge**, dual `2026-10-22` spot strip, quick melt calculator, filterable 22-listing master catalog, & interactive 12-point checklist |
| [`solitaires.html`](solitaires.html) | Category 1 — Solitaire Engagement Rings & Mountings (`8` verified listings; setting-only vs complete ring & mixed 14K/Platinum prong head analysis) |
| [`three-stone-halo.html`](three-stone-halo.html) | Category 2 — Three-Stone, Halo & Pavé Engagement Rings (`4` listings; forensic breakdown of two live `$20,671` & `$2,858` `18K vs 14K` spec contradictions) |
| [`bands.html`](bands.html) | Category 3 — Solid Gold Engagement Bands, Eternity Rings & 24K Bullion Bands (`9` solid listings + disqualified vermeil control; `1.33×–1.50×` melt floor & Size-10 reference weight analysis) |
| [`calculator.html`](calculator.html) | Full Interactive Gold Karat, Net Metal Weight, Gemstone Deduction (`0.200 g/ct`), Pure 24K Mass, Raw Melt Value & Retail Markup Calculator + Live 5-Karat Comparison Matrix |
| [`checklist.html`](checklist.html) | Complete 12-Point Buyer Verification Checklist, Copy-Paste Pre-Purchase Written Inquiry Script, FTC Terminology Decoder & 48-Hour Post-Arrival XRF Assay Protocol |
| [`sellers.html`](sellers.html) | Verified Seller Reputation, Street Address, Return Clock (`7d` Menē, `20d` Catbird, `30d-from-shipment` Blue Nile) & Warranty Fee Audit Matrix |
| [`standards.html`](standards.html) | Federal Regulations (`FTC Guide`, `16 CFR Part 23`, `15 U.S.C. § 297`, `CFPB/FCBA`), `NIST SP 811` constants, & `GIA Gems & Gemology` EDXRF / Carlsbad fraud lab findings |
| [`flagged.html`](flagged.html) | **Flagged for Review Register** — All `12` critical/high/medium irregularities, live retailer spec conflicts, disqualified vermeil traps, caught `404` links, & all `42` blank `UNVERIFIED` cells |
| [`audit.html`](audit.html) | Multi-Pass Anti-Hallucination & Security Verification Log (Passes 1–4 + CI enforcement gates) |
| [`coordination.html`](coordination.html) | Multi-Session Git Coordination Ledger (`COORDINATION.md`) & Preserved Sibling Session Archive (`docs/index.html`) |

---

## Run All Three Automated Anti-Hallucination & Security Checks

```bash
python3 scripts/check_site.py
python3 scripts/verify.py
python3 scripts/verify_a0be79d4.py
```

All three verification gates run automatically on every push and pull request in [`.github/workflows/pages.yml`](.github/workflows/pages.yml).
