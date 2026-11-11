#!/usr/bin/env python3
"""Hallucination, integrity and security check for the seller due-diligence register.

Session arena/f0dbdb3e-gold4.  Read-only: it never writes a file and never touches the network.

    python3 scripts/session_f0dbdb3e/check_register.py              # check the files on disk
    python3 scripts/session_f0dbdb3e/check_register.py --self-test  # prove the checks can fail

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

# Fixed identifiers that contain digits but are names, not figures. They are removed before the page's
# figures are compared with the evidence file.
NOT_FIGURES = ("karagemop466-tech/GOLD4", "session_f0dbdb3e", "due-diligence-f0dbdb3e", "arena/f0dbdb3e-gold4")


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


def run(ev: dict, page: str | None, report: str | None) -> list[tuple[bool, str, str]]:
    """Run every check on an evidence object and the published page/report text. Pure: no file is written."""
    results: list[tuple[bool, str, str]] = []

    def check(ok: bool, name: str, detail: str = "") -> None:
        results.append((bool(ok), name, detail))

    # ---- 1. schema --------------------------------------------------------------------------
    need = ["schema_version", "session", "no_hallucination_rule", "read_window_utc", "sellers", "reads",
            "not_found", "anchors", "observations", "irregularities", "customer_statements",
            "leads_unverified", "requests", "incidental", "derived", "count_claims", "limits"]
    missing = [k for k in need if k not in ev]
    check(not missing, "1. evidence file has every required section", ", ".join(missing))
    if missing:
        return results

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
    if page is None:
        check(False, "12. published page exists", str(PAGE))
    else:
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
        shown = re.findall(r'data-stat="([a-zA-Z0-9_\-]+)">(\d+)<', page)   # every occurrence, not one per key
        for key, val in shown:
            if key not in st:
                bad.append(f"page shows an unknown statistic {key}")
            elif st[key] != int(val):
                bad.append(f"statistic {key}: page shows {val}, recomputed {st[key]}")
        visible = re.sub(r"<style.*?</style>", " ", page, flags=re.S)
        visible = html.unescape(re.sub(r"<[^>]+>", " ", visible))
        for fixed in NOT_FIGURES:
            visible = visible.replace(fixed, " ")
        known = digit_runs(" ".join(strings_in(ev))) | {str(v) for v in st.values()}
        unknown = sorted(digit_runs(visible) - known, key=lambda x: (len(x), x))
        if unknown:
            bad.append("figures on the page that are not in the evidence file: " + ", ".join(unknown[:15]))
        check(not bad, f"15. page figures: {len(shown)} printed statistics recompute, and no figure appears that is absent from the evidence",
              "; ".join(bad))

        # ---- 16. page and report are exactly what the builder renders -------------------------
        bad = []
        try:
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            import build_register  # type: ignore

            if build_register.render_html(ev) != page:
                bad.append("index.html differs from a fresh render (hand-edited or stale)")
            if report is None:
                bad.append("report.md is missing")
            elif build_register.render_md(ev) != report:
                bad.append("report.md differs from a fresh render (hand-edited or stale)")
        except Exception as exc:  # noqa: BLE001
            bad.append(f"builder could not be run: {exc}")
        check(not bad, "16. index.html and report.md are byte-for-byte the builder's output for this evidence file",
              "; ".join(bad))

    return results


def number_of(name: str) -> int:
    return int(name.split(".", 1)[0])


def self_test(ev: dict, page: str, report: str) -> int:
    """Inject one fault at a time and require the named check to fail. Nothing on disk is changed."""
    import copy

    def obs_where(e, **kw):
        return next(o for o in e["observations"] if all(o.get(k) == v for k, v in kw.items()))

    def m_figure(e, p, r):
        o = obs_where(e, task="F0-1", seller_id="blue-nile", field="complaints_3y", profile="Blue Nile Inc")
        o["value"] = "142"
        return e, p, r

    def m_exact(e, p, r):
        obs_where(e, task="F0-2", seller_id="ross-simons", field="email")["value"] = "service@ross-simons.com"
        return e, p, r

    def m_blank_no_flag(e, p, r):
        next(o for o in e["observations"] if o["value"] is None)["flags"] = []
        return e, p, r

    def m_blank_with_quote(e, p, r):
        next(o for o in e["observations"] if o["value"] is None)["quote"] = "A+ Rated by BBB"
        return e, p, r

    def m_value_no_quote(e, p, r):
        next(o for o in e["observations"] if o["value"] is not None)["quote"] = ""
        return e, p, r

    def m_host(e, p, r):
        next(x for x in e["reads"] if x["read_id"] == "MJ-04")["url"] = "https://www.mejurs.us.com/faqs/"
        return e, p, r

    def m_http(e, p, r):
        next(x for x in e["reads"] if x["read_id"] == "BBB-01")["url"] = "http://www.bbb.org/x"
        return e, p, r

    def m_time(e, p, r):
        next(x for x in e["reads"] if x["read_id"] == "BBB-01")["read_utc"] = "2026-11-11T09:59:00Z"
        return e, p, r

    def m_wrong_class(e, p, r):
        obs_where(e, task="F0-3", seller_id="mene", field="cards")["read_id"] = "BBB-15"
        return e, p, r

    def m_other_seller(e, p, r):
        obs_where(e, task="F0-4", seller_id="mejuri", field="karat_stamp_statement")["read_id"] = "RS-03"
        return e, p, r

    def m_missing_cell(e, p, r):
        e["observations"] = [o for o in e["observations"]
                             if not (o["task"] == "F0-3" and o["seller_id"] == "catbird" and o["field"] == "cards")]
        return e, p, r

    def m_lead_as_data(e, p, r):
        e["leads_unverified"][0]["read_id"] = "MJ-01"
        return e, p, r

    def m_dangling(e, p, r):
        e["irregularities"][0]["basis"] = ["BBB-99"]
        return e, p, r

    def m_arith(e, p, r):
        e["derived"][1]["result"] = "7.5"
        return e, p, r

    def m_count(e, p, r):
        e["count_claims"][1]["expected"] = 9
        return e, p, r

    def m_script(e, p, r):
        return e, p.replace("</main>", "<script>alert(1)</script></main>"), r

    def m_remote(e, p, r):
        return e, p.replace("</main>", '<img src="https://example.com/x.png"></main>'), r

    def m_bad_host(e, p, r):
        return e, p.replace("</main>", '<a href="https://example.com/" rel="noopener noreferrer">x</a></main>'), r

    def m_broken_local(e, p, r):
        return e, p.replace('href="evidence.json"', 'href="evidence-missing.json"'), r

    def m_row_no_link(e, p, r):
        i = p.index('<table class="data" id="t-identity"')
        j = p.index("</tr>", p.index("<tbody>", i))
        row = p[i:j]
        stripped = re.sub(r'<a href="https://[^"]*"[^>]*>([^<]*)</a>', r"\1", row)
        return e, p[:i] + stripped + p[j:], r

    def m_invented_number(e, p, r):
        return e, p.replace("</main>", "<p>Average premium over melt value: 731 percent.</p></main>"), r

    def m_stat(e, p, r):
        return e, re.sub(r'data-stat="blank">\d+<', 'data-stat="blank">3<', p, count=1), r

    def m_stale_report(e, p, r):
        return e, p, r + "\nhand edit\n"

    cases = [
        ("a figure in a value that the page did not print", m_figure, 5),
        ("an 'exact' value that differs from the printed one", m_exact, 5),
        ("a blank cell without a flag", m_blank_no_flag, 4),
        ("a blank cell that still carries a quotation", m_blank_with_quote, 4),
        ("a value without the page's words", m_value_no_quote, 4),
        ("a seller fact sourced from a look-alike host", m_host, 2),
        ("a source address that is not https", m_http, 2),
        ("a read time outside the declared window", m_time, 2),
        ("a payment value sourced from BBB instead of the seller", m_wrong_class, 3),
        ("a stamp statement sourced from another seller's site", m_other_seller, 3),
        ("a seller missing from a table", m_missing_cell, 6),
        ("a search-result lead presented as a read", m_lead_as_data, 7),
        ("a finding that cites a page that was never read", m_dangling, 8),
        ("a calculation with the wrong result", m_arith, 9),
        ("a prose count that the data does not support", m_count, 10),
        ("a script injected into the page", m_script, 12),
        ("a remote resource loaded by the page", m_remote, 12),
        ("a link to a host that was never read", m_bad_host, 13),
        ("a broken local link", m_broken_local, 13),
        ("a table row stripped of its source links", m_row_no_link, 14),
        ("an invented figure typed into the page", m_invented_number, 15),
        ("a statistic on the page that the evidence does not support", m_stat, 15),
        ("a hand-edited report", m_stale_report, 16),
    ]
    base = run(ev, page, report)
    if not all(ok for ok, _, _ in base):
        print("SELF-TEST ABORTED: the unmodified files do not pass, so the faults cannot be isolated")
        return 1
    print("Self-test: one fault injected at a time; the named check must fail.")
    failed = 0
    for label, mutate, expect in cases:
        e2, p2, r2 = mutate(copy.deepcopy(ev), page, report)
        res = run(e2, p2, r2)
        tripped = sorted({number_of(n) for ok, n, _ in res if not ok})
        ok = expect in tripped
        failed += 0 if ok else 1
        print(("CAUGHT  " if ok else "MISSED  ") + f"{label:<62} expected check {expect:>2}; failed: {tripped or 'none'}")
    print()
    if failed:
        print(f"SELF-TEST RESULT: {failed} of {len(cases)} injected faults were NOT caught")
        return 1
    print(f"SELF-TEST RESULT: all {len(cases)} injected faults were caught")
    return 0


def main() -> int:
    if not EVIDENCE.exists():
        print("FAIL: evidence file is missing:", EVIDENCE)
        return 1
    ev = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    page = PAGE.read_text(encoding="utf-8") if PAGE.exists() else None
    report = REPORT.read_text(encoding="utf-8") if REPORT.exists() else None
    if "--self-test" in sys.argv[1:]:
        if page is None or report is None:
            print("SELF-TEST ABORTED: index.html or report.md is missing")
            return 1
        return self_test(ev, page, report)

    results = run(ev, page, report)
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
