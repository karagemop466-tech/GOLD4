#!/usr/bin/env python3
"""Build pages/pass21.html — the Pass 21 record (2026-11-11, session arena/4fe4a9c3-gold4).

NO HALLUCINATIONS. Every price, weight, count and quoted page string on the page is
read from committed files, never typed here:

  reviews/pass21/reconciliation.json   per-row verdicts (written by scripts/pass21_apply.py)
  reviews/pass21/hand_reads.json       this session's hand reads, verbatim
  reviews/pass21/gates.json            gate results (written by scripts/run_gates_pass21.py)
  data/rings.json, data/gold_spot.json, data/source_health.json, data/derived.json

Run after scripts/build_site.py.
"""
from __future__ import annotations

import json
import pathlib

import build_site as bs
from build_pass20 import prime_layout
from build_site import esc, no_hallucination_block, render

ROOT = pathlib.Path(__file__).resolve().parents[1]
P21 = ROOT / "reviews" / "pass21"
GH = "https://github.com/karagemop466-tech/GOLD4/blob/main/"

VERDICT = {
    "UNCHANGED": ("ok", "same price as October"),
    "SALE": ("warn", "sale price — temporary"),
    "CHANGED": ("warn", "price changed"),
    "SOURCE_DEAD": ("bad", "page gone — price blank"),
    "SOLD_OUT": ("bad", "sold out — price blank"),
    "NOT_REREAD": ("bad", "not re-read"),
}


def load(path: pathlib.Path):
    return json.loads(path.read_text(encoding="utf-8"))


def badge(label: str, kind: str) -> str:
    return f'<span class="badge b-{kind}">{esc(label)}</span>'


def money(v) -> str:
    if v is None:
        return '<span class="blank" title="no value could be confirmed">—</span>'
    v = float(v)
    return f"${v:,.0f}" if abs(v - round(v)) < 0.005 else f"${v:,.2f}"


def read_path_label(d: dict) -> str:
    hand = any("hand read" in p for p in d["read_paths"])
    run = any(p.startswith("runner") for p in d["read_paths"])
    if hand and run:
        return "runner + hand read"
    if hand:
        return "hand read"
    if run:
        return "runner"
    return "none"


def row_table(decisions: list[dict], rings: dict, derived: dict, only=None) -> str:
    out = []
    for d in decisions:
        if only and d["verdict"] not in only:
            continue
        r, dr = rings[d["id"]], derived[d["id"]]
        kind, label = VERDICT[d["verdict"]]
        priced = [q for q in d["quotes"] if "$" in q] or d["quotes"]
        quote = priced[0] if priced else ""
        before = money(d["stored_price_usd"])
        today = money(d["price_today_usd"])
        if d.get("list_price_usd") and d["verdict"] == "SALE":
            today += f'<span class="sub">list <s>{money(d["list_price_usd"])}</s></span>'
        w = (f'{r["weight_g"]:g} g' + ('<span class="sub">re-read 11 Nov</span>' if d["weight_reread_today"] else '<span class="sub">October read</span>')
             if r.get("weight_g") is not None else '<span class="blank">—</span><span class="sub">not published</span>')
        mult = dr.get("price_to_gold_multiple")
        notes = " ".join(d["notes"])
        out.append(f"""
  <tr data-row-id="{esc(d['id'])}" data-search="{esc((d['id'] + ' ' + r['retailer'] + ' ' + r['product_name'] + ' ' + d['verdict']).lower())}">
    <td class="id">{esc(d['id'])}</td>
    <td class="prod"><a href="{esc(r['url'])}" target="_blank" rel="noopener">{esc(r['product_name'])}</a>
        <span class="sub">{esc(r['retailer'])} · {esc(r['metal_label'])}</span></td>
    <td class="num">{before}<span class="sub">{esc(d['stored_price_captured_utc'] or '')}</span></td>
    <td class="num">{today}</td>
    <td>{badge(label, kind)}<span class="sub">{esc(read_path_label(d))}</span></td>
    <td class="num">{w}</td>
    <td class="num">{f'{mult:.2f}×' if mult else '<span class="blank">—</span>'}</td>
    <td class="small">{('<span class="mono">' + esc(quote) + '</span>') if quote else ''}{('<br>' + esc(notes)) if notes else ''}</td>
    <td class="src"><a href="{esc(r['url'])}" target="_blank" rel="noopener">official page</a></td>
  </tr>""")
    return f"""
<div class="table-wrap"><table>
  <thead><tr><th>ID</th><th>Ring</th><th class="num">Before (October)</th><th class="num">Read 11 Nov 2026</th>
  <th>Verdict · read path</th><th class="num">Weight</th><th class="num">Price ÷ gold</th>
  <th>What the page printed (verbatim) · notes</th><th>Source</th></tr></thead>
  <tbody>{''.join(out)}</tbody>
</table></div>"""


def ids(decisions, verdict) -> list[str]:
    return [d["id"] for d in decisions if d["verdict"] == verdict]


def main() -> None:
    prime_layout()
    rec = load(P21 / "reconciliation.json")
    hand = load(P21 / "hand_reads.json")
    gates = load(P21 / "gates.json") if (P21 / "gates.json").exists() else []
    rings_doc = load(ROOT / "data" / "rings.json")
    rings = {r["id"]: r for r in rings_doc["rows"]}
    derived = {r["id"]: r for r in load(ROOT / "data" / "derived.json")["rows"]}
    spot = load(ROOT / "data" / "gold_spot.json")
    health = load(ROOT / "data" / "source_health.json")
    dec = rec["rows"]
    vc = rec["verdict_counts"]
    n = len(dec)

    b = spot["benchmark"]
    prev = [p for p in spot["prior_captures"] if p.get("status") == "superseded"][-1]
    delta = (b["value_usd_per_oz"] / prev["value_usd_per_oz"] - 1) * 100
    usd_g = spot["constants"]["spot_usd_per_gram"]
    oz_g = spot["constants"]["troy_ounce_grams"]

    cross = "".join(f"""
  <tr><td>{esc(c['label'])}</td><td class="num">${c['value_usd_per_oz']:,.2f}</td>
      <td class="num">{c['spread_vs_benchmark_pct']:+.2f}%</td><td class="mono small">{esc(c['verbatim'])}</td>
      <td class="mono small">{esc(c['retrieved_utc'])}</td>
      <td class="src"><a href="{esc(c['source_url'])}" target="_blank" rel="noopener">official page</a></td></tr>"""
                    for c in spot.get("pass21_cross_checks", []))

    by_id = {d["id"]: d for d in dec}
    sale_bn = [i for i in ids(dec, "SALE") if i.startswith("BN-")]
    sale_rs = [i for i in ids(dec, "SALE") if i.startswith("RS-")]
    changed = ids(dec, "CHANGED")
    dead = ids(dec, "SOURCE_DEAD")
    sold = ids(dec, "SOLD_OUT")
    notread = ids(dec, "NOT_REREAD")
    lag = [r["id"] for r in rings.values() if "STRUCTURED_PRICE_LAGS_DISPLAY" in r["flags"]]
    oct_sweep = {r["key"]: r["classification"] for r in load(ROOT / "reports" / "live_source_check_20261023T202321Z.json")["results"]}
    dead_before = [i for i in dead if oct_sweep.get(i) == "HTTP_404"]
    hand_ids = [h["id"] for h in hand["rows"]]
    blocked = [h["id"] for h in health["rows"] if h["source_state"] in ("REFUSED_403", "REFUSED_429")]
    w_rows = [r["id"] for r in rings.values() if r.get("weight_g") is not None]
    w_not = [i for i in w_rows if not by_id[i]["weight_reread_today"]]

    def link(i: str) -> str:
        return f'<a href="{esc(rings[i]["url"])}" target="_blank" rel="noopener">{esc(i)}</a>'

    def links(lst) -> str:
        return ", ".join(link(i) for i in lst) or "none"

    def change_line(i: str) -> str:
        d = by_id[i]
        return f"{link(i)} {money(d['stored_price_usd'])} → {money(d['price_today_usd'])}"

    findings = [
        ("HIGH", "Two site-wide sales make the October prices wrong today",
         f"Blue Nile prints a 20% discount on {len(sale_bn)} settings in this list and Ross-Simons prints a sale price on {len(sale_rs)} rings. "
         "The table now shows the sale price that was read, with the list price struck through beside it. A sale price is temporary: "
         "it can end without notice, so treat the list price as the stable figure.",
         f"Blue Nile: {links(sale_bn)}. Ross-Simons: {links(sale_rs)}.", "SALE_PRICE_TEMPORARY"),
        ("HIGH", f"The automated price check would have confirmed {len(lag)} stale prices",
         f"On {len(lag)} Ross-Simons pages the visible text prints the sale price while the page's machine-readable data still carries the "
         "pre-sale amount. The repo's rule marks a price CONFIRMED when the machine-readable amount equals the stored one, so a check on "
         "11 November would have reported the October prices as confirmed although the page displayed lower ones. "
         "A CONFIRMED state is therefore evidence about the page's metadata, not about the price a shopper sees.",
         f"{links(lag)}. Each was compared with the visible page text.", "STRUCTURED_PRICE_LAGS_DISPLAY"),
        ("HIGH", "Prices changed with no sale label",
         "These pages print a different price from October and show no strikethrough or sale wording in the part that was read: "
         + "; ".join(change_line(i) for i in changed) + ". The two Menē prices float with the gold price, so they change daily.",
         f"{links(changed)}.", "PRICE_CHANGED_PASS21"),
        ("HIGH", "Pages that are gone: the current price is blank",
         f"{len(dead)} product pages no longer exist. The price cell is blank and the last value read is shown beside it with its October date. "
         f"{len(dead_before)} of them already returned 404 to the runner on 23 October; {len(dead) - len(dead_before)} is new this pass.",
         f"{links(dead)}.", "SOURCE_DEAD_PASS21"),
        ("MEDIUM", "Sold out: the current price is blank",
         "The page reports the item as sold out and offers no purchasable price.",
         f"{links(sold)}.", "SOLD_OUT_PASS21"),
        ("MEDIUM", "Rows the runner cannot read rest on one read path",
         f"The retailer's bot protection refused or rate-limited the GitHub runner on {len(blocked)} rows. Where a price is shown for them it comes from this "
         "session's hand read alone, with no second path to corroborate it.",
         f"{links(blocked)}.", "SOURCE_BOT_BLOCKED"),
        ("MEDIUM", "Not re-read at all",
         "No price or weight evidence was obtained for these rows on 11 November. They keep their October state.",
         f"{links(notread)}.", "PRICE_NOT_REREAD_PASS21"),
        ("MEDIUM", "Gram weights were re-read for only part of the list",
         f"{len(w_rows)} rows publish a gram weight. The weight was seen again on 11 November for {len(w_rows) - len(w_not)} of them. "
         "The others keep their October weight; the price-to-gold figure for those rows mixes a November price with an October weight.",
         f"Not re-read: {links(w_not)}.", "weight"),
        ("LOW", "A provenance bug in the tooling was fixed",
         "The script that stamps runner evidence into the dataset wrote \"Pass 15\" and that session's name into every row regardless of "
         "which pass ran it, and the freshness gate looked for that literal text. Both now take the pass label from the pass that runs them. "
         "No stored value was affected.",
         "scripts/apply_source_health.py, scripts/audit_freshness.py", "tooling"),
        ("LOW", "A workflow was temporarily given write access to retrieve the evidence",
         "The sandbox cannot download runner artifacts, so for one commit the source-check workflow was allowed to commit its raw evidence "
         "file to this branch. A security test (Gate 8) failed while that was in place, as it is designed to. The workflow was restored to its read-only "
         "form, byte-identical to main, before any data was changed.",
         ".github/workflows/live-source-check.yml", "process"),
    ]
    sev_kind = {"HIGH": "bad", "MEDIUM": "warn", "LOW": "mute"}
    finding_html = "".join(f"""
<div class="card" id="F21-{i:02d}">
  <h3>F21-{i:02d} · {esc(title)} {badge(sev, sev_kind[sev])}</h3>
  <p>{detail}</p>
  <p class="small"><strong>Rows / files:</strong> {where}</p>
</div>""" for i, (sev, title, detail, where, _flag) in enumerate(findings, start=1))

    src_rows = "".join(f"""
  <tr><td class="id">{esc(s['id'])}</td><td>{esc(s.get('tier') or '')}</td><td>{esc(s['publisher'])}</td>
      <td>{badge(s['source_state'], 'ok' if s['source_state'] == 'OK' else 'warn')}</td>
      <td class="num">{s.get('http_status') if s.get('http_status') is not None else '—'}</td>
      <td class="src"><a href="{esc(s['url'])}" target="_blank" rel="noopener">{esc(bs.short_url(s['url']))}</a></td></tr>"""
                       for s in health["sources"])

    gate_rows = "".join(f"""
  <tr><td class="id">{esc(g['gate'])}</td><td>{esc(g['name'])}</td>
      <td>{badge(g['status'], 'ok' if g['status'] == 'PASS' else 'bad')}</td>
      <td class="mono small">{esc(g['detail'])}</td>
      <td class="src"><a href="{GH}reviews/pass21/gates.json">project test evidence</a></td></tr>""" for g in gates)

    body = f"""
<section class="hero">
  <span class="eyebrow">Pass 21 · 11 November 2026 · session arena/4fe4a9c3-gold4</span>
  <h1>Re-verification after 19 days: what changed, and what could not be re-read.</h1>
  <p class="lede">The prices on this site were read on 22 and 23 October 2026. On 11 November a GitHub runner re-opened all {n} ring pages
  and this session hand-read {len(hand_ids)} of them. {rec['rows_with_price_read_today']} prices were read again;
  {vc.get('SALE', 0) + vc.get('CHANGED', 0)} of those differ from October. {vc.get('SOURCE_DEAD', 0) + vc.get('SOLD_OUT', 0)} rows now show a blank price.
  The gold benchmark moved {delta:+.2f}%.</p>
</section>
{no_hallucination_block('../')}

<div class="kpis">
  <div class="kpi"><div class="n">{vc.get('UNCHANGED', 0)}</div><div class="l">prices unchanged</div><div class="s">page printed the October amount</div></div>
  <div class="kpi"><div class="n">{vc.get('SALE', 0)}</div><div class="l">temporary sale prices</div><div class="s">list price shown beside each</div></div>
  <div class="kpi"><div class="n">{vc.get('CHANGED', 0)}</div><div class="l">prices changed</div><div class="s">no sale label on the page</div></div>
  <div class="kpi"><div class="n">{vc.get('SOURCE_DEAD', 0) + vc.get('SOLD_OUT', 0)}</div><div class="l">blank prices</div><div class="s">{vc.get('SOURCE_DEAD', 0)} pages gone · {vc.get('SOLD_OUT', 0)} sold out</div></div>
  <div class="kpi"><div class="n">{vc.get('NOT_REREAD', 0)}</div><div class="l">not re-read</div><div class="s">keeps its October state</div></div>
  <div class="kpi gold"><div class="n">${b['value_usd_per_oz']:,.2f}</div><div class="l">gold per troy ounce</div><div class="s">{esc(b['data_as_of_shown_on_source'])}</div></div>
</div>

<section class="section">
  <h2>How to read this page</h2>
  <div class="grid two">
    <div class="card"><h3>Two read paths, both recorded</h3>
      <p><strong>Runner:</strong> a GitHub Actions job fetched every URL at {esc(rec['runner_checked_utc'])} and saved the page text and
      machine-readable prices. <strong>Hand read:</strong> this session opened {len(hand_ids)} pages in a browser-rendered reader between
      08:00 and 08:50 UTC and copied the strings the page printed. Retailers that block the runner could only be read by hand.</p>
      <p class="small">Evidence files: <a href="{GH}reports/live_source_check_20261111T080309Z.json">runner sweep</a> ·
      <a href="{GH}reviews/pass21/hand_reads.json">hand reads</a> ·
      <a href="{GH}reviews/pass21/reconciliation.json">row-by-row reconciliation</a>.</p></div>
    <div class="card"><h3>What the rules were</h3>
      <p>A price was updated only where that day's evidence printed the current amount. The earlier value is kept in the row's history.
      A page that is gone or sold out gets a blank price, never a carried-over one. A row nobody could read keeps its October date and a flag.
      No number was estimated, averaged or converted.</p>
      <p class="small">The update is done by <span class="mono">scripts/pass21_apply.py</span>, which copies values from the two evidence
      files and types none of its own.</p></div>
  </div>
</section>

<section class="section">
  <h2>Gold benchmark</h2>
  <p class="sub">Every gold value on the site is recomputed from this reading: ${b['value_usd_per_oz']:,.2f} ÷ {oz_g} g = ${usd_g:,.4f} per gram.</p>
  <div class="table-wrap"><table>
    <thead><tr><th>Reading</th><th class="num">USD per oz</th><th class="num">vs benchmark</th><th>What the page printed</th><th>Read (UTC)</th><th>Source</th></tr></thead>
    <tbody>
      <tr><td><strong>World Gold Council panel — benchmark in use</strong></td><td class="num"><strong>${b['value_usd_per_oz']:,.2f}</strong></td>
          <td class="num">—</td><td class="mono small">{esc(' · '.join(hand['benchmark']['verbatim']))}</td>
          <td class="mono small">{esc(b['captured_utc'])}</td>
          <td class="src"><a href="{esc(b['source_url'])}" target="_blank" rel="noopener">official page</a></td></tr>
      <tr><td>Previous benchmark (superseded, kept on file)</td><td class="num">${prev['value_usd_per_oz']:,.2f}</td>
          <td class="num">{(prev['value_usd_per_oz'] / b['value_usd_per_oz'] - 1) * 100:+.2f}%</td>
          <td class="mono small">{esc(prev.get('data_as_of_shown_on_source', ''))}</td>
          <td class="mono small">{esc(prev.get('captured_utc', ''))}</td>
          <td class="src"><a href="{esc(prev['source_url'])}" target="_blank" rel="noopener">official page</a></td></tr>
      {cross}
    </tbody>
  </table></div>
  <p class="small">The three cross-checks were read by the runner one minute after the benchmark and are informational only.
  JM Bullion's figure is an ask price and includes a premium. None of these is a live quote.</p>
</section>

<section class="section" id="findings">
  <h2>Findings and irregularities</h2>
  <p class="sub">Each finding carries the rows it affects, linked to the official page. All are also listed on <a href="flagged.html">Flagged for Review</a>.</p>
  <div class="grid two">{finding_html}</div>
</section>

<section class="section" id="changed">
  <h2>Rows whose price changed or went blank ({vc.get('SALE', 0) + vc.get('CHANGED', 0) + vc.get('SOURCE_DEAD', 0) + vc.get('SOLD_OUT', 0)})</h2>
  {row_table(dec, rings, derived, only=("SALE", "CHANGED", "SOURCE_DEAD", "SOLD_OUT"))}
</section>

<section class="section" id="all">
  <h2>Every row, line by line ({n})</h2>
  <p class="sub">"Price ÷ gold" is the price read divided by the gold value of the published weight at the benchmark above. It is blank where the seller publishes no weight or the price is blank.</p>
  {bs.filter_bar(n)}
  {row_table(dec, rings, derived)}
</section>

<section class="section">
  <h2>Registered sources: reachability on 11 November</h2>
  <p class="sub">The runner checked that each of the {len(health['sources'])} registered sources still answers. This is a reachability check only:
  the text of the laws, guidance and return policies was <strong>not</strong> re-read this pass and keeps its October retrieval date.</p>
  <div class="table-wrap"><table>
    <thead><tr><th>Source</th><th>Tier</th><th>Publisher</th><th>State</th><th class="num">HTTP</th><th>Link</th></tr></thead>
    <tbody>{src_rows}</tbody>
  </table></div>
  <p class="small">The two FTC pages return 404 to the runner but load in a browser; that was established by hand in October and was not repeated this pass.</p>
</section>

<section class="section">
  <h2>What this pass did not do</h2>
  <div class="grid two">
    <div class="card"><h3>Not verified</h3>
      <ul>
        <li>No ring was bought, weighed or tested. No XRF or assay result exists for any row.</li>
        <li>No hallmark or maker's mark was seen: no seller publishes one.</li>
        <li>No seller's reputation was checked against an independent source.</li>
        <li>Return-policy wording was not re-read. Several sellers advertise extended holiday returns on their pages; the terms were not opened.</li>
        <li>{n - len(hand_ids)} of {n} rows were not hand-read. For those, the only evidence dated 11 November is the runner's fetch.</li>
      </ul></div>
    <div class="card"><h3>Before buying</h3>
      <p>Open the official page and read the price for the exact size, metal and stone you want. Ask the seller in writing for the gram weight,
      the karat stamp and maker's mark, and whether a resized ring can be returned. Pay by credit card and keep the listing and receipt.
      On arrival, have an independent jeweller weigh it and test the purity before you wear or resize it.
      A 14K or 18K stamp alone does not prove purity.</p>
      <p class="small"><strong>Recommended after every review:</strong> look for hallucinations. Pick rows at random, open the official link,
      and compare each number and its date with this page.</p></div>
  </div>
</section>

<section class="section">
  <h2>Checks run on the final tree</h2>
  <p class="sub">These gates test defined rules. Passing them does not prove a claim is true or that every error has been found.</p>
  <div class="table-wrap"><table>
    <thead><tr><th>Gate</th><th>Check</th><th>Result</th><th>Detail</th><th>Project source</th></tr></thead>
    <tbody>{gate_rows}</tbody>
  </table></div>
</section>
"""
    (ROOT / "pages" / "pass21.html").write_text(render("Pass 21 — re-verification after 19 days", body, "pass21", root="../", script=True), encoding="utf-8")
    print(f"wrote pages/pass21.html ({len(body)} chars of body)")


if __name__ == "__main__":
    main()
