#!/usr/bin/env python3
"""Hallucination, integrity and security check for the seller due-diligence register.

Session arena/f0dbdb3e-gold4.  Read-only: it never writes a file and never touches the network.

    python3 scripts/session_f0dbdb3e/check_register.py

What it can and cannot establish
--------------------------------
This sandbox has no general outbound internet from the shell, so the script cannot re-open a page.
It therefore does NOT prove that a quotation matches the live page.  It proves the things a script
can prove, each of which closes one way a made-up value could get in:

  * every value sits next to the words the page printed, and every figure in the value occurs in them;
  * a blank is really blank (no value, no quotation) and carries a flag saying why;
  * a seller fact is sourced from that seller's own domain, a reputation fact from bbb.org,
    a registry fact from a regulator -- never from a search-engine summary;
  * every calculation re-derives with exact decimal arithmetic;
  * every count the prose relies on is recomputed from the data;
  * the published page shows no figure that is absent from the evidence file, every table row
    carries an official https link, and the page loads no script and no remote resource;
  * the page and the Markdown report are byte-for-byte what the builder renders from the evidence.

Exit status 0 = every check passed.  A pass is not proof that any seller is trustworthy.
"""
from __future__ import annotations

import ast
import html
import json
import re
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
REVIEW = ROOT / "reviews" / "due-diligence-f0dbdb3e"
EVIDENCE = REVIEW / "evidence.json"
PAGE = REVIEW / "index.html"
REPORT = REVIEW / "report.md"

TASKS = ("F0-1", "F0-2", "F0-3", "F0-4")
BBB_FIELDS = ("profile", "accreditation", "rating", "complaints_3y", "complaints_12m",
              "complaint_status", "complaint_types", "customer_reviews")
REQUIRED = {
    "F0-2": ("entity", "phone", "email", "address"),
    "F0-3": ("cards", "irreversible_methods"),
    "F0-4": ("karat_stamp_statement", "makers_mark_statement"),
}
# Hosts a link on the published page may point to, beyond the hosts of the pages that were read.
EXTRA_LINK_HOSTS = {
    "reportfraud.ftc.gov": "complaint address printed on the FTC page read as FTC-01",
    "github.com": "this repository",
    "karagemop466-tech.github.io": "this project's published site",
}
REGULATOR_HOSTS = {"consumer.ftc.gov", "www.sec.gov"}
BBB_HOST = "www.bbb.org"

results: list[tuple[bool, str, str]] = []


def check(ok: bool, name: str, detail: str = "") -> None:
    results.append((bool(ok), name, detail))


def norm(text: str) -> str:
    """Collapse whitespace and unify typographic apostrophes/quotes so comparisons are fair."""
    text = text.replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"')
    return re.sub(r"\s+", " ", text).strip()


NUM = re.compile(r"\d+(?:[.,/:\-]\d+)*")


def figures(text: str) -> list[str]:
    return NUM.findall(text or "")


def digit_runs(text: str) -> set[str]:
    return set(re.findall(r"\d+", text or ""))


def host_of(url: str) -> str:
    return (urlparse(url).hostname or "").lower()


def belongs(host: str, domain: str) -> bool:
    return host == domain or host.endswith("." + domain)


def whole_token(value: str, quote: str) -> bool:
    pat = r"(?<![A-Za-z0-9+\-@.])" + re.escape(value) + r"(?![A-Za-z0-9+\-@])"
    return re.search(pat, quote) is not None


def safe_decimal(expr: str) -> Decimal:
    """Evaluate + - * / and parentheses over decimal literals, exactly."""
    if not re.fullmatch(r"[0-9.+\-*/() ]+", expr):
        raise ValueError("expression contains characters other than digits and + - * / ( )")

    def ev(node):
        if isinstance(node, ast.Expression):
            return ev(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return Decimal(ast.get_source_segment(expr, node))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -ev(node.operand)
        if isinstance(node, ast.BinOp):
            a, b = ev(node.left), ev(node.right)
            if isinstance(node.op, ast.Add):
                return a + b
            if isinstance(node.op, ast.Sub):
                return a - b
            if isinstance(node.op, ast.Mult):
                return a * b
            if isinstance(node.op, ast.Div):
                return a / b
        raise ValueError("unsupported expression")

    return ev(ast.parse(expr, mode="eval"))


def strings_in(obj) -> list[str]:
    out: list[str] = []
    if isinstance(obj, str):
        out.append(obj)
    elif isinstance(obj, bool):
        pass
    elif isinstance(obj, (int, float)):
        out.append(str(obj))
    elif isinstance(obj, dict):
        for v in obj.values():
            out.extend(strings_in(v))
    elif isinstance(obj, list):
        for v in obj:
            out.extend(strings_in(v))
    return out


def stats_of(ev: dict) -> dict[str, int]:
    """Counts the page prints.  Computed here independently of the builder."""
    obs = ev["observations"]
    by = lambda t, f: [o for o in obs if o["task"] == t and o["field"] == f]  # noqa: E731
    profiles = {(o["seller_id"], o.get("profile")) for o in obs if o["task"] == "F0-1"}
    acc_sellers = {o["seller_id"] for o in by("F0-1", "accreditation") if (o["value"] or "").startswith("Accredited")}
    notacc_sellers = {o["seller_id"] for o in by("F0-1", "accreditation") if o["value"] == "Not accredited"}
    unanswered = {(o["seller_id"], o.get("profile")) for o in by("F0-1", "complaint_status")
                  if "ALL_BBB_COMPLAINTS_UNANSWERED" in o["flags"]}
    irreversible = {o["seller_id"] for o in by("F0-3", "irreversible_methods")
                    if o["value"] and not o["value"].startswith("None listed")}
    s = {
        "sellers": len(ev["sellers"]),
        "reads": len(ev["reads"]),
        "not_found": len(ev["not_found"]),
        "observations": len(obs),
        "filled": sum(1 for o in obs if o["value"] is not None),
        "blank": sum(1 for o in obs if o["value"] is None),
        "irregularities": len(ev["irregularities"]),
        "irregularities_high": sum(1 for i in ev["irregularities"] if i["severity"] == "High"),
        "irregularities_medium": sum(1 for i in ev["irregularities"] if i["severity"] == "Medium"),
        "irregularities_low": sum(1 for i in ev["irregularities"] if i["severity"] == "Low"),
        "irregularities_info": sum(1 for i in ev["irregularities"] if i["severity"] == "Info"),
        "statements": len(ev["customer_statements"]),
        "leads": len(ev["leads_unverified"]),
        "requests": len(ev["requests"]),
        "bbb_profiles": len(profiles),
        "sellers_accredited": len(acc_sellers),
        "sellers_not_accredited": len(notacc_sellers - acc_sellers),
        "profiles_all_unanswered": len(unanswered),
        "cards_read": sum(1 for o in by("F0-3", "cards") if o["value"]),
        "cards_unread": sum(1 for o in by("F0-3", "cards") if not o["value"]),
        "irreversible_offered": len(irreversible),
        "makers_mark_published": sum(1 for o in by("F0-4", "makers_mark_statement") if o["value"]),
        "karat_statement_published": sum(1 for o in by("F0-4", "karat_stamp_statement") if o["value"]),
        "address_blank": sum(1 for o in by("F0-2", "address") if not o["value"]),
    }
    for t in TASKS:
        s["filled_" + t] = sum(1 for o in obs if o["task"] == t and o["value"] is not None)
        s["blank_" + t] = sum(1 for o in obs if o["task"] == t and o["value"] is None)
    return s


def main() -> int:
    if not EVIDENCE.exists():
        print("FAIL: evidence file is missing:", EVIDENCE)
        return 1
    ev = json.loads(EVIDENCE.read_text(encoding="utf-8"))

    # ---- 1. schema --------------------------------------------------------------------------
    need = ["schema_version", "session", "no_hallucination_rule", "read_window_utc", "sellers", "reads",
            "not_found", "anchors", "observations", "irregularities", "customer_statements",
            "leads_unverified", "requests", "incidental", "derived", "count_claims", "limits"]
    missing = [k for k in need if k not in ev]
    check(not missing, "1. evidence file has every required section", ", ".join(missing))

    sellers = {s["id"]: s for s in ev["sellers"]}
    reads = {r["read_id"]: r for r in ev["reads"]}
    obs = ev["observations"]

    # ---- 2. the read ledger -----------------------------------------------------------------
    bad = []
    if len(reads) != len(ev["reads"]):
        bad.append("duplicate read ids")
    lo, hi = ev["read_window_utc"]["first"], ev["read_window_utc"]["last"]
    seller_domains = {s["official_domain"]: sid for sid, s in sellers.items()}
    for r in ev["reads"]:
        u = r["url"]
        h = host_of(u)
        if not u.startswith("https://"):
            bad.append(f"{r['read_id']}: not https")
        if r.get("served_url") and not r["served_url"].startswith("https://"):
            bad.append(f"{r['read_id']}: served_url not https")
        if not re.fullmatch(r"2026-11-11T\d\d:\d\d(:\d\d)?Z", r["read_utc"]):
            bad.append(f"{r['read_id']}: bad timestamp {r['read_utc']}")
        elif not (lo[:16] <= r["read_utc"][:16] <= hi[:16]):
            bad.append(f"{r['read_id']}: {r['read_utc']} outside the declared read window")
        c = r["source_class"]
        if c == "bbb" and h != BBB_HOST:
            bad.append(f"{r['read_id']}: class bbb but host {h}")
        elif c == "regulator" and h not in REGULATOR_HOSTS:
            bad.append(f"{r['read_id']}: class regulator but host {h}")
        elif c == "seller_site" and not any(belongs(h, d) for d in seller_domains):
            bad.append(f"{r['read_id']}: class seller_site but host {h} is no seller's official domain")
        elif c not in ("bbb", "regulator", "seller_site"):
            bad.append(f"{r['read_id']}: unknown source class {c}")
        if r.get("status") != "read":
            bad.append(f"{r['read_id']}: status is not 'read'")
    check(not bad, f"2. read ledger: {len(reads)} pages, all https, official hosts only, timestamps inside the window",
          "; ".join(bad[:8]))

    # ---- 3. observations: identity, source class, seller-domain match -------------------------
    bad = []
    ids = [o["obs_id"] for o in obs]
    if len(set(ids)) != len(ids):
        bad.append("duplicate observation ids")
    for o in obs:
        oid = o["obs_id"]
        if o["task"] not in TASKS:
            bad.append(f"{oid}: unknown task")
            continue
        if o["seller_id"] not in sellers:
            bad.append(f"{oid}: unknown seller {o['seller_id']}")
            continue
        r = reads.get(o["read_id"])
        if r is None:
            bad.append(f"{oid}: read {o['read_id']} is not in the ledger")
            continue
        c, h, dom = r["source_class"], host_of(r["url"]), sellers[o["seller_id"]]["official_domain"]
        t = o["task"]
        if t == "F0-1" and c != "bbb":
            bad.append(f"{oid}: reputation value not sourced from bbb.org")
        if t == "F0-3" and not (c == "seller_site" and belongs(h, dom)):
            bad.append(f"{oid}: payment value not sourced from the seller's own domain")
        if t == "F0-2":
            if c == "seller_site" and not belongs(h, dom):
                bad.append(f"{oid}: sourced from another seller's domain")
            if c == "bbb" and o["value"] is not None and "THIRD_PARTY_RECORD_BBB" not in o["flags"]:
                bad.append(f"{oid}: BBB-sourced identity value lacks THIRD_PARTY_RECORD_BBB")
        if t == "F0-4":
            if c == "seller_site" and not belongs(h, dom):
                bad.append(f"{oid}: sourced from another seller's domain")
            if c == "bbb" and "SELLER_STATEMENT_PRINTED_ON_BBB" not in o["flags"]:
                bad.append(f"{oid}: BBB-sourced statement lacks SELLER_STATEMENT_PRINTED_ON_BBB")
            if c == "regulator":
                bad.append(f"{oid}: a seller's stamp statement cannot come from a regulator page")
        for f in o["flags"]:
            if not re.fullmatch(r"[A-Z0-9_]+", f):
                bad.append(f"{oid}: malformed flag {f!r}")
    check(not bad, f"3. {len(obs)} observations: each tied to a ledger read of the right source class and the right seller's domain",
          "; ".join(bad[:8]))

    # ---- 4. blank means blank, and a blank is flagged -----------------------------------------
    bad = []
    for o in obs:
        if o["value"] is None:
            if o["quote"] is not None:
                bad.append(f"{o['obs_id']}: blank value but a quotation is present")
            if not o["flags"]:
                bad.append(f"{o['obs_id']}: blank value without a flag")
        else:
            if not (o["quote"] or "").strip():
                bad.append(f"{o['obs_id']}: value without the page's words")
            if not str(o["value"]).strip():
                bad.append(f"{o['obs_id']}: empty-string value")
    n_blank = sum(1 for o in obs if o["value"] is None)
    check(not bad, f"4. blanks are blank and flagged ({n_blank} blank cells); every value carries the page's words",
          "; ".join(bad[:8]))

    # ---- 5. every figure in a value occurs in its quotation -----------------------------------
    bad = []
    n_fig = 0
    for o in obs:
        if o["value"] is None:
            continue
        v, q = norm(str(o["value"])), norm(o["quote"])
        qf = set(figures(q))
        for f in figures(v):
            n_fig += 1
            if f not in qf:
                bad.append(f"{o['obs_id']}: figure {f!r} in the value is not in the quotation")
        if o.get("exact") and not whole_token(v, q):
            bad.append(f"{o['obs_id']}: exact value {v!r} is not printed as such in the quotation")
    check(not bad, f"5. {n_fig} figures in values all occur in the quoted page text; exact values are printed verbatim",
          "; ".join(bad[:8]))

    # ---- 6. coverage: no seller silently missing from a table ---------------------------------
    bad = []
    for sid in sellers:
        profs = {}
        for o in obs:
            if o["task"] == "F0-1" and o["seller_id"] == sid:
                profs.setdefault(o.get("profile"), set()).add(o["field"])
        if not profs:
            bad.append(f"{sid}: no BBB profile row")
        for p, fields in profs.items():
            miss = set(BBB_FIELDS) - fields
            if miss or not p:
                bad.append(f"{sid}/{p}: BBB row lacks {sorted(miss)}")
        for t, fields in REQUIRED.items():
            have = {o["field"] for o in obs if o["task"] == t and o["seller_id"] == sid}
            miss = set(fields) - have
            if miss:
                bad.append(f"{sid}: {t} lacks {sorted(miss)}")
    check(not bad, f"6. all {len(sellers)} sellers appear in all four tables with every required cell (filled or flagged)",
          "; ".join(bad[:8]))

    # ---- 7. nothing is sourced from a search summary ------------------------------------------
    bad = []
    for lead in ev["leads_unverified"]:
        if "read_id" in lead or "value" in lead:
            bad.append(f"{lead['id']}: a lead must not carry a read id or a value")
        if re.search(r"https?://", lead["lead"]):
            bad.append(f"{lead['id']}: a lead must not carry a clickable address")
        vr = lead.get("verify_read_id")
        if vr not in reads:
            bad.append(f"{lead['id']}: verify_read_id {vr!r} is not in the ledger")
    for r in ev["reads"]:
        if "search" in r["source_class"]:
            bad.append(f"{r['read_id']}: search result in the read ledger")
    check(not bad, f"7. {len(ev['leads_unverified'])} unverified leads are kept apart from values and each names an official page to check",
          "; ".join(bad[:8]))

    # ---- 8. references resolve ----------------------------------------------------------------
    bad = []
    for a in ev["anchors"]:
        if a["read_id"] not in reads:
            bad.append(f"{a['id']}: unknown read")
    for i in ev["irregularities"]:
        if i["severity"] not in ("High", "Medium", "Low", "Info"):
            bad.append(f"{i['id']}: unknown severity")
        if i["seller_id"] != "all" and i["seller_id"] not in sellers:
            bad.append(f"{i['id']}: unknown seller")
        if not i["basis"]:
            bad.append(f"{i['id']}: no source")
        for b in i["basis"]:
            if b not in reads:
                bad.append(f"{i['id']}: unknown read {b}")
    for c in ev["customer_statements"]:
        r = reads.get(c["read_id"])
        if r is None or r["source_class"] != "bbb":
            bad.append(f"{c['id']}: a customer statement must cite a bbb.org read")
        if c["seller_id"] not in sellers:
            bad.append(f"{c['id']}: unknown seller")
    for n in ev["incidental"]:
        if n["read_id"] not in reads:
            bad.append(f"{n['id']}: unknown read")
    check(not bad, "8. every anchor, irregularity, customer statement and incidental note cites a read in the ledger",
          "; ".join(bad[:8]))

    # ---- 9. calculations re-derive exactly ----------------------------------------------------
    bad = []
    for d in ev["derived"]:
        try:
            exact = safe_decimal(d["expr"])
            places = len(d["result"].split(".")[1]) if "." in d["result"] else 0
            got = exact.quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP)
            if got != Decimal(d["result"]):
                bad.append(f"{d['id']}: {d['expr']} = {got}, file says {d['result']}")
        except Exception as exc:  # noqa: BLE001
            bad.append(f"{d['id']}: {exc}")
    check(not bad, f"9. {len(ev['derived'])} calculations re-derive with exact decimal arithmetic", "; ".join(bad))

    # ---- 10. counts the prose relies on -------------------------------------------------------
    bad = []
    rings = json.loads((ROOT / "data" / "rings.json").read_text(encoding="utf-8"))["rows"]
    for k in ev["count_claims"]:
        q = k["query"]
        if q == "sellers":
            got = len(sellers)
        elif q == "F0-2 address blank":
            got = sum(1 for o in obs if o["task"] == "F0-2" and o["field"] == "address" and o["value"] is None)
        elif q == "rows":
            got = len(rings)
        elif q == "retailer_id == mejuri":
            got = sum(1 for r in rings if r["retailer_id"] == "mejuri")
        elif q == "retailer_id == mejuri and weight_g is not null":
            got = sum(1 for r in rings if r["retailer_id"] == "mejuri" and r.get("weight_g") is not None)
        elif q == "retailer_id == sarraf and weight_g is not null":
            got = sum(1 for r in rings if r["retailer_id"] == "sarraf" and r.get("weight_g") is not None)
        else:
            bad.append(f"{k['id']}: unknown query")
            continue
        if got != k["expected"]:
            bad.append(f"{k['id']}: {k['claim']} = {got}, file says {k['expected']}")
    check(not bad, f"10. {len(ev['count_claims'])} counts used in the prose recompute from the data", "; ".join(bad))

    # ---- 11. agreement with the canonical seller file (read-only) -----------------------------
    bad = []
    canon = {s["id"]: s for s in json.loads((ROOT / "data" / "sellers.json").read_text(encoding="utf-8"))["sellers"]}
    if set(canon) != set(sellers):
        bad.append(f"seller ids differ from data/sellers.json: {sorted(set(canon) ^ set(sellers))}")
    agree = fills = 0
    for sid, s in sellers.items():
        c = canon.get(sid)
        if not c:
            continue
        h = host_of(c["official_url"])
        if not belongs(h, s["official_domain"]):
            bad.append(f"{sid}: official domain {s['official_domain']} does not match data/sellers.json ({h})")
        for field in ("phone", "email"):
            stored = (c.get("contact") or {}).get(field)
            mine = next((o for o in obs if o["task"] == "F0-2" and o["seller_id"] == sid and o["field"] == field), None)
            if mine is None or mine["value"] is None:
                continue
            if stored is None:
                fills += 1
                continue
            if field == "phone":
                a = re.sub(r"\D", "", stored)[-10:]
                ok = a in re.sub(r"\D", "", mine["quote"])
            else:
                ok = stored.lower() in mine["quote"].lower()
            if ok:
                agree += 1
            else:
                bad.append(f"{sid}: stored {field} {stored!r} is not in today's page text")
    check(not bad, f"11. data/sellers.json untouched and consistent: {agree} stored contact values agree with today's reads, "
                   f"{fills} stored nulls now have a read value (logged as a request, not written)", "; ".join(bad))

    # ---- 12-15. the published page ------------------------------------------------------------
    if not PAGE.exists():
        check(False, "12. published page exists", str(PAGE))
    else:
        page = PAGE.read_text(encoding="utf-8")
        low = page.lower()
        bad = []
        if "NO HALLUCINATIONS" not in page:
            bad.append("the no-hallucination statement is missing")
        if "../../index.html" not in page:
            bad.append("no link back to the landing page that carries the project's statement")
        for needle in ("<script", "javascript:", "<iframe", "<object", "<embed", "<form", "<img", "<link ", "@import", "url("):
            if needle in low:
                bad.append(f"forbidden construct {needle!r}")
        if re.search(r"\son[a-z]+\s*=", low):
            bad.append("inline event handler")
        if re.search(r"""\ssrc\s*=""", low):
            bad.append("a src= attribute (remote or local resource load)")
        check(not bad, "12. page carries the no-hallucination statement and loads no script, form, image or remote resource",
              "; ".join(bad))

        bad = []
        allowed_hosts = {host_of(r["url"]) for r in ev["reads"]} | {host_of(r["served_url"]) for r in ev["reads"] if r.get("served_url")}
        allowed_hosts |= set(EXTRA_LINK_HOSTS)
        anchors_in_page = set(re.findall(r'\sid="([^"]+)"', page))
        n_ext = n_loc = 0
        for m in re.finditer(r"<a\s+([^>]*)>", page):
            attrs = m.group(1)
            hm = re.search(r'href="([^"]*)"', attrs)
            if not hm:
                bad.append("anchor without href")
                continue
            href = html.unescape(hm.group(1))
            if href.startswith("https://"):
                n_ext += 1
                if host_of(href) not in allowed_hosts:
                    bad.append(f"link to a host that was not read: {host_of(href)}")
                rel = re.search(r'rel="([^"]*)"', attrs)
                if not rel or "noopener" not in rel.group(1) or "noreferrer" not in rel.group(1):
                    bad.append(f"external link without rel=noopener noreferrer: {href[:60]}")
            elif href.startswith("#"):
                if href[1:] not in anchors_in_page:
                    bad.append(f"in-page link to a missing anchor {href}")
            elif re.match(r"^[a-z][a-z0-9+.\-]*:", href):
                bad.append(f"link with a scheme other than https: {href[:40]}")
            else:
                n_loc += 1
                target = (REVIEW / href.split("#")[0]).resolve()
                if not target.exists():
                    bad.append(f"broken local link {href}")
                elif ROOT not in target.parents and target != ROOT:
                    bad.append(f"local link leaves the repository: {href}")
        check(not bad, f"13. links: {n_ext} external (https, official hosts only, rel=noopener noreferrer), {n_loc} local, none broken",
              "; ".join(sorted(set(bad))[:8]))

        bad = []
        n_rows = 0
        for tm in re.finditer(r'<table class="data"[^>]*>(.*?)</table>', page, flags=re.S):
            body = re.search(r"<tbody>(.*?)</tbody>", tm.group(1), flags=re.S)
            if not body:
                bad.append("a data table has no body")
                continue
            for row in re.findall(r"<tr[^>]*>(.*?)</tr>", body.group(1), flags=re.S):
                n_rows += 1
                if not re.search(r'href="https://', row):
                    cell = re.sub(r"<[^>]+>", " ", row)
                    bad.append("row without an official source link: " + norm(cell)[:60])
        check(not bad and n_rows > 0, f"14. every one of {n_rows} table rows carries an https link to an official source",
              "; ".join(bad[:6]))

        bad = []
        st = stats_of(ev)
        shown = dict(re.findall(r'data-stat="([a-zA-Z0-9_\-]+)">(\d+)<', page))
        for key, val in shown.items():
            if key not in st:
                bad.append(f"page shows an unknown statistic {key}")
            elif st[key] != int(val):
                bad.append(f"statistic {key}: page shows {val}, recomputed {st[key]}")
        visible = re.sub(r"<style.*?</style>", " ", page, flags=re.S)
        visible = html.unescape(re.sub(r"<[^>]+>", " ", visible))
        known = digit_runs(" ".join(strings_in(ev))) | {str(v) for v in st.values()}
        unknown = sorted(digit_runs(visible) - known, key=lambda x: (len(x), x))
        if unknown:
            bad.append("figures on the page that are not in the evidence file: " + ", ".join(unknown[:15]))
        check(not bad, f"15. page figures: {len(shown)} statistics recompute, and no figure appears that is absent from the evidence",
              "; ".join(bad))

        # ---- 16. page and report are exactly what the builder renders -------------------------
        bad = []
        try:
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            import build_register  # type: ignore

            if build_register.render_html(ev) != page:
                bad.append("index.html differs from a fresh render (hand-edited or stale)")
            if not REPORT.exists():
                bad.append("report.md is missing")
            elif build_register.render_md(ev) != REPORT.read_text(encoding="utf-8"):
                bad.append("report.md differs from a fresh render (hand-edited or stale)")
        except Exception as exc:  # noqa: BLE001
            bad.append(f"builder could not be run: {exc}")
        check(not bad, "16. index.html and report.md are byte-for-byte the builder's output for this evidence file",
              "; ".join(bad))

    # ---- report -------------------------------------------------------------------------------
    width = max(len(n) for _, n, _ in results)
    failed = 0
    print("Seller due-diligence register — hallucination, integrity and security check")
    print("evidence:", EVIDENCE.relative_to(ROOT))
    for ok, name, detail in results:
        print(("PASS  " if ok else "FAIL  ") + name.ljust(width) + (("   -> " + detail) if (detail and not ok) else ""))
        failed += 0 if ok else 1
    print()
    if failed:
        print(f"RESULT: {failed} of {len(results)} checks FAILED")
        return 1
    print(f"RESULT: all {len(results)} checks passed")
    print("Reminder: a pass shows the register is internally sound and sourced; it does not show that a seller is")
    print("trustworthy or that a quotation still matches the live page. Re-read the linked pages before relying on them.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
