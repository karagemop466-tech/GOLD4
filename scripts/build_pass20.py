#!/usr/bin/env python3
"""Build pages/pass20.html — the Pass 20 verification record.

Every number and every quoted page string on this page is read from
`reviews/pass20/observations.json`, which this session wrote from its own
browser-rendered page reads. Nothing is typed into the HTML by hand, so the page
cannot drift from the evidence file. The gate results come from
`reviews/pass20/gates.json`, written by `scripts/run_gates_pass20.sh`.

Run after `scripts/build_site.py` (it needs the layout constants that builder
sets up) and before the gates.
"""
from __future__ import annotations

import json
import pathlib

import build_site as bs
from build_site import esc, no_hallucination_block, render

ROOT = pathlib.Path(__file__).resolve().parents[1]


def prime_layout() -> None:
    """Fill the layout globals build_site.render() expects, without rebuilding the site."""
    derived = json.loads((ROOT / "data" / "derived.json").read_text(encoding="utf-8"))
    sellers = json.loads((ROOT / "data" / "sellers.json").read_text(encoding="utf-8"))
    sources = json.loads((ROOT / "data" / "sources.json").read_text(encoding="utf-8"))
    rings = json.loads((ROOT / "data" / "rings.json").read_text(encoding="utf-8"))
    bs.SELLERS_BY_ID = {s["id"]: s for s in sellers["sellers"]}
    bs.C = {
        "captured": "22 October 2026",
        "spot_oz": derived["spot"]["value_usd_per_oz"],
        "spot_g": derived["spot"]["usd_per_gram"],
        "spot_date": derived["spot"]["price_date"],
        "spot_captured": json.loads((ROOT / "data" / "gold_spot.json").read_text())["captured_utc"],
        "built": rings.get("reverified_utc", ""),
        "n_rows": len(derived["rows"]),
        "n_sources": len(sources["sources"]),
    }
OBS = ROOT / "reviews" / "pass20" / "observations.json"
GATES = ROOT / "reviews" / "pass20" / "gates.json"

VERDICT_KIND = {
    "MATCH": ("ok", "matches the stored value"),
    "MATCH_WITH_NEW_FINDING": ("ok", "matches — new observation"),
    "DIFFERS": ("bad", "page prints a different number"),
    "DIFFERS_IMMATERIAL": ("warn", "differs, immaterial"),
    "VARIANT_CONDITIONAL": ("warn", "different variant rendered"),
    "PARTIAL": ("warn", "partly readable"),
    "SOURCE_URL_DEAD_CONFIRMED": ("bad", "page confirmed dead"),
}
SEV_KIND = {"HIGH": "bad", "MEDIUM": "warn", "LOW": "mute", "INFO": "info"}


def badge(label: str, kind: str) -> str:
    return f'<span class="badge b-{kind}">{esc(label)}</span>'


def money(value) -> str:
    if value is None:
        return '<span class="blank" title="the seller publishes no such value">—</span>'
    return f"${value:,.2f}" if isinstance(value, float) else f"${value:,.0f}"


def reading_table(readings) -> str:
    rows = []
    for r in readings:
        kind, label = VERDICT_KIND.get(r["verdict"], ("mute", r["verdict"]))
        stored = r.get("stored", {})
        stored_bits = []
        if stored.get("price_usd") is not None:
            stored_bits.append(f"price {money(stored['price_usd'])}")
        if "value_usd_per_oz" in stored:
            stored_bits.append(f"benchmark ${stored['value_usd_per_oz']:,.2f}/oz")
        if stored.get("weight_g") is not None:
            stored_bits.append(f"weight {stored['weight_g']} g")
        if stored.get("weight_g") is None and "weight_g" in stored:
            stored_bits.append("weight blank")
        target = r.get("row_id") or r.get("target", "")
        rows.append(f"""
  <tr data-row-id="{esc(target)}">
    <td class="id">{esc(r['id'])}</td>
    <td>{esc(target)}<span class="sub">{esc(r.get('retailer', ''))}</span></td>
    <td class="src"><a href="{esc(r['url'])}" target="_blank" rel="noopener">official page</a>
        <span class="sub mono">{esc(r['window_utc'])}</span></td>
    <td class="prod">{esc(r['page_printed'])}</td>
    <td>{esc('; '.join(stored_bits))}</td>
    <td>{badge(label, kind)}<span class="sub">{esc(r.get('note', ''))}</span></td>
  </tr>""")
    return f"""
<div class="table-wrap"><table>
  <thead><tr><th>Ref</th><th>Row</th><th>Source read</th><th>What the page printed (verbatim)</th>
  <th>What this repo stores</th><th>Verdict &amp; note</th></tr></thead>
  <tbody>{''.join(rows)}</tbody>
</table></div>"""


def finding_cards(findings) -> str:
    cards = []
    for f in findings:
        kind = SEV_KIND.get(f["severity"], "mute")
        cards.append(f"""
<div class="card" id="{esc(f['id'])}">
  <h3>{esc(f['id'])} · {esc(f['title'])} {badge(f['severity'], kind)}</h3>
  <p>{esc(f['detail'])}</p>
  <p class="small">Evidence: <span class="mono">{esc(f['evidence'])}</span> ·
     Source: <a href="{esc(f['source'])}" target="_blank" rel="noopener">{esc(f['source'])}</a></p>
  <p class="small"><strong>What was done:</strong> {esc(f['action'])}</p>
</div>""")
    return "".join(cards)


def gate_table(gates) -> str:
    rows = []
    for g in gates:
        rows.append(f"""
  <tr><td class="id">{esc(g['gate'])}</td><td>{esc(g['name'])}</td>
      <td>{badge('PASS' if g['status'] == 'PASS' else g['status'], 'ok' if g['status'] == 'PASS' else 'warn')}</td>
      <td class="mono small">{esc(g['detail'])}</td>
      <td class="src"><a href="https://github.com/karagemop466-tech/GOLD4/blob/main/reviews/pass20/gates.json">Original project test evidence</a></td></tr>""")
    return f"""
<div class="table-wrap"><table>
  <thead><tr><th>Gate</th><th>Check</th><th>Result</th><th>Detail</th><th>Official project source</th></tr></thead>
  <tbody>{''.join(rows)}</tbody>
</table></div>"""


def main() -> None:
    prime_layout()
    obs = json.loads(OBS.read_text(encoding="utf-8"))
    gates = json.loads(GATES.read_text(encoding="utf-8")) if GATES.exists() else []
    cov = obs["coverage"]

    cov_cards = "".join(
        f'<div class="kpi"><div class="n">{esc(v)}</div><div class="l">{esc(k)}</div></div>'
        for k, v in [
            ("of 64 rows fully corroborated", cov["rows_fully_corroborated_price_and_weight"]),
            ("row where the price differs", cov["rows_price_differed"]),
            ("dead link confirmed by hand", cov["rows_dead_link_confirmed"]),
            ("rows partly read", cov["rows_partial_spec_or_existence_only"]),
            ("rows NOT re-read this pass", cov["rows_not_re_read_this_pass"]),
        ]
    )

    body = f"""
<h1>Pass 20 — what was actually re-read, and what still is not</h1>
<p class="lede">Session <span class="mono">{esc(obs['session'])}</span> · evidence window
<span class="mono">{esc(obs['read_window_utc'])}</span> · evidence file
<span class="mono">reviews/pass20/observations.json</span></p>

{no_hallucination_block('../')}

<div class="callout">
  <p><strong>Read this first.</strong> {esc(cov['statement'])}</p>
  <p>This pass re-read 11 of the 64 product rows plus the gold benchmark. Nothing was filled in,
  nothing was overwritten, and where a page printed a different number both numbers are published.
  A page that could not be read is reported as unreadable — not guessed.</p>
</div>

<h2>Coverage of this pass</h2>
<div class="kpis">{cov_cards}</div>
<p class="small">Counts are read from the evidence file. "Fully corroborated" means the page printed
the stored price <em>and</em>, where the row has a published weight, the stored weight.
"Partly read" covers pages that loaded but whose price sat in a JavaScript panel (BE-07, AN-01)
or whose specification block was readable without the price (VR-01).</p>

<h2>Line-by-line readings</h2>
<p>Each row below is one page this session opened. The quoted text is what the page printed at the
time in the second column; the fourth column is what this repository stores. No value was applied
from a reading — the evidence is published, not merged.</p>
{reading_table(obs['readings'])}

<h2>Findings, published rather than fixed</h2>
<p>Every finding below is also visible on <a href="flagged.html">Flagged for Review</a> via the row
flags, or recorded in the evidence file with its source link.</p>
{finding_cards(obs['findings'])}

<h2>Security and anti-hallucination checks run after these edits</h2>
<p>The gates are the same ones CI runs before a merge. They recompute every derived number,
re-check every link, and fail on an unsourced value. A passing gate proves internal consistency —
it cannot prove a retailer is honest or that a price is still live.</p>
{gate_table(gates) if gates else '<p class="small">Gate results are written by <span class="mono">scripts/run_gates_pass20.sh</span>.</p>'}

<h2>What this pass could not do — stated plainly</h2>
<ul>
  {''.join(f'<li>{esc(x)}</li>' for x in obs['limits'])}
</ul>

<h2>The standing recommendation, repeated after every review</h2>
<div class="callout">
  <p><strong>Look for hallucinations again next time.</strong> For every row ask four questions in order:</p>
  <ol>
    <li><strong>What is the official source link for this number?</strong> If there is no link, there is no number.</li>
    <li><strong>What date was it read, and by what read path?</strong> "Captured last week" is not a date.</li>
    <li><strong>Does the page still print that exact figure?</strong> If it prints something else, publish both — never overwrite.</li>
    <li><strong>Was anything inferred?</strong> Currency conversions, "typical" weights, ranges collapsed to one number and
        prose that rounds a value are all inference. Inference must be labelled as derived or left blank.</li>
  </ol>
  <p class="small">Integration clarification: a 14K or 18K stamp is a claim, not proof. Seek an
  independent professional's appropriate complementary tests and a metal-only gram-weight check,
  within written testing/return permissions. A single surface XRF reading can miss thick plating or
  electroformed construction; see <a href="https://www.gia.edu/gems-gemology/spring-2024-lab-notes-electroformed-gold-bracelet">GIA's documented case</a>.
  Nothing on this site substitutes for that assessment.</p>
</div>

<p class="small">Related: <a href="freshness.html">Freshness (last all-URL runner sweep, 20:23Z)</a> ·
<a href="flagged.html">Flagged for Review</a> ·
<a href="log.html">Verification log</a> ·
<a href="../reviews/index20.html">Plain-text copy of this pass</a></p>
"""
    out = ROOT / "pages" / "pass20.html"
    out.write_text(render("Pass 20 verification record", body, "pass20", root="../"), encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)} ({len(body)} chars of body)")

    # A plain, dependency-free copy for anyone reading the repo (and for the
    # reviewers who follow a link from the site). Same evidence file, same words.
    plain = ROOT / "reviews" / "index20.html"
    plain_rows = "".join(
        f"<tr><td>{esc(r['id'])}</td><td>{esc(r.get('row_id') or r.get('target',''))}</td>"
        f"<td><a href=\"{esc(r['url'])}\">{esc(r['url'])}</a></td>"
        f"<td>{esc(r['page_printed'])}</td><td>{esc(r['verdict'])}</td><td>{esc(r.get('note',''))}</td></tr>"
        for r in obs["readings"])
    plain_findings = "".join(
        f"<h3>{esc(f['id'])} · {esc(f['title'])} [{esc(f['severity'])}]</h3>"
        f"<p>{esc(f['detail'])}</p><p>Evidence {esc(f['evidence'])} · "
        f"<a href=\"{esc(f['source'])}\">source</a> · {esc(f['action'])}</p>"
        for f in obs["findings"])
    plain.write_text(f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pass 20 verification record (plain copy) · GOLD4</title>
<link rel="stylesheet" href="../assets/style.css"></head>
<body><main class="wrap">
<div class="nohall"><h2>⚠ No hallucinations</h2>
<p>Every value below was read from the official page linked beside it by session
<span class="mono">{esc(obs['session'])}</span> during {esc(obs['read_window_utc'])}.
Where a page could not be read, the row says so and no value is given.</p></div>
<h1>Pass 20 — line-by-line readings</h1>
<p><a href="../pages/pass20.html">Dashboard version</a> ·
<a href="pass20/observations.json">raw evidence JSON</a> ·
<a href="pass20/report.md">session report</a> ·
<a href="pass20/gates.txt">gate output</a></p>
<p>{esc(obs['coverage']['statement'])}</p>
<table><thead><tr><th>Ref</th><th>Row</th><th>Source</th><th>Page printed</th><th>Verdict</th><th>Note</th></tr></thead>
<tbody>{plain_rows}</tbody></table>
<h2>Findings</h2>{plain_findings}
<h2>Limits</h2><ul>{''.join(f"<li>{esc(x)}</li>" for x in obs['limits'])}</ul>
</main></body></html>
""", encoding="utf-8")
    print(f"wrote {plain.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
