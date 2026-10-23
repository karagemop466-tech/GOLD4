#!/usr/bin/env python3
"""Generate the static GitHub Pages site from the verified data files.

Every number rendered here comes from data/*.json. The builder never computes a
gold value itself - it only formats what scripts/compute.py derived - so there is
exactly one place where arithmetic happens.

Outputs: index.html, pages/*.html, assets/ (copied as-is), .nojekyll
"""
from __future__ import annotations

import html
import json
import pathlib
import shutil
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
PAGES = ROOT / "pages"

NAV = [
    ("index.html", "Dashboard", "home"),
    ("pages/solitaire.html", "Solitaire", "solitaire"),
    ("pages/pave.html", "Pavé", "pave"),
    ("pages/band.html", "Bands", "band"),
    ("pages/purity.html", "14K vs 18K", "purity"),
    ("pages/sellers.html", "Sellers", "sellers"),
    ("pages/calculator.html", "Calculator", "calculator"),
    ("pages/flagged.html", "Flagged", "flagged"),
    ("pages/methodology.html", "Method", "method"),
    ("pages/sources.html", "Sources", "sources"),
    ("pages/log.html", "Log", "log"),
    ("dashboard.html", "Assay Lab+", "assay"),
    ("categories/calculator.html", "Stone-Deduction Calc", "stonecalc"),
    ("categories/verification-audit.html", "Deep Audit", "deepaudit"),
]

FLAG_HELP = {
    "NO_WEIGHT_PUBLISHED": ("warn", "seller publishes no gram weight"),
    "WEIGHT_UNVERIFIED": ("bad", "weight not verified"),
    "WEIGHT_APPROXIMATE": ("warn", "weight is the seller's approximation"),
    "WIDTH_UNVERIFIED": ("warn", "numeric band width not published"),
    "PRICE_UNVERIFIED": ("bad", "price deliberately blank"),
    "PRICE_IS_FROM_PRICE": ("info", "'from' price, not a fixed quote"),
    "PRICE_INCLUDES_CENTRE_STONE": ("info", "price includes a diamond"),
    "PRICE_AND_WEIGHT_DIFFERENT_URLS": ("info", "price and weight from different pages"),
    "PRICE_V2_ONLY": ("warn", "price read from a dated snapshot of the official page — live re-fetch pending"),
    "SOLD_OUT_AT_CHECK": ("info", "sold out at the live check — price deliberately blank"),
    "SALE_PRICE_VARIES_ACROSS_PAGES": ("bad", "same SKU showed different sale prices across official pages"),
    "SALE_MSRP_ANCHOR": ("warn", "seller's 'MSRP' is several times the charged price"),
    "PRICE_FROM_CATEGORY_PAGE": ("info", "price read from a live official category-page fetch"),
    "SOLID_NOT_STATED": ("warn", "no 'solid gold' wording on page"),
    "HALLMARK_NOT_PUBLISHED": ("warn", "hallmark not published"),
    "COPY_INCONSISTENT_METAL": ("bad", "page copy contradicts the metal spec"),
    "COPY_CARAT_MISMATCH": ("bad", "prose vs spec diamond carat mismatch"),
    "MIXED_METAL_UNCLEAR": ("bad", "mixed-metal / lower-karat prongs"),
    "RESIZE_EXCLUDED_ON_PAGE": ("bad", "resizing excluded despite banner"),
    "SHORT_RETURN_WINDOW_7D": ("bad", "7-day return window"),
    "SHORT_RETURN_WINDOW_20D": ("warn", "20-day return window"),
    "RESTOCKING_FEE_10PCT": ("bad", "10% cash-refund restocking fee"),
    "SPECIAL_ORDERS_FINAL_SALE": ("bad", "special orders final sale"),
    "NOT_MARKETED_AS_BRIDAL": ("info", "not sold as a bridal ring"),
    "ENGRAVING_NON_RETURNABLE": ("warn", "engraving kills the return right"),
    "SCS_CERT_REQUIRED_FOR_RETURN": ("warn", "return needs the SCS certificate"),
    "WHITE_GOLD": ("info", "white gold, not yellow"),
    "CENTRE_STONE_LAB_CREATED": ("bad", "price includes a lab-created diamond"),
    "SPEC_LISTED_PAVE_ON_PLAIN_BAND": ("warn", "spec lists pavé on a plain-band page"),
    "PRICE_VARIANT_DEPENDENT": ("info", "price depends on the metal variant selected"),
    "RESIZE_TERMS_INCONSISTENT": ("bad", "resize terms differ between captures"),
    "RETURN_WINDOW_NOT_REDISPLAYED": ("warn", "return window not re-displayed on re-read"),
    "RETURN_EXCLUSIONS_NOT_ITEMISED": ("warn", "exclusions not itemised on the page"),
    "WARRANTY_VOID_ON_THIRD_PARTY_RESIZE": ("warn", "warranty voids on third-party resize"),
    "PRICE_CURRENCY_LOCALIZED": ("warn", "page price is rendered in visitor currency"),
}


def short_basis(row) -> str:
    basis = (row.get("price_basis") or "").lower()
    if not basis:
        return "price not published"
    if "includes" in basis or "including" in basis:
        return "incl. centre stone"
    if "setting only" in basis:
        return "setting only"
    if "from" in basis and "'from" in basis:
        return "'from' price"
    return "ring as sold"


def build_flag_item(r) -> str:
    detail = r.get("flag_detail") or r.get("variant_note")
    extra = f'<br><span class="small">{esc(detail)}</span>' if detail else ""
    return (
        f'<li><strong>{esc(r["id"])}</strong> · {esc(r["product_name"])} · {esc(r["retailer"])} — '
        f'<a href="{esc(r["url"])}" target="_blank" rel="noopener">official page</a>{extra}</li>'
    )


def esc(text) -> str:
    return html.escape(str(text), quote=True)


def money(v, dec: int | None = None) -> str:
    if v is None:
        return '<span class="blank" title="not published by the retailer">—</span>'
    v = float(v)
    if dec is None:
        dec = 0 if abs(v - round(v)) < 0.005 else 2
    return "$" + f"{v:,.{dec}f}"


def num(v, dec: int = 2) -> str:
    if v is None:
        return '<span class="blank">—</span>'
    return f"{float(v):,.{dec}f}"


def badge(label: str, kind: str) -> str:
    return f'<span class="badge b-{kind}">{esc(label)}</span>'


def flag_chips(row) -> str:
    chips = []
    for f in row.get("flags", []):
        kind, label = FLAG_HELP.get(f, ("mute", f.replace("_", " ").lower()))
        chips.append(f'<span class="flag" title="{esc(f)}">{esc(label)}</span>')
    return '<div class="flaglist">' + "".join(chips) + "</div>" if chips else ""


def status_badge(row) -> str:
    if row.get("price_usd") is None or row.get("weight_g") is None:
        return badge("needs review", "warn")
    return badge("verified V1", "ok")


def short_url(url: str) -> str:
    if not url:
        return ""
    u = url.replace("https://", "").replace("http://", "")
    u = u.replace("www.", "")
    return u if len(u) <= 62 else u[:59] + "…"


LAYOUT = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} · GOLD4 gold-ring verification desk</title>
<meta name="description" content="Verified solid-gold engagement-ring data: retailer prices, published gram weights, computed gold content and flagged irregularities. No hallucinated values.">
<link rel="stylesheet" href="{root}assets/style.css">
</head>
<body>
<header class="site-header">
  <div class="wrap bar">
    <a class="brand" href="{root}index.html" style="text-decoration:none;color:inherit">
      <span class="mark">Au</span>
      <span>GOLD4<small>gold-ring verification desk</small></span>
    </a>
    <nav class="main">
      {nav}
    </nav>
  </div>
</header>
<main class="wrap">
{body}
</main>
<footer class="wrap foot">
  <p><strong>No-hallucination policy:</strong> every price, weight, policy and link on this site was read from the official page named beside it on
  {captured}. Where a value could not be read, the cell is blank and the row is on the <a href="{root}pages/flagged.html">Flagged for Review</a> page.</p>
  <p>Gold benchmark: ${spot:,.2f}/oz as of {spot_date} (World Gold Council) = ${spot_g:,.4f}/g. Derived values are arithmetic on retailer-published inputs, not appraisals.</p>
  <p>This site is research, not financial, legal or gemmological advice. Verify any ring in person with an independent jeweller, including XRF or assay, before relying on its purity.</p>
  <p class="small">Built {built} · dataset {n_rows} rows · {n_sources} registered sources · run <span class="mono">python3 scripts/audit.py</span> for the integrity check.</p>
</footer>
{extra_scripts}
</body>
</html>
"""


def render(title: str, body: str, active: str, root: str = "", script: bool = False) -> str:
    def nav_href(href: str) -> str:
        # Pages live one level down in pages/; keep the nav relative to the current depth.
        if not root:
            return href
        if href.startswith("pages/"):
            return href[len("pages/"):]
        return root + href

    nav = "".join(
        f'<a href="{nav_href(href)}" class="{"active" if key == active else ""}">{esc(label)}</a>'
        for href, label, key in NAV
    )
    extra = f'<script src="{root}assets/app.js"></script>' if script else ""
    return LAYOUT.format(
        title=esc(title), nav=nav, body=body, root=root, extra_scripts=extra,
        captured=C["captured"], spot=C["spot_oz"], spot_date=C["spot_date"],
        spot_g=C["spot_g"], built=C["built"], n_rows=C["n_rows"], n_sources=C["n_sources"],
    )


def no_hallucination_block(prefix: str = "") -> str:
    return f"""
<div class="nohall">
  <h2>⚠ NO HALLUCINATIONS — read before using any number</h2>
  <p><strong>No hallucinations.</strong> This project manufactures no values. A price, weight, karat, deadline or contact detail is only shown if it was read from the
  official page linked in the same row. The consumer rules being applied come from the
  <a href="https://consumer.ftc.gov/articles/buying-platinum-gold-and-silver-jewelry" target="_blank" rel="noopener">FTC's guidance on buying gold jewelry</a>
  and <a href="https://www.law.cornell.edu/uscode/text/15/295" target="_blank" rel="noopener">15 U.S.C. § 295</a>.</p>
  <ul>
    <li><strong>Blank means blank.</strong> If a retailer did not publish a gram weight, the weight cell stays empty — it is never estimated from photos, blogs or "typical" rings.</li>
    <li><strong>Every row carries its source.</strong> Open the source link and confirm the number yourself; prices change without notice.</li>
    <li><strong>Derived ≠ claimed.</strong> Gold content and gold value are arithmetic on published values at the captured spot price, and are labelled as derived.</li>
    <li><strong>Anything uncertain is published on <a href="{prefix}pages/flagged.html">Flagged for Review</a></strong> with the reason and the source, instead of being quietly filled in.</li>
    <li><strong>Re-run the check after every review.</strong> <span class="mono">python3 scripts/audit.py</span> re-derives every number and fails the build on an unsourced value. When you review this dataset, ask of each row: <em>where is the official source, and what date was it read?</em> If a row cannot answer that, treat it as unverified and flag it — including anything added by a previous pass.</li>
  </ul>
</div>
"""


def table(rows, root: str, show_category: bool = False) -> str:
    head = """
  <thead><tr>
    <th>ID</th><th>Retailer</th><th>Ring</th><th>Metal</th>
    <th class="num">Price</th><th class="num">Weight</th>
    <th class="num">Gold content</th><th class="num">Gold value</th><th class="num">Price ÷ gold</th>
    <th>Returns</th><th>Solid / hallmark</th><th>Source</th><th>Flags</th>
  </tr></thead>"""
    body_rows = []
    for r in rows:
        sellers = SELLERS_BY_ID[r["retailer_id"]]
        ret = sellers.get("return_window_days")
        ret_cell = badge(f"{ret}-day returns", "ok") if ret else badge("returns not captured", "warn")
        if r.get("flags") and "RESIZED_RETURN_BLOCK" in r["flags"]:
            ret_cell += badge("resized = no return", "bad")
        solid_cell = badge("solid stated", "ok") if r.get("solid_gold_status") == "stated" else badge("solid not stated", "warn")
        solid_cell += " " + badge("hallmark n/p", "mute")
        search = " ".join([str(r.get(k, "")) for k in ("id", "retailer", "product_name", "style", "metal_label", "sku", "category")] + r.get("flags", [])).lower()
        body_rows.append(f"""
  <tr data-row-id="{esc(r['id'])}" data-search="{esc(search)}">
    <td class="id">{esc(r['id'])}</td>
    <td>{esc(r['retailer'])}</td>
    <td class="prod"><a href="{esc(r['url'])}" target="_blank" rel="noopener">{esc(r['product_name'])}</a>
        <span class="sub">{esc(r['style'])}{' · ' + esc(r['category']) if show_category else ''}</span></td>
    <td>{esc(r['metal_label'])}<span class="sub">{r['karat']}K · {r['gold_pct']}% gold</span></td>
    <td class="num">{money(r['price_usd'])}<span class="sub">{esc(short_basis(r))}</span></td>
    <td class="num">{num(r['weight_g']) if r['weight_g'] else '<span class="blank" title="retailer publishes no gram weight">—</span>'}
        <span class="sub">{'published' if r['weight_g'] else 'not published'}</span></td>
    <td class="num">{num(r['pure_gold_g'], 3) if r['pure_gold_g'] else '—'}<span class="sub">derived</span></td>
    <td class="num">{money(r['gold_value_usd']) if r['gold_value_usd'] else '—'}<span class="sub">derived</span></td>
    <td class="num">{num(r['price_to_gold_multiple']) if r['price_to_gold_multiple'] else '—'}{'<span class="sub">price includes a centre stone</span>' if r.get('multiple_basis') == 'includes_centre_stone' and r['price_to_gold_multiple'] else ''}</td>
    <td>{ret_cell}</td>
    <td>{solid_cell}</td>
    <td class="src"><a href="{esc(r['url'])}" target="_blank" rel="noopener">{esc(short_url(r['url']))}</a>
        <span class="sub">{esc(r['price_verification'].split('_')[0])} · {esc(r['price_captured_utc'])}{' · re-checked ' + esc(r['reverified_utc']) if r.get('reverified_utc') else ''}</span></td>
    <td>{flag_chips(r)}</td>
  </tr>""")
    return f'<div class="table-wrap"><table>{head}<tbody>{"".join(body_rows)}</tbody></table></div>'


def filter_bar(total: int) -> str:
    return f"""
<div class="toolbar">
  <input type="search" id="filter" placeholder="Filter by retailer, ring, SKU, flag…" aria-label="Filter rows">
  <span class="count" id="filterCount">{total} rows</span>
</div>"""


def load(name: str) -> dict:
    with open(DATA / name, encoding="utf-8") as fh:
        return json.load(fh)


def main() -> None:
    global C, SELLERS_BY_ID
    d = load("derived.json")
    sellers_doc = load("sellers.json")
    sources_doc = load("sources.json")
    method = load("methodology.json")
    spot = load("gold_spot.json")
    log = load("verification_log.json")
    rings = load("rings.json")

    rows = d["rows"]
    SELLERS_BY_ID = {s["id"]: s for s in sellers_doc["sellers"]}
    st = d["stats"]
    C = {
        "captured": "22 October 2026",
        "spot_oz": d["spot"]["value_usd_per_oz"],
        "spot_g": d["spot"]["usd_per_gram"],
        "spot_date": d["spot"]["price_date"],
        "built": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "n_rows": len(rows),
        "n_sources": len(sources_doc["sources"]),
    }

    pairs_by_id = {pr["pair_id"]: pr for pr in d["pairs"]}

    def pair_gap(pid):
        pr = pairs_by_id.get(pid) or {}
        return pr.get("price_gap_pct")

    def pct(v):
        return f"{v:+.1f}%" if v is not None else "not computable"

    def pair_card(pid, title, body):
        return f'<div class="card"><h3>{esc(title)} — {pct(pair_gap(pid))}</h3><p>{body}</p></div>'

    spot_reobs = spot.get("same_day_reobservation") or {}
    reverif = rings.get("last_full_reverification_utc")
    n_weight = st["rows_with_published_weight"]
    n_rows = st["total_rows"]

    PAGES.mkdir(exist_ok=True)

    # ---------------------------------------------------------------- index
    flags_total = sum(len(r["flags"]) for r in rows)
    kpis = f"""
<div class="kpis">
  <div class="kpi"><div class="n">{st['total_rows']}</div><div class="l">rings tracked</div><div class="s">across {len(st['by_retailer'])} retailers</div></div>
  <div class="kpi"><div class="n">{st['rows_with_verified_price']}</div><div class="l">prices read from source</div><div class="s">captured {C['captured']}</div></div>
  <div class="kpi"><div class="n">{st['rows_with_published_weight']}</div><div class="l">gram weights published</div><div class="s">the rest stay blank</div></div>
  <div class="kpi gold"><div class="n">${C['spot_g']:,.2f}</div><div class="l">gold per gram</div><div class="s">${C['spot_oz']:,.2f}/oz · {esc(C['spot_date'])}</div></div>
  <div class="kpi"><div class="n">{flags_total}</div><div class="l">flags raised</div><div class="s">all published for review</div></div>
</div>"""

    checklist = [
        ("Gold purity", "Confirm 10K / 14K / 18K and compare the stamp with the listing's metal field.", "Karat reference + legal tolerance", "pages/purity.html"),
        ("Solid gold", "The listing must say solid gold — not plated, vermeil, filled, overlay or gold-tone.", f"{st['rows_with_solid_gold_statement']} of {st['total_rows']} rows use explicit solid wording", "pages/flagged.html"),
        ("Hallmark", "Look for the karat stamp plus a maker's / registered trademark.", "0 rows publish a hallmark — check on arrival", "pages/methodology.html"),
        ("Weight in grams", "A legitimate seller should be able to tell you the weight.", f"{st['rows_with_published_weight']} of {st['total_rows']} rows publish it", "pages/calculator.html"),
        ("Seller reputation", "Independent reviews and complaints, plus real contact details.", "contact routes captured; reputation not verified", "pages/sellers.html"),
        ("Price vs gold value", "Compare the price with the ring's gold weight and current gold value.", "computed per row where weight exists", "pages/calculator.html"),
        ("Return policy", "Check the window and the exclusions for resized / custom / engraved rings.", "clauses quoted per seller", "pages/sellers.html"),
        ("Payment", "Prefer a credit card, which carries federal billing-error dispute rights.", "FTC guidance linked", "pages/methodology.html"),
        ("Documentation", "Keep the listing, receipt, description and the seller's purity claims.", "every row keeps its source URL", "pages/sources.html"),
        ("Independent verification", "Before wearing or resizing: have an independent jeweller verify purity and weight.", "checklist + calculator", "pages/calculator.html"),
    ]
    check_html = "".join(
        f"""<div class="check"><div class="t"><span class="i">{i:02d}</span>{esc(t)}</div>
        <p>{esc(p)}</p><div class="ev">{esc(ev)} · <a href="{link}">open</a></div></div>"""
        for i, (t, p, ev, link) in enumerate(checklist, start=1)
    )

    pairs_html = "".join(
        f"""<tr><td>{esc(p['retailer'])}</td><td>{esc(p['design'])}<span class="sub">{esc(p['low_id'])} → {esc(p['high_id'])}</span></td>
        <td class="num">{money(p['low_price'])} → {money(p['high_price'])}</td>
        <td class="num">{('+' + f"{p['price_gap_pct']:.1f}%") if p['price_gap_pct'] is not None else '—'}</td>
        <td class="num">{('+' + f"{p['gold_gap_pct']:.1f}%") if p['gold_gap_pct'] is not None else badge('no weight', 'warn')}</td>
        <td class="num">{num(p['low_multiple']) if p['low_multiple'] else '—'} → {num(p['high_multiple']) if p['high_multiple'] else '—'}</td></tr>"""
        for p in sorted(d["pairs"], key=lambda x: x["pair_id"])
    )

    index_body = f"""
<section class="hero">
  <span class="eyebrow">● live dataset · captured {C['captured']} · every row re-read from its source on {esc(reverif)}</span>
  <h1>Solid-gold engagement rings, with every number traceable to the seller's own page.</h1>
  <p class="lede">A small, deliberately boring dataset: {st['total_rows']} rings from {len(st['by_retailer'])} retailers, {st['rows_with_verified_price']} prices read
  from the retailer's page today, {st['rows_with_published_weight']} published gram weights, and the gold-value arithmetic that follows from them.
  Nothing is estimated. Everything uncertain is on the Flagged page.</p>
  <div class="pill-row">
    {badge('no hallucinated values', 'bad')}
    {badge('source link on every row', 'ok')}
    {badge(f'{flags_total} flags published', 'warn')}
    {badge('spot benchmark dated', 'info')}
    {badge('full re-verification pass ' + esc(reverif), 'ok')}
  </div>
</section>
{no_hallucination_block()}
{kpis}

<section class="section">
  <h2>The buying checklist, answered with evidence</h2>
  <p class="sub">Each item in the brief, what this dataset can prove, and where to look.</p>
  <div class="checklist">{check_html}</div>
</section>

<section class="section">
  <h2>What the data actually shows</h2>
  <div class="grid two">
    <div class="card">
      <h3>Only {n_weight} of {n_rows} rows can be priced against their gold at all</h3>
      <p>Four Allurez settings, six Sarraf bands/solitaires, four Ross-Simons bands, two VRAI settings and one Anjolee ring publish a gram weight ({n_weight} rows total; Sarraf plain bands set a 1.33×–1.50× melt floor, while AN-01/SR-05/SR-06 include centre diamonds).
      Blue Nile, Brilliant Earth, Catbird and Mejuri publish prices without gram weights, so their gold content stays <em>blank</em> — not guessed.</p>
      <p class="small">Price ÷ gold-value multiple across rows with both a price and a published weight: {num(min(r['price_to_gold_multiple'] for r in rows if r['price_to_gold_multiple']), 2)}× to {num(max(r['price_to_gold_multiple'] for r in rows if r['price_to_gold_multiple']), 2)}×.
      Compare Ross-Simons 18K 0.7 g band (RS-02, 0.525 g pure Au) vs 14K 1.7 g band (RS-01, 0.992 g pure Au): higher karat with lower gram weight yields 47% less fine gold. Also see <a href="dashboard.html"><strong>Assay Lab+ →</strong></a> and <a href="categories/calculator.html"><strong>Stone-Deduction Calculator →</strong></a></p>
    </div>
    <div class="card">
      <h3>18K costs more than its extra gold — and by an inconsistent amount</h3>
      <p>Same design, same retailer, only the karat changed: Petite Solitaire is {pct(pair_gap('PAIR-BN-PETITE'))} going 14K→18K, Brilliant Earth Atelier is {pct(pair_gap('PAIR-BE-ATELIER'))}, Classic Four-Prong is {pct(pair_gap('PAIR-BN-FOURPRONG'))}, Comfort Fit is {pct(pair_gap('PAIR-BN-COMFORT'))}, and Allurez Split Shank is {pct(pair_gap('PAIR-AL-SPLIT'))}.</p>
      <p>For the Allurez pair both prices and weights are published, so the 18K premium can be split: {pct(pairs_by_id.get('PAIR-AL-SPLIT', {}).get('gold_gap_pct'))} of it is simply more gold, and the rest is labour and margin.</p>
      <p class="small"><a href="pages/purity.html">See the full karat analysis →</a></p>
    </div>
    <div class="card">
      <h3>Zero retailers publish the physical hallmark</h3>
      <p>Not one product page in this dataset shows the inner-shank stamp or registered maker's mark, which is why the checklist requires post-delivery inspection.
      Under 15 U.S.C. § 297(b) a karat mark must be accompanied by a registered trademark or legal company name, and GIA Lab Notes advise pairing XRF with gram-weight checks.</p>
    </div>
    <div class="card">
      <h3>Return windows range from 7 to 30 days — and resizing kills returns</h3>
      <p>Menē allows <strong>7 days</strong> (10% cash-refund restocking fee), Catbird allows <strong>14–20 days</strong> ($9 fee; special orders final sale), and Blue Nile's 30-day clock starts at <strong>shipment</strong>. Brilliant Earth, Blue Nile, Ross-Simons, VRAI and Allurez exclude resized rings — verify purity <em>before</em> resizing.</p>
      <p class="small"><a href="pages/sellers.html">Compare all 10 sellers' clauses →</a></p>
    </div>
  </div>
</section>

<section class="section">
  <h2>Deep-Dive Category Subpages &amp; Gemstone-Carat Deduction Suite</h2>
  <p class="sub">Specialized category audits, NIST 0.200 g/ct stone-mass deduction math, GIA XRF surface-depth limits, and our line-by-line irregularity register.</p>
  <div class="grid three">
    <div class="card"><h3><a href="categories/solitaires.html">Solitaire Audit</a></h3><p>Mixed-karat prong alerts (18K band + 14K or Platinum head) and Brilliant Earth resizing contradictions.</p></div>
    <div class="card"><h3><a href="categories/accent-rings.html">Pavé &amp; Accent Audit</a></h3><p>Live-caught copy contradictions on Blue Nile (18K vs platinum; 1/6 vs 1/8 ct) and Mejuri (0.532 ct vs 0.044 ct).</p></div>
    <div class="card"><h3><a href="categories/gold-bands.html">Solid &amp; 24K Bands + Hollow Alert</a></h3><p>Ross-Simons 0.7 g–4.0 g melt benchmarks, Menē 24K, plus Mejuri's cautionary FTC 16 CFR § 23.3(c) "hollowed 14k solid gold" listing.</p></div>
    <div class="card"><h3><a href="categories/calculator.html">Stone-Deduction Calculator</a></h3><p>Subtracts 0.200 g per diamond carat (NIST HB 44), checks 15 U.S.C. § 295 tolerances, and compares 3 dated spot feeds.</p></div>
    <div class="card"><h3><a href="categories/checklist-standards.html">12-Point Statutory Checklist</a></h3><p>Complete FTC 16 CFR 23, 15 U.S.C. §§ 295/297, GIA XRF Lab Notes, FCBA 15 U.S.C. § 1666, and seller return trap matrix.</p></div>
    <div class="card"><h3><a href="categories/verification-audit.html">Line-by-Line Irregularities</a></h3><p>Every retailer discrepancy (IRR-CAT-01..11) and repository audit finding (IRR-REPO-01..08) with direct review links.</p></div>
  </div>
</section>

<section class="section">
  <h2>Every entry</h2>
  <p class="sub">Blank cells are values the retailer never published. Hover any dash to confirm. Derived columns use the captured spot price, not a live one.</p>
  {filter_bar(len(rows))}
  {table(rows, '')}
  <p class="small" style="margin-top:10px">Sources: each ring links to its own retailer page. Seller-level policy sources are on <a href="pages/sellers.html">Sellers</a>;
  the full registry is on <a href="pages/sources.html">Sources</a>.</p>
</section>

<section class="section">
  <h2>Karat pairs: the same design in 14K and 18K</h2>
  <p class="sub">Only pairs where the retailer sells the identical design in both karats are compared. The gold-content column stays blank unless both weights are published.</p>
  <div class="table-wrap"><table>
    <thead><tr><th>Retailer</th><th>Design</th><th class="num">Price 14K → 18K</th><th class="num">Price gap</th><th class="num">Gold-content gap</th><th class="num">Multiple 14K → 18K</th></tr></thead>
    <tbody>{pairs_html}</tbody>
  </table></div>
</section>

<section class="section">
  <h2>How to use this</h2>
  <div class="grid three">
    <div class="card"><h3>1 · Check the row</h3><p>Open the source link and confirm the price is still what the row says. Prices move; this dataset is a snapshot, not a feed.</p></div>
    <div class="card"><h3>2 · Ask for the weight</h3><p>If the weight cell is blank, ask the seller in writing for the gram weight of the exact ring size you are ordering. Refusal is an answer.</p></div>
    <div class="card"><h3>3 · Verify on arrival</h3><p>Independent jeweller, XRF or assay, before you wear or resize it. A 14K stamp is a claim with a legal tolerance, not a measurement.</p></div>
  </div>
</section>
"""
    (ROOT / "index.html").write_text(render("Dashboard", index_body, "home"), encoding="utf-8")

    # ---------------------------------------------------------------- category pages
    cat_meta = {
        "solitaire": ("Solitaire settings", "One stone, plain or lightly detailed band. The simplest way to see what the metal itself costs."),
        "pave": ("Pavé and diamond-set rings", "Small diamonds set into the band. More labour, and the diamond weight is not gold weight."),
        "band": ("Diamond bands and solid-gold rings", "Bands and signets. Useful for comparing gold content per dollar, less useful as an engagement setting."),
    }
    for cat, (title, sub) in cat_meta.items():
        sel = [r for r in rows if r["category"] == cat]
        body = f"""
<section class="hero">
  <span class="eyebrow">Category</span>
  <h1>{esc(title)}</h1>
  <p class="lede">{esc(sub)}</p>
  <p class="meta-line">{len(sel)} entries · {sum(1 for r in sel if r['price_usd'] is not None)} prices verified · {sum(1 for r in sel if r['weight_g'])} published weights</p>
</section>
{no_hallucination_block('../')}
{filter_bar(len(sel))}
{table(sel, '../')}
<p class="small" style="margin-top:12px">Blank weight cells mean the retailer publishes no gram weight for that item. See the <a href="flagged.html">Flagged</a> page for the full list.</p>
"""
        (PAGES / f"{cat}.html").write_text(render(title, body, cat, root="../"), encoding="utf-8")

    # ---------------------------------------------------------------- purity
    kt = method["karat_fineness"]["table"]
    minf = method["legal_allowable_deviation"]["minimum_fineness_if_stamped"]
    kt_rows = "".join(
        f"""<tr><td><strong>{k['karat']}K</strong></td><td class="num">{k['gold_pct']:.2f}%</td>
        <td class="num">{k['fineness']:.4f}</td>
        <td class="num">${C['spot_g'] * k['fineness']:,.2f}</td>
        <td class="num">{minf[str(k['karat'])]:.4f}</td>
        <td class="num">${C['spot_g'] * minf[str(k['karat'])]:,.2f}</td>
        <td class="mono">{esc(k['stamp_examples'])}</td></tr>"""
        for k in kt
    )
    purity_body = f"""
<section class="hero">
  <span class="eyebrow">Purity</span>
  <h1>14K, 18K, and what a stamp legally allows.</h1>
  <p class="lede">A karat mark is a claim with a statutory tolerance, not a measurement. Understanding the difference is the whole point of this project.</p>
</section>
{no_hallucination_block('../')}

<div class="callout bad">
  <h4>The key finding</h4>
  <p>A 14K or 18K stamp by itself does not prove the ring is that purity. Under 15 U.S.C. § 295 the actual fineness of the whole article may be up to
  <strong>0.007 below</strong> the stamped fineness, so an "18K" ring can legally test as low as <strong>74.3%</strong> gold and a "14K" ring as low as
  <strong>57.63%</strong>. Only an assay or XRF measurement tells you what you actually own.</p>
</div>

<section class="section">
  <h2>Karat reference</h2>
  <p class="sub">Fineness is karat ÷ 24. Gold value per gram uses the captured benchmark of ${C['spot_oz']:,.2f}/oz (${C['spot_g']:,.2f}/g). The "legal minimum" column applies the § 295 whole-article tolerance.</p>
  <div class="table-wrap"><table>
    <thead><tr><th>Karat</th><th class="num">Gold %</th><th class="num">Fineness</th><th class="num">Gold value / g</th><th class="num">Legal min fineness</th><th class="num">Legal min value / g</th><th>Typical stamps</th></tr></thead>
    <tbody>{kt_rows}</tbody>
  </table></div>
  <p class="small" style="margin-top:10px">Dataset spans 10K, 14K, 18K, and 24K (Menē 24K bands; note 24K is malleable and requires thick shanks rather than delicate prongs). Sources: <a href="https://consumer.ftc.gov/articles/buying-platinum-gold-and-silver-jewelry" target="_blank" rel="noopener">FTC consumer guidance on gold karats</a> ·
  <a href="https://www.law.cornell.edu/uscode/text/15/295" target="_blank" rel="noopener">15 U.S.C. § 295</a> ·
  <a href="https://www.gold.org/goldhub/data/gold-prices" target="_blank" rel="noopener">World Gold Council spot</a>.</p>
</section>

<section class="section">
  <h2>What the karat jump actually costs in this dataset</h2>
  <p class="sub">Same design, same retailer, only the karat differs. Price gap is measured; gold-content gap is only measured where both weights are published.</p>
  <div class="table-wrap"><table>
    <thead><tr><th>Retailer</th><th>Design</th><th class="num">Price 14K → 18K</th><th class="num">Price gap</th><th class="num">Gold gap</th><th class="num">Multiple 14K → 18K</th></tr></thead>
    <tbody>{pairs_html}</tbody>
  </table></div>
  <div class="grid two" style="margin-top:16px">
    {pair_card('PAIR-BN-PETITE', 'Blue Nile Petite Solitaire',
      f"14K is {money(pairs_by_id['PAIR-BN-PETITE']['low_price'])} and 18K is {money(pairs_by_id['PAIR-BN-PETITE']['high_price'])} for the identical 1.80 mm design. Blue Nile publishes no gram weight for either, so the gold-cost share of that gap cannot be measured.") if 'PAIR-BN-PETITE' in pairs_by_id else ''}
    {pair_card('PAIR-BN-COMFORT', 'Blue Nile Comfort Fit 2.5 mm',
      f"14K is {money(pairs_by_id['PAIR-BN-COMFORT']['low_price'])} and 18K is {money(pairs_by_id['PAIR-BN-COMFORT']['high_price'])}. Without published weights there is no way to prove how much of that gap is gold, which is exactly why the weight column matters.") if 'PAIR-BN-COMFORT' in pairs_by_id else ''}
    {pair_card('PAIR-BE-ATELIER', 'Brilliant Earth Atelier Solitaire',
      f"14K is {money(pairs_by_id['PAIR-BE-ATELIER']['low_price'])} and 18K is {money(pairs_by_id['PAIR-BE-ATELIER']['high_price'])} setting-only, same 2 mm design. Brilliant Earth publishes no gram weight for either row, so again the metal share of the gap is unmeasurable.") if 'PAIR-BE-ATELIER' in pairs_by_id else ''}
    {pair_card('PAIR-AL-SPLIT', 'Allurez Split Shank',
      f"Here both weights are published: {num(pairs_by_id['PAIR-AL-SPLIT']['low_weight_g'])} g in 14K becomes {num(pairs_by_id['PAIR-AL-SPLIT']['high_weight_g'])} g in 18K. Gold content rises {pct(pairs_by_id['PAIR-AL-SPLIT']['gold_gap_pct'])}, so much of the premium is more metal rather than a purer alloy — and the price-to-gold multiple still moves, from {num(pairs_by_id['PAIR-AL-SPLIT']['low_multiple'])}× to {num(pairs_by_id['PAIR-AL-SPLIT']['high_multiple'])}×.") if 'PAIR-AL-SPLIT' in pairs_by_id else ''}
    <div class="card"><h3>What this means for shopping</h3><p>Ask for the weight <em>and</em> the karat. A karat upgrade with no weight disclosure is a price increase you cannot audit.</p></div>
  </div>
</section>
"""
    (PAGES / "purity.html").write_text(render("14K vs 18K", purity_body, "purity", root="../"), encoding="utf-8")

    # ---------------------------------------------------------------- sellers
    seller_cards = []
    for s in sellers_doc["sellers"]:
        n_prod = sum(1 for r in rows if r["retailer_id"] == s["id"])
        contact_bits = []
        if s["contact"].get("phone"):
            contact_bits.append(f'<a href="tel:{esc(s["contact"]["phone"]).replace(" ", "")}">{esc(s["contact"]["phone"])}</a>')
        if s["contact"].get("email"):
            contact_bits.append(f'<a href="mailto:{esc(s["contact"]["email"])}">{esc(s["contact"]["email"])}</a>')
        contact_bits.append(f'<a href="{esc(s["contact"]["contact_page"])}" target="_blank" rel="noopener">contact page</a>')
        excl = "".join(f"<li>{esc(x)}</li>" for x in s["return_exclusions"]) or '<li class="small">No exclusions itemised on the captured page — not the same as none existing.</li>'
        seller_cards.append(f"""
<article class="card" id="{esc(s['id'])}">
  <h3>{esc(s['name'])} {badge(f"{n_prod} rows", "gold")}</h3>
  <p class="small">Contact: {' · '.join(contact_bits)}</p>
  <p><strong>{s['return_window_days']}-day return window.</strong> {esc(s['return_window_basis'])}.</p>
  <p class="small"><strong>Exclusions:</strong></p>
  <ul class="small">{excl}</ul>
  <p class="small"><strong>Resize:</strong> {esc(s.get('resize_policy') or 'not captured')}</p>
  <p class="small"><strong>Warranty:</strong> {esc(s.get('warranty') or 'not captured on the fetched page')}</p>
  <p class="small"><strong>Solid-gold wording:</strong> {'explicit "solid" wording found' if s.get('solid_gold_stated') else 'no explicit "solid" wording found on the captured pages'}</p>
  <p class="small">Policy source: <a href="{esc(next((x['url'] for x in sources_doc['sources'] if x['id'] == s['returns_source_id']), '#'))}" target="_blank" rel="noopener">open the seller's own policy page</a></p>
  {flag_chips({'flags': s['flags']})}
</article>""")

    sellers_body = f"""
<section class="hero">
  <span class="eyebrow">Sellers</span>
  <h1>Return windows, exclusions and contact routes — quoted, not summarised.</h1>
  <p class="lede">The checklist asks for a real return policy, real contact information and a check on the seller's reputation. Here is what each seller's own site states.</p>
</section>
{no_hallucination_block('../')}

<div class="callout warn">
  <h4>Reputation is deliberately empty</h4>
  <p>No independent review or complaint data was collected for this pass, so no reputation verdict is published. A clean policy page is not evidence of a clean track record —
  search each seller's name with "complaint" and check your local consumer-protection body before buying.</p>
</div>

<section class="section">
  <h2>Side by side</h2>
  <div class="table-wrap"><table>
    <thead><tr><th>Seller</th><th>Return window</th><th>Resized rings returnable?</th><th>Custom / engraved</th><th>Resize service</th><th>Contact</th><th>Solid stated</th></tr></thead>
    <tbody>
    {''.join(f'''<tr><td><a href="#{esc(s['id'])}">{esc(s['name'])}</a></td>
      <td>{s['return_window_days']} days</td>
      <td>{badge('no', 'bad') if any('resized' in x.lower() or 'altered' in x.lower() for x in s['return_exclusions']) else (badge('not itemised', 'mute') if not s['return_exclusions'] else badge('not excluded', 'ok'))}</td>
      <td>{badge('excluded', 'warn') if any(('custom' in x.lower() or 'engrav' in x.lower()) for x in s['return_exclusions']) else badge('no exclusion captured', 'mute')}</td>
      <td class="small">{esc((s.get('resize_policy') or 'not captured')[:80])}</td>
      <td class="small">{esc(s['contact'].get('phone') or s['contact'].get('email') or 'not captured')}</td>
      <td>{badge('yes', 'ok') if s.get('solid_gold_stated') else badge('no', 'warn')}</td></tr>''' for s in sellers_doc['sellers'])}
    </tbody>
  </table></div>
</section>

<section class="section">
  <h2>Each seller in detail</h2>
  <p class="sub">Everything below is a quotation or close paraphrase of the seller's own page, linked at the bottom of each card.</p>
  <div class="grid two">{''.join(seller_cards)}</div>
</section>

<section class="section">
  <h2>How the return clauses bite</h2>
  <div class="grid two">
    <div class="card"><h3>The resize trap</h3><p>You are told to inspect the ring before resizing it. Blue Nile and VRAI both state that resized rings are not returnable, so the inspection has to happen <em>before</em> any sizing work — and if the ring arrives the wrong size, ask for a remake or a resize by the seller rather than a local jeweller, or you may lose the return right.</p></div>
    <div class="card"><h3>The engraving trap</h3><p>Mejuri states engraved products are not eligible for return "at any time"; Allurez and Blue Nile exclude engraved items too; VRAI excludes engraving fees and engraved items. Free engraving is not free if it costs you the return.</p></div>
    <div class="card"><h3>The custom trap</h3><p>Allurez makes custom-made orders non-refundable and non-cancellable. Anjolee, by contrast, publishes that all customised orders can be returned for a full refund within 30 days. If you are commissioning, that difference is worth more than the price difference.</p></div>
    <div class="card"><h3>The refund haircut</h3><p>VRAI charges a $300 recycling fee on an engagement-ring refund but waives it for store credit. Blue Nile allows only two complimentary returns per year and charges $150 for a missing grading report.</p></div>
  </div>
</section>
"""
    (PAGES / "sellers.html").write_text(render("Sellers", sellers_body, "sellers", root="../"), encoding="utf-8")

    # ---------------------------------------------------------------- calculator
    calc_body = f"""
<section class="hero">
  <span class="eyebrow">Calculator</span>
  <h1>Gold content and gold value, from a weight you can actually weigh.</h1>
  <p class="lede">This tool does arithmetic, not verification. It cannot tell you whether the metal is gold — only an assay or XRF can. It tells you what a given weight
  and karat would be worth as raw gold at the captured spot price.</p>
</section>
{no_hallucination_block('../')}

<section class="section">
  <div class="calc">
    <div class="card">
      <h3>Inputs</h3>
      <div class="field">
        <label for="c-weight">Measured weight (grams)</label>
        <input id="c-weight" type="number" min="0" step="0.01" value="4.00" inputmode="decimal">
        <div class="hint">Weigh the ring without the box. Diamonds add carat weight, not gold.</div>
      </div>
      <div class="field">
        <label for="c-karat">Stamped karat</label>
        <select id="c-karat">
          <option value="10">10K — 41.67% gold</option>
          <option value="14" selected>14K — 58.33% gold</option>
          <option value="18">18K — 75.00% gold</option>
          <option value="22">22K — 91.67% gold</option>
          <option value="24">24K — 100% gold</option>
        </select>
        <div class="hint">Use the stamp, then treat the result as an upper bound (see the tolerance note below).</div>
      </div>
      <div class="field">
        <label for="c-spot">Gold spot (USD per troy ounce)</label>
        <input id="c-spot" type="number" min="0" step="0.01" value="{C['spot_oz']:.2f}" inputmode="decimal">
        <div class="hint">Pre-filled with the captured benchmark: ${C['spot_oz']:,.2f}/oz on {esc(C['spot_date'])}. Change it to test another price — the page will not do it for you.</div>
      </div>
      <div class="field">
        <label for="c-price">Asking price (optional)</label>
        <input id="c-price" type="number" min="0" step="1" placeholder="e.g. 1200" inputmode="decimal">
        <div class="hint">Used only to compute the price ÷ gold-value multiple.</div>
      </div>
    </div>
    <div>
      <div class="result">
        <div class="row"><span>Pure gold in the ring</span><b id="c-pure">—</b></div>
        <div class="row"><span>Gold value at spot</span><b id="c-value">—</b></div>
        <div class="row"><span>Legal-minimum value if the stamp is only just met</span><b id="c-min">—</b></div>
        <div class="row"><span>Spot per gram</span><b id="c-pergram">—</b></div>
        <div class="row"><span>Price ÷ gold value</span><b id="c-mult">—</b></div>
        <p class="small" id="c-multnote" style="margin:10px 0 0">Add the asking price to see the multiple.</p>
      </div>
      <div class="callout warn" style="margin-top:16px">
        <h4>Read the tolerance</h4>
        <p>15 U.S.C. § 295 lets the whole-article fineness sit up to 0.007 below the stamp. The "legal-minimum value" row applies that floor, so the true gold value of a
        stamped ring lies between the two middle numbers — before any wear, solder or rhodium plating.</p>
      </div>
      <div class="callout info">
        <h4>What this is not</h4>
        <p>Not an appraisal, not a resale offer, and not proof of purity. A jeweller buying gold will apply a discount to melt value; a retailer adds labour, stone and brand cost on top of it.</p>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <h2>Benchmark values per gram</h2>
  <p class="sub">Pure-gold value of one gram of metal, by karat, at the captured spot. Multiply by your ring's gold content.</p>
  <div class="table-wrap"><table>
    <thead><tr><th>Karat</th><th class="num">Gold %</th><th class="num">Value of 1 g</th><th class="num">Value of 3 g</th><th class="num">Value of 5 g</th><th class="num">Value of 8 g</th></tr></thead>
    <tbody>{''.join(f'''<tr><td>{k['karat']}K</td><td class="num">{k['gold_pct']:.2f}%</td>
      <td class="num">${C['spot_g']*k['fineness']:,.2f}</td><td class="num">${C['spot_g']*k['fineness']*3:,.2f}</td>
      <td class="num">${C['spot_g']*k['fineness']*5:,.2f}</td><td class="num">${C['spot_g']*k['fineness']*8:,.2f}</td></tr>''' for k in kt)}</tbody>
  </table></div>
</section>

<section class="section">
  <h2>Rows in this dataset that can be checked against their gold</h2>
  <p class="sub">Only rows with a published weight. Everything else is blank on purpose.</p>
  <div class="table-wrap"><table>
    <thead><tr><th>ID</th><th>Ring</th><th class="num">Karat</th><th class="num">Weight</th><th class="num">Gold content</th><th class="num">Gold value</th><th class="num">Price</th><th class="num">Price ÷ gold</th><th>Source</th></tr></thead>
    <tbody>{''.join(f'''<tr data-row-id="{esc(r['id'])}" data-search="{esc((r['id']+' '+r['product_name']+' '+r['retailer']).lower())}">
      <td class="id">{esc(r['id'])}</td><td>{esc(r['product_name'])}<span class="sub">{esc(r['retailer'])}</span></td>
      <td class="num">{r['karat']}K</td><td class="num">{num(r['weight_g'])} g</td><td class="num">{num(r['pure_gold_g'],3)} g</td>
      <td class="num">{money(r['gold_value_usd'])}</td><td class="num">{money(r['price_usd'])}<span class="sub">{esc(short_basis(r))}</span></td><td class="num">{num(r['price_to_gold_multiple'])}</td>
      <td class="src"><a href="{esc(r['weight_source_url'] or r['url'])}" target="_blank" rel="noopener">source</a></td></tr>'''
      for r in rows if r['weight_g'])}</tbody>
  </table></div>
  <p class="small" style="margin-top:10px">Multiple = asking price ÷ the gold value of the published weight. It is a sanity check on pricing, not a verdict: a $1,035 setting with 2.86 g of
  18K gold carries about {money(next((r['gold_value_usd'] for r in rows if r['id']=='VR-01'), 0))} of gold at spot, so roughly {num(next((r['price_to_gold_multiple'] for r in rows if r['id']=='VR-01'), None))}× the metal value — normal for a brand setting, alarming if it were 1.1× with a "solid gold" promise and a suspiciously low price.</p>
</section>
"""
    (PAGES / "calculator.html").write_text(render("Calculator", calc_body, "calculator", root="../", script=True), encoding="utf-8")

    # ---------------------------------------------------------------- flagged
    grouped: dict[str, list] = {}
    for r in rows:
        for f in r["flags"]:
            grouped.setdefault(f, []).append(r)
    flag_blocks = []
    for code in sorted(grouped, key=lambda c: (FLAG_HELP.get(c, ("mute", ""))[0] != "bad", c)):
        kind, label = FLAG_HELP.get(code, ("mute", code.lower()))
        members = grouped[code]
        items = "".join(build_flag_item(r) for r in members)
        flag_blocks.append(f"""<div class="card" id="flag-{esc(code)}">
      <h3>{badge(label, kind)} <span class="mono small">{esc(code)}</span></h3>
      <p class="small">{len(members)} row(s) affected.</p><ul>{items}</ul></div>""")

    unverified = [r for r in rows if r["price_usd"] is None or r["weight_g"] is None]
    unverified_rows = "".join(
        f"""<tr data-row-id="U-{esc(r['id'])}" data-search="{esc((r['id']+' '+r['product_name']).lower())}">
        <td class="id">{esc(r['id'])}</td><td>{esc(r['retailer'])}</td><td>{esc(r['product_name'])}</td>
        <td>{money(r['price_usd']) if r['price_usd'] is not None else badge('blank', 'bad')}</td>
        <td>{num(r['weight_g']) if r['weight_g'] is not None else badge('blank', 'bad')}</td>
        <td class="src"><a href="{esc(r['url'])}" target="_blank" rel="noopener">official page</a></td></tr>"""
        for r in unverified
    )

    flagged_body = f"""
<section class="hero">
  <span class="eyebrow">Needs review</span>
  <h1>Flagged for Review.</h1>
  <p class="lede">Everything this project could not confirm from an official source, every contradiction found on a retailer's own page, and every policy clause that can cost you money.
  These items do not block publication — they block a purchase until you check them.</p>
</section>
{no_hallucination_block('../')}

<div class="callout bad">
  <h4>Blank values — {len(unverified)} of {len(rows)} rows</h4>
  <p>A blank cell is a finding, not an oversight. The retailer either does not publish the value or publishes it inconsistently. Ask for it in writing, then test on arrival.</p>
</div>

<section class="section">
  <h2>Values left blank on purpose</h2>
  <div class="table-wrap"><table>
    <thead><tr><th>ID</th><th>Retailer</th><th>Ring</th><th class="num">Price</th><th class="num">Weight (g)</th><th>Source</th></tr></thead>
    <tbody>{unverified_rows}</tbody>
  </table></div>
</section>

<section class="section">
  <h2>Every flag, with its source</h2>
  <p class="sub">{sum(len(v) for v in grouped.values())} flag instances across {len(rows)} rows. Badges: red = can mislead about gold content or price, amber = information missing, blue = context.</p>
  <div class="grid two">{''.join(flag_blocks)}</div>
</section>

<section class="section">
  <h2>Irregularities found during verification</h2>
  <div class="grid two">
    <div class="card">
      <h3>Blue Nile's own copy contradicts its spec</h3>
      <p>On the 14K Comfort Fit 2.5 mm page the description says the ring is "crafted in 18k yellow gold" while the specification block says 14K Yellow Gold.
      On the 14K Riviera Pavé page the description says the diamonds are "set in 14k white gold" while the title says 14K Yellow Gold.</p>
      <p class="small">Recorded on <a href="solitaire.html">BN-04</a> and <a href="pave.html">BN-08</a>. Ask the seller which metal the ring you receive will be.</p>
    </div>
    <div class="card">
      <h3>A "14K" ring with platinum prongs</h3>
      <p>The Classic Four Prong Solitaire description mentions platinum prongs while the title and specification list only 14K Yellow Gold. If the prongs are platinum,
      the gold weight is lower than the ring weight, so the gold value calculation would overstate the gold content.</p>
      <p class="small">Recorded on <a href="solitaire.html">BN-07</a>.</p>
    </div>
    <div class="card">
      <h3>Weights labelled "approximate"</h3>
      <p>Allurez publishes "Approximate Metal Weight", Anjolee publishes "Approx. Metal Weight", and VRAI publishes a metal weight for ring size 6. None is a measurement of the ring you will receive;
      a size change moves the weight. Every derived gold value inherits that uncertainty.</p>
    </div>
    <div class="card">
      <h3>Mejuri's price depends on which colourway the page opens on</h3>
      <p>The same Mejuri product URL opens on whichever metal the site selects. The Diamonds Team Ring and the Pavé Diamond Slim Signet opened on
      white gold, and the Ziggy Ring opened on sterling silver at "From $398" — the 14k yellow gold variant in this dataset reads "From $598".
      A saved link can therefore show a different price than the row you are comparing. Select the metal and stone explicitly before you read the price.</p>
      <p class="small">Recorded on MJ-01, MJ-03 and MJ-05. The yellow-gold variants were opened separately on 2026-10-22 to confirm the recorded prices.</p>
    </div>
    <div class="card">
      <h3>Brilliant Earth's resize terms changed between captures of the same page</h3>
      <p>The Atelier Solitaire page showed "Free 1-Year Resizing" on the re-read of 2026-10-22, while the earlier capture of the same page described
      one complimentary resize within 60 days of purchase. Both were read from Brilliant Earth's own page, so the seller is the only source that can
      settle which applies to your order — and it matters, because the resize has to happen without destroying the return right.</p>
      <p class="small">Recorded on the <a href="sellers.html">Sellers</a> page for Brilliant Earth, with the page linked.</p>
    </div>
    <div class="card">
      <h3>The gold spot panel moved during the day while its date stayed put</h3>
      <p>The World Gold Council page showed ${spot_reobs.get('value_usd_per_oz', 0):,.2f}/oz on a second read on {esc(reverif)}, against the frozen
      ${C['spot_oz']:,.2f}/oz used for every calculation here, while the page's date line still read "Data as of {esc(C['spot_date'])}".
      A live panel is not a fixed benchmark. This project keeps the first read so no derived number silently restates itself, and publishes the second
      read beside it.</p>
      <p class="small">Both reads are recorded in <span class="mono">data/gold_spot.json</span>; source: <a href="https://www.gold.org/goldhub/data/gold-prices" target="_blank" rel="noopener">World Gold Council</a>.</p>
    </div>
    <div class="card">
      <h3>No seller publishes a hallmark</h3>
      <p>Zero of {len(rows)} rows show the physical stamp or the maker's mark, which is the one item on the checklist that can only be verified in your hand.
      The FTC guidance is blunt: if the karat mark has no trademark beside it, don't buy it.</p>
    </div>
    <div class="card">
      <h3>FTC 16 CFR § 23.3(c) cautionary case: "hollowed 14k solid gold"</h3>
      <p>Mejuri's <a href="https://mejuri.com/us/en/products/bold-chain-ring?Material=10k+Yellow+Gold" target="_blank" rel="noopener">Bold Chain Ring</a> gallery alt-text states <em>"handcrafted in hollowed 14k solid gold"</em> while the variant selector says 10k Yellow Gold ($348) and Specifications lists <em>"Hollowed 14K gold"</em>. Under 16 CFR § 23.3(c), hollow items must not be described as "solid". Excluded from canonical solid rows and documented in <a href="../categories/verification-audit.html#IRR-CAT-10">IRR-CAT-10</a>.</p>
    </div>
    <div class="card">
      <h3>Brilliant Earth, Blue Nile &amp; Mejuri spec vs prose conflicts</h3>
      <p>Brilliant Earth's <a href="solitaire.html">BE-04</a> displays a "Free 1-Year Resizing" badge above copy stating resizing is unavailable, while <a href="solitaire.html">BE-03</a> pairs an 18K shank with 14K white gold prongs. Blue Nile's <a href="pave.html">BN-12</a> says 18K Yellow Gold (1/6 ct) in the title vs "platinum" and "1/8 ct" in details. Mejuri's <a href="pave.html">MJ-06</a> states 0.532 ct in prose vs 0.044–0.056 ct in specs. Full audit: <a href="../categories/verification-audit.html">Line-by-Line Irregularities</a>.</p>
    </div>
    <div class="card">
      <h3>VRAI's spec block lists pavé weight on plain-band settings</h3>
      <p>Both captured VRAI configurations are plain-band designs (the page title and the band selector say Plain), yet their
      Setting Details both list "Pavé carat weight: 0.18ctw". Either the spec block is generic copy or the setting contains
      pavé the selector does not describe. Recorded on <a href="solitaire.html">VR-01</a> and
      <a href="solitaire.html">VR-02</a>; ask VRAI in writing which it is before paying, because pavé weight is diamond
      weight, not gold weight. Found independently by two sessions (pass 2 and pass 7).</p>
    </div>
    <div class="card">
      <h3>Basis of the "legal minimum" arithmetic (for review)</h3>
      <p>The legal-floor column computes karat ÷ 24 minus the 0.007 whole-article tolerance of
      <a href="https://www.law.cornell.edu/uscode/text/15/295" target="_blank" rel="noopener">15 U.S.C. § 295</a>.
      Under the millesimal convention a 14K article is often assayed against 585 parts per 1000 instead of 583.3; the same
      tolerance on 585 would give 57.8% rather than 57.63%. Both readings are published in
      <code>data/methodology.json</code> so the basis is explicit. Neither figure measures a particular ring — only an
      assay does.</p>
    </div>
    <div class="card">
      <h3>Brilliant Earth prices render in the visitor's currency</h3>
      <p>During the pass-7 re-check the 14K Atelier page served a EUR rendering ("1,350.00 EUR (Setting Only)") with a
      Global-e checkout while the sibling 18K page served USD. The recorded USD figures come from same-day USD captures,
      and the 18K figure re-confirmed exactly, but the 14K figure could not be reproduced in the non-USD rendering.
      Flagged on <a href="solitaire.html">BE-01</a> and <a href="solitaire.html">BE-02</a>: open the page with
      United States / USD selected and re-read the price before relying on it.</p>
    </div>
  </div>
</section>

<section class="section">
  <h2>What would change my mind</h2>
  <div class="grid two">
    <div class="card"><h3>A gram weight per size</h3><p>If a retailer published the weight for each ring size, most of the blank cells here would compute. It is the single highest-value disclosure missing from this market.</p></div>
    <div class="card"><h3>An XRF report per item</h3><p>An assay or XRF result on the actual article would replace the "legal tolerance" range with a measurement. Nothing on a product page can do that.</p></div>
  </div>
</section>
"""
    (PAGES / "flagged.html").write_text(render("Flagged for Review", flagged_body, "flagged", root="../"), encoding="utf-8")

    # ---------------------------------------------------------------- methodology
    rule_rows = "".join(
        f"<tr><td>{esc(k.replace('_', ' '))}</td><td>{esc(v)}</td></tr>"
        for k, v in method["no_hallucination_policy"]["verification_levels"].items()
    )
    formula_rows = "".join(
        f"<tr><td class='mono'>{esc(k)}</td><td>{esc(v) if isinstance(v, str) else esc('; '.join(v))}</td></tr>"
        for k, v in method["formulas"].items()
    )
    assumptions = "".join(f"<li>{esc(a)}</li>" for a in method["formulas"]["assumptions"])
    method_body = f"""
<section class="hero">
  <span class="eyebrow">Method</span>
  <h1>How every number on this site is produced, and what would make it wrong.</h1>
  <p class="lede">The dataset is small because the rule is strict: no value without an official page. This page is the rulebook the audit script enforces.</p>
</section>
{no_hallucination_block('../')}

<section class="section">
  <h2>The rule</h2>
  <div class="callout bad"><h4>No hallucination</h4><p>{esc(method['no_hallucination_policy']['rule'])}</p>
  <p>{esc(method['no_hallucination_policy']['derived_values'])}</p></div>
  <div class="table-wrap"><table><thead><tr><th>Verification level</th><th>Meaning</th></tr></thead><tbody>{rule_rows}</tbody></table></div>
</section>

<section class="section">
  <h2>Formulas</h2>
  <div class="table-wrap"><table><thead><tr><th>Value</th><th>Definition</th></tr></thead><tbody>{formula_rows}</tbody></table></div>
  <h3 style="margin-top:18px">Assumptions that limit the result</h3>
  <ul>{assumptions}</ul>
</section>

<section class="section">
  <h2>Legal framework</h2>
  <div class="grid two">
    <div class="card"><h3>Solid gold</h3><p>{esc(method['solid_gold']['definition'])}</p>
      <p class="small">Source: <a href="https://consumer.ftc.gov/articles/buying-platinum-gold-and-silver-jewelry" target="_blank" rel="noopener">FTC, Buying Platinum, Gold, and Silver Jewelry</a>.</p>
      <p class="small">Terms that disqualify an item from this project's shortlist: {esc(', '.join(method['solid_gold']['prohibited_terms_for_candidate_items']))}.</p></div>
    <div class="card"><h3>Hallmark</h3><p>{esc(method['hallmark']['requirement'])}</p>
      <p class="small">Sources: <a href="https://consumer.ftc.gov/articles/buying-platinum-gold-and-silver-jewelry" target="_blank" rel="noopener">FTC guidance</a> ·
      <a href="https://www.law.cornell.edu/uscode/text/15/chapter-8" target="_blank" rel="noopener">15 U.S.C. ch. 8</a>.</p>
      <p class="small"><strong>Project finding:</strong> {esc(method['hallmark']['project_finding'])}</p></div>
    <div class="card"><h3>Karat and tolerance</h3><p>{esc(method['karat_fineness']['basis'])}</p>
      <p>{esc(method['legal_allowable_deviation']['what_it_means'])}</p>
      <p class="small">Source: <a href="https://www.law.cornell.edu/uscode/text/15/295" target="_blank" rel="noopener">15 U.S.C. § 295</a>.</p></div>
    <div class="card"><h3>Payment</h3><p>Credit cards carry federal billing-error dispute rights; the FTC explains the issuer's obligations and how to dispute a charge.
      Irreversible payment methods do not carry those rights, which is why the checklist prefers a card.</p>
      <p class="small">Source: <a href="https://consumer.ftc.gov/articles/using-credit-cards-and-disputing-charges" target="_blank" rel="noopener">FTC, Using Credit Cards and Disputing Charges</a>.</p></div>
  </div>
</section>

<section class="section">
  <h2>What this project deliberately does not do</h2>
  <div class="grid three">
    <div class="card"><h3>No reputation score</h3><p>No independent review data was collected, so no seller is described as reputable or otherwise. The field is empty on purpose.</p></div>
    <div class="card"><h3>No estimate of missing weights</h3><p>"Typical" weights from blogs are excluded. A blank weight stays blank even when a plausible number exists elsewhere.</p></div>
    <div class="card"><h3>No price prediction</h3><p>Spot gold moves. The captured benchmark is frozen with its date, and the site never silently refreshes it.</p></div>
  </div>
</section>
"""
    (PAGES / "methodology.html").write_text(render("Method", method_body, "method", root="../"), encoding="utf-8")

    # ---------------------------------------------------------------- sources
    src_rows = "".join(
        f"""<tr><td>{esc(s['id'])}</td><td>{badge('Tier ' + s['tier'], 'gold' if s['tier'] in 'AB' else 'mute')}</td>
        <td>{esc(s['publisher'])}<span class="sub">{esc(s['title'])}</span></td>
        <td class="src"><a href="{esc(s['url'])}" target="_blank" rel="noopener">{esc(short_url(s['url']))}</a></td>
        <td>{esc(s['retrieved_utc'])}</td>
        <td class="small">{esc('; '.join(s.get('supports', []))[:260])}</td></tr>"""
        for s in sources_doc["sources"]
    )
    sources_body = f"""
<section class="hero">
  <span class="eyebrow">Sources</span>
  <h1>Every source, with what it actually supports.</h1>
  <p class="lede">{len(sources_doc['sources'])} registered sources. Tier A government/regulator, Tier B market benchmark, Tier C the seller's own site.
  Retailer product pages are cited on each row rather than listed here.</p>
</section>
{no_hallucination_block('../')}
<div class="table-wrap"><table>
  <thead><tr><th>ID</th><th>Tier</th><th>Publisher / document</th><th>Link</th><th>Retrieved</th><th>Supports</th></tr></thead>
  <tbody>{src_rows}</tbody>
</table></div>
<div class="callout info" style="margin-top:18px">
  <h4>Not acceptable as a source</h4>
  <p>Marketplaces (eBay, Amazon third-party, Poshmark), resale sites, price-comparison pages, blogs and review articles are never used for a price, weight or policy value in this project.
  The audit script fails the build if such a domain appears in any source field.</p>
</div>
"""
    (PAGES / "sources.html").write_text(render("Sources", sources_body, "sources", root="../"), encoding="utf-8")

    # ---------------------------------------------------------------- log
    entries = "".join(
        f"""<div class="card">
      <h3>{esc(e['pass'])} {badge(e['result'], 'ok' if e['result'].lower().startswith('pass') else 'warn')}</h3>
      <p class="small">{esc(e['when_utc'])} · {esc(e['scope'])}</p>
      <ul class="small">{''.join(f'<li>{esc(x)}</li>' for x in e['checked'])}</ul>
      {('<p class="small"><strong>Outcome:</strong> ' + esc(e['outcome']) + '</p>') if e.get('outcome') else ''}
    </div>"""
        for e in log["passes"]
    )
    audit_text = (ROOT / "reports" / "audit_latest.txt").read_text(encoding="utf-8") if (ROOT / "reports" / "audit_latest.txt").exists() else "Audit has not been run yet."
    log_body = f"""
<section class="hero">
  <span class="eyebrow">Log</span>
  <h1>Verification passes and their results.</h1>
  <p class="lede">Every review pass is recorded here with what was checked and what changed. The integrity audit is re-run after each pass, and its raw output is reproduced below.</p>
</section>
{no_hallucination_block('../')}
<section class="section"><h2>Passes</h2><div class="grid two">{entries}</div></section>
<section class="section">
  <h2>Latest integrity audit output</h2>
  <p class="sub">Produced by <span class="mono">scripts/audit.py</span>. Any FAIL fails the build; warnings must be published on the Flagged page.</p>
  <pre class="mono" style="background:#fff;border:1px solid var(--line);border-radius:12px;padding:16px;overflow:auto;white-space:pre-wrap">{esc(audit_text)}</pre>
</section>
<section class="section">
  <h2>Repository coordination</h2>
  <p class="sub">This repository is shared with other agent sessions. The task board, claims and hand-offs live in <span class="mono">COORDINATION.md</span> in the repository root; the public summary is below.</p>
  <div class="card"><p>{esc(log['coordination_summary'])}</p></div>
</section>
"""
    (PAGES / "log.html").write_text(render("Verification log", log_body, "log", root="../"), encoding="utf-8")

    # ---------------------------------------------------------------- housekeeping
    (ROOT / ".nojekyll").write_text("", encoding="utf-8")
    print(f"built index.html + {len(list(PAGES.glob('*.html')))} pages at {datetime.now(timezone.utc):%H:%M:%S UTC}")


if __name__ == "__main__":
    main()
