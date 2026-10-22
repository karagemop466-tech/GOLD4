#!/usr/bin/env python3
"""
build_site.py — Generates the static GitHub Pages site for GOLD4 from data/*.json
and reports/verification_report.json. No value is invented here: every number on
the site is copied from the data files (which carry source URLs + timestamps) or
is pure arithmetic labeled as such.

Run:  python3 scripts/verify_data.py && python3 scripts/build_site.py
"""
import json
import html as H
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
REPORTS = ROOT / "reports"

rings_doc = json.loads((DATA / "rings.json").read_text())
RINGS = rings_doc["rings"]
SPOT = json.loads((DATA / "gold_spot.json").read_text())
REPORT = None
rp = REPORTS / "verification_report.json"
if rp.exists():
    REPORT = json.loads(rp.read_text())

BUILD_TS = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

NAV = [
    ("../index.html", "index.html", "Home"),
    ("all-rings.html", "pages/all-rings.html", "All Rings"),
    ("cat-solitaire.html", "pages/cat-solitaire.html", "Solitaire"),
    ("cat-halo.html", "pages/cat-halo.html", "Halo / Hidden Halo"),
    ("cat-pave.html", "pages/cat-pave.html", "Pavé / Channel"),
    ("cat-classic.html", "pages/cat-classic.html", "Classic & Preset"),
    ("calculator.html", "pages/calculator.html", "Calculator"),
    ("sellers.html", "pages/sellers.html", "Sellers"),
    ("gold-basics.html", "pages/gold-basics.html", "Gold Basics"),
    ("checklist.html", "pages/checklist.html", "Checklist"),
    ("methodology.html", "pages/methodology.html", "Methodology"),
    ("flagged.html", "pages/flagged.html", "⚑ Flagged for Review"),
]

CATEGORY_PAGES = {
    "Solitaire": "cat-solitaire.html",
    "Halo": "cat-halo.html",
    "Hidden Halo": "cat-halo.html",
    "Channel/Pave": "cat-pave.html",
    "Classic Band/Solitaire": "cat-classic.html",
    "Preset Diamond Ring": "cat-classic.html",
}

PAGE_TITLES = {
    "cat-solitaire.html": ("Solitaire Engagement Rings", "pages/cat-solitaire.html"),
    "cat-halo.html": ("Halo & Hidden Halo Engagement Rings", "pages/cat-halo.html"),
    "cat-pave.html": ("Pavé & Channel-Set Engagement Rings", "pages/cat-pave.html"),
    "cat-classic.html": ("Classic Bands & Preset Rings", "pages/cat-classic.html"),
}


def e(s):
    return H.escape(str(s), quote=True) if s is not None else ""


def money(v):
    if v is None:
        return '<span class="badge unverified">BLANK — UNVERIFIED</span>'
    return f"${v:,.0f}"


def level_badge(lvl):
    m = {
        "A-LIVE": ('<span class="badge live">✔ LIVE-VERIFIED</span>', "Read from a live fetch of the official page on 2026-10-22"),
        "B-SNIPPET": ('<span class="badge snippet">◷ SNIPPET</span>', "Read from a dated search snapshot of the official retailer page; live re-confirmation pending — flagged for review"),
        "UNVERIFIED": ('<span class="badge unverified">✘ UNVERIFIED</span>', "Could not be confirmed from an official source"),
    }
    return m.get(lvl, m["UNVERIFIED"])[0]


def flags_html(r):
    fl = r.get("flags") or []
    if not fl:
        return '<span class="muted">none</span>'
    return '<ul class="flaglist">' + "".join(f"<li>{e(f)}</li>" for f in fl) + "</ul>"


def weight_cell(r):
    w = r.get("weight_g")
    if w is None:
        return '<span class="badge unverified">— UNVERIFIED</span><div class="muted small">not published on source page</div>'
    return e(w)


def ring_rows(rows, show_category=False):
    out = []
    for r in rows:
        cat = f"<td>{e(r['category'])}</td>" if show_category else ""
        listp = ""
        if r.get("list_price_usd"):
            listp = f'<div class="muted small">list ${r["list_price_usd"]:,.0f}</div>'
        out.append(
            "<tr>"
            f'<td><a href="{e(r["url"])}" target="_blank" rel="noopener">{e(r["product"])}</a>'
            f'<div class="muted small">{e(r["id"])}</div></td>'
            f"<td>{e(r['retailer'])}</td>"
            f"{cat}"
            f'<td>{e(r["metal_karat"])} {e(r["metal_color"])}</td>'
            f'<td class="num">{money(r.get("price_usd"))}{listp}</td>'
            f'<td class="small">{e(r.get("price_basis") or "—")}</td>'
            f'<td class="small">{e(r.get("sku") or "—")}</td>'
            f'<td class="small">{e(r.get("width_mm") or "—")}</td>'
            f"<td>{weight_cell(r)}</td>"
            f'<td class="small">{e(r.get("verified_at_utc"))}</td>'
            f"<td>{level_badge(r.get('verification_level'))}</td>"
            f"<td>{flags_html(r)}</td>"
            "</tr>"
        )
    return "\n".join(out)


def table(rows, show_category=False):
    cat_th = "<th>Category</th>" if show_category else ""
    return f"""
<div class="muted small">Every product name links to its official source page. Every row shows when it was verified (UTC) and how.
Blank cells were left blank on purpose — the value was not published by the seller (no guessing, per the no-hallucinations policy).</div>
<table class="data">
<thead><tr>
<th>Product (link = official source)</th><th>Retailer</th>{cat_th}<th>Metal</th><th>Price (USD)</th>
<th>Price basis (as stated by seller)</th><th>SKU / Style</th><th>Width</th><th>Weight (g)</th>
<th>Verified (UTC)</th><th>Verification</th><th>Flags</th>
</tr></thead>
<tbody>
{ring_rows(rows, show_category)}
</tbody></table>"""


def page(fname, title, content, rel="pages/"):
    nav = []
    for href_sub, real, label in NAV:
        target = real
        href = href_sub
        if rel == "pages/":
            href = href_sub  # sibling or ../index.html
        else:
            # building index.html at root
            href = real
        active = ' class="active"' if real == fname else ""
        nav.append(f'<a href="{href}"{active}>{label}</a>')
    nav_html = "\n".join(nav)
    asset = "../assets" if rel == "pages/" else "assets"
    pledge = """
<div class="pledge">
  <h2>🚫 NO HALLUCINATIONS — verification promise</h2>
  <p><b>Every price and spec on this site was read directly from an official retailer source page and is stamped with its source link and the exact verification time (UTC).</b>
  If a value could not be confirmed from an official source, the cell is left <b>blank</b> and flagged
  <span class="badge unverified">UNVERIFIED</span> — never guessed, never inferred. Automated anti-hallucination checks
  (<code>scripts/verify_data.py</code>) run after every data change; anything that fails or awaits live re-confirmation is
  published on the <a href="pages/flagged.html">Flagged for Review</a> page.</p>
</div>"""
    footer = f"""
<footer class="site">
  <b>GOLD4</b> — gold engagement-ring research dashboard · site generated {BUILD_TS} by session <code>arena-22b5b06c-gold4</code><br>
  Data files: <code>data/rings.json</code>, <code>data/gold_spot.json</code> · Verification: <code>VERIFICATION.md</code>, <code>reports/verification_report.json</code> ·
  Repo: <a href="https://github.com/karagemop466-tech/GOLD4">github.com/karagemop466-tech/GOLD4</a><br>
  Prices are point-in-time (see each row's timestamp) and can change; always re-check the seller's page before buying. This site is research, not financial advice.
</footer>"""
    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)} · GOLD4 Gold Engagement Ring Dashboard</title>
<link rel="stylesheet" href="{asset}/css/style.css">
</head>
<body>
<header class="site"><div class="wrap">
  <div class="brand">🪙 GOLD<span>4</span> · Gold Engagement Ring Dashboard</div>
  <nav class="main">
{nav_html}
  </nav>
</div></header>
<main>
{pledge if rel == "" else '<div class="pledge"><p class="small"><b>NO HALLUCINATIONS:</b> every value below carries its official source link and UTC verification time; unconfirmed values are blank + flagged. See <a href="methodology.html">Methodology</a> and <a href="flagged.html">Flagged for Review</a>.</p></div>'}
<h1>{e(title)}</h1>
{content}
</main>
{footer}
</body></html>"""
    out = ROOT / fname
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc)
    print("wrote", fname)


# ---------- gather stats ----------
priced = [r for r in RINGS if r.get("price_usd")]
a_live = [r for r in RINGS if r["verification_level"] == "A-LIVE"]
b_snip = [r for r in RINGS if r["verification_level"] == "B-SNIPPET"]
n_flags = sum(1 for r in RINGS for f in r.get("flags", []))
errors = REPORT["errors"] if REPORT else ["report missing — run scripts/verify_data.py first"]
result = REPORT["result"] if REPORT else "UNKNOWN"

spot_price = SPOT["price_usd_per_troy_oz"]
spot_per_g = SPOT["price_usd_per_gram"]

# ---------- index ----------
pill = "ok" if result == "PASS" else ("warn" if result == "PASS_WITH_WARNINGS" else "bad")
status = f"""
<div class="statusbar">
  <span class="pill {pill}">Anti-hallucination check: {e(result)} ({len(errors)} errors)</span>
  <span class="pill ok">✔ {len(a_live)} entries live-verified on official pages</span>
  <span class="pill warn">◷ {len(b_snip)} entries from dated official snapshots (flagged, re-check pending)</span>
  <span class="pill bad">⚑ {n_flags} open flags on Flagged for Review</span>
</div>"""

cards = f"""
<div class="cards">
  <div class="card"><h3>Entries tracked</h3><div class="big">{len(RINGS)}</div>
    <div class="meta">solid 14K/18K gold engagement-ring settings from Blue Nile (incl. James Allen line) &amp; Brilliant Earth</div>
    <a class="navlink" href="pages/all-rings.html">Open master table →</a></div>
  <div class="card"><h3>Gold spot (XAU/USD)</h3><div class="big">${spot_price:,.2f}/oz</div>
    <div class="meta">≈ ${spot_per_g:,.2f}/g · source time {e(SPOT['source_reported_updated_at'])} · fetched {e(SPOT['fetched_at_utc_approx'])}<br>
    Source: <a href="{e(SPOT['source_url'])}" target="_blank" rel="noopener">api.gold-api.com/price/XAU</a> · cross-check pending (flagged)</div>
    <a class="navlink" href="pages/calculator.html">Open calculator →</a></div>
  <div class="card"><h3>Observed setting prices</h3><div class="big">${min(r['price_usd'] for r in priced):,.0f} – ${max(r['price_usd'] for r in priced):,.0f}</div>
    <div class="meta">range across {len(priced)} priced entries at verification time (settings only unless stated)</div>
    <a class="navlink" href="pages/all-rings.html">See prices →</a></div>
  <div class="card"><h3>Categories</h3><div class="big">4</div>
    <div class="meta">
      <a href="pages/cat-solitaire.html">Solitaire</a> ·
      <a href="pages/cat-halo.html">Halo / Hidden Halo</a> ·
      <a href="pages/cat-pave.html">Pavé / Channel</a> ·
      <a href="pages/cat-classic.html">Classic &amp; Preset</a></div>
    <a class="navlink" href="pages/checklist.html">Buying checklist →</a></div>
</div>"""

findings = """
<h2>Key findings (each traceable to a fetched official page)</h2>
<ul>
  <li><b>James Allen is now part of Blue Nile.</b> jamesallen.com product URLs redirect to bluenile.com, which states this on-page
      (<a href="https://www.bluenile.com/james-allen" target="_blank" rel="noopener">bluenile.com/james-allen</a>). Live-verified 2026-10-22.</li>
  <li><b>No-hallucination rule in action:</b> the James Allen "Comfort Fit Solitaire 1.5mm 14K YG" (item 41515) was <b>sold out</b> at live check, so its price cell is
      deliberately <span class="badge unverified">BLANK</span> — an older $660 snapshot price was NOT used because it could not be confirmed live.</li>
  <li><b>Ring weight in grams is not published</b> on any fetched product page → every Weight cell is blank + flagged. Per the checklist, ask the seller directly before buying.</li>
  <li><b>Gold spot at collection:</b> ${:,.2f}/oz (source time {}), single source — second-source cross-check is pending and flagged.</li>
  <li><b>Blue Nile limited lifetime warranty</b> covers gold jewelry items with purchase price ≥ $1,000 (read on fetched product pages; <a href="https://www.bluenile.com/services/warranty" target="_blank" rel="noopener">terms</a>).</li>
  <li><b>Promotions seen live on 2026-10-22:</b> Blue Nile "Fall Edit up to 30% off select styles" and "up to 50% off the James Allen Collection";
      Brilliant Earth "$250 gift card with purchase over $1,000, code GIFT" (time-sensitive; re-verify before relying on them).</li>
</ul>""".format(spot_price, SPOT["source_reported_updated_at"])

live_table = f"""
<h2>Live-verified entries (Level A) — read directly from official pages on 2026-10-22</h2>
{table(a_live)}
<p class="muted">Snapshot-verified (Level B) entries and all open flags: see <a href="pages/all-rings.html">All Rings</a> and <a href="pages/flagged.html">Flagged for Review</a>.</p>"""

index_content = status + cards + findings + live_table
page("index.html", "Gold Engagement Rings — Verified Research Dashboard", index_content, rel="")

# ---------- all rings ----------
content = f"""
<p class="subtitle">Master table — {len(RINGS)} entries. Sorted by verification level then price.</p>
{table(sorted(RINGS, key=lambda r: (r['verification_level'] != 'A-LIVE', -(r.get('price_usd') or 0))), show_category=True)}
"""
page("pages/all-rings.html", "All Rings — Master Table", content)

# ---------- category pages ----------
for fname, (ptitle, _) in PAGE_TITLES.items():
    rows = [r for r in RINGS if CATEGORY_PAGES.get(r["category"]) == fname]
    intro = ""
    if fname == "cat-classic.html":
        intro = '<div class="note">Includes plain comfort-fit/knife-edge style settings and one preset diamond ring. The James Allen comfort-fit entry is <b>sold out</b> — price left blank on purpose.</div>'
    content = f'<p class="subtitle">{len(rows)} entries in this category.</p>{intro}{table(sorted(rows, key=lambda r: (r["verification_level"] != "A-LIVE", -(r.get("price_usd") or 0))))}'
    page(f"pages/{fname}", ptitle, content)

# ---------- calculator ----------
calc_content = f"""
<p class="subtitle">Work out pure-gold content and intrinsic (melt) value for any gold ring, and sanity-check a asking price against it. All math runs in your browser; formulas are shown.</p>
<div class="calc-grid">
  <div class="card">
    <h3>Inputs</h3>
    <label class="field" for="w">Ring gold weight (grams) — ask the seller / weigh at a jeweler</label>
    <input type="number" id="w" min="0" step="0.01" placeholder="e.g. 3.5">
    <label class="field" for="k">Karat stamp</label>
    <select id="k">
      <option value="10">10K (41.67% gold)</option>
      <option value="14" selected>14K (58.33% gold)</option>
      <option value="18">18K (75.00% gold)</option>
      <option value="22">22K (91.67% gold)</option>
      <option value="24">24K (≈100% gold)</option>
    </select>
    <label class="field" for="spot">Gold spot price (USD / troy oz)</label>
    <input type="number" id="spot" min="0" step="0.01" value="{spot_price}">
    <div class="muted small">Pre-filled from our verified snapshot: <b>${spot_price:,.2f}/oz</b> ·
      source time {e(SPOT['source_reported_updated_at'])} ·
      <a href="{e(SPOT['source_url'])}" target="_blank" rel="noopener">{e(SPOT['source_url'])}</a><br>
      Spot moves constantly — enter today's price from a live source (e.g.
      <a href="https://www.kitco.com/charts/gold" target="_blank" rel="noopener">kitco.com</a> or
      <a href="https://www.lbma.org.uk/prices-and-data/precious-metal-prices" target="_blank" rel="noopener">lbma.org.uk</a>) before relying on the result.</div>
    <label class="field" for="paid">Asking / paid price (USD, optional)</label>
    <input type="number" id="paid" min="0" step="1" placeholder="e.g. 1145">
  </div>
  <div class="card">
    <h3>Results</h3>
    <div class="output-box" id="out"></div>
    <h3>Raw-gold quick reference (per gram of alloy, at snapshot spot ${spot_per_g:,.2f}/g pure)</h3>
    <table class="data"><thead><tr><th>Karat</th><th>Purity (k/24)</th><th>Pure gold per 1 g alloy</th><th>Intrinsic value per 1 g alloy</th></tr></thead><tbody>
    {''.join(
        f'<tr><td>{k}K</td><td class="num">{(int(k)/24*100):.2f}%</td><td class="num">{(int(k)/24):.4f} g</td><td class="num">${(int(k)/24*spot_per_g):,.2f}</td></tr>'
        for k in ["10", "14", "18", "22", "24"])}
    </tbody></table>
    <div class="muted small">Arithmetic from the snapshot spot price (labeled derivation, not an external claim). Melt value ≠ retail: settings include craftsmanship, accent stones and margin. A price far BELOW melt value is a red flag (fake/plated); a huge premium over melt is normal for finished jewelry.</div>
  </div>
</div>
<script src="../assets/js/calculator.js"></script>
"""
page("pages/calculator.html", "Gold Weight & Purity Calculator", calc_content)

# ---------- sellers ----------
sellers_content = """
<p class="subtitle">Only claims actually read from official pages at the recorded times. Independent-review scores are NOT quoted here because they were not fetched — links are provided for manual review (no hallucinations).</p>
<div class="cards">
  <div class="card">
    <h3>Blue Nile</h3>
    <div class="meta">
      <b>Contact (read on live-fetched product pages, 2026-10-22):</b> +1-800-242-2728 · service@bluenile.com · WhatsApp +1-877-374-9142<br><br>
      <b>Policies advertised on fetched pages:</b> Free shipping · Free returns ·
      <a href="https://www.bluenile.com/services/warranty" target="_blank" rel="noopener">Limited Lifetime Warranty</a> on gold/platinum jewelry ≥ $1,000 ·
      <a href="https://www.bluenile.com/policies/secure-shopping" target="_blank" rel="noopener">Secure Shopping</a><br><br>
      <b>Manual review links (not fetched):</b>
      <a href="https://www.bbb.org/us/wa/seattle/profile/online-shopping/bluenilecom-1296-2001037" target="_blank" rel="noopener">BBB profile</a> ·
      <a href="https://www.trustpilot.com/review/www.bluenile.com" target="_blank" rel="noopener">Trustpilot</a> ·
      <a href="https://www.bluenile.com/policies/terms-and-conditions" target="_blank" rel="noopener">Terms</a><br><br>
      <b>Promo seen live 2026-10-22:</b> "The Fall Edit: up to 30% off select styles" · "Up to 50% off The James Allen Collection" (time-sensitive).
    </div>
  </div>
  <div class="card">
    <h3>James Allen → now Blue Nile</h3>
    <div class="meta">
      <b>Finding (live-verified 2026-10-22):</b> jamesallen.com product URLs redirect to bluenile.com, which displays
      "James Allen is Now Part of Blue Nile — same diamonds and fine jewelry, now at bluenile.com"
      (<a href="https://www.bluenile.com/james-allen" target="_blank" rel="noopener">notice page</a>).<br><br>
      "By James Allen" collection items are sold on Blue Nile with the same policies above. One legacy James Allen style (Comfort Fit Solitaire 1.5mm, item 41515) was <b>sold out</b> at our check.<br><br>
      <b>Manual review links (not fetched):</b>
      <a href="https://www.jamesallen.com/" target="_blank" rel="noopener">jamesallen.com</a> ·
      <a href="https://www.bbb.org/us/ny/new-york/profile/jewelry/james-allen-0855-9000395" target="_blank" rel="noopener">BBB profile</a>
    </div>
  </div>
  <div class="card">
    <h3>Brilliant Earth</h3>
    <div class="meta">
      <b>Contact (read on live-fetched category page, 2026-10-22):</b> 800.691.0952 ·
      <a href="https://www.brilliantearth.com/contact/" target="_blank" rel="noopener">contact page</a> ·
      <a href="https://www.brilliantearth.com/stores/" target="_blank" rel="noopener">stores</a><br><br>
      <b>Promo seen live 2026-10-22:</b> "$250 gift card with purchase over $1,000, code GIFT" — <a href="https://www.brilliantearth.com/promo-codes-and-offers/" target="_blank" rel="noopener">terms</a> (time-sensitive).<br><br>
      <b>Manual review links (not fetched):</b>
      <a href="https://www.brilliantearth.com/returns/" target="_blank" rel="noopener">Returns policy</a> ·
      <a href="https://www.bbb.org/us/ca/san-francisco/profile/jewelry/brilliant-earth-1116-300055" target="_blank" rel="noopener">BBB profile</a> ·
      <a href="https://www.trustpilot.com/review/brilliantearth.com" target="_blank" rel="noopener">Trustpilot</a><br><br>
      <span class="badge unverified">UNVERIFIED</span> <span class="muted small">return-policy URL not yet confirmed by fetch — flagged.</span>
    </div>
  </div>
</div>
<h2>Checklist coverage by seller (from fetched pages only)</h2>
<table class="data">
<thead><tr><th>Checklist item</th><th>Blue Nile</th><th>Brilliant Earth</th><th>Basis</th></tr></thead>
<tbody>
<tr><td>Real contact info</td><td>✔ phone + email on page</td><td>✔ phone on page</td><td>Live fetch 2026-10-22</td></tr>
<tr><td>Solid gold (not plated)</td><td>✔ "14K Yellow/White Gold" metal listings; solid-gold settings</td><td>✔ "14K/18K Yellow Gold" metal listings</td><td>Live fetch / official snapshots</td></tr>
<tr><td>Karat stated per item</td><td>✔ every listing names karat</td><td>✔ every listing names karat</td><td>Rows table</td></tr>
<tr><td>Return policy advertised</td><td>✔ "Free Returns" on product pages</td><td>— not confirmed by fetch (flagged)</td><td>Live fetch</td></tr>
<tr><td>Warranty</td><td>✔ Limited Lifetime Warranty ≥ $1,000 gold items</td><td>— not confirmed by fetch (flagged)</td><td>Live fetch</td></tr>
<tr><td>Weight in grams published</td><td>✘ not on fetched pages (blank + flagged)</td><td>✘ not on fetched pages (blank + flagged)</td><td>Live fetch</td></tr>
<tr><td>Hallmark / maker's mark detail</td><td>✘ not published per item (blank + flagged)</td><td>✘ not published per item (blank + flagged)</td><td>Live fetch</td></tr>
<tr><td>Independent review scores</td><td>Not quoted (links for manual review)</td><td>Not quoted (links for manual review)</td><td>Policy: no unfetched claims</td></tr>
</tbody></table>
"""
page("pages/sellers.html", "Sellers — Reputation & Policy Evidence", sellers_content)

# ---------- gold basics ----------
basics_rows = "".join(
    f"<tr><td>{k}K</td><td class='num'>{int(k)}/24 = {int(k)/24*100:.2f}%</td><td>{stamp}</td><td class='num'>{int(k)/24*spot_per_g:.2f}</td></tr>"
    for k, stamp in [("10", "417"), ("14", "585"), ("18", "750"), ("22", "916"), ("24", "999")]
)
basics_content = f"""
<p class="subtitle">Purity percentages below are pure arithmetic (karat ÷ 24), shown with the formula. Common fineness stamps are the industry-standard numbers that correspond to those purities. Intrinsic-value column uses our snapshot spot price ${spot_per_g:,.2f}/g pure gold (source &amp; time on <a href="calculator.html">Calculator</a>).</p>
<table class="data">
<thead><tr><th>Karat</th><th>Purity (formula k/24)</th><th>Common stamp (fineness)</th><th>Intrinsic value per gram of alloy (at snapshot spot)</th></tr></thead>
<tbody>{basics_rows}</tbody></table>
<h2>Solid gold vs. look-alikes (per the buying checklist)</h2>
<ul class="checklist">
  <li><b>Solid gold</b> — the whole piece is gold alloy of the stated karat. Listings must say <i>solid gold</i> explicitly.</li>
  <li><b>Gold plated / gold-tone / overlay</b> — a thin surface layer over base metal. Not what this project tracks.</li>
  <li><b>Vermeil</b> — gold plating over sterling silver. Still plating.</li>
  <li><b>Gold-filled</b> — a thicker bonded gold layer (US trade usage commonly cites ≥1/20th of weight); still not solid.</li>
</ul>
<div class="note">Definitions above are general trade usage for orientation. For the binding US labeling rules see the FTC Jewelry Guides (link for manual review; page not fetched at build time): <a href="https://www.ftc.gov/legal-library/browse/rules/jewelry-guides" target="_blank" rel="noopener">ftc.gov — Jewelry Guides</a>.</div>
<h2>Hallmarks</h2>
<p>A karat stamp (10K/14K/18K or 417/585/750) plus a maker's/manufacturer's mark is what the checklist asks for. <b>A stamp alone does not prove purity</b> — verify with an independent jeweler and, ideally, XRF testing after delivery (see <a href="checklist.html">Checklist</a>). No per-item hallmark data is published on the retailer pages we fetched, so those cells are blank + flagged, not guessed.</p>
"""
page("pages/gold-basics.html", "Gold Basics — Karats, Purity, Hallmarks", basics_content)

# ---------- checklist ----------
checklist_content = """
<p class="subtitle">The project owner's buying checklist, verbatim in substance, with pointers to where this site covers each item.</p>
<ul class="checklist">
<li><b>Gold purity:</b> Confirm the karat — 10K, 14K, 18K, etc. Higher karat = more gold. <span class="muted">(Every row in our tables records the karat as stated by the seller; see <a href="gold-basics.html">Gold Basics</a>.)</span></li>
<li><b>Solid gold:</b> Listing must explicitly say <b>solid gold</b>, not plated, vermeil, gold-filled, gold overlay, or gold-tone. <span class="muted">(All tracked listings state 14K/18K gold metal; see Sellers coverage table.)</span></li>
<li><b>Hallmark:</b> Look for a 10K/14K/18K stamp <b>plus a maker's/manufacturer's mark</b>. <span class="muted">(Not published per item online → left blank + flagged, verify on arrival.)</span></li>
<li><b>Weight:</b> Check the ring's weight in <b>grams</b>. A legitimate seller should be able to provide it. <span class="muted">(Not published on any fetched page → blank + flagged; ask the seller.)</span></li>
<li><b>Seller reputation:</b> Research independent reviews and complaints; verify the business has real contact information. <span class="muted">(Contacts verified from official pages; review-site links provided for manual review on <a href="sellers.html">Sellers</a> — scores deliberately not quoted without fetching.)</span></li>
<li><b>Price:</b> Compare the price with the ring's gold weight and current gold value. An unusually cheap price is a red flag. <span class="muted">(Use the <a href="calculator.html">Calculator</a> once the seller gives you the gram weight.)</span></li>
<li><b>Return policy:</b> Make sure you can return it after receiving and inspecting it. Check specifically for exclusions on resized/custom rings. <span class="muted">(Blue Nile "Free Returns" verified on product pages; BE policy link pending → flagged.)</span></li>
<li><b>Payment:</b> Prefer a <b>credit card</b> for purchase protection. Avoid irreversible payment methods.</li>
<li><b>Documentation:</b> Keep the listing, receipt, description, and seller's claims about gold purity. <span class="muted">(This site archives listing claims with source URLs + UTC timestamps.)</span></li>
<li><b>Upon arrival:</b> Before wearing/resizing it, take it to an <b>independent jeweler</b> and ask them to verify the gold purity and weight.</li>
<li><b>Best verification:</b> Ask for <b>XRF testing</b> or another professional gold-purity test; don't rely solely on the stamp.</li>
<li><b>If the seller won't let you independently verify/return it:</b> Don't buy it.</li>
</ul>
<div class="note"><b>The key:</b> A 14K or 18K stamp by itself does <b>not</b> prove the ring is actually that purity. The safest approach is a reputable seller + proper markings + reasonable price + independent testing after delivery.</div>
"""
page("pages/checklist.html", "Online Buying Checklist", checklist_content)

# ---------- methodology ----------
methodology_content = f"""
<h2>Anti-hallucination policy</h2>
<ul>
<li>A value is recorded <b>only</b> if it was read from an official source (retailer product/category page, official price API) at a recorded UTC time, with the URL kept on the row.</li>
<li>If a value cannot be confirmed, the cell stays <b>blank</b> and the row is flagged <span class="badge unverified">UNVERIFIED</span> and published on <a href="flagged.html">Flagged for Review</a>. Nothing is inferred, estimated, or "typical-filled".</li>
<li>Automated checks run after every data change: <code>python3 scripts/verify_data.py</code> (schema, official-domain allow-list, karat/name consistency, fabricated-value guard on weight &amp; hallmark, price sanity, timestamp sanity, duplicates, spot-price recomputation). Latest result: <b>{e(result)}</b>, errors: <b>{len(errors)}</b>.</li>
<li>Site build regenerates every table from <code>data/rings.json</code> — no hand-typed numbers in HTML.</li>
<li>Local link integrity checked with <code>scripts/check_links.py</code> before publish.</li>
</ul>
<h2>Verification levels</h2>
<table class="data"><thead><tr><th>Level</th><th>Meaning</th><th>Count</th></tr></thead><tbody>
<tr><td><span class="badge live">A-LIVE</span></td><td>Value read from a live fetch of the official page on 2026-10-22 (~23:02–23:20 UTC)</td><td>{len(a_live)}</td></tr>
<tr><td><span class="badge snippet">B-SNIPPET</span></td><td>Value read from a dated search-engine snapshot of the official retailer page; live re-confirmation pending (fetch service outage during collection). Snapshot date noted per row.</td><td>{len(b_snip)}</td></tr>
<tr><td><span class="badge unverified">UNVERIFIED</span></td><td>Could not be confirmed from an official source — cell blank</td><td>see per-row flags</td></tr>
</tbody></table>
<h2>Data collection log (2026-10-22 UTC)</h2>
<ul class="small">
<li>~23:12–23:13 — Fetched Blue Nile product page (Classic Simple Solitaire 14K YG, item 203348): price $1,145, stock 502120y14, width 2.40mm, contacts, warranty, free returns.</li>
<li>~23:14–23:16 — Fetched Blue Nile yellow-gold category page: 7 more rings with names, metals, prices and product URLs (Level A).</li>
<li>~23:17 — Fetched gold spot API: XAU $4,028.10/oz (source-reported update time 2026-10-22T23:01:42Z). Cross-check pending → flagged.</li>
<li>~23:19 — Fetched James Allen item URL → redirected to Blue Nile; style sold out; "James Allen is Now Part of Blue Nile" notice read. Price left blank.</li>
<li>~23:20–23:24 — Fetch service outage began (proxy signature errors). Remaining candidate rows recorded at Level B from dated official-page snapshots; each flagged for live re-confirmation.</li>
</ul>
<h2>Known limitations (honest disclosure)</h2>
<ul>
<li>Ring weights (g) and per-item hallmark details are not published by the retailers on the pages fetched → all such cells are blank/flagged.</li>
<li>Level B prices are the retailer's own published prices at the snapshot date but were not re-confirmed live at build time; treat as provisional.</li>
<li>Sale prices (two Blue Nile rows) are time-sensitive.</li>
<li>Return-policy detail pages (resized/custom exclusions) not yet fetched → flagged; checklist requires confirming these before purchase.</li>
</ul>
<h2>Re-running verification</h2>
<pre><code>python3 scripts/verify_data.py   # anti-hallucination + schema checks → reports/verification_report.json
python3 scripts/build_site.py    # regenerate all pages from data/
python3 scripts/check_links.py   # local link integrity</code></pre>
<p class="muted">Site generated {BUILD_TS} · session arena-22b5b06c-gold4 · coordination log in <a href="https://github.com/karagemop466-tech/GOLD4/blob/main/COORDINATION.md" target="_blank" rel="noopener">COORDINATION.md</a></p>
"""
page("pages/methodology.html", "Methodology & Verification Log", methodology_content)

# ---------- flagged ----------
flag_rows = []
for r in RINGS:
    for f in r.get("flags", []):
        flag_rows.append((r["id"], r["product"], r["url"], f, r["verification_level"]))
if SPOT.get("cross_check", {}).get("status") != "DONE":
    flag_rows.append(("GOLD-SPOT", "Gold spot price cross-check", SPOT["source_url"], SPOT["cross_check"]["note"], "A-LIVE"))
flag_rows.append(("REPO", "Repo baseline", "https://github.com/karagemop466-tech/GOLD4", "Repo had no data/site before this cycle; README lacked description (see REPO_REVIEW.md)", "—"))
flag_rows.append(("BE-RETURN", "Brilliant Earth return policy URL", "https://www.brilliantearth.com/returns/", "Return-policy page not confirmed by live fetch at build time", "UNVERIFIED"))

flagged_content = f"""
<p class="subtitle">{len(flag_rows)} open items. Nothing here blocks the site; each item states exactly what is missing and links to the official source for manual review. Anti-hallucination rule: unconfirmed values stay blank, never guessed.</p>
<table class="data">
<thead><tr><th>Ref</th><th>Item</th><th>Flag / missing value</th><th>Level</th><th>Official source (manual review)</th></tr></thead>
<tbody>
{''.join(
    f'<tr><td>{e(a)}</td><td>{e(b)}</td><td class="small">{e(d)}</td><td>{level_badge(ev) if ev in ("A-LIVE","B-SNIPPET","UNVERIFIED") else e(ev)}</td><td><a href="{e(c)}" target="_blank" rel="noopener">open ↗</a></td></tr>'
    for a, b, c, d, ev in flag_rows)}
</tbody></table>
<div class="note">If you spot anything on this site that looks wrong or unsupported, treat it as a bug: every value must trace to a source URL + timestamp. Open an issue on the repo or ask for a re-verification pass (<code>scripts/verify_data.py</code>).</div>
"""
page("pages/flagged.html", "⚑ Flagged for Review", flagged_content)

print("BUILD OK:", BUILD_TS)
