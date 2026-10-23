# Pass 17 — direct official-source observations

**Session:** `arena/bc872fef-gold4`  
**Review date:** 2026-10-23 (UTC)  
**Rule:** no hallucinations. These are dated observations, not permanent prices. A mismatch, missing currency, ambiguous variant or inaccessible page is flagged; no gap is inferred or filled.

## Direct reads in this session

| Item | Official source | What the official page displayed in this review | Decision |
|---|---|---|---|
| Gold benchmark | [World Gold Council — Gold spot prices](https://www.gold.org/goldhub/data/gold-prices) | `USD /oz 3,996.31`; page/chart date `22 October, 2026`; `Data as of 22 October, 2026`; market data attributed to ICE Data Services. Two reads in this session returned the same displayed figure. Capture record: `2026-10-23T20:18:09Z`. | Replace the calculation benchmark with the new dated capture; preserve USD 4,024.45 in `prior_captures`; recompute all derived outputs. |
| AL-01 | [Allurez — Engraved Floral Solitaire](https://www.allurez.com/products/floral-solitaire-engagement-ring-14k-yellow-gold) | `$585`; `Setting only. Center stone sold separately.`; `Metal: 14k Yellow Gold`; style `NG4426`; `Approximate Metal Weight 3.58 grams`. | Matches the stored fields. Weight remains approximate; no hallmark or explicit solid-gold wording is inferred. |
| BN-22 | [Blue Nile — Wide Band Solitaire, 5 mm](https://www.bluenile.com/engagement-rings/design-your-own-ring/wide-band-solitaire-engagement-ring-in-14k-yellow-gold-5mm-item-203321) | `$2,050 (Setting Price)`; stock `501580y14`; `14K Yellow Gold`; `5.00mm`. Product prose still says `this platinum solitaire setting`. | Stored price/specifications match. The metal-copy contradiction remains flagged; gram weight remains blank. |
| VR-01 | [VRAI — Classic 4-prong dome configuration](https://www.vrai.com/configure/setting-to-diamond/classic-4-prong-dome/round-brilliant-yellow-gold-40635875360861) | `18k Yellow Gold`; `Band: Plain band`; `Band width: Standard`; `Band depth: 1.6mm`; `Metal weight: 2.86g (Ring size 6)`; `Pavé carat weight: 0.18ctw`. | Weight and plain-band/pavé-spec inconsistency corroborated. No new configured price is claimed from this read; the separate listing “From” price remains flagged. |
| MN-01 | [Menē — Knot Ring, 24k gold](https://mene.com/products/knot-ring-gold) | `$1,442 USD` on the rendered product page; size choices are present and products are described as sold by weight. Stored snapshot: `$1,465`. | Publish as a price difference for review. Do not overwrite: this read does not establish that the stored and current displays are the same size/weight configuration. |
| BE-05 | [Brilliant Earth — Freesia Hidden Halo, 14K yellow gold](https://www.brilliantearth.com/Freesia-Hidden-Halo-Diamond-Ring-14K-Gold-BE1D3939-76789075/) | `€1,350.00 (Setting Only)`; currency selector showed EUR; style `BE1D3939-14KY`; `14K Yellow Gold`; width `2-1.3 mm`; claw prong. The earlier USD 1,190 value was snapshot-only. | Current USD price is **blank** and flagged `PRICE_UNVERIFIED`. Preserve the historical USD observation and current EUR observation in review notes. No currency conversion. |

| RS-05 | [Ross-Simons — migrated item 990022](https://www.ross-simons.com/products/990022) | `Sale price $2,819`; item `990022`; `14kt White Gold`; GIA Cert `2225975086`; 0.80 ct round diamond; original price `$3,995`. | Third independent corroboration of the migrated-URL finding. Preserve PR #41's canonical URL correction and original price capture; obtain fresh runner evidence at the new URL. |
| Sarraf returns | [Sarraf — 30 Day Returns and Exchange Policy](https://www.sarraf.com/30-day-returns-and-exchange-policy/) | Returns/exchanges within 30 days of receipt; original condition; engraved/custom/special-order exclusions and insured-return instructions; wholesale terms separately labelled. | Replace the registry's product-page URL with this dedicated official policy URL; keep the policy claims narrowly tied to the page. |
| Sarraf warranty | [Sarraf — Lifetime Guarantee](https://www.sarraf.com/lifetime-guarantee/) | Repair/replacement shipping and handling fee is `$100 or 10% of current price, whichever is greater`; third-party alteration voids the Lifetime Guarantee; wholesale orders excluded. | Register separately as the warranty source rather than asking a returns URL to support warranty terms. |

## Automated evidence rules reviewed before the all-row run

- **CONFIRMED** now requires one distinct USD structured offer equal to the stored value. Missing currency is not assumed to be USD.
- Several variant offers that happen to include the stored amount produce `MULTIPLE_OFFERS_INCLUDE_STORED`, not an exact-variant confirmation.
- HTTP 403, 404, soft-404, JavaScript shells, timeouts and redirect refusals describe the check result; they do not prove a product fact or justify a replacement value.
- Redirects are restricted to HTTPS and the registered host allow-list.
- Evidence application cannot rewrite prices, weights or URLs. Historical manual notes are preserved; duplicate automated evidence segments are removed.

## Limits and required follow-up

This table is a manual sample, not a claim that every row was manually re-read. The separate GitHub-runner artifact covers every canonical ring URL and every registered source; `pages/freshness.html` reconciles all rows line by line. Seller reputation and physical hallmarks remain unverified, and no XRF/assay test was performed.

**Recommendation after every review:** repeat the hallucination scan, re-derive every calculation, inspect blank cells, and open the official link for any row considered for purchase.
