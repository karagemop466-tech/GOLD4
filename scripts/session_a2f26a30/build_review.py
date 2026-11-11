#!/usr/bin/env python3
"""Deterministic November review: no data enrichment or current-price inference."""
import argparse
from collections import Counter
from datetime import date, datetime, timezone
from hashlib import sha256
from html import escape
import json
from pathlib import Path
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
INPUTS = ('data/rings.json', 'data/sources.json', 'data/sellers.json',
          'data/gold_spot.json', 'reviews/currency-a2f26a30.json', 'reviews/current-a2f26a30.json')
OUTPUTS = ('reports/current-a2f26a30-register.json', 'pages/current-review.html',
           'reviews/current-a2f26a30.md')


def read(root, name):
    return json.loads((root / name).read_text())


def official_url(value, allowed):
    if not isinstance(value, str) or any(c.isspace() or ord(c) < 32 for c in value):
        raise ValueError('Unsafe official URL')
    p = urlsplit(value)
    if (p.scheme != 'https' or p.username is not None or p.password is not None
            or p.port not in (None, 443) or p.hostname not in allowed or '\\' in value):
        raise ValueError('Unregistered official URL: ' + value)
    return escape(value, quote=True)


def outputs(root=ROOT):
    evidence = read(root, INPUTS[-1])
    rows = read(root, 'data/rings.json')['rows']
    sources = read(root, 'data/sources.json')['sources']
    sellers = read(root, 'data/sellers.json')['sellers']
    allowed = {urlsplit(s['url']).hostname for s in sources}
    allowed.update(urlsplit(s['official_url']).hostname for s in sellers)
    # www and apex names used by existing canonical official product URLs.
    allowed |= {h.removeprefix('www.') for h in allowed if h}
    allowed |= {'www.' + h for h in list(allowed) if h and not h.startswith('www.')}
    review_date = date.fromisoformat(evidence['review_date_utc'])
    if review_date > datetime.now(timezone.utc).date():
        raise ValueError('Dated review is in the future relative to the UTC build clock')
    for observation in evidence['product_observations'] + evidence['reference_observations']:
        read_date = date.fromisoformat(observation['read_date_utc'])
        if read_date > review_date:
            raise ValueError('Observation read date is after the dated review')
        chunks = observation['chunks_read']
        if (not chunks or any(type(c) is not int or c < 0 for c in chunks)
                or len(set(chunks)) != len(chunks)):
            raise ValueError('Invalid inspected chunk list')
        if not observation['verbatim_excerpts'] or not observation['finding']:
            raise ValueError('Observation lacks evidence or limitation')
    observations = {o['id']: o for o in evidence['product_observations']}
    ids = [r['id'] for r in rows]
    if len(set(ids)) != len(ids) or not set(observations) <= set(ids):
        raise ValueError('Duplicate row ID or unknown observation')
    if len(observations) != len(evidence['product_observations']):
        raise ValueError('Duplicate observation')
    corrections = read(root, 'reviews/currency-a2f26a30.json')['quarantined_rows']
    register = []
    for row in rows:
        official_url(row['url'], allowed)
        obs = observations.get(row['id'])
        if obs:
            if obs['source_url'] != row['url'] or obs.get('current_configured_price_usd') is not None:
                raise ValueError('Observation source mismatch or unsupported current price')
            status = 'partial_official_read_needs_review'
            finding = obs['finding']
        else:
            status = 'not_reopened_needs_review'
            finding = 'Not re-opened in this pass. Historical facts have NOT been independently re-verified today.'
        register.append({
            'id': row['id'], 'retailer': row['retailer'], 'product_name': row['product_name'],
            'category': row['category'], 'source_url': row['url'],
            'historical_capture_date': row.get('price_captured_utc'),
            'official_read_date': obs['read_date_utc'] if obs else None,
            'current_exact_price_usd': None, 'current_exact_metal_weight_g': None,
            'current_price_status': 'UNVERIFIED', 'purchase_approved': False,
            'review_status': status, 'finding': finding,
            'inherited_flags': row['flags'],
        })
    stats = dict(total_rows=len(rows), sampled_product_urls=len(observations),
                 not_reopened=len(rows)-len(observations),
                 retailers=len(set(r['retailer_id'] for r in rows)),
                 confirmed_current_configured_prices=0, purchase_approvals=0,
                 populated_dated_usd_amounts=sum(r.get('price_usd') is not None for r in rows),
                 quarantined_currency_rows=len(corrections),
                 categories=dict(Counter(r['category'] for r in rows)))
    doc = {'schema': 1, 'review_date_utc': evidence['review_date_utc'],
           'input_sha256': {p: sha256((root / p).read_bytes()).hexdigest() for p in INPUTS},
           'stats': stats, 'rows': register}
    e = escape
    body_rows = []
    for r in register:
        body_rows.append(f'''<tr data-row-id="{e(r['id'])}"><td>{e(r['id'])}</td>
<td>{e(r['retailer'])}<br>{e(r['product_name'])}<br><span class="sub">{e(r['category'])}</span></td>
<td>{e(r['historical_capture_date'] or '')}</td><td>{e(r['official_read_date'] or '')}</td>
<td class="current-price"></td><td class="current-weight"></td>
<td><strong>UNVERIFIED · needs review</strong><br>{e(r['finding'])}<details><summary>Inherited flags (historical)</summary>{e(', '.join(r['inherited_flags']))}</details></td>
<td class="src"><a href="{official_url(r['source_url'], allowed)}" rel="noopener">Official product</a></td></tr>''')
    sample_rows = []
    for o in evidence['product_observations'] + evidence['reference_observations']:
        excerpts = ' · '.join(o['verbatim_excerpts'])
        sample_rows.append(f'''<tr><td>{e(o['id'])}</td><td>{e(o['read_date_utc'])}<br>Chunks {e(', '.join(map(str,o['chunks_read'])))}</td>
<td>{e(excerpts)}</td><td>{e(o['finding'])}</td>
<td class="src"><a href="{official_url(o['source_url'], allowed)}" rel="noopener">Official source</a></td></tr>''')
    html = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>November evidence review · GOLD4</title><link rel="stylesheet" href="../assets/style.css"></head>
<body><header class="site-header"><div class="wrap bar"><a class="brand" href="../index.html">Au · GOLD4</a>
<nav class="main" aria-label="Review navigation"><a href="../index.html">Dashboard</a><a href="solitaire.html">Solitaire</a><a href="pave.html">Pavé</a><a href="band.html">Bands</a><a href="calculator.html">Calculator</a><a href="readiness.html">Readiness</a><a href="flagged.html">Flagged for Review</a></nav></div></header>
<main class="wrap"><aside class="nohall"><strong>NO HALLUCINATIONS — no current complete-ring quotes confirmed.</strong>
Unsupported numeric cells stay blank. A displayed price or a source link is not a checkout quote or a purity test.
This is a dated {e(evidence['review_date_utc'])} review, not a live feed. Automated checks cannot prove the absence of hallucinations.</aside>
<section class="hero"><p class="eyebrow">Dated evidence review · {e(evidence['review_date_utc'])}</p><h1>See what was checked. See what is still unknown.</h1>
<p class="lede">{stats['total_rows']} existing candidates / {stats['retailers']} retailers. {stats['sampled_product_urls']} official product URLs sampled in partial chunks;
{stats['not_reopened']} not re-opened by this session. Separately attributed completed runner/re-read work is integrated below. {stats['populated_dated_usd_amounts']} dated USD amounts remain in canonical tables; {stats['quarantined_currency_rows']} unsupported assertions have been blanked. All rows audited structurally; no full external line-by-line re-verification is claimed. No purchase approvals.</p></section>
<div class="callout bad" id="flagged"><h2>Flagged for Review — November findings</h2>
<ul><li>Comparisons in this sampled review use the October snapshot inspected at the start of this session. Displays differed on Menē, Blue Nile, Ross-Simons and Brilliant Earth; later canonical updates, if any, retain their own attribution and capture dates. This review does not overwrite them.</li>
<li>Blue Nile BN-22: gold title versus platinum copy. Mejuri MJ-01: selected white gold versus yellow-gold materials/canonical variant. VRAI VR-01: size-6 weight versus size-5 selection and plain/pavé conflict.</li>
<li>SR-03 weight is approximate and explicitly size 10; not a weight guarantee for all sizes. Clearance/custom/testing-return conditions and independent reputation remain unresolved.</li>
<li>The full runner sweep could not be manually dispatched (GitHub API HTTP 403). Partial page-reader evidence below is the only new external product evidence claimed in this pass.</li>
<li><strong>Eight USD amounts quarantined:</strong> AN-01, VR-01, BE-01/02/03/05/06/07 lacked explicit USD in the stored runner/hand evidence. A dollar symbol or four-currency menu is not proof of USD. VR-01 also used a Similar Styles amount. Canonical price cells are now blank and flagged; <a href="../reviews/currency-a2f26a30.json">attributed original claims and official URLs</a> are preserved. No guessed currency conversion or amount is substituted.</li>
<li><a href="reread-4fe4a9c3.html">Completed peer re-read</a>: its all-URL runner evidence and 16 hand reads remain owner-attributed. Its original pre-quarantine summary/self-check is historical, not a test of this corrected snapshot. Its recorded hand-read window ends at 08:50Z, after its original ready commit; timestamp provenance is also needs review.</li>
<li><a href="https://github.com/karagemop466-tech/GOLD4/pull/65">Concurrent PR #65</a> reuses already-published Pass 21 evidence paths for different observations. Unique naming/preservation was requested; this integration does not overwrite those originals or treat the conflicting PR as verified combined evidence.</li>
<li>Prior published Pass 21 coverage arithmetic needs review: its evidence lists only one product row out of 64, so 63—not 59—were not re-opened. The other four reads are references/site checks, not product rows. <a href="https://github.com/karagemop466-tech/GOLD4/blob/3c271ce/reviews/pass21/observations.json">Original project evidence</a> is preserved; this does not invalidate its actual AL-01 read.</li>
<li>Companion policy findings are available in the <a href="../reviews/assurance-91e9aba0/index.html">independent seller-policy review</a>. Its recorded read window ends at 08:40Z, later than this integration’s 08:08Z observation; timestamp provenance needs review. Its claims have not been independently re-read or promoted by this session.</li>
<li>Security gap repaired: source fetches now reject off-list/non-HTTPS redirects before following them. Network errors remain unknown-cause failures, not inferred dead links or inferred environment blocks.</li></ul>
<p>Official evidence and exact scope are in the source-linked table below. <strong>Needs review does not mean counterfeit.</strong></p></div>
<section class="section"><h2>Inspected official excerpts — observations, not approved quotes</h2>
<p>Excerpts use normalized whitespace. Dollar symbols are retained exactly; no currency code is inferred. No variant, size, complete-ring total or current metal weight is filled from these excerpts. WGC data-date is November 10, distinct from the November 11 read date. The calculator uses the canonical stored benchmark with its own capture and source-data dates. This review records a separate observation, not an automatic spot update.</p>
<div class="table-wrap"><table><thead><tr><th>Record</th><th>Read date / chunks</th><th>Official excerpt</th><th>Interpretation / limits</th><th>Source</th></tr></thead><tbody>{''.join(sample_rows)}</tbody></table></div></section>
<section class="section"><h2>All-candidate current-evidence register</h2><p>Empty cells mean <strong>unverified</strong>, never zero. Historical capture dates describe stored records, not today’s verification. The <a href="../index.html">historical dashboard</a> preserves original observations; the <a href="readiness.html">readiness register</a> covers the full checklist.</p>
<div class="table-wrap"><table><thead><tr><th>ID</th><th>Candidate / category</th><th>Historical price capture</th><th>Sample read</th><th>Current exact price (USD)</th><th>Current exact metal grams</th><th>Status / findings</th><th>Source</th></tr></thead><tbody>{''.join(body_rows)}</tbody></table></div></section>
<section class="section"><h2>Verification limits and next safe step</h2><ul>{''.join('<li>'+e(x)+'</li>' for x in evidence['limitations'])}</ul>
<p>{e(evidence['recommendation'])}</p><p>Do not purchase if the seller will not permit appropriate independent verification and an eligible return. Do not resize/wear first. Agree testing/return terms in writing; a single surface XRF result is not a guarantee of construction.</p>
<p><a href="../reviews/current-a2f26a30.json">Recorded excerpts and scope (JSON)</a> · <a href="../reports/current-a2f26a30-register.json">Hash-bound register (JSON)</a> · <a href="../reviews/current-a2f26a30.md">Repository review</a> · <a href="../reports/current-a2f26a30-checks.txt">Actual automated-check output</a></p></section></main>
<footer class="wrap foot">Research, not an endorsement or legal advice. US consumer guidance is not a Swiss-law determination. Readiness gaps remain open.</footer></body></html>'''
    md = f'''# November evidence / repository review — {evidence['review_date_utc']}

**NO HALLUCINATIONS.** {stats['total_rows']} candidates, {stats['retailers']} retailers; {stats['sampled_product_urls']} product URLs sampled in partial chunks; {stats['not_reopened']} not reopened. All exact-current price and weight fields remain blank. No ring purchase-approved.

## Sources and external coverage

New evidence: [recorded excerpts](current-a2f26a30.json). Official URLs are linked per excerpt and per candidate in [the published review](../pages/current-review.html). WGC printed 4,059.49 USD/troy oz with data date 10 November 2026, read 11 November; this session does not replace the canonical benchmark. FTC official guidance read in chunk 0. Dates are read dates, not claimed source publication dates.

Ten partial product reads are not full re-verification. Displays differ for MN-01, BN-22, RS-05, BE-05. Currency codes, size, item variant, settings versus complete rings and return eligibility are never inferred. All findings are published on the clearly labelled Flagged for Review link. No historical evidence deleted or rewritten.

## Repository review / irregularities

- **Final currency/target quarantine:** eight November 11 canonical USD assertions are blanked and flagged (AN-01, VR-01, BE-01/02/03/05/06/07). The runner metadata and stored hand excerpts lack explicit USD; BE-05 footer chunk 7 lists AUD/CAD/GBP/USD choices without an active selection. VR-01 also used a related-product amount. [Original attributed claims and official links](currency-a2f26a30.json) are preserved. No other amount is inferred. A new currency gate rejects bare-dollar and menu-based promotion.
- Completed #59 source work is integrated with attribution, including raw all-URL sweep, 16 hand reads, original reconciliation/self-check and superseded-price history. Those original reports are the **pre-quarantine snapshot**, not a current canonical test. Its future-ended 08:50Z read window is flagged, not silently accepted.
- Concurrent #65 modifies existing Pass 21 evidence paths with different content; unique names were requested. This integration preserves the already-published originals rather than overwriting them.

- Flagged a prior published coverage arithmetic error with its immutable project evidence: [Pass 21 observations](https://github.com/karagemop466-tech/GOLD4/blob/3c271ce/reviews/pass21/observations.json) list one product read, but claim 59 unread of 64. The supported unread count is 63; the other four reads are not product rows. Original evidence remains unchanged.
- Companion [seller-policy assurance](assurance-91e9aba0/index.html) is retained and linked. Its read window extends to 08:40Z, later than this session’s ~08:08Z integration clock; timestamp provenance is flagged, not silently accepted. No companion claims are promoted to new firsthand evidence.
- Reviewed canonical ring rows structurally: IDs, official-domain product links, existing capture dates/flags and current-value nonpromotion. New deterministic register hashes its canonical inputs and sampled observations.
- Reviewed source fetcher's URL handling, redirect chain, response limit, classification and --only scope. Fixed redirect validation before network follow; credential/port/scheme/host rejection; labelled body truncation. Fixed --only unexpectedly adding all policy URLs. Unknown-cause connection failures no longer automatically become ENVIRONMENT_BLOCKED when all requests fail.
- The inherited Gate 4 console slogan “ZERO HALLUCINATIONS” and Gate 7 “is recent” summary overstate what passing software checks establish: Gate 7 explicitly warns the full-sweep evidence is old. Treat those slogans as unproven, not factual assurance. No scanner proves gold authenticity, truthful seller claims, complete market coverage or absence of hallucinations. Existing historic reports claiming full passes are preserved as dated records, not treated as this session's evidence.
- Manual workflow dispatch returned HTTP 403 Resource not accessible by integration. No fresh full-sweep artifact inspected. Workflow run success, if later observed, is not itself inspected product evidence.
- Local link checks establish repository-relative target existence, not that every remote product URL works or every remote fragment is valid. Full external link/content review remains **needs review**.
- Source registry and old review prose include academic/industry publishers as well as government sources; official-project check logs are software evidence, not retailer or assay evidence.
- Automatic GitHub Pages upload previously sent the whole repository directory. This pass limits publication to public site/data/evidence assets, excluding Git internals and build tooling from the deployed artifact. A frozen placeholder mini-site had seven broken relative links; staging replaces only its deployed copy with an archive notice linking to the preserved Git snapshot and current dashboard. The original repository snapshot is untouched. All staged HTML local-file targets are checked before upload.

## Checks and repeat recommendation

Run `python3 scripts/session_a2f26a30/run_checks.py` after every review. [Actual output](../reports/current-a2f26a30-checks.txt) records exit codes. The new source-security and report tests use synthetic fixtures, not retailer observations. CI keeps all existing gates and adds the new tests and deterministic-output checks.

{evidence['recommendation']}
'''
    return dict(zip(OUTPUTS, [json.dumps(doc, indent=2, ensure_ascii=False)+'\n', html, md]))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    failures = []
    for name, content in outputs().items():
        path = ROOT / name
        if args.check:
            if not path.exists() or path.read_text() != content:
                failures.append(name)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
    if failures:
        print('FAIL stale review outputs:', ', '.join(failures))
        return 1
    print('PASS November review ' + ('freshness' if args.check else 'build'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
