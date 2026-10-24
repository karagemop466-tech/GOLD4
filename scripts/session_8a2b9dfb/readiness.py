#!/usr/bin/env python3
"""Conservative checklist evidence register, not a purchase-approval engine.

Build: python3 scripts/session_8a2b9dfb/readiness.py
Check: python3 scripts/session_8a2b9dfb/readiness.py --check

Reads canonical inputs without modifying them. The output is deterministic and
hash-bound to those inputs. A historical record, boolean or source-health match
is never promoted to a current selected-configuration price or physical assay.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date
from decimal import Decimal, InvalidOperation
from hashlib import sha256
from html import escape
import json
import math
from pathlib import Path
import re
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
OBSERVATIONS = "scripts/session_8a2b9dfb/source_observations.json"
OUTPUT_JSON = "reports/readiness-8a2b9dfb.json"
OUTPUT_HTML = "pages/readiness.html"
INPUTS = ("data/rings.json", "data/sellers.json", "data/sources.json", OBSERVATIONS)
V1 = "V1_direct_page_fetch"
RETAILER_DOMAINS = {
    "allurez": "allurez.com", "blue-nile": "bluenile.com",
    "brilliant-earth": "brilliantearth.com", "vrai": "vrai.com",
    "mejuri": "mejuri.com", "anjolee": "anjolee.com", "sarraf": "sarraf.com",
    "catbird": "catbirdnyc.com", "mene": "mene.com", "ross-simons": "ross-simons.com",
}
REFERENCE_HOSTS = {"consumer.ftc.gov", "www.gia.edu", "mene.com", "www.mene.com", "www.brilliantearth.com", "github.com"}
UNSAFE_URL = re.compile(r'[\x00-\x20\x7f\\<>"`]|%(?:0[0-9a-f]|1[0-9a-f]|7f)', re.I)
EXPLICIT_SOLID = re.compile(
    r"\bsolid\s+(?:(?:yellow|white|rose|recycled|\d{1,2}\s*k(?:arat)?)\s+){0,3}gold\b", re.I
)
CONFLICTING_SOLID = re.compile(
    r"\b(?:not(?:\s+necessarily)?\s+solid|hollow(?:ed)?|(?:electro)?plat(?:e|ed|ing)|vermeil|filled|overlay|electroform\w*|gold[- ]tone)\b", re.I
)
CONFLICT_FLAGS = {"COPY_INCONSISTENT_METAL", "MIXED_METAL_UNCLEAR", "SPEC_LISTED_PAVE_ON_PLAIN_BAND"}


def no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path: Path):
    def invalid_constant(value):
        raise ValueError(f"Non-finite JSON constant: {value}")
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=no_duplicate_keys,
                      parse_constant=invalid_constant)


def safe_url(value, retailer_id=None):
    """Allow exact approved public HTTPS hosts; never render an unsafe href."""
    if not isinstance(value, str) or not value or UNSAFE_URL.search(value):
        return None
    try:
        parsed = urlsplit(value)
        hosts = REFERENCE_HOSTS if retailer_id is None else {
            RETAILER_DOMAINS.get(retailer_id, ""), "www." + RETAILER_DOMAINS.get(retailer_id, "")
        }
        if (parsed.scheme != "https" or parsed.hostname not in hosts or
                parsed.username is not None or parsed.password is not None or
                parsed.port not in (None, 443) or
                (parsed.hostname == "github.com" and not parsed.path.startswith("/karagemop466-tech/GOLD4/"))):
            return None
    except ValueError:
        return None
    return value


def positive_number(value):
    """No bools, strings, units, NaNs, infinities, zero or negative amounts."""
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
        return None
    try:
        number = Decimal(str(value))
        if number.is_finite() and number > 0 and math.isfinite(float(number)):
            return number
    except (ValueError, InvalidOperation, OverflowError):
        pass
    return None


def date_only(value):
    if not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError:
        return None


def explicit_solid_wording(value):
    return (isinstance(value, str) and bool(EXPLICIT_SOLID.search(value))
            and not CONFLICTING_SOLID.search(value))


def evaluate_row(row, seller, sources, capture_date):
    """Report evidence, not truth. Unsupported fields stay None, not estimates."""
    retailer_id = row.get("retailer_id")
    product_url = safe_url(row.get("url"), retailer_id)
    flags = []
    if not product_url:
        flags.append("OFFICIAL_PRODUCT_LINK_UNVERIFIED")
    karat = positive_number(row.get("karat"))
    karat = int(karat) if karat in {Decimal(k) for k in (10, 14, 18, 22, 24)} and product_url else None
    if karat is None:
        flags.append("KARAT_CLAIM_UNVERIFIED")

    solid_quote = row.get("solid_gold_statement")
    solid_ok = (product_url and row.get("solid_gold_status") == "stated"
                and explicit_solid_wording(solid_quote))
    if not solid_ok:
        flags.append("EXPLICIT_SOLID_WORDING_UNVERIFIED")
    if row.get("solid_gold_status") == "stated" and not explicit_solid_wording(solid_quote):
        flags.append("SOLID_STATUS_NOT_SUPPORTED_BY_RECORDED_WORDING")

    weight_url = safe_url(row.get("weight_source_url"), retailer_id)
    weight = positive_number(row.get("weight_g"))
    scope = row.get("weight_scope")
    if not (weight is not None and weight_url and row.get("weight_verification") == V1
            and isinstance(scope, str) and scope.strip()):
        weight = None
        flags.append("SOURCED_WEIGHT_AND_SCOPE_UNVERIFIED")
    weight_date = date_only(row.get("weight_captured_utc")) if weight is not None else None
    if weight is not None and weight_date is None:
        flags.append("WEIGHT_FIELD_CAPTURE_DATE_NOT_RECORDED")

    # A return-window integer cannot establish eligibility of a customized ring,
    # permission to test it, or the refund route/fees. No default window is used.
    policy_id = row.get("returns_source_id") or seller.get("returns_source_id")
    policy_url = safe_url(sources.get(policy_id, {}).get("url"), retailer_id)
    if not policy_url:
        flags.append("OFFICIAL_RETURN_POLICY_LINK_UNVERIFIED")
    contact = seller.get("contact") if isinstance(seller.get("contact"), dict) else {}
    contact_url = safe_url(contact.get("contact_page"), retailer_id)

    # Neither a boolean 'hallmark published', nor 'reputation verified', nor an
    # HTTP 200/CONFIRMED structured amount supplies the necessary underlying
    # item-specific evidence. This report deliberately has no approval override.
    flags += ["HALLMARK_PLUS_MAKER_NOT_DOCUMENTED", "CURRENT_CONFIGURED_QUOTE_UNVERIFIED",
              "INDEPENDENT_REPUTATION_RESEARCH_UNVERIFIED", "RETURN_AND_TESTING_RIGHTS_UNVERIFIED",
              "CONFIGURED_CREDIT_CARD_OPTION_UNVERIFIED", "PHYSICAL_TEST_NOT_DOCUMENTED"]
    conflicts = sorted(set(row.get("flags", [])) & CONFLICT_FLAGS)
    if conflicts:
        flags.append("PRODUCT_SPECIFICATION_CONFLICT_REQUIRES_REVIEW")

    return {
        "id": row.get("id"), "retailer": row.get("retailer"),
        "product_name": row.get("product_name"), "category": row.get("category"),
        "official_product_url": product_url,
        "record_capture_date_utc": date_only(capture_date),
        "recorded_karat_claim": karat,
        "recorded_explicit_solid_wording": solid_quote if solid_ok else None,
        "unsupported_recorded_solid_wording": solid_quote if not solid_ok and isinstance(solid_quote, str) else None,
        "recorded_weight_g": float(weight) if weight is not None else None,
        "recorded_weight_scope": scope if weight is not None else None,
        "weight_source_url": weight_url if weight is not None else None,
        "weight_field_capture_date_utc": weight_date,
        "hallmark_and_maker_evidence": None,
        "current_exact_price_usd": None,
        "independent_reputation_evidence": None,
        "configured_return_and_testing_eligibility": None,
        "configured_credit_card_option": None,
        "physical_test_result": None,
        "official_return_policy_url": policy_url,
        "official_contact_route_url": contact_url,
        "source_health_state_as_recorded": (row.get("source_check") or {}).get("state"),
        "source_health_price_state_as_recorded": (row.get("source_check") or {}).get("price_state"),
        "source_health_checked_utc_as_recorded": (row.get("source_check") or {}).get("checked_utc"),
        "inherited_specification_conflicts": conflicts,
        "online_evidence_complete": False,
        "decision": "EVIDENCE_INCOMPLETE_NOT_PURCHASE_APPROVED",
        "flags": sorted(set(flags)),
    }


def build_report(root: Path):
    loaded = {name: read_json(root / name) for name in INPUTS}
    rings, sellers, sources, observations = (loaded[name] for name in INPUTS)
    seller_list = sellers["sellers"]
    source_list = sources["sources"]
    if len({x["id"] for x in seller_list}) != len(seller_list):
        raise ValueError("Duplicate seller IDs")
    if len({x["id"] for x in source_list}) != len(source_list):
        raise ValueError("Duplicate source IDs")
    seller_map = {x["id"]: x for x in seller_list}
    source_map = {x["id"]: x for x in source_list}
    rows = []
    ids = set()
    for raw in rings["rows"]:
        row_id = raw.get("id")
        if not isinstance(row_id, str) or not re.fullmatch(r"[A-Z]{2}-\d{2}", row_id) or row_id in ids:
            raise ValueError(f"Invalid/duplicate row ID: {row_id}")
        if raw.get("retailer_id") not in seller_map:
            raise ValueError(f"Unknown seller for {row_id}")
        ids.add(row_id)
        row = evaluate_row(raw, seller_map[raw["retailer_id"]], source_map, rings.get("captured_utc"))
        if not row["official_product_url"]:
            raise ValueError(f"Unsafe or missing official product URL for {row_id}; no page generated")
        rows.append(row)
    if not rows:
        raise ValueError("Empty candidate list; no completeness claims generated")
    obs_sources = observations["sources"]
    obs_ids = {s["id"] for s in obs_sources}
    if len(obs_ids) != len(obs_sources) or not date_only(observations.get("review_date_utc")):
        raise ValueError("Invalid observation IDs/date")
    for source in obs_sources:
        if not safe_url(source["url"]):
            raise ValueError("Observation source is not an approved official HTTPS URL")
    for finding in observations["findings"]:
        if not finding["source_ids"] or set(finding["source_ids"]) - obs_ids or set(finding["row_ids"]) - ids:
            raise ValueError(f"Finding lacks valid sources/rows: {finding['id']}")
    return {
        "schema_version": "1.0.0", "kind": "checklist_evidence_completeness_not_purchase_approval",
        "review_date_utc": observations["review_date_utc"],
        "limits": "Historical canonical claims are not independently re-certified by this register. No selected-configuration quote, reputation assessment, return/testing permission, hallmark/maker proof or physical test is supplied. Current-price fields remain null. Automated checks cannot prove the absence of hallucinations.",
        "input_sha256": {name: sha256((root / name).read_bytes()).hexdigest() for name in INPUTS},
        "stats": {
            "candidates": len(rows), "retailers": len({r["retailer"] for r in rows}),
            "recorded_explicit_solid_wording": sum(r["recorded_explicit_solid_wording"] is not None for r in rows),
            "recorded_sourced_weights": sum(r["recorded_weight_g"] is not None for r in rows),
            "complete_online_evidence": sum(r["online_evidence_complete"] for r in rows),
            "current_exact_quotes": sum(r["current_exact_price_usd"] is not None for r in rows),
            "flags": dict(sorted(Counter(f for r in rows for f in r["flags"]).items())),
        },
        "official_observations": observations,
        "rows": rows,
    }


def e(value):
    return escape(str(value), quote=True)


def link(url, label):
    return f'<a href="{e(url)}" rel="noopener noreferrer">{e(label)}</a>' if url else ""


def badge(label, kind="warn"):
    return f'<span class="badge b-{e(kind)}">{e(label)}</span>'


def render_html(report):
    stats = report["stats"]
    obs = report["official_observations"]
    sources = {s["id"]: s for s in obs["sources"]}
    finding_rows = []
    for f in obs["findings"]:
        refs = "<br>".join(link(sources[x]["url"], sources[x]["title"]) for x in f["source_ids"])
        finding_rows.append(f'<tr><td>{e(f["id"])}<br>{badge(f["status"], "ok" if f["status"].startswith("done") else "warn")}</td><td><strong>{e(f["title"])}</strong><p>{e(f["detail"])}</p></td><td class="src">{refs}</td></tr>')
    product_rows = []
    for row in report["rows"]:
        solid = (f'<q>{e(row["recorded_explicit_solid_wording"])}</q><span class="sub">Recorded seller wording, not an assay</span>'
                 if row["recorded_explicit_solid_wording"] else badge("Unverified"))
        weight = (f'<strong>{e(format(row["recorded_weight_g"], ".4g"))} g</strong><span class="sub">{e(row["recorded_weight_scope"])}</span>'
                  + link(row["weight_source_url"], "Official weight source")
                  + ('<span class="sub">Historical field capture: ' + e(row["weight_field_capture_date_utc"]) + '.</span>'
                     if row["weight_field_capture_date_utc"] else '<span class="sub">Historical record; field-specific capture date not recorded.</span>')
                  if row["recorded_weight_g"] is not None else badge("Unverified"))
        details = ["A current size/configuration-specific USD quote is not established.",
                   "Karat mark AND maker/company-mark evidence have not been documented together.",
                   "Independent reputation/complaint research is not supplied.",
                   "Return eligibility after independent inspection/testing is not established for this configuration.",
                   "A protected credit-card option for this configuration is not established.",
                   "No physical purity/weight verification has been performed for this candidate."]
        if row["unsupported_recorded_solid_wording"]:
            details.append("Recorded text does not establish explicit solid wording: " + row["unsupported_recorded_solid_wording"])
        if row["inherited_specification_conflicts"]:
            details.append("Inherited specification conflicts: " + ", ".join(row["inherited_specification_conflicts"]))
        checked = row["source_health_checked_utc_as_recorded"]
        if checked:
            details.append("Historical source-health observation: " + str(checked) + "; "
                           + str(row["source_health_state_as_recorded"]) + " / "
                           + str(row["source_health_price_state_as_recorded"]) + ". Not a current checkout quote.")
        detail_html = "".join(f'<li>{e(x)}</li>' for x in details)
        search = " ".join(str(row.get(x) or "") for x in ("id", "retailer", "product_name", "category", "recorded_karat_claim"))
        policy = link(row["official_return_policy_url"], "Official policy")
        contact = link(row["official_contact_route_url"], "Official contact route")
        karat = f'{e(row["recorded_karat_claim"])}K' if row["recorded_karat_claim"] is not None else ""
        product_rows.append(f'''<tr data-row-id="{e(row['id'])}" data-search="{e(search.lower())}">
<td class="src"><strong>{e(row['id'])} · {e(row['retailer'])}</strong><br>{link(row['official_product_url'], row['product_name'])}<span class="sub">{e(row['category'])} · record capture {e(row['record_capture_date_utc'] or 'unverified')}</span></td>
<td>{karat}<span class="sub">Recorded claim, not measured purity</span></td><td>{solid}</td><td>{weight}</td>
<td class="current-price" aria-label="Unverified current selected-configuration USD price"></td>
<td>{badge('Unverified')}<span class="sub">No combined karat + maker-mark evidence</span></td>
<td>{policy}<span class="sub">Applicability / testing permission unverified</span></td>
<td>{contact}<span class="sub">Independent reputation unverified</span></td>
<td>{badge('Evidence incomplete')}<details><summary>Why this is not purchase-approved</summary><ul>{detail_html}</ul></details></td></tr>''')
    observation_rows = []
    for source in obs["sources"]:
        quoted = " ".join(source["quotes"])
        observation_rows.append(f'<tr><td>{e(source["title"])}<span class="sub">{e("Chunks " + ", ".join(map(str, source["chunks_reviewed"])) if source["chunks_reviewed"] else "Pinned repository code; local runtime test")} · {e(source.get("review_date_utc", report["review_date_utc"]))} UTC</span></td><td><q>{e(quoted)}</q><p>{e(source["observation"])}</p></td><td class="src">{link(source["url"], "Official source")}</td></tr>')
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Purchase readiness · GOLD4</title><meta name="description" content="Source-linked checklist evidence gaps for every GOLD4 ring candidate. No inferred prices or purchase approvals.">
<link rel="stylesheet" href="../assets/style.css"><script defer src="../assets/app.js"></script>
<style>summary{{cursor:pointer;font-weight:600}}details{{min-width:190px;margin-top:8px}}details ul{{padding-left:17px;max-width:42ch}}caption{{text-align:left;padding:14px 12px;color:#52525b}}.current-price{{min-width:120px}}.readiness-table{{min-width:1320px}}.skip{{position:absolute;left:-9999px}}.skip:focus{{position:fixed;top:8px;left:8px;z-index:100;background:white;padding:12px}}q{{quotes:"“" "”"}}.table-wrap:focus-visible{{outline:3px solid #a8802a}}</style></head>
<body><a class="skip" href="#content">Skip to content</a>
<header class="site-header"><div class="wrap bar"><a class="brand" href="../index.html"><span class="mark">Au</span>GOLD4 <small>Evidence before purchase</small></a>
<nav class="main" aria-label="Main navigation"><a href="../index.html">Dashboard</a><a href="purity.html">Buying checklist</a><a href="calculator.html">Gold calculator</a><a href="flagged.html">Flagged for Review</a><a href="readiness.html" class="active" aria-current="page">Readiness</a></nav></div></header>
<main class="wrap" id="content">
<div class="nohall"><h2>NO HALLUCINATIONS — evidence is not purchase approval</h2>
<p>Unknown values stay blank. A historical price, a karat stamp, a seller claim or a successful automated source check is not proof of current price, solid construction or measured purity. Look for hallucinations after every review; automated checks only test their programmed rules.</p>
<p><strong>No candidate currently has complete evidence for your pre-purchase checklist.</strong> That is an evidence-completeness finding, not a claim that any ring is fake. No ring has been independently assayed for this project.</p></div>
<section class="hero"><span class="eyebrow">Requirement-by-requirement register</span><h1>What is still missing before buying?</h1>
<p class="lede">Every candidate, with its official links and unresolved buying requirements. No manual research input is required to generate this register.</p>
<p class="meta-line">Selected-source review: {e(report['review_date_utc'])} UTC. All other product facts below are inherited, dated research records, <strong>not freshly re-certified facts</strong>. No size or final checkout configuration was selected.</p></section>
<div class="kpis"><div class="kpi"><div class="n">{stats['candidates']}</div><div class="l">Candidates / {stats['retailers']} retailers</div></div>
<div class="kpi gold"><div class="n">{stats['recorded_explicit_solid_wording']}</div><div class="l">Explicit solid-wording records</div><div class="s">Not proof of construction</div></div>
<div class="kpi"><div class="n">{stats['recorded_sourced_weights']}</div><div class="l">Sourced weight records</div><div class="s">Size-specific / often approximate</div></div>
<div class="kpi"><div class="n">{stats['complete_online_evidence']}</div><div class="l">Complete pre-purchase evidence</div><div class="s">No purchase approvals</div></div></div>
<section class="section" id="flagged"><h2>Flagged for Review — requirement findings</h2><p class="sub">New findings are published, not silently corrected. Unverified items do not block publishing this research.</p>
<div class="table-wrap" tabindex="0" role="region" aria-label="Requirement findings"><table><thead><tr><th>ID / status</th><th>Finding and limits</th><th>Official sources</th></tr></thead><tbody>{''.join(finding_rows)}</tbody></table></div>
<p>See also the <a href="flagged.html">canonical Flagged for Review register</a> and <a href="../reviews/readiness-8a2b9dfb.md">review methods and security checks</a>.</p></section>
<section class="section" id="candidates"><h2>All candidates — checklist evidence gaps</h2>
<p class="sub">Current exact-price cells are intentionally blank for all {stats['candidates']} rows. No historical/structured amount is promoted to a selected-size quote. Metal and weight columns are explicitly labelled inherited seller claims. Blank does not mean zero.</p>
<div class="toolbar"><label for="filter">Find a candidate</label><input id="filter" type="search" placeholder="Search seller, ID, style or karat"><span id="filterCount" class="count" aria-live="polite"></span></div>
<div class="table-wrap" tabindex="0" role="region" aria-label="Scrollable candidate readiness table"><table class="readiness-table"><caption>Evidence completeness, not a ranking, authentication result or recommendation to buy.</caption>
<thead><tr><th>Candidate / official product</th><th>Claimed karat</th><th>Explicit solid wording</th><th>Recorded weight / scope</th><th>Current exact USD quote</th><th>Karat + maker mark</th><th>Returns / testing</th><th>Seller due diligence</th><th>Readiness / explanation</th></tr></thead><tbody>{''.join(product_rows)}</tbody></table></div></section>
<section class="section"><h2>Checks that cannot be completed by a product listing</h2>
<div class="grid two"><div class="card"><h3>Before paying</h3><p>Require the exact metal, size, weight scope and price; explicit solid-gold wording; karat and maker-mark evidence; independent seller research; written return eligibility including resized/custom exclusions and inspection/testing permission. Prefer a credit card, not an irreversible payment. Preserve the listing and all written claims.</p><p>{link(sources['ftc-jewelry-r8']['url'], 'FTC jewelry buying guidance')} · <a href="purity.html">Full project checklist</a></p></div>
<div class="card"><h3>After delivery, before wearing or resizing</h3><p>Arrange an independent professional check of weight, markings, construction and purity within the applicable return window. Ask the professional which tests are appropriate. Obtain the seller’s written permission before any test that may alter the ring.</p><p><strong>One XRF reading is not a guarantee:</strong> GIA documents thick plating/electroforming that XRF alone may miss. {link(sources['gia-electroformed-r8']['url'], 'Official GIA case study')}</p></div></div></section>
<section class="section"><h2>Selected official sources actually opened in this review</h2><p class="sub">Only these sources/chunks were re-opened in this session. The remaining product rows were evaluated against their existing records, not re-read live. Product prices, seller reputation and physical purity were not comprehensively re-verified.</p>
<div class="table-wrap" tabindex="0" role="region" aria-label="Selected official source observations"><table><thead><tr><th>Source / scope</th><th>Observed wording and interpretation limits</th><th>Official link</th></tr></thead><tbody>{''.join(observation_rows)}</tbody></table></div></section>
<section class="section"><h2>Reproducible, source-bound analysis</h2><p>The builder leaves canonical data unchanged. Its machine-readable output contains input-file SHA-256 hashes, every row’s evidence gaps, and the selected-source observations. Rebuilding from unchanged inputs gives byte-identical output; <code>--check</code> detects stale generated output.</p>
<p><a href="../reports/readiness-8a2b9dfb.json">Download readiness JSON</a> · <a href="../reports/readiness-checks-8a2b9dfb.txt">Executed security / hallucination / link checks</a> · <a href="calculator.html">Dated gold-content calculator and raw-gold arithmetic</a></p></section>
<footer class="foot"><p>Research only, not legal, financial or gemological advice. No payment was made and no seller was contacted on your behalf.</p><p><strong>Repeat the hallucination review after every change.</strong> Official source links enable review but do not independently prove the claims on them.</p></footer></main></body></html>
'''


def outputs(root):
    report = build_report(root)
    return {OUTPUT_JSON: json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
            OUTPUT_HTML: render_html(report)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check generated output for input drift; write nothing")
    args = parser.parse_args()
    result = outputs(ROOT)
    stale = []
    for name, content in result.items():
        path = ROOT / name
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                stale.append(name)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    if stale:
        raise SystemExit("FAIL: readiness outputs missing/stale: " + ", ".join(stale))
    print("PASS: readiness register " + ("matches canonical input hashes" if args.check else "built")
          + "; unsupported current quotes remain blank; no purchase approvals.")


if __name__ == "__main__":
    main()
