# Re-read of 2026-11-11 — re-verification after 19 days (session 4fe4a9c3)

Session `arena/4fe4a9c3-gold4`. **No hallucinations:** every value below is copied from the evidence files; nothing was inferred.

## Evidence

| File | What it is |
|---|---|
| `reports/live_source_check_20261111T080309Z.json` | GitHub runner, read-only GET of 64 ring URLs + 32 sources, 2026-11-11T08:03:09Z |
| `reviews/reread-4fe4a9c3/hand_reads.json` | 16 rows + the benchmark, hand-read in a browser-rendered reader, verbatim strings |
| `reviews/reread-4fe4a9c3/reconciliation.json` | row-by-row verdicts combining both read paths |
| `reviews/reread-4fe4a9c3/gates.json`, `gates.txt` | the twelve gate commands on the final tree |

## Gold benchmark

World Gold Council panel: **$4,059.49/oz**, "Data as of 10 November, 2026", read 2026-11-11T08:01Z — <https://www.gold.org/goldhub/data/gold-prices>.
Previous benchmark $3,996.31/oz (+1.58%). Runner cross-checks: Kitco 24K value per oz $4,057.00; BullionVault current gold price per oz $4,059.81; JM Bullion gold ASK (includes a premium) $4,071.46.

## Row by row

| ID | Before | Read 11 Nov | List | Verdict | Read path | Weight re-seen | Official page |
|---|---|---|---|---|---|---|---|
| AL-01 | $585 | $585 |  | UNCHANGED | runner + hand | yes | <https://www.allurez.com/products/floral-solitaire-engagement-ring-14k-yellow-gold> |
| AL-02 | $724 | $724 |  | UNCHANGED | runner | yes | <https://www.allurez.com/products/milgrain-trellis-solitaire-engagement-ring-14k-yellow-gold> |
| AL-03 | $848 | $848 |  | UNCHANGED | runner | yes | <https://www.allurez.com/products/split-shank-solitaire-engagement-ring-14k-yellow-gold> |
| AL-04 | $1,425 | $1,425 |  | UNCHANGED | runner | yes | <https://www.allurez.com/products/split-shank-solitaire-engagement-ring-18k-yellow-gold> |
| AN-01 | $870.76 | $870.76 |  | UNCHANGED | hand | no | <https://www.anjolee.com/rings/diamond-solitaire-engagement-rings/Six-Curved-Prongs-Solitaire-Diamond-Engagement-Ring.aspx> |
| BE-01 | $1,190 | $1,190 |  | UNCHANGED | hand | n/a | <https://www.brilliantearth.com/Atelier-Solitaire-Ring-14K-Gold-BE1D2444-76788321/> |
| BE-02 | $1,390 | $1,390 |  | UNCHANGED | hand | n/a | <https://www.brilliantearth.com/Atelier-Solitaire-Ring-Gold-BE1D2444-42024993/> |
| BN-01 | $1,000 | $800 | $1,000 | SALE | runner | n/a | <https://www.bluenile.com/engagement-rings/design-your-own-ring/petite-solitaire-engagement-ring-in-14k-yellow-gold-item-195639> |
| BN-02 | $1,155 | $924 | $1,155 | SALE | runner | n/a | <https://www.bluenile.com/engagement-rings/design-your-own-ring/petite-solitaire-engagement-ring-in-18k-yellow-gold-item-195269> |
| BN-03 | $1,000 | $800 | $1,000 | SALE | runner | n/a | <https://www.bluenile.com/engagement-rings/design-your-own-ring/classic-six-prong-solitaire-engagement-ring-in-14k-yellow-gold-item-203272> |
| BN-04 | $935 | $748 | $935 | SALE | runner + hand | n/a | <https://www.bluenile.com/engagement-rings/design-your-own-ring/classic-comfort-fit-solitaire-engagement-ring-in-14k-yellow-gold-25mm-item-203284> |
| BN-05 | $1,310 | $1,048 | $1,310 | SALE | runner | n/a | <https://www.bluenile.com/engagement-rings/design-your-own-ring/classic-comfort-fit-solitaire-engagement-ring-in-18k-yellow-gold-25mm-item-194941> |
| BN-06 | $1,295 | $1,036 | $1,295 | SALE | runner | n/a | <https://www.bluenile.com/engagement-rings/design-your-own-ring/six-prong-low-dome-comfort-fit-solitaire-engagement-ring-in-18k-yellow-gold-2mm-item-195379> |
| BN-07 | $870 | $696 | $870 | SALE | runner | n/a | <https://www.bluenile.com/engagement-rings/design-your-own-ring/classic-four-prong-solitaire-engagement-ring-in-14k-yellow-gold-item-203257> |
| BN-08 | $1,500 | $1,200 | $1,500 | SALE | runner | n/a | <https://www.bluenile.com/engagement-rings/design-your-own-ring/riviera-pave-diamond-engagement-ring-in-14k-yellow-gold-1-6-ct-tw-item-203512> |
| MJ-01 | $548 | $548 |  | UNCHANGED | runner | n/a | <https://mejuri.com/products/diamonds-team-ring> |
| MJ-02 | $648 | $648 |  | UNCHANGED | runner | n/a | <https://mejuri.com/products/diamonds-band> |
| MJ-03 | $548 | $548 |  | UNCHANGED | runner | n/a | <https://mejuri.com/products/pave-diamond-slim-signet-ring> |
| MJ-04 | $798 | $798 |  | UNCHANGED | runner | n/a | <https://mejuri.com/products/pave-diamond-thin-dome-ring> |
| MJ-05 | $598 | $598 |  | UNCHANGED | runner | n/a | <https://mejuri.com/products/bezel-lab-grown-diamond-zig-zag-ring> |
| VR-01 | $1,035 | $1,035 |  | UNCHANGED | hand | yes | <https://www.vrai.com/configure/setting-to-diamond/classic-4-prong-dome/round-brilliant-yellow-gold-40635875360861> |
| VR-02 | — | — |  | NOT_REREAD | none | no | <https://www.vrai.com/configure/setting-to-diamond/signature-6-prong/round-brilliant-yellow-gold-32891144798301> |
| BE-03 | $850 | $850 |  | UNCHANGED | hand | n/a | <https://www.brilliantearth.com/Six-Prong-Petite-Comfort-Fit-1.5mm-Solitaire-Ring-Gold-BE1199H6-1912137/> |
| SR-01 | $352 | $352 |  | UNCHANGED | runner | yes | <https://www.sarraf.com/products/10k-White-Gold-5mm-High-Polished-Traditional-Domed-Wedding-Band.html> |
| SR-02 | $1,063 | $1,063 |  | UNCHANGED | runner | yes | <https://www.sarraf.com/products/14k-gold-6mm-high-polished-comfort-fit-wedding-band.html> |
| SR-03 | $871 | $871 |  | UNCHANGED | runner + hand | yes | <https://www.sarraf.com/products/18k-Yellow-Gold-5mm-High-Polished-Traditional-Domed-Wedding-Band.html> |
| SR-04 | $1,436 | $1,436 |  | UNCHANGED | runner | yes | <https://www.sarraf.com/products/18K-Gold-6mm-High-Polished-Flat-Comfort-Fit-Wedding-Band.html> |
| SR-05 | $2,858 | $2,858 |  | UNCHANGED | runner | yes | <https://www.sarraf.com/products/14k-yellow-gold-mens-solitaire-diamond-ring-1-2-ct.html> |
| SR-06 | $4,068 | $4,068 |  | UNCHANGED | runner | yes | <https://www.sarraf.com/products/18k-yellow-gold-mens-solitaire-diamond-ring-3-4-ct.html> |
| SR-07 | $2,183 | $2,183 |  | UNCHANGED | runner | n/a | <https://www.sarraf.com/products/14k-gold-1-2-ctw-diamond-solitaire-engagement-diamond-ring.html> |
| SR-08 | $2,461 | $2,461 |  | UNCHANGED | runner | n/a | <https://www.sarraf.com/products/18k-yellow-gold-1-2-carat-round-diamond-solitaire-engagement-ring.html> |
| CB-01 | $3,900 | $3,900 |  | UNCHANGED | runner | n/a | <https://www.catbirdnyc.com/the-swan-solitaire-2475.html> |
| CB-02 | $313.50 | $313.50 | $418 | UNCHANGED | runner | n/a | <https://www.catbirdnyc.com/grand-painters-ring.html> |
| MN-01 | $1,465 | $1,455 |  | CHANGED | runner | n/a | <https://mene.com/products/knot-ring-gold> |
| MN-02 | $1,730 | $1,719 |  | CHANGED | runner | n/a | <https://mene.com/products/etruscan-sun-band-gold> |
| BN-09 | $1,125 | — |  | SOURCE_DEAD | runner | n/a | <https://www.bluenile.com/engagement-rings/design-your-own-ring/classic-four-prong-solitaire-engagement-ring-in-18k-yellow-gold-item-500000y> |
| BN-10 | $1,145 | — |  | SOURCE_DEAD | runner | n/a | <https://www.bluenile.com/engagement-rings/design-your-own-ring/low-dome-comfort-fit-solitaire-engagement-ring-in-14k-yellow-gold-item-502120y14> |
| BN-11 | $1,805 | — |  | SOURCE_DEAD | runner | n/a | <https://www.bluenile.com/engagement-rings/design-your-own-ring/french-pave-diamond-engagement-ring-in-18k-yellow-gold-1-20-ct-tw-item-502520y> |
| BN-12 | $2,515 | — |  | SOURCE_DEAD | runner | n/a | <https://www.bluenile.com/engagement-rings/design-your-own-ring/tapered-baguette-diamond-engagement-ring-in-18k-yellow-gold-1-6-ct-tw-item-501670y> |
| BN-13 | $2,260 | $1,808 | $2,260 | SALE | runner | n/a | <https://www.bluenile.com/engagement-rings/design-your-own-ring/solitaire-engagement-ring-with-pave-basket-in-14k-yellow-gold-by-james-allen-item-311230> |
| BN-14 | $1,385 | $1,108 | $1,385 | SALE | runner | n/a | <https://www.bluenile.com/engagement-rings/design-your-own-ring/solitaire-engagement-ring-with-intricate-basket-in-14k-yellow-gold-by-james-allen-item-315036> |
| BN-15 | $975 | $780 | $975 | SALE | runner | n/a | <https://www.bluenile.com/engagement-rings/design-your-own-ring/east-west-knife-edge-cathedral-solitaire-engagement-ring-in-14k-yellow-gold-by-james-allen-item-311246> |
| BN-16 | $1,565 | $1,252 | $1,565 | SALE | runner | n/a | <https://www.bluenile.com/engagement-rings/design-your-own-ring/pave-diamond-halo-engagement-ring-in-14k-yellow-gold-oval-by-james-allen-item-311127> |
| BN-17 | $1,555 | $1,244 | $1,555 | SALE | runner | n/a | <https://www.bluenile.com/engagement-rings/design-your-own-ring/pave-diamond-halo-engagement-ring-in-14k-yellow-gold-pear-by-james-allen-item-311121> |
| BN-18 | $1,255 | $1,004 | $1,255 | SALE | runner | n/a | <https://www.bluenile.com/engagement-rings/design-your-own-ring/petite-hidden-halo-solitaire-plus-diamond-engagement-ring-in-14k-yellow-gold-item-192506> |
| BN-19 | $2,350 | $1,880 | $2,350 | SALE | runner | n/a | <https://www.bluenile.com/engagement-rings/design-your-own-ring/bow-tie-engagement-ring-with-channel-set-round-diamonds-in-14k-yellow-gold-by-james-allen-item-304294> |
| BN-20 | $965 | $772 | $965 | SALE | runner | n/a | <https://www.bluenile.com/engagement-rings/design-your-own-ring/woven-solitaire-engagement-ring-in-14k-yellow-gold-by-james-allen-item-310896> |
| BN-21 | $1,290 | $1,032 | $1,290 | SALE | runner | n/a | <https://www.bluenile.com/engagement-rings/design-your-own-ring/knife-edge-solitaire-engagement-ring-in-14k-yellow-gold-item-192261> |
| BN-22 | $2,050 | $1,640 | $2,050 | SALE | runner | n/a | <https://www.bluenile.com/engagement-rings/design-your-own-ring/wide-band-solitaire-engagement-ring-in-14k-yellow-gold-5mm-item-203321> |
| BN-23 | $5,190 | $4,152 | $5,190 | SALE | runner | n/a | <https://www.bluenile.com/engagement-rings/design-your-own-ring/emerald-cut-diamond-engagement-ring-in-14k-yellow-gold-1-ct-tw-item-203303> |
| BN-24 | $1,145 | $916 | $1,145 | SALE | runner | n/a | <https://www.bluenile.com/engagement-rings/design-your-own-ring/classic-simple-solitaire-engagement-ring-in-14k-white-gold-item-195730> |
| BN-25 | $2,210 | — |  | SOLD_OUT | runner | n/a | <https://www.bluenile.com/engagement-rings/design-your-own-ring/pave-contour-diamond-engagement-ring-in-14k-white-gold-by-james-allen-item-315661> |
| BN-26 | — | — |  | SOLD_OUT | runner | n/a | <https://www.bluenile.com/engagement-rings/design-your-own-ring/14k-yellow-gold-15mm-comfort-fit-engagement-ring-item-41515> |
| BE-04 | $1,090 | — |  | SOURCE_DEAD | hand | n/a | <https://www.brilliantearth.com/Fairmined-Hollis-Knife-Edge-Solitaire-Engagement-Ring-Gold-BE1FM0126/> |
| BE-05 | $1,190 | $990 |  | CHANGED | hand | n/a | <https://www.brilliantearth.com/Freesia-Hidden-Halo-Diamond-Ring-14K-Gold-BE1D3939-76789075/> |
| BE-06 | $1,390 | $1,190 |  | CHANGED | hand | n/a | <https://www.brilliantearth.com/Freesia-Hidden-Halo-Diamond-Ring-Gold-BE1D3939-19424930/> |
| BE-07 | $1,350 | $1,350 |  | UNCHANGED | hand | n/a | <https://www.brilliantearth.com/Fleur-Solitaire-Ring-14K-Gold-BE1574-76785943/> |
| RS-01 | $400 | $320 | $400 | SALE | hand | yes | <https://www.ross-simons.com/jewelry/rings/571221.html> |
| RS-02 | $249 | $199.20 | $249 | SALE | runner + hand | yes | <https://www.ross-simons.com/jewelry/rings/985230.html> |
| RS-03 | $595 | $476 | $595 | SALE | hand | yes | <https://www.ross-simons.com/jewelry/rings/820263.html> |
| RS-04 | $1,195 | $956 | $1,195 | SALE | runner + hand | yes | <https://www.ross-simons.com/jewelry/rings/823796.html> |
| RS-05 | $2,819 | $2,537.10 | $3,995 | SALE | runner | n/a | <https://www.ross-simons.com/products/990022> |
| MJ-06 | $1,100 | $1,100 |  | UNCHANGED | runner | n/a | <https://mejuri.com/us/en/products/diamond-eternity-band?Material=14k+Yellow+Gold&Stone=Natural+Diamond> |
| MJ-07 | $348 | $348 |  | UNCHANGED | runner | n/a | <https://mejuri.com/us/en/products/diamonds-line-ring> |

## Not verified this pass

- 48 of 64 rows were not hand-read; their only evidence dated 2026-11-11 is the runner fetch
- Not re-read at all: VR-02
- Gram weights re-seen for 15 of 17 rows; not re-seen: AN-01, VR-02
- Return-policy, warranty, law and guidance text: reachability checked only, wording not re-read
- No XRF or assay result, no hallmark, no independently verified seller reputation for any row

## Gates

| Gate | Status | Detail |
|---|---|---|
| 1 | PASS | RESULT: PASS  (126 passed, 0 warnings, 0 failures) · exit 0 |
| 2 | PASS | PASS: 31 pages checked; local links resolve; every populated row carries an official source link; no-hallucination warning and FTC reference present. · exit 0 |
| 3 | PASS | Records audited: 64 · exit 0 · exit 0 |
| 4 | PASS | STATUS                  : PASS — ZERO HALLUCINATIONS, ZERO BROKEN LINKS, ZERO SECURITY ERRORS. · exit 0 |
| 5 | PASS | RESULT: PASS — zero hallucinated/unsourced values, zero phantom math, zero broken local links. · exit 0 |
| 6a | PASS | SELF-TEST PASSED — a known-wrong CFR citation was correctly rejected · exit 0 |
| 6b | PASS | Citation-integrity gate: 110 CFR section references checked across 42 files (rule violations: label=0, sentence=0). · exit 0 |
| 7 | PASS | RESULT: PASS — 295 checks, 8 warning(s), 0 failures · exit 0 |
| 8 | PASS | OK · exit 0 |
| 9a | PASS | OK · exit 0 |
| 9b | PASS | 10 calculator runtime tests passed. Fixtures are hypothetical arithmetic, not sourced offers. · exit 0 |
| 9c | PASS | PASS: readiness register matches canonical input hashes; unsupported current quotes remain blank; no purchase approvals. · exit 0 |
