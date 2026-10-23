#!/usr/bin/env python3
"""Publish a conservative current-session review; never copy historic prices as current."""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def esc(value):
    return html.escape(str(value), quote=True)


def build():
    rings = json.loads((ROOT / 'data/rings.json').read_text())['rows']
    health = json.loads((ROOT / 'data/source_health.json').read_text())
    states = {r['id']: r for r in health['rows']}
    evidence_candidates = sorted((ROOT / 'reports').glob('live_source_check_2*.json'))
    evidence_path = evidence_candidates[-1] if evidence_candidates else None
    fresh = json.loads(evidence_path.read_text()) if evidence_path else None
    fresh_by_id = {r['key']: r for r in fresh.get('results', []) if r.get('kind') == 'ring'} if fresh else {}
    evidence_note = ('<p>Latest inspected runner evidence: <a href="../reports/' + esc(evidence_path.name) + '">raw GET observations</a>. '
                     'Recorded collection time: ' + esc(fresh.get('checked_utc')) + '; collector session: ' + esc(fresh.get('session', 'not recorded')) + '. '
                     'These are automated HTTP observations, not configuration-specific price or purity verification. '
                     'The source-health reconciliation applies the same artifact to every canonical row; mismatches and unreachable sources stay flagged.</p>') if fresh else '<p>No runner artifact is available for inspection. No fresh factual confirmation is claimed and every current-quote cell remains blank.</p>'
    observations = json.loads((ROOT / 'reviews/session-986df4df-observations.json').read_text())['observations']
    observations_html = '<section class="section"><h2>Selected official pages independently re-opened</h2><p>These are observations of selected pages/chunks by session 986df4df, not current checkout quotes. All dated 23 October 2026. Other rows are not claimed as manually re-verified by that session.</p><div class="table-wrap"><table><thead><tr><th>ID</th><th>Observed text / summary</th><th>Finding</th><th>Official source</th></tr></thead><tbody>'
    for item in observations:
        observations_html += '<tr><td>' + esc(item['id']) + '</td><td>' + esc(item['observed_text']) + '</td><td>' + esc(item['finding']) + '</td><td><a href="' + esc(item['url']) + '">Official page</a></td></tr>'
    observations_html += '</tbody></table></div><p><a href="../reviews/session-986df4df-observations.json">Dated observation record and inspected chunks</a> · <a href="../reviews/pass17/official_source_observations.md">Final integration direct-source log</a> · <a href="../reviews/pass17_repo_review_0e04577b.md">Complete line-by-line repository review</a></p></section>'
    rows = []
    for ring in rings:
        prior = states.get(ring['id'], {})
        observation = fresh_by_id.get(ring['id'], {})
        observed = (str(observation.get('checked_utc')) + ' / ' + str(observation.get('classification'))) if observation else 'UNVERIFIED — no inspected runner observation for this row'
        flags = ', '.join(ring.get('flags', [])) or 'No historical flags recorded; not purchase approval'
        rows.append(f'''<tr data-review-id="{esc(ring['id'])}">
<td>{esc(ring['id'])}</td><td>{esc(ring['retailer'])}</td>
<td>{esc(ring['product_name'])}</td>
<td>{esc(observed)}</td>
<td class="current-price" aria-label="Unverified current price"></td>
<td>UNVERIFIED — no current-session configuration-specific quote</td>
<td>{esc(prior.get('checked_utc', 'Not checked'))}<br>{esc(prior.get('source_state', 'NOT_CHECKED'))} / {esc(prior.get('price_state', 'NOT_CHECKED'))} (historical evidence only)</td>
<td>{esc(flags)}</td><td><a href="{esc(ring['url'])}" target="_blank" rel="noopener noreferrer">Official product</a></td></tr>''')
    body = '''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Current-session review · GOLD4</title><link rel="stylesheet" href="../assets/style.css"></head>
<body><header class="site-header"><div class="wrap bar"><a class="brand" href="../index.html">Au · GOLD4</a>
<nav class="main"><a href="../index.html">Dashboard</a><a href="flagged.html">Flagged for Review</a><a href="freshness.html">Historical evidence</a><a href="calculator.html">Calculator</a></nav></div></header>
<main class="wrap"><section class="hero"><span class="eyebrow">Combined current review · latest runner evidence ''' + esc(fresh.get('checked_utc') if fresh else 'not available') + '''</span>
<h1>Current review — Flagged for Review</h1>
<p class="lede">NO HALLUCINATIONS: unconfirmed current prices stay blank. This is a candidate register, not an approved purchase list or a complete inventory of rings available online.</p></section>
<div class="nohall"><h2>What this session can actually verify</h2>
<p>Selected official sources were independently re-opened by earlier review sessions (observations below), and the latest runner artifact supplies automated HTTP observations for the canonical row URLs. Neither is a manual independent re-verification of every product. Existing dated captures are preserved as historical claims, not newly verified facts.
A successful HTTP response or a matching structured-data price does not prove the selected size, metal, stone, availability, taxes, shipping, or actual gold purity.
No current configuration-specific quote, weight, hallmark or seller reputation is inferred here. All current-price cells below are intentionally empty.</p>
<p>Internal arithmetic, citation and security gates test specific rules; passing them is not proof that a claim is true or that all hallucinations have been found.
<strong>Recommend a hallucination review after every review and before buying.</strong> Compare each field against its official source and keep a dated copy.</p>
<p>See the <a href="../reviews/session-986df4df.md">session findings and limitations</a>, <a href="../reports/session-986df4df-checks.txt">executed gate log</a>,
<a href="../data/source_health.json">reconciled source evidence summary</a>, and <a href="../reports/live_source_check_latest.json">latest raw evidence</a>.
This register never copies a stored historical price into a current-quote cell. Canonical corrections and their evidence are documented in the <a href="../reviews/pass17/official_source_observations.md">final integration source log</a> and <a href="log.html">verification log</a>.</p></div>
<section class="section"><h2>Security / hallucination irregularities</h2><div class="table-wrap"><table>
<thead><tr><th>Finding</th><th>Disposition</th><th>Source / review link</th></tr></thead><tbody>
<tr><td>Missing currency was treated as USD in the price reconciler</td><td>Fixed: only explicit USD qualifies. Legacy CONFIRMED states remain historical, not re-certified.</td><td><a href="https://github.com/karagemop466-tech/GOLD4/blob/arena/986df4df-gold4/scripts/build_source_health.py">Reconciler code</a></td></tr>
<tr><td>Permissive numeric parsing could turn signed/currency text into another amount</td><td>Fixed: reject negatives, nonfinite values and ambiguous formatted text. Regression tests added.</td><td><a href="https://github.com/karagemop466-tech/GOLD4/blob/arena/986df4df-gold4/scripts/test_assurance.py">Regression tests</a></td></tr>
<tr><td>Source-check evidence must be inspectable without giving the network collector write access</td><td>Collection is read-only. A separate same-repository PR job alone may write, validates the branch ref and commits only raw report artifacts; no product data is changed. Branch expressions stay out of shell code.</td><td><a href="../.github/workflows/live-source-check.yml">Workflow</a></td></tr>
<tr><td>Historical retailer statements do not prove physical purity, maker mark or independent reputation</td><td>Unverified; no purchase approval. A stamp alone is insufficient.</td><td><a href="https://consumer.ftc.gov/articles/buying-platinum-gold-and-silver-jewelry">Official FTC consumer guidance (re-opened this session)</a></td></tr>
</tbody></table></div></section>
<section class="section"><h2>Every candidate, reviewed without filling unknowns</h2><!-- current-evidence -->
<p>Historical evidence timestamp and state are shown only for provenance. Blank current price does not mean free or unavailable.
All rows need a current official quote and independent gold verification before purchase.</p>
<div class="table-wrap"><table><thead><tr><th>ID</th><th>Seller</th><th>Product</th><th>Session runner observation</th><th>Current verified price (USD)</th><th>Current status</th><th>Prior evidence</th><th>Prior flags</th><th>Official source</th></tr></thead><tbody>'''
    body = body.replace('<!-- current-evidence -->', evidence_note + observations_html)
    body += '\n'.join(rows)
    body += '''</tbody></table></div></section><section class="section"><h2>Before any purchase</h2>
<p>Require an explicit solid-gold description, karat, gram weight and weight scope, maker mark plus hallmark, written return and independent-testing permission (including resize/custom exclusions), and a current configuration-specific price.
Keep the listing and receipt; prefer a credit card. Before wearing or resizing, have an independent jeweler check weight and purity with an appropriate professional test, such as XRF with its limitations explained.
If independent verification and a suitable return are not allowed, do not buy.</p>
<p>The calculator uses a dated benchmark, not a live bullion price or a resale quote. Gross ring weight must not be passed off as metal-only weight when stones or other materials are included.</p></section></main></body></html>'''
    (ROOT / 'pages/session-review.html').write_text(body, encoding='utf-8')
    print(f'Published {len(rows)} sourced rows; current verified prices: 0 (all blank).')


if __name__ == '__main__':
    build()
