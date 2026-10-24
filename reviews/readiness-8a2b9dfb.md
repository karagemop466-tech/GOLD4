# Requirement-readiness review — session 8a2b9dfb

**Product/FTC/GIA source reads:** 2026-10-23 UTC. **Additional Cornell LII statute-text read:** 2026-10-24 UTC (academic legal publisher). **Integration/testing:** 2026-10-24 UTC. **Branch:** `arena/8a2b9dfb-gold4`.

## No hallucinations: what this review does and does not establish

This is an evidence-completeness review and final integration of the existing candidate list, **not** certification of every product. It preserves the completed independent reviews and canonical integration from PRs [#49](https://github.com/karagemop466-tech/GOLD4/pull/49), [#51](https://github.com/karagemop466-tech/GOLD4/pull/51), [#52](https://github.com/karagemop466-tech/GOLD4/pull/52), [#53](https://github.com/karagemop466-tech/GOLD4/pull/53) and the owner's close-outs [#54](https://github.com/karagemop466-tech/GOLD4/pull/54), [#55](https://github.com/karagemop466-tech/GOLD4/pull/55) and [#56](https://github.com/karagemop466-tech/GOLD4/pull/56). Former owner PR [#47](https://github.com/karagemop466-tech/GOLD4/pull/47) closed unmerged; shared files were claimed only after the replacement owner's work merged/released.

- All **64 candidates / 10 retailers** are evaluated automatically. Seventeen have recorded literal solid-gold quotations and 17 have sourced, scoped historical gram weights. **Zero** have a complete pre-purchase evidence set.
- All **64 current exact-price cells remain blank**, not zero. A stored amount or matching schema.org price is not a size/stone-bound checkout quote. Historical amounts remain explicitly historical.
- Purity, a certificate, a product name and a status flag do not supply missing explicit solid wording. Neither karat nor maker marks establish measured purity or construction.
- Return-window integers do not establish cash-refund, custom/resized/engraved or testing eligibility. Absence of a recorded exclusion is not permission. These fields remain unverified.
- No independent reputation investigation, seller contact, purchase, card authorization or physical assay was performed. No ring is purchase-approved.
- **After every review, look for hallucinations again.** Automated tests reject defined failure cases; passing cannot prove every assertion true.

## Official sources actually opened

The remote reader succeeded on the product/FTC/GIA pages on **23 October**, before the post-midnight integration; the separately labelled LII statute read is **24 October**. Only the listed chunks were reviewed. Exact excerpts and limits are in [`source_observations.json`](../scripts/session_8a2b9dfb/source_observations.json).

| Official source | Reviewed chunks | Supports / limits |
|---|---|---|
| [FTC jewelry guidance](https://consumer.ftc.gov/articles/buying-platinum-gold-and-silver-jewelry) | 0 | Karat AND company-mark guidance; solid versus hollow/plated descriptions; seller research and written return policy. Not product authentication. |
| [Menē Knot Ring](https://mene.com/products/knot-ring-gold) | 0 | 24k Gold and Crafted-on-Demand. Reviewed product block did not supply explicit solid wording or selected-size grams. No exact quote inferred. |
| [Menē Etruscan Sun Band](https://mene.com/products/etruscan-sun-band-gold) | 0 | 24k Gold, Crafted-on-Demand and engraving option. No selected-size grams or final configured quote established. |
| [Menē returns index](https://mene.com/customer-care/en-US/articles/returns-319505) | 0 | Seven-day merchandise-credit route, not complete cash-refund/exclusion terms. Linked detailed help articles were not opened. |
| [Menē Terms of Service / Purchase](https://mene.com/terms-of-service) | 0–3 of 7 | Effective date Sep 2, 2026; weight/final-price variability; conditional refund/fees and customized/engraved discretionary-return exclusion. Chunks 4–6 not reviewed. Crafted-on-demand alone is NOT treated as a return exclusion. |
| [GIA electroformed-bracelet case](https://www.gia.edu/gems-gemology/spring-2024-lab-notes-electroformed-gold-bracelet) | 0 | Surface XRF did not establish solid construction; complementary professional tests may be needed. No candidate was tested. |
| [Brilliant Earth Freesia / BE-05](https://www.brilliantearth.com/Freesia-Hidden-Halo-Diamond-Ring-14K-Gold-BE1D3939-76789075/) | 0, 2, 3, 4, 5 of 8 | Chunk 4 explicitly shows USD, $1,190 (Setting Only), BE1D3939-14KY and 14K Yellow Gold. Size/centre diamond unselected; no grams. Chunks 1, 6, 7 not reviewed. |

| [15 U.S.C. § 295 at Cornell LII](https://www.law.cornell.edu/uscode/text/15/295) | 0; **24 October UTC** | Academic legal publisher, not a government/retailer page. Solder-free 0.003 and additional entire-metal tests are concurrent, not alternatives; 0.007 for other covered articles, 0.003 for watchcases/flatware. The calculator illustration is not a compliance test. |

A [general GIA chemical-analysis article](https://www.gia.edu/gems-gemology/winter-2024-chemical-analysis) was also opened at chunk 0, but is not used as evidence for solid-gold authentication. The bracelet case is the directly relevant warning. The pinned [historical calculator source](https://github.com/karagemop466-tech/GOLD4/blob/a832eed3a95e7f7e11b5a5bda2daf3228efa7c6d/assets/app.js) was read locally and executed with synthetic Node VM inputs; that is code inspection, not a retailer observation. WGC/source-health evidence is inherited and explicitly attributed, not a fresh read by this session.

## Findings and disposition

| ID | Finding / disposition | Official evidence |
|---|---|---|
| R8-SOLID-01 | **Corrected canonical evidence:** MN-01/MN-02 formerly said `stated` on a quote that only said pure 24k. Unsupported statement now blank / `not_stated`; unsourced “solid” removed from descriptive labels. Previous labels, quote and status remain in the dated review block. No price/weight changed. This does not allege plating/hollow construction. | [Knot](https://mene.com/products/knot-ring-gold), [Sun Band](https://mene.com/products/etruscan-sun-band-gold), [FTC](https://consumer.ftc.gov/articles/buying-platinum-gold-and-silver-jewelry). |
| R8-RETURNS-02 | **Needs review:** seven days is not an unconditional cash-refund promise. Reviewed terms distinguish credit, Customer Care refund requests, conditional restocking up to 10%, missing-certificate assessment of 5%, and customized/engraved/personalized discretionary exclusions. Seller data is not silently rewritten; no order-specific legal conclusion. | [Official terms](https://mene.com/terms-of-service). |
| R8-WEIGHT-03 | **Needs review:** crafted-on-demand weight/final price may vary. No grams back-solved or default amount promoted to a final quote. No blanket crafted-on-demand return exclusion inferred. | [Knot](https://mene.com/products/knot-ring-gold), [Sun Band](https://mene.com/products/etruscan-sun-band-gold), [terms](https://mene.com/terms-of-service). |
| R8-XRF-04 | **Testing caution:** a stamp or single surface XRF result is not a solid-construction guarantee. Request an independent professional's appropriate complementary testing, within written inspection/testing/return permission. No candidate was tested. | [GIA case](https://www.gia.edu/gems-gemology/spring-2024-lab-notes-electroformed-gold-bracelet), [FTC](https://consumer.ftc.gov/articles/buying-platinum-gold-and-silver-jewelry). |
| R8-CALC-05 | **Code/prose repaired:** finite input `1e308` could overflow to infinity and a false zero price multiple. Complete-number parsing, supported-karat checks and intermediate/result guards now blank unsafe output. Nominal/statutory illustrations no longer claim measured bounds. Ten runtime regressions use hypothetical arithmetic fixtures. Analysis also distinguishes percentage increase in gold content from the fraction of a price premium, removes unsupported labour/margin allocation and “normal” brand-price judgements, and labels the VR-01 size mismatch. Seller-wide solid wording is no longer inferred from booleans. | [Pinned original implementation](https://github.com/karagemop466-tech/GOLD4/blob/a832eed3a95e7f7e11b5a5bda2daf3228efa7c6d/assets/app.js), [GIA caveat](https://www.gia.edu/gems-gemology/spring-2024-lab-notes-electroformed-gold-bracelet), [official original generator](https://github.com/karagemop466-tech/GOLD4/blob/9f08b6d09265c65f054c3973f73bdeb2ba3c87ab/scripts/build_site.py). |
| R8-BE05-06 | **Provenance repaired:** unchanged 1190 USD, setting-only amount moves from V2 to V1 based on explicit USD/style/metal evidence, captured 23 October. Prior snapshot/EUR/localization and runner-403 history remains. No current exact-size/centre-stone quote or gram weight inferred. | [Official product, chunk 4](https://www.brilliantearth.com/Freesia-Hidden-Halo-Diamond-Ring-14K-Gold-BE1D3939-76789075/). |

Remaining data gaps publish rather than blocking research release: 47 rows lack explicit solid wording, 47 lack sourced scoped weights, 17 historical weights lack field-specific capture dates, and 10 have inherited specification-conflict flags. All current exact quotes, mark-pair evidence, independent reputation research, configured card/testing/return applicability and physical results remain unverified. No captured product-price amount, gram weight, benchmark or source-health record is changed by this session.

## Implementation and checks

- [`pages/readiness.html`](../pages/readiness.html) and [`reports/readiness-8a2b9dfb.json`](../reports/readiness-8a2b9dfb.json) are deterministic and SHA-256-bound to all inputs. `--check` writes nothing and fails on stale/missing output. Canonical build regenerates them automatically.
- Finite positive numeric inputs, first-hand provenance, approved official source and non-empty weight scope are required for historical-weight display. No estimated weights, inferred currency or configuration-bound current quote is synthesized.
- HTTPS exact-host allowlists reject credentials, lookalike hosts, non-standard ports and control/markup injection; output is escaped. No new external runtime dependency or remote API call.
- Canonical navigation/top policy/Flagged link Readiness. Table rows for ring comparisons, karat/benchmark arithmetic, seller policies, methodology and historical test results now link their relevant official external source or original official-project evidence.
- The expanded row-citation test first caught **nine** missing source links in Pass 20's historic gate table. Those now link the unchanged original `reviews/pass20/gates.json`; the original results are not relabelled as new tests. The review generator also uses the new capture-date footer and current complementary-testing caveat. Its observations/quotes/review report remain unchanged.
- **22 readiness tests and 10 calculator runtime tests pass locally.** Pages CI Gate 9 adds both suites plus deterministic freshness. All nine gates / twelve commands passed on the current integration candidate, including 8 existing assurance tests. Three source-health warnings retain the separate runner-403 path for BE-05/06/07; these are not erased by a browser read. The suite is repeated after merging any newer main changes; actual executed output is retained in [`reports/readiness-checks-8a2b9dfb.txt`](../reports/readiness-checks-8a2b9dfb.txt).

```bash
python3 scripts/compute.py
python3 scripts/build_site.py
python3 scripts/build_pass20.py
python3 scripts/gen_verification.py
python3 scripts/session_8a2b9dfb/test_readiness.py
node scripts/session_8a2b9dfb/test_calculator.js
python3 scripts/session_8a2b9dfb/readiness.py --check
python3 scripts/session_8a2b9dfb/run_checks.py  # all twelve CI commands; preserves actual output
```

Inherited scanner stdout uses phrases such as “ZERO HALLUCINATIONS.” This review does **not** endorse a universal semantic guarantee: the tests only establish their programmed checks. The full log records their exact output, preceded by the limitation. The README's Pass 20 untouched-row typo is corrected from 54 to 53, matching 64 total minus 11 reviewed.

Release/PR/deployment evidence is recorded in the appended [coordination entry](../COORDINATION.md) after it is actually obtained. No pending operation is described as completed.

## Confirmed publication and post-deploy correction

PR [#57](https://github.com/karagemop466-tech/GOLD4/pull/57) merged 2026-10-24T00:22:01Z as `90cb0efc9d2181f5f0a344a0b3dd3b57b951016c`. Production [run 40044621776](https://github.com/karagemop466-tech/GOLD4/actions/runs/40044621776) succeeded with all nine gates and Pages deploy; Pages API reported `built` on that commit, no error. Live dashboard, Readiness and calculator were fetched and matched the new findings, 251 canonical flags, blank exact quotes and repaired calculator labels/default arithmetic. The separate successful read-only [source run 40044322397](https://github.com/karagemop466-tech/GOLD4/actions/runs/40044322397) is **not** used as inspected per-URL evidence.

Live review caught an inherited single-day capture label and stale hardcoded Sarraf multiple range. The close-out derives the display range from populated prices' actual explicit dates (**22–23 October 2026**), never the build date; missing/invalid dates yield unverified, not a fallback date. It removes the obsolete range and universal solid-gold hero, and places the full front-page policy before the candidate headline. A new adversarial formatting regression brings readiness tests to 22. A separate 24-October read of the LII statute text also clarifies that the solder-free 0.003 and additional entire-metal requirements are concurrent, not alternatives; the 0.007 illustration alone does not test compliance. This new read is dated separately from the 23-October retailer evidence. No product or benchmark data changes. Corrective PR/deployment state is recorded only after actual confirmation in the board/PR thread.

## Remaining boundaries

This finite candidate list does not enumerate every ring for sale online. A link or seller statement is not an assay. Historical amounts and policies can change; source-health matches do not bind an exact selected variant. Inaccessible pages, unknown fields and pending verification remain visible. Continue independent source and hallucination review before using this research to make a purchase; seller refusal of independent testing or suitable return rights is a **do-not-buy** condition.
