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
    rows = []
    for ring in rings:
        prior = states.get(ring['id'], {})
        flags = ', '.join(ring.get('flags', [])) or 'No historical flags recorded; not purchase approval'
        rows.append(f'''<tr data-review-id="{esc(ring['id'])}">
<td>{esc(ring['id'])}</td><td>{esc(ring['retailer'])}</td>
<td>{esc(ring['product_name'])}</td>
<td class="current-price" aria-label="Unverified current price"></td>
<td>UNVERIFIED — no current-session configuration-specific quote</td>
<td>{esc(prior.get('checked_utc', 'Not checked'))}<br>{esc(prior.get('source_state', 'NOT_CHECKED'))} / {esc(prior.get('price_state', 'NOT_CHECKED'))} (historical evidence only)</td>
<td>{esc(flags)}</td><td><a href="{esc(ring['url'])}" target="_blank" rel="noopener noreferrer">Official product</a></td></tr>''')
    body = '''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Current-session review · GOLD4</title><link rel="stylesheet" href="../assets/style.css"></head>
<body><header class="site-header"><div class="wrap bar"><a class="brand" href="../index.html">Au · GOLD4</a>
<nav class="main"><a href="../index.html">Dashboard</a><a href="flagged.html">Flagged for Review</a><a href="freshness.html">Historical evidence</a><a href="calculator.html">Calculator</a></nav></div></header>
<main class="wrap"><section class="hero"><span class="eyebrow">Review date: 23 October 2026 · session 986df4df</span>
<h1>Current-session review — Flagged for Review</h1>
<p class="lede">NO HALLUCINATIONS: unconfirmed current prices stay blank. This is a candidate register, not an approved purchase list or a complete inventory of rings available online.</p></section>
<div class="nohall"><h2>What this session can actually verify</h2>
<p>The sandbox cannot directly access retailer or regulator hosts. Existing dated captures are preserved as historical claims, not newly verified facts.
A successful HTTP response or a matching structured-data price does not prove the selected size, metal, stone, availability, taxes, shipping, or actual gold purity.
No current price, weight, hallmark or seller reputation is inferred here. All current-price cells below are intentionally empty.</p>
<p>Internal arithmetic, citation and security gates test specific rules; passing them is not proof that a claim is true or that all hallucinations have been found.
<strong>Recommend a hallucination review after every review and before buying.</strong> Compare each field against its official source and keep a dated copy.</p>
<p>See the <a href="../reviews/session-986df4df.md">session findings and limitations</a>, <a href="../reports/session-986df4df-checks.txt">executed gate log</a>,
<a href="../data/source_health.json">prior source evidence summary</a>, and <a href="../reports/live_source_check_latest.json">prior raw evidence</a>.
No stored product price, weight or purity has been changed in this session.</p></div>
<section class="section"><h2>Security / hallucination irregularities</h2><div class="table-wrap"><table>
<thead><tr><th>Finding</th><th>Disposition</th><th>Source / review link</th></tr></thead><tbody>
<tr><td>Missing currency was treated as USD in the price reconciler</td><td>Fixed: only explicit USD qualifies. Legacy CONFIRMED states remain historical, not re-certified.</td><td><a href="https://github.com/karagemop466-tech/GOLD4/blob/arena/986df4df-gold4/scripts/build_source_health.py">Reconciler code</a></td></tr>
<tr><td>Permissive numeric parsing could turn signed/currency text into another amount</td><td>Fixed: reject negatives, nonfinite values and ambiguous formatted text. Regression tests added.</td><td><a href="https://github.com/karagemop466-tech/GOLD4/blob/arena/986df4df-gold4/scripts/test_assurance.py">Regression tests</a></td></tr>
<tr><td>Source-check workflow wrote to PR branches and interpolated a branch name into shell</td><td>Fixed: read-only token, upload artifacts only; no branch-writing shell step.</td><td><a href="https://github.com/karagemop466-tech/GOLD4/blob/arena/986df4df-gold4/.github/workflows/live-source-check.yml">Workflow</a></td></tr>
<tr><td>Historical retailer statements do not prove physical purity, maker mark or independent reputation</td><td>Unverified; no purchase approval. A stamp alone is insufficient.</td><td><a href="https://consumer.ftc.gov/articles/buying-platinum-gold-and-silver-jewelry">Official FTC consumer guidance (not re-fetched this session)</a></td></tr>
</tbody></table></div></section>
<section class="section"><h2>Every candidate, reviewed without filling unknowns</h2>
<p>Historical evidence timestamp and state are shown only for provenance. Blank current price does not mean free or unavailable.
All rows need a current official quote and independent gold verification before purchase.</p>
<div class="table-wrap"><table><thead><tr><th>ID</th><th>Seller</th><th>Product</th><th>Current verified price (USD)</th><th>Current status</th><th>Prior evidence</th><th>Prior flags</th><th>Official source</th></tr></thead><tbody>'''
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
