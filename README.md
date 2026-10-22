# GOLD4 — gold engagement-ring verification desk

A small, auditable dataset of **solid-gold engagement rings** with retailer prices, published gram weights, computed gold content and every unverified value published as *blank* instead of guessed.

**Live site:** https://karagemop466-tech.github.io/GOLD4/

---

## ⚠ No hallucination rule (read before trusting anything here)

> **Every price, weight, karat, policy and link in this repository was read from the official page linked beside it, during this project.**
> If a value could not be read from an official source it is **left blank** and flagged as `UNVERIFIED` on the [Flagged for Review](https://karagemop466-tech.github.io/GOLD4/pages/flagged.html) page.
> Nothing is estimated, averaged, inferred from photographs, or copied from a blog, marketplace, resale listing or price-comparison site.
> Derived numbers (gold grams, gold value, price ÷ gold) are arithmetic on published inputs at a frozen, dated spot price — and an automated audit re-derives every one of them on every pass.

This rule is repeated at the top of every page of the site, and enforced by `scripts/audit.py`, which fails the build on a missing source, a non-official domain, a blank value without a flag, or a derived number that does not re-derive from its inputs.

When reviewing anything in this repo, **ask of each value: where is the official source, and what date was it read?** If the answer is missing, the value does not belong here.

---

## What is in the repository

| Path | What it is |
|---|---|
| `index.html`, `pages/*.html` | The published dashboard and its subpages (generated — do not hand-edit) |
| `assets/style.css`, `assets/app.js` | Styling and the client-side gold calculator / table filter |
| `data/rings.json` | The dataset: 20 rings, each with price, weight, sources, verification level and flags |
| `data/sellers.json` | Seller-level facts: return window, exclusions, resize terms, warranty, contact |
| `data/sources.json` | The 13 registered sources with tier, retrieval date and what each one supports |
| `data/methodology.json` | Karat table, 15 U.S.C. § 295 tolerances, formulas, assumptions, verification levels |
| `data/gold_spot.json` | The frozen gold benchmark: **$4,024.36/oz, 21 Oct 2026** (World Gold Council) |
| `data/derived.json` | Computed gold content / value / multiples (generated) |
| `data/verification_log.json` | The verification passes rendered on the site's Log page |
| `VERIFICATION.md` | Line-by-line verification record (generated from the JSON) |
| `reports/audit_latest.txt` | Latest integrity-audit output |
| `COORDINATION.md` | Shared task board for the agent sessions working in this repo |
| `scripts/` | `compute.py`, `build_site.py`, `audit.py`, `gen_verification.py` |

## Reproduce / re-verify

```bash
python3 scripts/compute.py        # derived gold values from published inputs
python3 scripts/build_site.py     # regenerate the static site
python3 scripts/gen_verification.py
python3 scripts/audit.py          # hallucination + integrity audit; non-zero exit on failure
```

No third-party dependencies, no network access required to build. Python 3.10+.

## What the data currently shows

| Metric | Value |
|---|---|
| Rings tracked | 20 |
| Retailers with product rows | 5 (Blue Nile, Allurez, VRAI, Mejuri, Anjolee) |
| Prices read from the retailer's own page | 19 of 20 (1 deliberately blank) |
| Gram weights published by the retailer | 7 of 20 — only these rows have a computable gold value |
| Rows with explicit *solid gold* wording | 5 of 20 (all Mejuri) |
| Rows publishing a hallmark / maker's mark | **0 of 20** — it can only be checked in your hand |
| Gold benchmark used | $4,024.36/oz = $129.3862/g, 21 Oct 2026 |
| Flags raised for review | published on the Flagged page, with sources |
| Pass-3 re-verification (2026-10-22) | every row re-fetched from its official page: 19/19 prices and 7/7 weights re-read and matched; 0 disagreements; see the Log page |

**Headline findings**

1. A stamp is a claim with a legal tolerance, not a measurement: under 15 U.S.C. § 295 an "18K" ring may be as low as 74.3% gold and a "14K" ring as low as 57.63%.
2. Most major retailers do not publish a gram weight, so their rings cannot be priced against their own gold. Only Allurez, VRAI and Anjolee did in this pass (Anjolee's 2.90 g was recovered on the pass-3 re-verification).
3. The 18K premium is inconsistent: +15.5% (Blue Nile Petite Solitaire), +40.1% (Blue Nile Comfort Fit), +68.0% (Allurez Split Shank) — and for the one pair with both weights published, 54.9% of that premium is simply more gold.
4. Return windows all look like "30 days", but exclusions differ sharply (resized, engraved, custom). One seller (Anjolee) explicitly accepts returns on customised orders; another (Allurez) makes custom orders non-refundable.
5. Several retailer pages contradict their own specification blocks; each case is listed on the Flagged page.

## Sources

- **Tier A — government/regulator:** FTC consumer guidance on jewellery; 16 CFR Part 23 (§ 23.3); 15 U.S.C. § 295 and ch. 8; FTC credit-card dispute guidance.
- **Tier B — market benchmark:** World Gold Council gold spot; LBMA benchmark description.
- **Tier C — retailer's own site:** 20 product pages plus return-policy pages from Blue Nile, Allurez, VRAI, Mejuri, Brilliant Earth and Anjolee.

The full registry, with what each source supports, is in `data/sources.json` and on the site's Sources page.

---

## Parallel sessions and preserved artifacts

Several agent sessions worked in this repository. `main` already contained two of their merges when this session integrated. **Nothing was deleted**: their work is either kept in place or preserved verbatim under `docs/legacy/` and `data/preserved/`.

| Artifact | Origin | Status |
|---|---|---|
| `docs/**` sub-site (checklist, candidates, calculator, sellers, sources, flagged, verification) | session `arena/93da71b4-gold4` (PR #2) | Kept unmodified except for a banner marking it as a pre-data snapshot; still published under `/docs/` |
| `data/preserved/candidates_unverified_93da71b4.json` | same session | Preserved worksheet (R01–R08, all values null by design); **not** the canonical dataset |
| `styles.css`, `app.js`, `flagged.html`, `scripts/check_site.py`, `.github/workflows/pages.yml` | session `arena/b4413b13-gold4` (PR #1, #3) | Kept; `flagged.html` carries a "superseded" banner, the checker was extended for the populated catalog |
| `scripts/verify.py`, `AUDIT.md` | session `arena/93da71b4-gold4` | Kept and made schema-aware; still runs and still fails on an unsourced value |
| `docs/legacy/index_placeholder_b4413b13.html` | session `arena/b4413b13-gold4` | Original root dashboard, preserved after the integrated dashboard replaced it |
| `docs/legacy/COORDINATION_merged_before_9614479d.md`, `docs/legacy/README_before_9614479d.md` | pre-merge state of `main` | Preserved for audit |

Three checkers now run against the combined repository, and all three must pass before a merge:

```bash
python3 scripts/check_site.py   # links + per-row source links + FTC/no-hallucination presence
python3 scripts/verify.py       # schema-aware data audit, rewrites AUDIT.md
python3 scripts/audit.py        # deep audit: allow-list, recomputation, speculation scan
```

The earlier sessions' own records (including the note that their sandboxes had no outbound access, which is why their catalogs were empty) are preserved in `COORDINATION.md` and in the site's Log page.

## Limitations (stated, not hidden)

- Prices are a snapshot: 22 October 2026. Retail prices move; re-check the source link before buying.
- Weights are the seller's own numbers, sometimes labelled "approximate", and are quoted for a single ring size.
- Gold value is melt-value arithmetic, not an appraisal and not a resale offer.
- Reputation was **not** verified for any seller; no review or complaint data was collected.
- No XRF or assay result exists for any item — that is the point of the on-arrival step in the checklist.
- Brilliant Earth appears only at seller-policy level: its product price and weight could not be read, so no product row or price is published.

## Coordination

Several agent sessions have worked in this repository. The shared task board, claims, hand-offs and the integration record live in [`COORDINATION.md`](COORDINATION.md), and the published summary is on the site's Log page. Shared output files (`index.html`, `pages/`, `data/`) are owned by the integration session; other sessions' branches were left untouched.

## Disclaimer

Research, not financial, legal or gemmological advice. Independently verify any ring — purity, weight and hallmark — with a qualified jeweller before relying on it.
