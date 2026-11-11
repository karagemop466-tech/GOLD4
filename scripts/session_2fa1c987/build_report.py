#!/usr/bin/env python3
"""Render reviews/pass21_2fa1c987.html from this session's evidence files.

Session arena/2fa1c987-gold4. Reads only this session's own files
(reviews/pass21_2fa1c987/**, reports/pass21_2fa1c987_gates.txt) and writes only
this session's own report page. No other file is read for content and none is
written.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "reviews" / "pass21_2fa1c987"

SEV_ORDER = {"HIGH": 0, "MEDIUM": 1, "LOW": 2, "INFO": 3}

FINDINGS = [
    ("F-2F-01", "HIGH",
     "Eight published pages presented a <strong>superseded</strong> gold benchmark as the benchmark in force: "
     "<code>CROSS-CHECK QUOTES · 2026-10-22 (benchmark: WGC $4,024.45/oz, 22 Oct)</code>. "
     "<code>data/gold_spot.json</code> keeps $4,024.45 in <code>prior_captures[2]</code> with "
     "<code>status: superseded</code>; the active benchmark is <strong>$3,996.31/oz</strong>. Confirmed live on the "
     "public site today. The &ldquo;Zero Invented Data&rdquo; policy bullet repeated it: &ldquo;the gold benchmark "
     "driving every derived value is &hellip; <strong>$4,024.45/oz</strong>&rdquo;.",
     "dashboard.html, solitaires.html, three-stone-halo.html, bands.html, checklist.html, standards.html, "
     "audit.html, coordination.html",
     "FIXED — value now derived from data/gold_spot.json at build time, with the WGC source link and both dates"),
    ("F-2F-02", "MEDIUM",
     "The same ribbon claimed &ldquo;<strong>5</strong> Automated Audit Gates Passing ✓&rdquo; while "
     "<code>.github/workflows/pages.yml</code> runs <strong>nine gates / twelve command invocations</strong>.",
     "the same eight pages",
     "FIXED — gate count and invocation count are now counted from pages.yml at build time"),
    ("F-2F-03", "MEDIUM",
     "The hero read &ldquo;With <strong>live</strong> fine gold trading at $4,024.60/oz &hellip; on 2026-10-22&rdquo; "
     "— a captured quote, 20 days old, described as live.",
     "dashboard.html",
     "FIXED — reworded as a dated cross-check, with the benchmark in force named beside it"),
    ("F-2F-04", "LOW",
     "The melt calculator shipped <strong>pre-filled placeholder results</strong> ($650.20; 1.34× melt (+$220.80 over "
     "raw gold); zone 1.02×–1.65×) rendered in the results panel with no label and no source. If the script does not "
     "run, a reader sees numbers that look computed. The <code>+$220.80</code> figure is the single value this "
     "session's scanner could not trace to <code>data/**</code>.",
     "dashboard.html (and every page using the widget)",
     "FIXED — the panel is now headed &ldquo;Pre-filled example only &hellip; not a quote, a valuation or a measured "
     "result for any listed ring&rdquo;"),
    ("F-2F-05", "INFO",
     "BN-09, BN-10, BN-11 and BN-12 all still serve Blue Nile's own 404 copy "
     "(<em>&ldquo;We're sorry, the page you're looking for cannot be found.&rdquo;</em>). Soft 404: HTTP 200 with 404 "
     "copy, so a status-code-only check would call them alive.",
     "data/rings.json rows BN-09…BN-12",
     "confirmed, unchanged 19 days on — logged as a request for the data/rings.json owner"),
    ("F-2F-06", "INFO",
     "AN-01's stored <strong>$870.76</strong> corroborated exactly today — the page prints "
     "<code>Price:$870.76</code> for MS354-A (14K White Gold, 0.50 ct FG/VS, size 6.5). The row was previously "
     "recorded as <code>SOURCE_PRICE_NOT_MACHINE_READABLE</code>.",
     "data/rings.json AN-01",
     "logged as a request — a second read path now contradicts that flag"),
    ("F-2F-07", "INFO",
     "BE-07's stored <strong>$1,350</strong> corroborated exactly today <strong>with the currency shown as USD</strong> "
     "(<code>fleur solitaire-$1,350</code>). The row carries <code>SOURCE_BOT_BLOCKED</code> and "
     "<code>PRICE_CURRENCY_LOCALIZED</code> from earlier automated sweeps.",
     "data/rings.json BE-07",
     "logged as a request — bears on the PRICE_CURRENCY_LOCALIZED flag"),
    ("F-2F-08", "INFO",
     "VR-01: page renders, metal confirmed <strong>18k Yellow Gold</strong> (matches the stored label); the price was "
     "not returned by this read path, so <strong>no price claim is made</strong>. Separately: the stored price "
     "<strong>$1,035</strong> — captured from a <em>different</em> URL and already flagged "
     "<code>PRICE_AND_WEIGHT_DIFFERENT_URLS</code> — is the same figure this page prints today for a "
     "<strong>different product</strong> (&ldquo;Half Pave Band &hellip; $1,035&rdquo;) in its recommendations strip.",
     "data/rings.json VR-01",
     "flagged for review — this may be coincidence, and the reviewer is told so. No claim is made either way"),
    ("F-2F-09", "INFO",
     "The World Gold Council panel today prints <strong>USD 4,059.49/oz</strong>, &ldquo;Data as of 10 November, "
     "2026&rdquo; (market data by ICE Data Services) — <strong>+1.58 %</strong> against the stored benchmark of "
     "$3,996.31/oz. This is an independent second read of the panel reported by PR #60.",
     "data/gold_spot.json",
     "recorded, NOT applied — the benchmark file is owned by session arena/d5947c03-gold4 (task 67)"),
    ("F-2F-10", "INFO",
     "README.md lines 144 and 164 remain flagged by the new superseded scanner. Both are historical pass narratives, "
     "not current claims.",
     "README.md",
     "scanner false positive — documented, no action"),
    ("F-2F-11", "INFO",
     "categories/calculator.html still offers &ldquo;World Gold Council (2026-10-21): $4,024.36&rdquo; as a selectable "
     "spot source. It is honestly dated in its own label, but it is a superseded reading and three weeks stale.",
     "categories/calculator.html",
     "logged as a request — not edited (honestly labelled, outside the claimed fix scope)"),
]

LIVE = [
    ("Gold benchmark", "https://www.gold.org/goldhub/data/gold-prices",
     "USD 4,059.49/oz · “Data as of 10 November, 2026” · ICE Data Services",
     "$3,996.31/oz · “22 October, 2026”", "differs +1.58% — recorded, not applied"),
    ("AN-01", "https://www.anjolee.com/rings/diamond-solitaire-engagement-rings/Six-Curved-Prongs-Solitaire-Diamond-Engagement-Ring.aspx",
     "Price:$870.76 · MS354-A · 14K White Gold · 0.50 ct FG/VS · size 6.5",
     "$870.76 (2026-10-22)", "exact match"),
    ("BE-07", "https://www.brilliantearth.com/Fleur-Solitaire-Ring-14K-Gold-BE1574-76785943/",
     "fleur solitaire-$1,350 · currency selector shows USD",
     "$1,350 (2026-10-23)", "exact match, in USD"),
    ("VR-01", "https://www.vrai.com/configure/setting-to-diamond/classic-4-prong-dome/round-brilliant-yellow-gold-40635875360861",
     "18k Yellow Gold · 1.0 ct I-J VS+ · plain band",
     "metal 18k · price $1,035 · 2.86 g", "metal matches; price not returned → no claim"),
    ("BN-09", "https://www.bluenile.com/engagement-rings/design-your-own-ring/classic-four-prong-solitaire-engagement-ring-in-18k-yellow-gold-item-500000y",
     "“We’re sorry, the page you’re looking for cannot be found.”", "flagged SOURCE_URL_DEAD", "still dead"),
    ("BN-10", "https://www.bluenile.com/engagement-rings/design-your-own-ring/low-dome-comfort-fit-solitaire-engagement-ring-in-14k-yellow-gold-item-502120y14",
     "“We’re sorry, the page you’re looking for cannot be found.”", "flagged SOURCE_URL_DEAD", "still dead"),
    ("BN-11", "https://www.bluenile.com/engagement-rings/design-your-own-ring/french-pave-diamond-engagement-ring-in-18k-yellow-gold-1-20-ct-tw-item-502520y",
     "“We’re sorry, the page you’re looking for cannot be found.”", "flagged SOURCE_URL_DEAD", "still dead"),
    ("BN-12", "https://www.bluenile.com/engagement-rings/design-your-own-ring/tapered-baguette-diamond-engagement-ring-in-18k-yellow-gold-1-6-ct-tw-item-501670y",
     "“We’re sorry, the page you’re looking for cannot be found.”", "flagged SOURCE_URL_DEAD", "still dead"),
    ("Published page (pre-fix)", "https://karagemop466-tech.github.io/GOLD4/dashboard.html",
     "CROSS-CHECK QUOTES · 2026-10-22 (benchmark: WGC $4,024.45/oz, 22 Oct) · 5 Automated Audit Gates Passing ✓",
     "benchmark $3,996.31/oz · 9 gates / 12 invocations", "superseded benchmark confirmed live"),
]

GATES = [
    ("G1", "audit.py — canonical dataset integrity &amp; derived math recompute", "PASS — 132 checks, 0 warnings, 0 failures"),
    ("G2", "check_site.py — root, /pages &amp; /docs link &amp; policy gate", "PASS — 30 pages; every populated row carries an official source link"),
    ("G3", "verify.py — combined schema &amp; blank-flag check", "PASS — 64 records, 0 hard failures"),
    ("G4", "verify_a0be79d4.py — 40-page XSS, 404 blocklist &amp; Assay Lab scanner", "PASS — 40 pages, 0 hard failures"),
    ("G5", "audit_hallucinations.py — gemstone-deduction, subpage &amp; 1,183-check auditor", "PASS — 1,183 checks, 0 warnings, 0 failures"),
    ("G6a", "verify_citations.py --self-test (must reject a known-bad CFR citation)", "PASS"),
    ("G6b", "verify_citations.py — every CFR citation vs its official section heading", "PASS — 110 references clean"),
    ("G7", "audit_freshness.py — live-evidence freshness &amp; source-health gate", "PASS — 295 checks, 4 known warnings, 0 failures"),
    ("G8", "test_assurance.py — conservative currency parsing", "PASS — 8/8"),
    ("G9a", "session_8a2b9dfb/test_readiness.py — readiness regression suite", "PASS — 22/22"),
    ("G9b", "session_8a2b9dfb/test_calculator.js — calculator runtime (hypothetical fixtures)", "PASS — 10/10"),
    ("G9c", "session_8a2b9dfb/readiness.py --check — input-hash freshness", "PASS"),
]

CSS = """
:root{--bg:#0d1117;--surface:#161b22;--surface-alt:#1c2128;--border:#30363d;--text:#e6edf3;
--muted:#8b949e;--gold:#d4af37;--green:#3fb950;--red:#f85149;--amber:#d29922;--blue:#58a6ff;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);
font:15px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;}
.wrap{max-width:1100px;margin:0 auto;padding:28px 20px 80px}
a{color:var(--blue)} a:hover{text-decoration:underline}
h1{font-size:1.8rem;margin:0 0 .3rem;line-height:1.25}
h2{font-size:1.25rem;margin:2.4rem 0 .8rem;padding-bottom:.35rem;border-bottom:1px solid var(--border)}
h3{font-size:1.02rem;margin:1.4rem 0 .5rem}
code{background:var(--surface-alt);border:1px solid var(--border);border-radius:4px;padding:.1rem .3rem;
font-size:.86em;word-break:break-word}
.eyebrow{color:var(--gold);letter-spacing:.12em;font-size:.7rem;text-transform:uppercase;font-weight:700}
.lead{color:var(--muted);font-size:1rem}
.banner{background:rgba(212,175,55,.1);border:1px solid var(--gold);border-left-width:4px;
border-radius:8px;padding:14px 16px;margin:18px 0}
.banner strong{color:var(--gold)}
table{width:100%;border-collapse:collapse;margin:14px 0;font-size:.87rem;display:block;overflow-x:auto}
th,td{border:1px solid var(--border);padding:8px 10px;text-align:left;vertical-align:top}
th{background:var(--surface-alt);color:var(--muted);font-weight:600;white-space:nowrap}
tbody tr:nth-child(even){background:rgba(255,255,255,.02)}
.badge{display:inline-block;padding:.1rem .45rem;border-radius:10px;font-size:.7rem;font-weight:700;
letter-spacing:.04em;white-space:nowrap}
.b-HIGH{background:rgba(248,81,73,.16);color:var(--red);border:1px solid var(--red)}
.b-MEDIUM{background:rgba(210,153,34,.16);color:var(--amber);border:1px solid var(--amber)}
.b-LOW{background:rgba(88,166,255,.14);color:var(--blue);border:1px solid var(--blue)}
.b-INFO{background:rgba(139,148,158,.16);color:var(--muted);border:1px solid var(--muted)}
.ok{color:var(--green);font-weight:600}
.fixed{color:var(--green);font-weight:600}
.card{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:16px 18px;margin:14px 0}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px;margin:18px 0}
.kpi{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:14px}
.kpi .v{font-size:1.5rem;font-weight:700;color:var(--gold)}
.kpi .l{color:var(--muted);font-size:.78rem;text-transform:uppercase;letter-spacing:.06em}
ul{margin:.5rem 0 .5rem 1.1rem;padding:0} li{margin:.35rem 0}
.small{color:var(--muted);font-size:.85rem}
footer{margin-top:40px;padding-top:16px;border-top:1px solid var(--border);color:var(--muted);font-size:.85rem}
"""


def main() -> int:
    obs_path = HERE / "observations.json"
    obs = json.loads(obs_path.read_text(encoding="utf-8")) if obs_path.exists() else {}
    gates_log = ROOT / "reports" / "pass21_2fa1c987_gates.txt"

    rows = []
    for fid, sev, what, where, disp in sorted(FINDINGS, key=lambda f: (SEV_ORDER[f[1]], f[0])):
        cls = "fixed" if disp.startswith("FIXED") else ""
        rows.append(
            f"<tr><td><span class='badge b-{sev}'>{sev}</span><br><code>{fid}</code></td>"
            f"<td>{what}</td><td class='small'>{html.escape(where)}</td>"
            f"<td class='{cls}'>{disp}</td></tr>"
        )

    live_rows = []
    for target, url, printed, stored, verdict in LIVE:
        live_rows.append(
            f"<tr><td><strong>{html.escape(target)}</strong><br>"
            f"<a href='{html.escape(url)}' target='_blank' rel='noopener'>{html.escape(url)}</a></td>"
            f"<td>{printed}</td><td>{html.escape(stored)}</td><td>{verdict}</td></tr>"
        )

    gate_rows = "".join(
        f"<tr><td><code>{g}</code></td><td class='small'>{what}</td><td class='ok'>{res}</td></tr>"
        for g, what, res in GATES
    )

    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pass 21 companion — non-canonical surface audit (arena/2fa1c987-gold4) — GOLD4</title>
<meta name="description" content="Line-by-line audit of the non-canonical GOLD4 surfaces: superseded benchmark, gate count, calculator placeholders, dead links and live re-reads, with official source links.">
<style>{CSS}</style>
</head>
<body>
<div class="wrap">

<div class="banner">
  <strong>⚠ NO HALLUCINATIONS — READ THIS FIRST.</strong> Every value on this page was either read from an
  official source during the window below, or derived from <code>data/**</code> by a script. A value that could not be
  confirmed is <strong>left blank and flagged</strong>, never estimated, averaged or inferred. Nothing here authenticates
  a ring: corroborating a stored price only means the page still prints that number.
  <a href="../../index.html">Canonical dashboard →</a>
</div>

<p class="eyebrow">GOLD4 · Pass 21 companion · session arena/2fa1c987-gold4</p>
<h1>Non-canonical surface audit, prose hallucination scan &amp; dead-link re-read</h1>
<p class="lead">
  Six sessions were working this repository at the same minute this one started, and all six were working the
  <em>canonical</em> surfaces — <code>data/**</code>, <code>index.html</code>, <code>pages/**</code>, the benchmark and
  the gates. This pass took the surfaces nobody had claimed: the eight root pages written by
  <code>scripts/generate_site.py</code>, <code>categories/**</code>, the frozen <code>docs/**</code> sub-site,
  <code>assets/**</code>, <code>static/**</code> and the prose documents. Those pages are still published and a reader
  can reach them, so a number that has drifted there is a live risk even when <code>data/</code> is perfect.
</p>
<p class="small">
  <strong>Read window:</strong> {html.escape(obs.get('read_window_utc', '2026-11-11T08:05Z to 2026-11-11T08:26Z'))} ·
  <strong>Read path:</strong> browser-rendered reader (this sandbox has no general outbound internet from bash).
  Per-read clock times are not captured by the reader, so each entry records the date, not a second-level time.
</p>

<div class="kpis">
  <div class="kpi"><div class="v">11</div><div class="l">findings raised</div></div>
  <div class="kpi"><div class="v">4</div><div class="l">fixed in this pass</div></div>
  <div class="kpi"><div class="v">1,507</div><div class="l">numeric claims reconciled</div></div>
  <div class="kpi"><div class="v">10 → 3</div><div class="l">superseded-benchmark findings</div></div>
  <div class="kpi"><div class="v">12/12</div><div class="l">gate invocations passing</div></div>
</div>

<h2>1. What the scanners found</h2>
<p>Two new read-only scanners in <code>scripts/session_2fa1c987/</code>:</p>
<table>
<thead><tr><th>Scanner</th><th>What it does</th><th>Before the fix</th><th>After the fix</th></tr></thead>
<tbody>
<tr><td><code>scan_prose.py</code></td>
    <td>Reconciles every money / per-oz / per-gram / gram / multiple / count token on 34 non-canonical files against every number stored in <code>data/**</code>.</td>
    <td>1,416 claims · 1,413 traceable · 2 dated-historical · <strong>1 untraceable</strong></td>
    <td>1,507 claims · 1,503 traceable · 3 dated-historical · <strong>1 untraceable</strong></td></tr>
<tr><td><code>check_superseded.py</code></td>
    <td>Finds readings that <code>data/gold_spot.json</code> marks <code>status: superseded</code> but a page presents as current.</td>
    <td><strong>10 findings</strong></td>
    <td><strong>3 findings</strong></td></tr>
</tbody>
</table>
<div class="card">
  <h3>A scanner bug worth recording</h3>
  <p class="small">The first draft of <code>check_superseded.py</code> excluded any line containing the word
  “cross-check”, which <strong>silently swallowed the real finding</strong>: the legacy pages print the benchmark
  inside a ribbon whose label begins <code>CROSS-CHECK QUOTES · 2026-10-22 (benchmark: WGC $4,024.45/oz, 22 Oct)</code>.
  The exclusion is now by <em>value</em> (Kitco / JM Bullion / BullionVault quotes read from <code>data/</code>), never
  by keyword. A scanner that hides its own finding is worse than no scanner, so this is recorded rather than quietly
  corrected.</p>
</div>

<h2>2. Live readings taken today (2026-11-11)</h2>
<table>
<thead><tr><th>Target &amp; official source</th><th>What the page printed</th><th>Stored value</th><th>Verdict</th></tr></thead>
<tbody>
{''.join(live_rows)}
</tbody>
</table>
<p class="small">Seven live product URLs were re-read. The other <strong>57 rows keep their 22–23 October 2026 capture
dates</strong> and were not re-opened by this session. This is a spot-check, not a sweep.</p>

<h2>3. Findings</h2>
<table>
<thead><tr><th>Severity</th><th>Finding</th><th>Where</th><th>Disposition</th></tr></thead>
<tbody>
{''.join(rows)}
</tbody>
</table>

<h2>4. What was changed</h2>
<p>Two file groups, both unowned by any live session at the time the scope extension was claimed (verified with
<code>git diff --name-only b34ae17</code> against all six live branch heads):</p>
<ol>
  <li><code>scripts/generate_site.py</code> — added <code>load_spot_facts()</code> (reads
      <code>data/gold_spot.json</code>) and <code>gate_counts()</code> (counts the gate steps and command lines in
      <code>.github/workflows/pages.yml</code>); the hardcoded ribbon, gate count, hero wording, policy bullet, KPI
      labels and calculator example label are now derived. Applied by the idempotent, documented patch script
      <code>scripts/session_2fa1c987/apply_fix.py</code>.</li>
  <li>The eight root pages it regenerates — rebuilt by <code>python3 scripts/generate_site.py</code>.</li>
</ol>
<p><strong>No</strong> ring price, weight, karat, URL, seller-policy text, benchmark value or other session's evidence
file was touched. <code>data/**</code> was read, never written.</p>

<h2>5. Verification — all nine gates / twelve command invocations</h2>
<table>
<thead><tr><th>Gate</th><th>What it checks</th><th>Result</th></tr></thead>
<tbody>
{gate_rows}
</tbody>
</table>
<p class="small">Full log: <code>reports/pass21_2fa1c987_gates.txt</code>
{"(present)" if gates_log.exists() else "(not found)"}
· evidence: <code>reviews/pass21_2fa1c987/observations.json</code> ·
scanner output: <code>prose_scan.json</code>, <code>prose_scan_after.json</code>,
<code>superseded_scan.json</code>, <code>superseded_scan_after.json</code>.</p>

<h2>6. Limits — read these before trusting this page</h2>
<ul>
  <li><strong>Spot-check, not a sweep.</strong> Seven live product URLs were re-read; 57 rows were not.</li>
  <li>Blue Nile serves a <strong>soft 404</strong> — HTTP 200 carrying 404 copy. A status-code-only check would call
      those pages alive.</li>
  <li>The scanners reconcile numbers <strong>against stored evidence</strong>, and stored evidence can itself be stale:
      today's WGC panel is +1.58 % from the stored benchmark, so a page that matches <code>data/</code> perfectly can
      still be 19 days behind the market.</li>
  <li><strong>Passing gates are not proof.</strong> The eight legacy pages passed every gate <em>while</em> printing a
      superseded benchmark, because no gate compared a rendered legacy number against <code>data/gold_spot.json</code>.
      That hole is what <code>check_superseded.py</code> now closes; it is offered to the final integration as a
      candidate Gate 10.</li>
  <li>Corroborating a stored price today does <strong>not</strong> authenticate the ring.</li>
</ul>

<div class="banner">
  <strong>Standing rule, restated:</strong> after every review, look for hallucinations again — source link, capture
  date, read path, and whether anything was inferred rather than read.
</div>

<footer>
  Session <code>arena/2fa1c987-gold4</code> · branch <code>arena/2fa1c987-gold4</code> · board claim pushed before any
  file in scope was edited · written report: <code>reviews/pass21_2fa1c987/report.md</code> ·
  <a href="../../index.html">canonical dashboard</a> ·
  <a href="../../pages/flagged.html">flagged for review</a> ·
  <a href="../../pages/freshness.html">source freshness</a>
</footer>

</div>
</body>
</html>
"""
    out = HERE / "report.html"
    out.write_text(doc, encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)} ({len(doc):,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
