# November evidence / repository review — 2026-11-11

**NO HALLUCINATIONS.** 64 candidates, 10 retailers; 10 product URLs sampled in partial chunks; 54 not reopened. All exact-current price and weight fields remain blank. No ring purchase-approved.

## Sources and external coverage

New evidence: [recorded excerpts](current-a2f26a30.json). Official URLs are linked per excerpt and per candidate in [the published review](../pages/current-review.html). WGC printed 4,059.49 USD/troy oz with data date 10 November 2026, read 11 November; the historical canonical benchmark is not replaced. FTC official guidance read in chunk 0. Dates are read dates, not claimed source publication dates.

Ten partial product reads are not full re-verification. Displays differ for MN-01, BN-22, RS-05, BE-05. Currency codes, size, item variant, settings versus complete rings and return eligibility are never inferred. All findings are published on the clearly labelled Flagged for Review link. No historical evidence deleted or rewritten.

## Repository review / irregularities

- Flagged a prior published coverage arithmetic error with its immutable project evidence: [Pass 21 observations](https://github.com/karagemop466-tech/GOLD4/blob/3c271ce/reviews/pass21/observations.json) list one product read, but claim 59 unread of 64. The supported unread count is 63; the other four reads are not product rows. Original evidence remains unchanged.
- Reviewed canonical ring rows structurally: IDs, official-domain product links, existing capture dates/flags and current-value nonpromotion. New deterministic register hashes its canonical inputs and sampled observations.
- Reviewed source fetcher's URL handling, redirect chain, response limit, classification and --only scope. Fixed redirect validation before network follow; credential/port/scheme/host rejection; labelled body truncation. Fixed --only unexpectedly adding all policy URLs. Unknown-cause connection failures no longer automatically become ENVIRONMENT_BLOCKED when all requests fail.
- The inherited Gate 4 console slogan “ZERO HALLUCINATIONS” and Gate 7 “is recent” summary overstate what passing software checks establish: Gate 7 explicitly warns the full-sweep evidence is old. Treat those slogans as unproven, not factual assurance. No scanner proves gold authenticity, truthful seller claims, complete market coverage or absence of hallucinations. Existing historic reports claiming full passes are preserved as dated records, not treated as this session's evidence.
- Manual workflow dispatch returned HTTP 403 Resource not accessible by integration. No fresh full-sweep artifact inspected. Workflow run success, if later observed, is not itself inspected product evidence.
- Local link checks establish repository-relative target existence, not that every remote product URL works or every remote fragment is valid. Full external link/content review remains **needs review**.
- Source registry and old review prose include academic/industry publishers as well as government sources; official-project check logs are software evidence, not retailer or assay evidence.
- Automatic GitHub Pages upload previously sent the whole repository directory. This pass limits publication to public site/data/evidence assets, excluding Git internals and build tooling from the deployed artifact.

## Checks and repeat recommendation

Run `python3 scripts/session_a2f26a30/run_checks.py` after every review. [Actual output](../reports/current-a2f26a30-checks.txt) records exit codes. The new source-security and report tests use synthetic fixtures, not retailer observations. CI keeps all existing gates and adds the new tests and deterministic-output checks.

After every review, look for hallucinations again: official source, exact variant, currency, gram scope, capture date and testing/return conditions. Automated checks cannot prove absence of hallucinations.
