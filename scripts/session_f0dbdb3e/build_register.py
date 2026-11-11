#!/usr/bin/env python3
"""Render the seller due-diligence register from its evidence file.

Session arena/f0dbdb3e-gold4.

    python3 scripts/session_f0dbdb3e/build_register.py          # write index.html and report.md
    python3 scripts/session_f0dbdb3e/build_register.py --check  # fail if the files on disk are stale

The page is generated, never hand-edited: every figure, quotation, link and timestamp on it comes from
reviews/due-diligence-f0dbdb3e/evidence.json.  The builder adds no fact of its own -- only layout, the
counts of what the evidence file contains, and fixed explanatory wording.  The output is deterministic
(no clock, no randomness), so the checker can require the files on disk to equal a fresh render.

The page is plain HTML and CSS: no script, no form, no image and no remote resource.
"""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REVIEW = ROOT / "reviews" / "due-diligence-f0dbdb3e"
EVIDENCE = REVIEW / "evidence.json"
PAGE = REVIEW / "index.html"
REPORT = REVIEW / "report.md"
REPO_URL = "https://github.com/karagemop466-tech/GOLD4"

TASKS = ("F0-1", "F0-2", "F0-3", "F0-4")
SEVERITY_ORDER = {"High": 0, "Medium": 1, "Low": 2, "Info": 3}

# Flags that describe a risk to the buyer (shown in red); every other flag is shown in grey,
# and the flag on a blank cell is shown in amber.
RISK_FLAGS = {
    "BBB_LOWEST_GRADE", "BBB_LOW_GRADE", "ALL_BBB_COMPLAINTS_UNANSWERED", "BBB_REVIEW_AVERAGE_LOW_DESPITE_HIGH_GRADE",
    "DISCOUNT_FOR_IRREVERSIBLE_PAYMENT", "WIRE_OFFERED", "CRYPTOCURRENCY_OFFERED", "CHECKS_AND_MONEY_ORDERS_OFFERED",
    "BANK_TRANSFER_OFFERED_IN_SOME_COUNTRIES", "CHARGEBACK_COST_RECOVERY_CLAUSE",
    "CARDS_ISSUED_OUTSIDE_US_AND_CANADA_NOT_ACCEPTED", "SOLID_WORDING_DOES_NOT_EXCLUDE_HOLLOW_FORM",
    "TEXT_ONLY_LINE_NO_VOICE_NUMBER_PRINTED", "TESTER_MAY_READ_BELOW_24K_AT_SOLDER_OR_FINDINGS",
    "ADVERTISED_WEIGHT_IS_AN_INVENTORY_AVERAGE", "PROFILE_TEXT_DESCRIBES_ANOTHER_BRAND", "IDENTITY_MATCH_BY_NAME_ONLY",
    "PAGE_PRINTS_TWO_WIRE_MINIMUMS", "BBB_PAGE_PRINTS_TWO_TOTALS",
}

# A question to put to the seller in writing, generated from the flags a seller carries.
QUESTIONS = [
    (("MAKERS_MARK_STATEMENT_NOT_FOUND",),
     "Which maker's mark or registered trademark is struck inside this ring, next to the karat mark?"),
    (("KARAT_STAMP_STATEMENT_NOT_FOUND", "GENERAL_STATEMENT_NOT_A_PER_RING_PROMISE", "CAPTION_ONLY_NO_POLICY_SENTENCE",
      "STATEMENT_LIMITED_TO_THE_ITALIAN_GOLD_ASSORTMENT"),
     "Is this specific ring stamped with its karat, and where on the ring is the stamp?"),
    (("SOLID_WORDING_DOES_NOT_EXCLUDE_HOLLOW_FORM",),
     "Is this ring hollow-form or solid metal throughout, and what does it weigh in grams?"),
    (("PAYMENT_METHODS_NOT_READABLE", "PAYMENT_PAGE_NOT_FOUND", "CARD_TYPES_NOT_PRINTED_IN_CHUNKS_READ"),
     "Which credit cards do you accept at checkout, and is the card charged by you or by a third party?"),
    (("CHARGEBACK_COST_RECOVERY_CLAUSE",),
     "How does the chargeback clause in your terms apply if the ring fails an independent purity test and a refund is refused?"),
    (("CARDS_ISSUED_OUTSIDE_US_AND_CANADA_NOT_ACCEPTED",),
     "Your page says cards issued outside the United States and Canada are not accepted: which payment method with dispute rights can a buyer abroad use?"),
    (("DISCOUNT_FOR_IRREVERSIBLE_PAYMENT", "WIRE_OFFERED", "CRYPTOCURRENCY_OFFERED", "BANK_TRANSFER_OFFERED_IN_SOME_COUNTRIES"),
     "Please confirm I can pay the full price by credit card (not wire, bank transfer or cryptocurrency)."),
    (("NO_STREET_ADDRESS_ON_CONTACT_PAGE", "ADDRESS_PRINTED_FOR_SAMPLE_SUBMISSIONS_ONLY"),
     "What is the legal name and street address of the company I am contracting with?"),
    (("TESTER_MAY_READ_BELOW_24K_AT_SOLDER_OR_FINDINGS",),
     "Does this ring contain solder or any component below the stated purity, and where?"),
    (("ADVERTISED_WEIGHT_IS_AN_INVENTORY_AVERAGE",),
     "What is the measured weight of the piece you will ship, and what tolerance applies?"),
    (("TEXT_ONLY_LINE_NO_VOICE_NUMBER_PRINTED", "NO_CUSTOMER_SERVICE_PHONE_ON_CONTACT_PAGE", "CUSTOMER_EMAIL_IS_A_WEB_FORM",
      "CONTACT_PAGE_PRINTS_A_FORM_ONLY"),
     "Which e-mail address and telephone number should I use if there is a problem with the order?"),
]

FIELD_LABEL = {
    "profile": "BBB profile", "accreditation": "Accreditation", "rating": "BBB grade",
    "complaints_3y": "Complaints, last 3 years", "complaints_12m": "Complaints, last 12 months",
    "complaint_status": "How BBB files them", "complaint_types": "Complaint types", "customer_reviews": "Customer reviews on BBB",
    "entity": "Legal entity or registry record", "phone": "Telephone", "email": "E-mail", "address": "Street address",
    "cards": "Credit cards accepted", "irreversible_methods": "Methods that cannot be disputed like a card charge",
    "incentive_or_clause": "Incentive or clause", "karat_stamp_statement": "Karat-stamp statement",
    "makers_mark_statement": "Maker's-mark statement", "other_purity_statement": "Other purity statements",
}
TASK_LABEL = {"F0-1": "Reputation", "F0-2": "Identity and contact", "F0-3": "Payment", "F0-4": "Stamps"}


def e(text) -> str:
    return html.escape(str(text), quote=True)


def stats_of(ev: dict) -> dict[str, int]:
    obs = ev["observations"]

    def by(task, field):
        return [o for o in obs if o["task"] == task and o["field"] == field]

    profiles = []
    for o in obs:
        if o["task"] == "F0-1":
            key = (o["seller_id"], o.get("profile"))
            if key not in profiles:
                profiles.append(key)
    accredited = {o["seller_id"] for o in by("F0-1", "accreditation") if (o["value"] or "").startswith("Accredited")}
    not_accredited = {o["seller_id"] for o in by("F0-1", "accreditation") if o["value"] == "Not accredited"} - accredited
    s = {
        "sellers": len(ev["sellers"]),
        "reads": len(ev["reads"]),
        "not_found": len(ev["not_found"]),
        "observations": len(obs),
        "filled": sum(1 for o in obs if o["value"] is not None),
        "blank": sum(1 for o in obs if o["value"] is None),
        "irregularities": len(ev["irregularities"]),
        "statements": len(ev["customer_statements"]),
        "leads": len(ev["leads_unverified"]),
        "requests": len(ev["requests"]),
        "bbb_profiles": len(profiles),
        "sellers_accredited": len(accredited),
        "sellers_not_accredited": len(not_accredited),
        "profiles_all_unanswered": sum(1 for o in by("F0-1", "complaint_status") if "ALL_BBB_COMPLAINTS_UNANSWERED" in o["flags"]),
        "cards_read": sum(1 for o in by("F0-3", "cards") if o["value"]),
        "cards_unread": sum(1 for o in by("F0-3", "cards") if not o["value"]),
        "irreversible_offered": sum(1 for o in by("F0-3", "irreversible_methods")
                                    if o["value"] and not o["value"].startswith("None listed")),
        "makers_mark_published": sum(1 for o in by("F0-4", "makers_mark_statement") if o["value"]),
        "karat_statement_published": sum(1 for o in by("F0-4", "karat_stamp_statement") if o["value"]),
        "address_blank": sum(1 for o in by("F0-2", "address") if not o["value"]),
    }
    for sev in SEVERITY_ORDER:
        s["irregularities_" + sev.lower()] = sum(1 for i in ev["irregularities"] if i["severity"] == sev)
    for t in TASKS:
        s["filled_" + t] = sum(1 for o in obs if o["task"] == t and o["value"] is not None)
        s["blank_" + t] = sum(1 for o in obs if o["task"] == t and o["value"] is None)
    return s


# --------------------------------------------------------------------------------------------------
# HTML
# --------------------------------------------------------------------------------------------------
CSS = """
:root{--bg:#f7f5ef;--ink:#1c1a15;--mut:#6a6254;--line:#e0d9cb;--gold:#96772a;--card:#fff;--ok:#1b6a39;--warn:#8a5a00;--bad:#8f2216;--dark:#15130f}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:#73560f}
header{background:var(--dark);color:#f6f1e6;padding:18px 20px 14px}
.wrap{max-width:1240px;margin:0 auto}
header h1{margin:0 0 4px;font-size:21px;letter-spacing:.2px}
header p{margin:0;color:#cfc6b6;font-size:13.5px}
.nohall{background:#3a2c0d;color:#ffe9b0;border-top:3px solid var(--gold);padding:12px 20px;font-size:14px}
.nohall strong{letter-spacing:.6px}
.nohall a{color:#ffe9b0}
nav{background:#fff;border-bottom:1px solid var(--line);padding:8px 20px;position:sticky;top:0;z-index:5}
nav .wrap{display:flex;flex-wrap:wrap;gap:4px 14px;font-size:13px}
nav a{text-decoration:none;padding:2px 0}
nav a:hover{text-decoration:underline}
nav .sep{color:var(--line)}
main{max-width:1240px;margin:0 auto;padding:18px 20px 60px}
h2{font-size:18px;margin:34px 0 8px;padding-bottom:6px;border-bottom:2px solid var(--line);scroll-margin-top:52px}
h3{font-size:15px;margin:20px 0 6px;color:var(--gold)}
p,li{font-size:14.5px}
.small{font-size:12.5px;color:var(--mut)}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:14px 0}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 12px}
.kpi .n{font-size:25px;font-weight:650;letter-spacing:-.5px;line-height:1.15}
.kpi .l{font-size:12px;color:var(--mut);text-transform:uppercase;letter-spacing:.35px;margin-top:2px}
.kpi.bad .n{color:var(--bad)} .kpi.warn .n{color:var(--warn)} .kpi.ok .n{color:var(--ok)}
.table-wrap{overflow-x:auto;border:1px solid var(--line);border-radius:10px;background:var(--card);margin:10px 0 6px}
table{width:100%;border-collapse:collapse}
th,td{padding:8px 10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top;font-size:13.5px}
th{background:#f2eee4;font-size:12px;text-transform:uppercase;letter-spacing:.3px;color:#4a4438;white-space:nowrap}
tbody tr:last-child td{border-bottom:none}
td.seller{font-weight:650;white-space:nowrap}
.v{display:block}
.blank{display:inline-block;color:var(--warn);font-weight:650;border:1px dashed #c9a14a;border-radius:6px;padding:0 6px;background:#fff8e6}
.flag{display:inline-block;font:11px/1.5 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;border-radius:5px;padding:0 5px;margin:2px 3px 0 0;border:1px solid var(--line);color:#4a4438;background:#f6f3ec;word-break:break-word}
.flag.risk{color:var(--bad);border-color:#e3b9b3;background:#fdf1ef}
.flag.unv{color:var(--warn);border-color:#e6cf9a;background:#fff8e6}
.note{display:block;font-size:12.5px;color:var(--mut);margin-top:3px}
details{margin-top:3px}
summary{cursor:pointer;font-size:12px;color:#73560f}
q{display:block;font-size:12.5px;color:#3c372d;background:#faf8f2;border-left:3px solid var(--gold);padding:5px 8px;margin-top:3px;quotes:none}
.src a{white-space:nowrap}
.src .t{color:var(--mut);font-size:11.5px}
.src span.one{display:block}
.sev{display:inline-block;border-radius:5px;padding:0 7px;font-size:12px;font-weight:650;color:#fff}
.sev.High{background:var(--bad)} .sev.Medium{background:var(--warn)} .sev.Low{background:#6a6254} .sev.Info{background:#3e5c76}
.callout{background:#fff;border-left:4px solid var(--gold);padding:10px 14px;border-radius:0 8px 8px 0;margin:12px 0}
.callout.warn{border-left-color:var(--warn)}
ul.tight{margin:6px 0 6px 18px;padding:0}
ul.tight li{margin:3px 0}
.cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:12px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 14px}
.card h3{margin-top:2px}
code{background:#f2eee4;padding:1px 5px;border-radius:4px;font-size:12.5px}
footer{border-top:1px solid var(--line);margin-top:36px;padding-top:14px;font-size:12.5px;color:var(--mut)}
@media print{nav{position:static}details{display:block}details>summary{display:none}}
"""


def render_html(ev: dict) -> str:
    sellers = ev["sellers"]
    name = {s["id"]: s["name"] for s in sellers}
    name["all"] = "All ten sellers"
    reads = {r["read_id"]: r for r in ev["reads"]}
    obs = ev["observations"]
    st = stats_of(ev)

    def stat(key: str) -> str:
        return f'<span data-stat="{e(key)}">{st[key]}</span>'

    def ext(url: str, label: str) -> str:
        return f'<a href="{e(url)}" rel="noopener noreferrer nofollow">{e(label)}</a>'

    def src(read_ids) -> str:
        seen, parts = set(), []
        for rid in read_ids:
            if rid in seen:
                continue
            seen.add(rid)
            r = reads[rid]
            parts.append(f'<span class="one">{ext(r["url"], rid)} <span class="t">{e(r["read_utc"][11:])}</span></span>')
        return "".join(parts)

    def flags_html(flags, blank=False) -> str:
        out = []
        for f in flags:
            cls = "flag unv" if blank else ("flag risk" if f in RISK_FLAGS else "flag")
            out.append(f'<span class="{cls}">{e(f)}</span>')
        return "".join(out)

    def cell(items) -> str:
        if not items:
            return '<span class="small">Nothing found on the pages read</span>'
        out = []
        for o in items:
            if o["value"] is None:
                part = '<span class="v"><span class="blank">blank — not confirmed</span></span>' + flags_html(o["flags"], blank=True)
            else:
                part = (f'<span class="v">{e(o["value"])}</span>'
                        f'<details><summary>words on the page</summary><q>{e(o["quote"])}</q></details>'
                        + flags_html(o["flags"]))
            if o.get("note"):
                part += f'<span class="note">{e(o["note"])}</span>'
            out.append(f"<div>{part}</div>")
        return "".join(out)

    def of(task, sid, field, profile=None):
        return [o for o in obs if o["task"] == task and o["seller_id"] == sid and o["field"] == field
                and (profile is None or o.get("profile") == profile)]

    def table(table_id: str, head, rows) -> str:
        th = "".join(f"<th>{e(h)}</th>" for h in head)
        return (f'<div class="table-wrap"><table class="data" id="{e(table_id)}"><thead><tr>{th}</tr></thead>'
                f'<tbody>{"".join(rows)}</tbody></table></div>')

    P: list[str] = []
    P.append("<!DOCTYPE html>")
    P.append('<html lang="en">')
    P.append("<head>")
    P.append('<meta charset="utf-8">')
    P.append('<meta name="viewport" content="width=device-width, initial-scale=1">')
    P.append('<meta name="robots" content="noindex">')
    P.append("<title>Seller due-diligence register — reputation, identity, payment, stamps (read 2026-11-11)</title>")
    P.append(f"<style>{CSS}</style>")
    P.append("</head>")
    P.append("<body>")
    P.append('<header><div class="wrap">')
    P.append("<h1>Seller due-diligence register</h1>")
    P.append(f'<p>Reputation · business identity · payment protection · hallmark and maker\'s-mark disclosure — '
             f'{stat("sellers")} sellers, every value read on 2026-11-11 between {e(ev["read_window_utc"]["first"][11:])} and '
             f'{e(ev["read_window_utc"]["last"][11:])} UTC. Session <code>{e(ev["session"])}</code>.</p>')
    P.append("</div></header>")

    P.append('<div class="nohall"><div class="wrap"><strong>NO HALLUCINATIONS.</strong> '
             + e(ev["no_hallucination_rule"])
             + ' This page applies the project\'s standing statement on the <a href="../../index.html">landing page</a>: '
               'a figure appears here only with the official page it was read from, the time it was read and the words the page printed. '
               'Blank cells are deliberate. Reading a complaint record is not the same as vetting a seller — no seller is endorsed here.'
               '</div></div>')

    P.append('<nav><div class="wrap">'
             '<a href="#summary">Summary</a><a href="#findings">Findings</a><a href="#reputation">Reputation</a>'
             '<a href="#identity">Identity</a><a href="#payment">Payment</a><a href="#stamps">Stamps</a>'
             '<a href="#flagged">Flagged for review</a><a href="#statements">Customer statements</a><a href="#leads">Leads</a>'
             '<a href="#ask">Ask the seller</a><a href="#method">Method</a><a href="#ledger">Read ledger</a><a href="#requests">Requests</a>'
             '<span class="sep">|</span>'
             '<a href="../../index.html">Project home</a><a href="../../pages/sellers.html">Sellers</a>'
             '<a href="../../pages/flagged.html">Flagged</a><a href="../../pages/readiness.html">Readiness</a>'
             '<a href="../../pages/calculator.html">Calculator</a>'
             "</div></nav>")

    P.append("<main>")

    # ---------------- summary
    P.append('<h2 id="summary">Summary</h2>')
    P.append("<p>The buying checklist asks for three things the dataset had never recorded for any seller: independent "
             "reviews and complaints, payment by credit card rather than an irreversible method, and a karat stamp "
             "together with a maker's mark. This register reads those three things from official pages for all ten "
             "sellers. It changes no ring row, price, weight or stored policy.</p>")
    kp = [
        ("", "reads", "official pages read"),
        ("", "observations", "table cells recorded"),
        ("ok", "filled", "cells with a value and the page's words"),
        ("warn", "blank", "cells left blank and flagged"),
        ("bad", "irregularities", "irregularities logged"),
        ("", "bbb_profiles", "BBB profiles read"),
        ("ok", "sellers_accredited", "sellers BBB-accredited"),
        ("warn", "sellers_not_accredited", "sellers not accredited"),
        ("bad", "profiles_all_unanswered", "BBB profiles with every complaint unanswered"),
        ("ok", "cards_read", "sellers whose card acceptance was read"),
        ("warn", "cards_unread", "sellers whose payment methods could not be read"),
        ("bad", "irreversible_offered", "sellers offering wire, bank transfer or crypto"),
        ("warn", "karat_statement_published", "sellers with any karat-stamp statement"),
        ("bad", "makers_mark_published", "seller naming a maker's mark"),
    ]
    P.append('<div class="kpis">' + "".join(
        f'<div class="kpi {c}"><div class="n">{stat(k)}</div><div class="l">{e(l)}</div></div>' for c, k, l in kp) + "</div>")
    P.append('<div class="callout">Three source classes are used and nothing else: the seller\'s own website; the Better '
             'Business Bureau\'s own website (an independent complaint registry); and US regulator websites (ftc.gov, sec.gov). '
             f'Search-engine summaries are never a source: {stat("leads")} things seen only in search results are listed '
             'separately under <a href="#leads">Leads</a> and are not data.</div>')

    # ---------------- findings
    P.append('<h2 id="findings">Findings and analysis</h2>')
    P.append("<p>Ordered by how much they matter to a buyer. Each one is a reading of the tables below, with its sources.</p>")
    rows = []
    for i in sorted(ev["irregularities"], key=lambda x: (SEVERITY_ORDER[x["severity"]], x["id"])):
        rows.append(f'<tr><td><code>{e(i["id"])}</code><br><span class="sev {e(i["severity"])}">{e(i["severity"])}</span></td>'
                    f'<td class="seller">{e(name[i["seller_id"]])}</td>'
                    f'<td><strong>{e(i["title"])}</strong><span class="note">{e(i["detail"])}</span></td>'
                    f'<td>{e(i["action"])}</td><td class="src">{src(i["basis"])}</td></tr>')
    P.append(table("t-findings", ["ID", "Seller", "What was found", "What to do about it", "Sources · read (UTC)"], rows))

    # ---------------- reputation
    P.append('<h2 id="reputation">1 · Reputation — what the Better Business Bureau prints</h2>')
    P.append("<p>One row per BBB profile; two sellers have two profiles. BBB grades run from A+ to F and are, in BBB's words, "
             "its opinion of how a business is likely to interact with its customers. Complaint counts are not adjusted "
             "for company size.</p>")
    rows, seen = [], []
    for o in obs:
        if o["task"] != "F0-1":
            continue
        key = (o["seller_id"], o["profile"])
        if key in seen:
            continue
        seen.append(key)
        sid, prof = key
        cols = ["profile", "accreditation", "rating", "complaints_3y", "complaints_12m", "complaint_status", "complaint_types",
                "customer_reviews"]
        tds = "".join(f"<td>{cell(of('F0-1', sid, c, prof))}</td>" for c in cols)
        rids = [x["read_id"] for c in cols for x in of("F0-1", sid, c, prof)]
        rows.append(f'<tr><td class="seller">{e(name[sid])}</td>{tds}<td class="src">{src(rids)}</td></tr>')
    P.append(table("t-reputation", ["Seller", "BBB profile", "Accreditation", "Grade", "Complaints 3 yr", "12 mo",
                                    "How BBB files them", "Complaint types", "Customer reviews", "Sources · read (UTC)"], rows))
    a6 = next(a for a in ev["anchors"] if a["id"] == "A-6")
    a7 = next(a for a in ev["anchors"] if a["id"] == "A-7")
    P.append(f'<div class="callout warn"><strong>How BBB says to read this.</strong> <q>{e(a6["quote"])}</q><q>{e(a7["quote"])}</q>'
             f'<span class="small">Printed at the foot of every BBB profile read; cited from {src([a6["read_id"]])}</span></div>')

    # ---------------- identity
    P.append('<h2 id="identity">2 · Business identity and real contact information</h2>')
    P.append("<p>Read from each seller's own contact and terms pages, from the SEC where the seller or its parent files there, "
             "and — clearly flagged — from BBB where the seller's own pages name no legal entity. "
             f'{stat("address_blank")} of {stat("sellers")} contact pages print no corporate street address.</p>')
    rows = []
    for s in sellers:
        sid = s["id"]
        cols = ["entity", "phone", "email", "address"]
        tds = "".join(f"<td>{cell(of('F0-2', sid, c))}</td>" for c in cols)
        rids = [x["read_id"] for c in cols for x in of("F0-2", sid, c)]
        rows.append(f'<tr><td class="seller">{e(name[sid])}</td>{tds}<td class="src">{src(rids)}</td></tr>')
    P.append(table("t-identity", ["Seller", "Legal entity or registry record", "Telephone", "E-mail", "Street address",
                                  "Sources · read (UTC)"], rows))

    # ---------------- payment
    P.append('<h2 id="payment">3 · Payment protection</h2>')
    P.append("<p>The checklist says to pay by credit card and to avoid methods that cannot be disputed. This table records what "
             "each seller's own payment page prints. It does not test a checkout.</p>")
    rows = []
    for s in sellers:
        sid = s["id"]
        cols = ["cards", "irreversible_methods", "incentive_or_clause"]
        tds = "".join(f"<td>{cell(of('F0-3', sid, c))}</td>" for c in cols)
        rids = [x["read_id"] for c in cols for x in of("F0-3", sid, c)]
        rows.append(f'<tr><td class="seller">{e(name[sid])}</td>{tds}<td class="src">{src(rids)}</td></tr>')
    P.append(table("t-payment", ["Seller", "Credit cards accepted", "Methods that cannot be disputed like a card charge",
                                 "Incentive or clause", "Sources · read (UTC)"], rows))

    # ---------------- stamps
    P.append('<h2 id="stamps">4 · Hallmark and maker\'s-mark disclosure</h2>')
    a2 = next(a for a in ev["anchors"] if a["id"] == "A-2")
    a3 = next(a for a in ev["anchors"] if a["id"] == "A-3")
    P.append(f'<div class="callout"><strong>The rule this is measured against (FTC).</strong> <q>{e(a2["quote"])}</q><q>{e(a3["quote"])}</q>'
             f'<span class="small">{src([a2["read_id"]])}</span></div>')
    P.append("<p>What each seller publishes about the marks struck inside its gold rings. A sentence on a website is a seller's "
             "claim; it is not evidence of a stamp inside any particular ring, and a karat stamp alone does not prove purity.</p>")
    rows = []
    for s in sellers:
        sid = s["id"]
        cols = ["karat_stamp_statement", "makers_mark_statement", "other_purity_statement"]
        tds = "".join(f"<td>{cell(of('F0-4', sid, c))}</td>" for c in cols)
        rids = [x["read_id"] for c in cols for x in of("F0-4", sid, c)]
        rows.append(f'<tr><td class="seller">{e(name[sid])}</td>{tds}<td class="src">{src(rids)}</td></tr>')
    P.append(table("t-stamps", ["Seller", "Karat-stamp statement", "Maker's-mark statement", "Other purity statements",
                                "Sources · read (UTC)"], rows))

    # ---------------- flagged for review
    P.append('<h2 id="flagged">Flagged for review</h2>')
    P.append(f"<p>Every cell this register could not confirm, with the page that was read and the reason. {stat('blank')} cells are "
             "blank. None of them blocks publication; each is something to check by hand or to ask the seller.</p>")
    rows = []
    for o in obs:
        if o["value"] is not None:
            continue
        who = name[o["seller_id"]] + (f' — {o["profile"]}' if o.get("profile") else "")
        rows.append(f'<tr><td class="seller">{e(who)}</td><td>{e(TASK_LABEL[o["task"]])}</td><td>{e(FIELD_LABEL[o["field"]])}</td>'
                    f'<td>{flags_html(o["flags"], blank=True)}</td><td>{e(o.get("note") or "")}</td>'
                    f'<td class="src">{src([o["read_id"]])}</td></tr>')
    P.append(table("t-flagged", ["Seller", "Table", "Cell", "Why it is blank", "Note", "Page that was read · (UTC)"], rows))

    # ---------------- customer statements
    P.append('<h2 id="statements">Customer and seller statements printed by BBB</h2>')
    P.append("<p>Quoted because they bear on purity, weight or documentation. Each is one person's statement as BBB prints it. "
             "BBB does not verify them and neither does this project; reviewer names are left out.</p>")
    rows = []
    for c in ev["customer_statements"]:
        rows.append(f'<tr><td><code>{e(c["id"])}</code></td><td class="seller">{e(name[c["seller_id"]])}</td>'
                    f'<td>{e(c["kind"])}<span class="note">dated {e(c["printed_date"])} on BBB</span></td>'
                    f'<td><q>{e(c["quote"])}</q></td><td>{e(c["why"])}</td><td class="src">{src([c["read_id"]])}</td></tr>')
    P.append(table("t-statements", ["ID", "Seller", "What it is", "Words printed", "Why it is listed", "Source · read (UTC)"], rows))

    # ---------------- leads
    P.append('<h2 id="leads">Leads — seen only in search results, not verified</h2>')
    P.append('<div class="callout warn">Nothing in this table is data. Each line is something a search result showed and that '
             "no official page confirmed in this pass. The last column is the official page to check it against.</div>")
    rows = []
    for lead in ev["leads_unverified"]:
        rows.append(f'<tr><td><code>{e(lead["id"])}</code></td><td class="seller">{e(name[lead["seller_id"]])}</td>'
                    f'<td><strong>{e(lead["topic"])}</strong><span class="note">{e(lead["lead"])}</span></td>'
                    f'<td>{e(lead["why"])}</td><td class="src">{src([lead["verify_read_id"]])}</td></tr>')
    P.append(table("t-leads", ["ID", "Seller", "Lead (unverified)", "Why it matters", "Official page to check"], rows))

    # ---------------- ask the seller
    P.append('<h2 id="ask">Questions to put to the seller in writing before paying</h2>')
    P.append("<p>Generated from the flags each seller carries above. A written answer is documentation; a refusal to answer is an "
             "answer too. The checklist's last line stands: do not buy if the seller will not allow verification or return.</p>")
    P.append('<div class="cols">')
    for s in sellers:
        sid = s["id"]
        have = {f for o in obs if o["seller_id"] == sid for f in o["flags"]}
        qs = [q for keys, q in QUESTIONS if have & set(keys)]
        P.append(f'<div class="card"><h3>{e(name[sid])}</h3><ul class="tight">' + "".join(f"<li>{e(q)}</li>" for q in qs) + "</ul></div>")
    P.append("</div>")
    a4 = next(a for a in ev["anchors"] if a["id"] == "A-4")
    a5 = next(a for a in ev["anchors"] if a["id"] == "A-5")
    P.append(f'<div class="callout"><strong>If something goes wrong (FTC).</strong> <q>{e(a4["quote"])}</q><q>{e(a5["quote"])}</q>'
             f'<span class="small">{src([a4["read_id"]])} · complaint address printed on that page: '
             f'{ext("https://reportfraud.ftc.gov/", "ReportFraud.ftc.gov")}</span></div>')

    # ---------------- calculations and incidental
    P.append('<h2 id="calc">Calculations and incidental reads</h2>')
    rows = []
    for d in ev["derived"]:
        rows.append(f'<tr><td><code>{e(d["id"])}</code></td><td>{e(d["what"])}</td><td><code>{e(d["expr"])}</code></td>'
                    f'<td><strong>{e(d["result"])} {e(d["unit"])}</strong></td><td>{e(d["inputs_from"])}</td></tr>')
    P.append('<p class="small">The only arithmetic on this page. Inputs are figures quoted above; the checker re-derives each with exact decimals.</p>')
    P.append('<div class="table-wrap"><table><thead><tr><th>ID</th><th>What</th><th>Expression</th><th>Result</th><th>Inputs from</th></tr></thead>'
             f'<tbody>{"".join(rows)}</tbody></table></div>')
    rows = []
    for n in ev["incidental"]:
        rows.append(f'<tr><td><code>{e(n["id"])}</code></td><td class="seller">{e(n["row"])}</td><td>{e(n["what"])}<q>{e(n["quote"])}</q></td>'
                    f'<td>{e(n["stored"])}<span class="note">{e(n["status"])}</span></td><td class="src">{src([n["read_id"]])}</td></tr>')
    P.append(table("t-incidental", ["ID", "Row", "What the page printed", "Stored value", "Source · read (UTC)"], rows))

    # ---------------- method
    P.append('<h2 id="method">Method, limits and how to re-check</h2>')
    P.append('<div class="cols">')
    P.append('<div class="card"><h3>How each value was recorded</h3><ul class="tight">'
             f'<li>{e(ev["reader"])}</li><li>{e(ev["timestamp_rule"])}</li><li>{e(ev["quote_rule"])}</li>'
             "</ul></div>")
    P.append('<div class="card"><h3>What this register does not establish</h3><ul class="tight">'
             + "".join(f"<li>{e(x)}</li>" for x in ev["limits"]) + "</ul></div>")
    P.append('<div class="card"><h3>Checks run on this page</h3><ul class="tight">'
             "<li>Every value sits next to the words the page printed, and every figure in a value occurs in those words.</li>"
             "<li>A blank is blank and carries a flag.</li>"
             "<li>Seller facts come from that seller's own domain, reputation facts from bbb.org, registry facts from a regulator.</li>"
             "<li>Every calculation re-derives exactly; every count in the prose is recomputed.</li>"
             "<li>No figure appears on this page that is absent from the evidence file; every table row has an official https link.</li>"
             "<li>The page loads no script, form, image or remote resource, and equals a fresh render of the evidence file.</li>"
             "</ul><p class=\"small\">Run <code>python3 scripts/session_f0dbdb3e/check_register.py</code>. A pass shows the register is "
             "sound and sourced. It cannot show that a quotation still matches the live page — open the links. "
             "After every review, look for hallucinations again.</p></div>")
    P.append("</div>")
    P.append(f'<p class="small">Machine-readable evidence: <a href="evidence.json">evidence.json</a> · text report: '
             f'<a href="report.md">report.md</a> · repository: {ext(REPO_URL, "karagemop466-tech/GOLD4")}</p>')

    # ---------------- ledger
    P.append('<h2 id="ledger">Read ledger — every page opened</h2>')
    P.append(f"<p>{stat('reads')} pages, in the order they are cited. Where a page is long, the part that was read is stated.</p>")
    rows = []
    for r in ev["reads"]:
        extra = ""
        if r.get("served_url"):
            extra += f'<span class="note">served as {ext(r["served_url"], r["served_url"])}</span>'
        if r.get("note"):
            extra += f'<span class="note">{e(r["note"])}</span>'
        rows.append(f'<tr><td><code>{e(r["read_id"])}</code></td><td>{e(r["publisher"])}</td>'
                    f'<td>{ext(r["url"], r["page_title"])}{extra}</td>'
                    f'<td>{e(r["read_utc"])}</td><td>{e(r["chunks_read"])}</td></tr>')
    P.append(table("t-ledger", ["ID", "Publisher", "Page", "Read (UTC)", "Part read"], rows))
    P.append(f"<h3>Addresses that answered “not found” ({stat('not_found')})</h3>")
    P.append('<p class="small">Listed so that nobody cites them and nobody guesses them again. No value is attributed to them.</p>')
    P.append('<ul class="tight">' + "".join(
        f'<li><code>{e(n["url"])}</code> — {e(n["result"])} — {e(n["read_utc"])} ({e(name[n["seller_id"]])})</li>' for n in ev["not_found"])
        + "</ul>")

    # ---------------- requests
    P.append('<h2 id="requests">Requests logged for the owners of shared files</h2>')
    P.append("<p>This session edits no shared file. Each line is a request recorded on the coordination board.</p>")
    rows = []
    for q in ev["requests"]:
        rows.append(f"<tr><td><code>{e(q['id'])}</code></td><td>{e(q['target'])}</td><td>{e(q['owner'])}</td><td>{e(q['request'])}</td></tr>")
    P.append('<div class="table-wrap"><table><thead><tr><th>ID</th><th>File</th><th>Owner</th><th>Request</th></tr></thead>'
             f'<tbody>{"".join(rows)}</tbody></table></div>')

    P.append('<footer>Generated by <code>scripts/session_f0dbdb3e/build_register.py</code> from '
             '<code>reviews/due-diligence-f0dbdb3e/evidence.json</code>. Not hand-edited. '
             "Automated checks find defined errors; they do not prove that a seller is trustworthy or that a ring is gold. "
             'Back to the <a href="../../index.html">project home</a>.</footer>')
    P.append("</main>")
    P.append("</body>")
    P.append("</html>")
    return "\n".join(P) + "\n"


# --------------------------------------------------------------------------------------------------
# Markdown
# --------------------------------------------------------------------------------------------------
def render_md(ev: dict) -> str:
    sellers = ev["sellers"]
    name = {s["id"]: s["name"] for s in sellers}
    name["all"] = "All ten sellers"
    reads = {r["read_id"]: r for r in ev["reads"]}
    obs = ev["observations"]
    st = stats_of(ev)

    def md(text) -> str:
        return str(text).replace("|", "\\|").replace("\n", " ")

    def val(items) -> str:
        if not items:
            return "—"
        out = []
        for o in items:
            if o["value"] is None:
                out.append("**blank** — " + ", ".join(f"`{f}`" for f in o["flags"]) + f" ({o['read_id']})")
            else:
                flags = (" " + " ".join(f"`{f}`" for f in o["flags"])) if o["flags"] else ""
                out.append(f"{md(o['value'])}{flags} ({o['read_id']})")
        return "<br>".join(out)

    def of(task, sid, field, profile=None):
        return [o for o in obs if o["task"] == task and o["seller_id"] == sid and o["field"] == field
                and (profile is None or o.get("profile") == profile)]

    L: list[str] = []
    L.append("# Seller due-diligence register")
    L.append("")
    L.append(f"Session `{ev['session']}` · every value read on 2026-11-11 between {ev['read_window_utc']['first'][11:]} and "
             f"{ev['read_window_utc']['last'][11:]} UTC · generated from `evidence.json`, not hand-edited.")
    L.append("")
    L.append(f"> **NO HALLUCINATIONS.** {ev['no_hallucination_rule']}")
    L.append("")
    L.append("The page with the quotations for every cell is `index.html` in this folder. The bracketed codes below are read IDs; "
             "their addresses and read times are in the ledger at the end.")
    L.append("")
    L.append("## Summary")
    L.append("")
    L.append("| Measure | Count |")
    L.append("|---|---|")
    for key, label in [("sellers", "Sellers covered"), ("reads", "Official pages read"), ("observations", "Table cells recorded"),
                       ("filled", "Cells with a value and the page's words"), ("blank", "Cells left blank and flagged"),
                       ("irregularities", "Irregularities logged"), ("bbb_profiles", "BBB profiles read"),
                       ("sellers_accredited", "Sellers BBB-accredited"), ("sellers_not_accredited", "Sellers not accredited"),
                       ("profiles_all_unanswered", "BBB profiles with every complaint unanswered"),
                       ("cards_read", "Sellers whose card acceptance was read"),
                       ("cards_unread", "Sellers whose payment methods could not be read"),
                       ("irreversible_offered", "Sellers offering wire, bank transfer or cryptocurrency"),
                       ("karat_statement_published", "Sellers with any karat-stamp statement"),
                       ("makers_mark_published", "Sellers naming a maker's mark"),
                       ("leads", "Unverified leads kept apart from data")]:
        L.append(f"| {label} | {st[key]} |")
    L.append("")
    L.append("## Findings")
    L.append("")
    L.append("| ID | Severity | Seller | Finding | What to do | Sources |")
    L.append("|---|---|---|---|---|---|")
    for i in sorted(ev["irregularities"], key=lambda x: (SEVERITY_ORDER[x["severity"]], x["id"])):
        L.append(f"| {i['id']} | {i['severity']} | {md(name[i['seller_id']])} | **{md(i['title'])}** — {md(i['detail'])} | "
                 f"{md(i['action'])} | {', '.join(i['basis'])} |")
    L.append("")
    L.append("## 1 · Reputation — what the Better Business Bureau prints")
    L.append("")
    L.append("| Seller | BBB profile | Accreditation | Grade | Complaints 3 yr | 12 mo | How BBB files them | Customer reviews |")
    L.append("|---|---|---|---|---|---|---|---|")
    seen = []
    for o in obs:
        if o["task"] != "F0-1":
            continue
        key = (o["seller_id"], o["profile"])
        if key in seen:
            continue
        seen.append(key)
        sid, prof = key
        cols = ["profile", "accreditation", "rating", "complaints_3y", "complaints_12m", "complaint_status", "customer_reviews"]
        L.append(f"| {md(name[sid])} | " + " | ".join(val(of("F0-1", sid, c, prof)) for c in cols) + " |")
    L.append("")
    L.append("## 2 · Business identity and contact")
    L.append("")
    L.append("| Seller | Legal entity or registry record | Telephone | E-mail | Street address |")
    L.append("|---|---|---|---|---|")
    for s in sellers:
        L.append(f"| {md(s['name'])} | " + " | ".join(val(of("F0-2", s["id"], c)) for c in ("entity", "phone", "email", "address")) + " |")
    L.append("")
    L.append("## 3 · Payment protection")
    L.append("")
    L.append("| Seller | Credit cards accepted | Methods that cannot be disputed like a card charge | Incentive or clause |")
    L.append("|---|---|---|---|")
    for s in sellers:
        L.append(f"| {md(s['name'])} | " + " | ".join(val(of("F0-3", s["id"], c))
                                                      for c in ("cards", "irreversible_methods", "incentive_or_clause")) + " |")
    L.append("")
    L.append("## 4 · Hallmark and maker's-mark disclosure")
    L.append("")
    L.append("| Seller | Karat-stamp statement | Maker's-mark statement | Other purity statements |")
    L.append("|---|---|---|---|")
    for s in sellers:
        L.append(f"| {md(s['name'])} | " + " | ".join(val(of("F0-4", s["id"], c)) for c in
                                                      ("karat_stamp_statement", "makers_mark_statement", "other_purity_statement")) + " |")
    L.append("")
    L.append("## Flagged for review — every blank cell")
    L.append("")
    L.append("| Seller | Table | Cell | Why it is blank | Page that was read |")
    L.append("|---|---|---|---|---|")
    for o in obs:
        if o["value"] is not None:
            continue
        who = name[o["seller_id"]] + (f" — {o['profile']}" if o.get("profile") else "")
        r = reads[o["read_id"]]
        L.append(f"| {md(who)} | {TASK_LABEL[o['task']]} | {FIELD_LABEL[o['field']]} | {', '.join('`' + f + '`' for f in o['flags'])} | "
                 f"[{o['read_id']}]({r['url']}) |")
    L.append("")
    L.append("## Unverified leads (search results only — not data)")
    L.append("")
    for lead in ev["leads_unverified"]:
        r = reads[lead["verify_read_id"]]
        L.append(f"- **{lead['id']} · {name[lead['seller_id']]} · {lead['topic']}.** {lead['lead']} "
                 f"*Check against:* [{lead['verify_read_id']}]({r['url']}).")
    L.append("")
    L.append("## Requests logged for the owners of shared files")
    L.append("")
    for q in ev["requests"]:
        L.append(f"- **{q['id']}** — `{q['target']}` — {q['request']}")
    L.append("")
    L.append("## What this register does not establish")
    L.append("")
    for x in ev["limits"]:
        L.append(f"- {x}")
    L.append("")
    L.append("## Read ledger")
    L.append("")
    L.append("| ID | Publisher | Page | Read (UTC) | Part read |")
    L.append("|---|---|---|---|---|")
    for r in ev["reads"]:
        L.append(f"| {r['read_id']} | {md(r['publisher'])} | [{md(r['page_title'])}]({r['url']}) | {r['read_utc']} | {md(r['chunks_read'])} |")
    L.append("")
    L.append("Check: `python3 scripts/session_f0dbdb3e/check_register.py`. A pass shows the register is sound and sourced; "
             "it does not show that a seller is trustworthy. After every review, look for hallucinations again.")
    return "\n".join(L) + "\n"


def main() -> int:
    ev = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    page, report = render_html(ev), render_md(ev)
    if "--check" in sys.argv[1:]:
        stale = []
        if not PAGE.exists() or PAGE.read_text(encoding="utf-8") != page:
            stale.append(str(PAGE.relative_to(ROOT)))
        if not REPORT.exists() or REPORT.read_text(encoding="utf-8") != report:
            stale.append(str(REPORT.relative_to(ROOT)))
        if stale:
            print("STALE: " + ", ".join(stale) + " — re-run the builder")
            return 1
        print("OK: index.html and report.md equal a fresh render of evidence.json")
        return 0
    PAGE.write_text(page, encoding="utf-8")
    REPORT.write_text(report, encoding="utf-8")
    print(f"wrote {PAGE.relative_to(ROOT)} ({len(page):,} bytes) and {REPORT.relative_to(ROOT)} ({len(report):,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
