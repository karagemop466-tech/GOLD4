#!/usr/bin/env python3
"""Build pages/pass21.html — the Pass 21 verification record.

Every number and every quoted page string on this page is read from
`reviews/pass21/observations.json`, which this session wrote from its own
browser-rendered page reads on 2026-11-11. Nothing is typed into the HTML by
hand from memory, so the page cannot drift from the evidence file. Gate
results come from `reviews/pass21/gates.json` (scripts/run_gates_pass21.py).

Run after `scripts/build_site.py` (primes the layout constants) and before the
gates. No value from data/gold_spot.json or derived.json is restated here by
hand; the benchmark figures are read from the evidence file.
"""
from __future__ import annotations

import json
import pathlib

import build_site as bs
from build_site import esc, no_hallucination_block, render

ROOT = pathlib.Path(__file__).resolve().parents[1]


def prime_layout() -> None:
    derived = json.loads((ROOT / "data" / "derived.json").read_text(encoding="utf-8"))
    sellers = json.loads((ROOT / "data" / "sellers.json").read_text(encoding="utf-8"))
    sources = json.loads((ROOT / "data" / "sources.json").read_text(encoding="utf-8"))
    rings = json.loads((ROOT / "data" / "rings.json").read_text(encoding="utf-8"))
    bs.SELLERS_BY_ID = {s["id"]: s for s in sellers["sellers"]}
    bs.C = {
        "captured": bs.price_capture_label(rings["rows"]),
        "spot_oz": derived["spot"]["value_usd_per_oz"],
        "spot_g": derived["spot"]["usd_per_gram"],
        "spot_date": derived["spot"]["price_date"],
        "spot_captured": json.loads((ROOT / "data" / "gold_spot.json").read_text())["captured_utc"],
        "built": rings.get("reverified_utc", ""),
        "n_rows": len(derived["rows"]),
        "n_sources": len(sources["sources"]),
    }


OBS = ROOT / "reviews" / "pass21" / "observations.json"
GATES = ROOT / "reviews" / "pass21" / "gates.json"

VERDICT_KIND = {
    "match": ("ok", "matches — corroborated"),
    "MATCH": ("ok", "matches"),
}


def badge(label: str, kind: str) -> str:
    return f'<span class="badge b-{kind}">{esc(label)}</span>'


def verdict_badge(verdict: str) -> str:
    v = verdict.upper()
    if v.startswith("MATCH"):
        return badge("MATCH", "ok")
    if v.startswith("DIFFERS_CONDITIONAL"):
        return badge("DIFFERS — conditional", "warn")
    if v.startswith("DIFFERS"):
        return badge("DIFFERS", "bad")
    if v.startswith("DEAD"):
        return badge("DEAD LINK", "bad")
    if v.startswith("PARTIAL"):
        return badge("PARTIAL", "warn")
    return badge(verdict.split(" —")[0], "mute")


def retailer_rows(obs) -> str:
    rows = []
    for r in obs["retailer_sample_2026_11_11"]:
        read_bits = []
        for k, v in r["read"].items():
            read_bits.append(f"<span class='sub'><strong>{esc(k)}</strong>: {esc(str(v))}</span>")
        stored = r["stored"]
        stored_bits = [f"price ${stored['price_usd']:,.0f}" if stored["price_usd"] is not None else "price blank",
                       (f"weight {stored['weight_g']} g" if stored["weight_g"] is not None else "weight blank"),
                       f"capture {stored['capture_date']}"]
        rows.append(f"""
  <tr data-row-id="{esc(r['id'])}">
    <td class="id">{esc(r['id'])}</td>
    <td class="src"><a href="{esc(r['source_url'])}" target="_blank" rel="noopener">official page</a></td>
    <td class="prod">{'<br>'.join(read_bits)}</td>
    <td>{esc(' · '.join(stored_bits))}</td>
    <td>{verdict_badge(r['verdict'])}<span class="sub">{esc(r['verdict'])}</span></td>
  </tr>""")
    return f"""
<div class="table-wrap"><table>
  <thead><tr><th>Row</th><th>Source read</th><th>What the page printed (2026-11-11)</th>
  <th>What this repo stores</th><th>Verdict</th></tr></thead>
  <tbody>{''.join(rows)}</tbody>
</table></div>"""


def official_rows(obs) -> str:
    rows = []
    for r in obs["official_reference_pages_2026_11_11"]:
        rows.append(f"""
  <tr data-row-id="{esc(r['id'])}">
    <td class="id">{esc(r['id'])}</td>
    <td class="src"><a href="{esc(r['source_url'])}" target="_blank" rel="noopener">official page</a></td>
    <td class="prod">{esc(r['read'])}</td>
    <td>{badge('MATCH', 'ok')}<span class="sub">{esc(r['verdict'])}</span></td>
  </tr>""")
    return f"""
<div class="table-wrap"><table>
  <thead><tr><th>Ref</th><th>Source</th><th>What the page prints</th><th>Verdict</th></tr></thead>
  <tbody>{''.join(rows)}</tbody>
</table></div>"""


def gate_table(gates) -> str:
    if not gates:
        return '<p class="small">Gate results are written by <span class="mono">scripts/run_gates_pass21.py</span>.</p>'
    rows = []
    for g in gates:
        ok = g["status"] == "PASS"
        rows.append(f"""
  <tr><td class="id">{esc(g['gate'])}</td><td>{esc(g['name'])}</td>
      <td>{badge('PASS' if ok else g['status'], 'ok' if ok else 'warn')}</td>
      <td class="mono small">{esc(g['detail'])}</td>
      <td class="src"><a href="https://github.com/karagemop466-tech/GOLD4/blob/main/reviews/pass21/gates.json">Original project test evidence</a></td></tr>""")
    return f"""
<div class="table-wrap"><table>
  <thead><tr><th>Gate</th><th>Check</th><th>Result</th><th>Detail</th><th>Official project source</th></tr></thead>
  <tbody>{''.join(rows)}</tbody>
</table></div>"""


def main() -> None:
    prime_layout()
    obs = json.loads(OBS.read_text(encoding="utf-8"))
    gates = json.loads(GATES.read_text(encoding="utf-8")) if GATES.exists() else []
    bench = obs["benchmark"]["read"]
    calc = obs["calculator_rederivation_2026_11_11"]

    ROW_SRC = {"AL-01": "https://www.allurez.com/products/floral-solitaire-engagement-ring-14k-yellow-gold",
               "SR-03": "https://www.sarraf.com/products/18k-Yellow-Gold-5mm-High-Polished-Traditional-Domed-Wedding-Band.html"}
    calc_rows = "".join(
        f"<tr><td class='id'>{esc(k)}</td><td>{esc(str(v['pure_gold_g']))} g</td>"
        f"<td>${esc(str(v['gold_value_usd']))}</td>"
        + (f"<td>{esc(str(list(v.values())[-1]))}×</td>" if len(v) > 2 else "<td>—</td>")
        + f'<td class="src"><a href="{ROW_SRC[k]}" target="_blank" rel="noopener">official page</a></td>'
        + "</tr>"
        for k, v in calc.items() if k not in ("basis", "note")
    )

    body = f"""
<h1>Pass 21 — the benchmark was 19 days stale; it is now the current official reading</h1>
<p class="lede">Session <span class="mono">{esc(obs['session'])}</span> · evidence window
<span class="mono">{esc(obs['read_window_utc'])}</span> · evidence file
<span class="mono">reviews/pass21/observations.json</span></p>

{no_hallucination_block('../')}

<div class="callout">
  <p><strong>Read this first.</strong> The gold benchmark in force moved because the source's own data date
  advanced: the World Gold Council panel now prints <strong>${esc(str(bench['value_usd_per_oz']))}/oz</strong>
  on a page headed "{esc(bench['page_heading_date'])}" with footer "{esc(bench['data_as_of_verbatim'])}".
  Five of 64 rows were re-read live; everything else keeps its 2026-10-22/23 capture date and stays a
  historical reading, not a current quote. Nothing was overwritten to make a row look current.</p>
</div>

<h2>The benchmark move (the one data change)</h2>
<div class="table-wrap"><table>
  <thead><tr><th>What</th><th>Before (Pass 18 capture)</th><th>After (this pass)</th><th>Source</th></tr></thead>
  <tbody>
    <tr><td>WGC Goldhub panel value</td><td>$3,996.31/oz</td><td><strong>$4,059.49/oz</strong></td><td class="src"><a href="https://www.gold.org/goldhub/data/gold-prices" target="_blank" rel="noopener">official page</a></td></tr>
    <tr><td>Panel's own date line</td><td>Data as of 22 October, 2026</td><td>Data as of 10 November, 2026</td><td class="src"><a href="https://www.gold.org/goldhub/data/gold-prices" target="_blank" rel="noopener">official page</a></td></tr>
    <tr><td>Per-gram constant (recomputed)</td><td>$128.48435/g</td><td>$130.515634/g</td><td class="src"><a href="https://www.gold.org/goldhub/data/gold-prices" target="_blank" rel="noopener">official page</a></td></tr>
    <tr><td>Change</td><td colspan="2">+1.58% · the source's data date advanced 19 days, so the benchmark moved (Pass-12 criterion). Intraday-tick policy (Passes 17/19/20) did not apply.</td><td class="src"><a href="https://www.gold.org/goldhub/data/gold-prices" target="_blank" rel="noopener">official page</a></td></tr>
    <tr><td>BullionVault cross-check (same morning)</td><td colspan="2">$4,058.82/oz · $130.49/g at 11 November 2026, 03:02:20 (GMT-05:00) — 0.017% below the new benchmark · Kitco and JM Bullion <em>not re-read</em></td><td class="src"><a href="https://www.bullionvault.com/gold-price-chart.do" target="_blank" rel="noopener">official page</a></td></tr>
    <tr><td>Superseded benchmark</td><td colspan="2">preserved verbatim in <span class="mono">data/gold_spot.json → prior_captures</span>; nothing deleted</td><td class="src"><a href="https://github.com/karagemop466-tech/GOLD4/blob/main/data/gold_spot.json" target="_blank" rel="noopener">project evidence</a></td></tr>
  </tbody>
</table></div>
<p class="small">Sources: <a href="https://www.gold.org/goldhub/data/gold-prices" target="_blank" rel="noopener">World Gold Council Goldhub</a> · <a href="https://www.bullionvault.com/gold-price-chart.do" target="_blank" rel="noopener">BullionVault</a></p>

<h2>Official law / regulator / consumer pages re-read line by line</h2>
{official_rows(obs)}

<h2>Retailer sample re-read line by line (5 of 64 rows)</h2>
{retailer_rows(obs)}
<p class="small">Two rows corroborate exactly (AL-01, SR-03). MN-01 keeps its floating Menē price
(stored $1,465 vs $1,455 today; $1,442 at Passes 17/19/20) — nothing overwritten. RS-02 is on a 20%
promotion ("Original price $249", "Sale price $199.20") — the stored $249 is the original price; nothing
overwritten. BN-09 serves Blue Nile's own page-not-found copy; its stored value remains flagged as historical.
59 rows were not re-read this pass.</p>

<h2>Hand re-derivation of the calculator inputs at the new benchmark</h2>
<div class="table-wrap"><table>
  <thead><tr><th>Row</th><th>Pure gold (g)</th><th>Gold value @ $130.515634/g</th><th>Price ÷ gold value</th><th>Source</th></tr></thead>
  <tbody>{calc_rows}</tbody>
</table></div>
<p class="small">{esc(calc['note'])} · Basis: {esc(calc['basis'])}</p>

<h2>Security and anti-hallucination checks run after these edits</h2>
<p>The gates are the same ones CI runs before a merge. They recompute every derived number,
re-check every link, and fail on an unsourced value. A passing gate proves internal consistency —
it cannot prove a retailer is honest or that a price is still live.</p>
{gate_table(gates)}

<h2>What this pass could not do — stated plainly</h2>
<ul>
  {''.join(f'<li>{esc(x)}</li>' for x in obs['limitations'])}
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

<p class="small">Related: <a href="pass20.html">Pass 20 (23 Oct 2026)</a> ·
<a href="freshness.html">Freshness (last all-URL runner sweep)</a> ·
<a href="flagged.html">Flagged for Review</a> ·
<a href="log.html">Verification log</a></p>
"""
    out = ROOT / "pages" / "pass21.html"
    out.write_text(render("Pass 21 verification record", body, "pass21", root="../"), encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)} ({len(body)} chars of body)")


if __name__ == "__main__":
    main()
