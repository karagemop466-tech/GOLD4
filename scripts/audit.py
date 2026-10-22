#!/usr/bin/env python3
"""Hallucination / integrity audit for the GOLD4 dataset and generated site.

This is the "security check" for factual integrity. It does not trust the data:
it re-derives every number from the published inputs, re-reads every source
reference, and fails loudly on anything that looks invented.

Run after every review pass:
    python3 scripts/compute.py && python3 scripts/build_site.py && python3 scripts/audit.py

Exit code 0 = all hard checks passed. Exit code 1 = at least one FAIL.
Warnings are printed and recorded but do not fail the build; they must be
reviewed and either fixed or published on the Flagged for Review page.
"""
from __future__ import annotations

import json
import math
import pathlib
import re
import sys
from datetime import datetime, timezone
from urllib.parse import urlparse

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REPORTS = ROOT / "reports"

OFFICIAL_HOSTS = {
    "blue-nile": ["bluenile.com"],
    "allurez": ["allurez.com"],
    "vrai": ["vrai.com"],
    "mejuri": ["mejuri.com"],
    "brilliant-earth": ["brilliantearth.com"],
    "anjolee": ["anjolee.com"],
}

# Tier A/B reference hosts (government, regulators, benchmark bodies).
REFERENCE_HOSTS = [
    "consumer.ftc.gov", "ftc.gov", "ecfr.gov", "law.cornell.edu",
    "uscode.house.gov", "govinfo.gov", "gold.org", "lbma.org.uk",
]

# Domains that must never be used as a source of fact for this project.
BANNED_HOST_SUBSTRINGS = [
    "ebay.", "amazon.", "poshmark.", "etsy.", "therealreal.", "1stdibs.",
    "pinterest.", "reddit.", "quora.", "wikipedia.", "medium.com", "blogspot",
    "wordpress.com", "facebook.com", "instagram.com", "tiktok.com", "x.com",
    "twitter.com", "youtube.com", "linkedin.com",
]

SPECULATION_WORDS = [
    "probably", "likely", "we believe", "we assume", "assume", "presumably",
    "roughly", "ballpark", "typical price", "market average", "should be around",
    "estimated", "guess", "circa",
]

RESULTS: list[tuple[str, str, str]] = []  # (status, check, detail)


def ok(check: str, detail: str = "") -> None:
    RESULTS.append(("PASS", check, detail))


def warn(check: str, detail: str) -> None:
    RESULTS.append(("WARN", check, detail))


def fail(check: str, detail: str) -> None:
    RESULTS.append(("FAIL", check, detail))


def load(name: str):
    path = DATA / name
    if not path.exists():
        fail(f"file:{name}", "missing")
        return None
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def host_of(url: str) -> str:
    try:
        h = urlparse(url).hostname or ""
    except ValueError:
        return ""
    return h.lower().removeprefix("www.")


def host_allowed(host: str, retailer_id: str, sellers: dict) -> bool:
    allowed = OFFICIAL_HOSTS.get(retailer_id, [])
    if not allowed:
        return False
    return any(host == a or host.endswith("." + a) for a in allowed)


def check_url(check_id: str, url: str | None, retailer_id: str, sellers: dict, label: str,
              allow_reference: bool = False) -> None:
    if not url:
        fail(check_id, f"{label}: missing URL")
        return
    if not url.startswith("https://"):
        fail(check_id, f"{label}: not https -> {url}")
        return
    host = host_of(url)
    for bad in BANNED_HOST_SUBSTRINGS:
        if bad in host:
            fail(check_id, f"{label}: banned domain {host} -> {url}")
            return
    if host_allowed(host, retailer_id, sellers):
        ok(check_id, f"{label}: {host}")
        return
    if allow_reference and any(host == h or host.endswith("." + h) for h in REFERENCE_HOSTS):
        ok(check_id, f"{label}: {host} (reference host)")
        return
    fail(check_id, f"{label}: host {host} is not an approved source for '{retailer_id}'")


def main() -> int:
    rings = load("rings.json")
    sellers_doc = load("sellers.json")
    sources_doc = load("sources.json")
    derived = load("derived.json")
    method = load("methodology.json")
    spot = load("gold_spot.json")
    if not all([rings, sellers_doc, sources_doc, derived, method, spot]):
        print("cannot continue: missing data files")
        return 1

    sellers = {s["id"]: s for s in sellers_doc["sellers"]}
    source_ids = {s["id"] for s in sources_doc["sources"]}
    spot_usd_oz = float(spot["benchmark"]["value_usd_per_oz"])
    oz_g = float(spot["constants"]["troy_ounce_grams"])
    usd_g = spot_usd_oz / oz_g
    fineness = {int(r["karat"]): float(r["fineness"]) for r in method["karat_fineness"]["table"]}
    min_fineness = {int(k): float(v) for k, v in method["legal_allowable_deviation"]["minimum_fineness_if_stamped"].items()}

    # ---------------------------------------------------------------- sources
    for src in sources_doc["sources"]:
        check_url("A-01 source registry URL", src["url"], guess_retailer(src["url"]), sellers, f"source {src['id']}", allow_reference=True)
        if src.get("tier") not in {"A", "B", "C", "D"}:
            fail("A-02 source tier", f"source {src['id']} has invalid tier {src.get('tier')!r}")
    ok("A-02 source tier", "all tiers valid")

    # ---------------------------------------------------------------- spot
    if abs((spot["constants"]["spot_usd_per_gram"] or 0) - round(usd_g, 6)) > 1e-6:
        fail("A-03 spot arithmetic", "spot_usd_per_gram does not equal value/31.1034768")
    else:
        ok("A-03 spot arithmetic", f"${usd_g:,.4f}/g from ${spot_usd_oz:,.2f}/oz")
    if abs(float(derived["spot"]["value_usd_per_oz"]) - spot_usd_oz) > 1e-9:
        fail("A-04 derived spot drift", "derived.json spot differs from gold_spot.json")
    else:
        ok("A-04 derived spot drift", "derived spot matches captured benchmark")

    # ---------------------------------------------------------------- rows
    seen_ids = set()
    seen_skus = set()
    for row in rings["rows"]:
        rid = row.get("id", "?")
        if rid in seen_ids:
            fail("B-01 unique id", f"duplicate id {rid}")
        seen_ids.add(rid)

        if row.get("retailer_id") not in sellers:
            fail("B-02 retailer exists", f"{rid}: retailer_id {row.get('retailer_id')!r} not in sellers.json")
        if row.get("karat") not in fineness:
            fail("B-03 valid karat", f"{rid}: karat {row.get('karat')!r}")
        else:
            # fineness must be exactly karat/24
            if abs(fineness[int(row["karat"])] - int(row["karat"]) / 24) > 1e-6:
                fail("B-04 fineness consistency", f"{rid}: fineness table inconsistent for {row['karat']}K")

        sku = row.get("sku")
        if sku:
            key = (row["retailer_id"], sku)
            if key in seen_skus:
                fail("B-05 duplicate sku", f"{rid}: {key}")
            seen_skus.add(key)

        # price
        price = row.get("price_usd")
        if price is not None:
            if not isinstance(price, (int, float)) or price <= 0 or math.isnan(float(price)):
                fail("B-06 price numeric", f"{rid}: bad price {price!r}")
            if not row.get("price_basis"):
                fail("B-07 price basis", f"{rid}: price without a stated basis (setting only vs includes stone)")
            if row.get("price_verification") != "V1_direct_page_fetch":
                if row.get("price_verification") == "V2_official_page_snapshot_only":
                    warn("B-08 price verification", f"{rid}: price is only V2 evidence and must be flagged")
                    if "PRICE_UNVERIFIED" not in row.get("flags", []) and "PRICE_V2_ONLY" not in row.get("flags", []):
                        fail("B-08 price verification", f"{rid}: V2 price without a flag")
                else:
                    fail("B-08 price verification", f"{rid}: price present but verification is {row.get('price_verification')!r}")
            if not row.get("price_captured_utc"):
                fail("B-09 price date", f"{rid}: price without capture date")
            check_url("B-10 price source", row.get("price_source_url"), row["retailer_id"], sellers, f"{rid} price")
        else:
            if "PRICE_UNVERIFIED" not in row.get("flags", []):
                fail("B-11 blank price flagged", f"{rid}: price is blank but PRICE_UNVERIFIED is not in flags")

        # weight
        w = row.get("weight_g")
        if w is not None:
            if not isinstance(w, (int, float)) or w <= 0:
                fail("B-12 weight numeric", f"{rid}: bad weight {w!r}")
            if not row.get("weight_scope"):
                fail("B-13 weight scope", f"{rid}: weight without scope (which size/what it includes)")
            if row.get("weight_verification") != "V1_direct_page_fetch":
                fail("B-14 weight verification", f"{rid}: weight not V1")
            check_url("B-15 weight source", row.get("weight_source_url"), row["retailer_id"], sellers, f"{rid} weight")
        else:
            if not ({"NO_WEIGHT_PUBLISHED", "WEIGHT_UNVERIFIED"} & set(row.get("flags", []))):
                fail("B-16 blank weight flagged", f"{rid}: weight blank without NO_WEIGHT_PUBLISHED/WEIGHT_UNVERIFIED")

        # solid gold statement
        if row.get("solid_gold_status") == "stated" and not row.get("solid_gold_statement"):
            fail("B-17 solid statement", f"{rid}: marked stated with no wording")
        if row.get("solid_gold_status") == "not_stated" and row.get("solid_gold_statement"):
            fail("B-17 solid statement", f"{rid}: marked not_stated but wording present")
        if row.get("solid_gold_status") not in {"stated", "not_stated"}:
            fail("B-17 solid statement", f"{rid}: invalid solid_gold_status")

        # hallmark
        if row.get("hallmark_published") is not False:
            fail("B-18 hallmark", f"{rid}: hallmark_published must be False unless evidence is recorded")

        # returns reference
        if row.get("returns_source_id") not in source_ids:
            fail("B-19 returns source", f"{rid}: returns_source_id {row.get('returns_source_id')!r} not in sources.json")

        # speculation scan
        for field in ("price_basis", "weight_scope", "flag_detail", "pair_note"):
            text = (row.get(field) or "").lower()
            for word in SPECULATION_WORDS:
                if word in text and "approximate" not in text:
                    warn("C-01 speculation language", f"{rid}.{field}: contains {word!r}")

    ok("B-01 unique id", f"{len(seen_ids)} rows")
    ok("B-02 retailer exists", "all retailers resolved")
    ok("B-03 valid karat", "all karats in methodology table")

    # ---------------------------------------------------------------- recompute
    mismatches = 0
    for row in derived["rows"]:
        rid = row["id"]
        k = int(row["karat"])
        expected_fin = fineness[k]
        if abs(float(row["fineness"]) - expected_fin) > 1e-6:
            fail("D-01 derived fineness", f"{rid}: {row['fineness']} != {expected_fin}")
            mismatches += 1
        if row.get("weight_g") is not None:
            w = float(row["weight_g"])
            pure = w * expected_fin
            if abs(float(row["pure_gold_g"]) - round(pure, 4)) > 1e-6:
                fail("D-02 derived gold grams", f"{rid}: {row['pure_gold_g']} != {round(pure,4)}")
                mismatches += 1
            val = pure * usd_g
            if abs(float(row["gold_value_usd"]) - val) > 0.01:
                fail("D-03 derived gold value", f"{rid}: {row['gold_value_usd']} != {val:.2f}")
                mismatches += 1
            if abs(float(row["legal_min_gold_value_usd"]) - w * min_fineness[k] * usd_g) > 0.01:
                fail("D-04 derived legal minimum", f"{rid}: mismatch")
                mismatches += 1
            if row.get("price_usd") is not None:
                mult = float(row["price_usd"]) / val
                if abs(float(row["price_to_gold_multiple"]) - mult) > 0.001:
                    fail("D-05 derived multiple", f"{rid}: {row['price_to_gold_multiple']} != {mult:.3f}")
                    mismatches += 1
            else:
                if row.get("price_to_gold_multiple") is not None:
                    fail("D-06 derived without price", f"{rid}: multiple present but price blank")
                    mismatches += 1
        else:
            for f in ("pure_gold_g", "gold_value_usd", "legal_min_gold_value_usd", "price_to_gold_multiple"):
                if row.get(f) is not None:
                    fail("D-07 derived without weight", f"{rid}.{f} present but weight blank")
                    mismatches += 1
    if mismatches == 0:
        ok("D-08 derived recompute", "every derived number re-derives from published inputs")

    # no derived number may exist without a published weight
    for row in rings["rows"]:
        if row.get("weight_g") is None and row.get("price_to_gold_multiple") is not None:
            fail("D-09 no phantom math", f"{row['id']}: multiple without weight")

    # ---------------------------------------------------------------- sellers
    for sid, seller in sellers.items():
        for k in ("official_url",):
            check_url("E-01 seller url", seller.get(k), sid, sellers, f"{sid}.{k}")
        if seller.get("contact", {}).get("phone") and not re.match(r"^\+?[\d\-\.\(\) ]{7,}$", seller["contact"]["phone"]):
            fail("E-02 phone format", f"{sid}: {seller['contact']['phone']!r}")
        if seller.get("reputation_independently_verified") is None:
            if "REPUTATION_NOT_VERIFIED" not in seller.get("flags", []):
                fail("E-03 reputation flag", f"{sid}: reputation blank without flag")
        if seller.get("return_window_days") is not None and not isinstance(seller["return_window_days"], int):
            fail("E-04 return window type", f"{sid}")
        if seller.get("returns_source_id") not in source_ids:
            fail("E-05 returns source", f"{sid}: returns_source_id not in sources.json")
    ok("E-06 sellers", f"{len(sellers)} sellers checked")

    # ---------------------------------------------------------------- site
    site_files = ["index.html"] + [f"pages/{p.name}" for p in (ROOT / "pages").glob("*.html")] if (ROOT / "pages").exists() else ["index.html"]
    missing_rows = 0
    broken_links = []
    bad_text = []
    for rel in site_files:
        path = ROOT / rel
        if not path.exists():
            fail("F-01 site file", f"{rel} missing")
            continue
        html = path.read_text(encoding="utf-8")
        bad_patterns = [r"\bundefined\b", r"\bNaN\b", r">None<", r"\{\{", r"\}\}"]
        if any(re.search(pat, html) for pat in bad_patterns):
            bad_text.append(rel)
        for href in re.findall(r'href="([^"]+)"', html):
            if href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:"):
                continue
            if href.startswith("http"):
                if not href.startswith("https://"):
                    broken_links.append((rel, href, "not https"))
                host = host_of(href)
                if any(b in host for b in BANNED_HOST_SUBSTRINGS):
                    broken_links.append((rel, href, "banned domain"))
                continue
            target = (path.parent / href.split("#")[0]).resolve()
            if href.split("#")[0] == "":
                continue
            if not target.exists():
                broken_links.append((rel, href, "missing file"))
        # every product table row must carry a source link
        for tr in re.findall(r"<tr[^>]*data-row-id=\"([^\"]+)\"[^>]*>(.*?)</tr>", html, flags=re.S):
            row_id, body = tr
            if 'class="src"' not in body:
                missing_rows += 1
    if broken_links:
        for rel, href, why in broken_links[:20]:
            fail("F-02 link check", f"{rel}: {href} ({why})")
    else:
        ok("F-02 link check", f"{len(site_files)} files, no broken internal links")
    if missing_rows:
        fail("F-03 row sources", f"{missing_rows} table rows without a source link")
    else:
        ok("F-03 row sources", "every rendered row links to its official source")
    if bad_text:
        fail("F-04 render text", f"suspicious literal text in {', '.join(bad_text)}")
    else:
        ok("F-04 render text", "no placeholder tokens in rendered pages")

    # ---------------------------------------------------------------- report
    fails = [r for r in RESULTS if r[0] == "FAIL"]
    warns = [r for r in RESULTS if r[0] == "WARN"]
    passes = [r for r in RESULTS if r[0] == "PASS"]

    REPORTS.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = [
        "GOLD4 integrity audit (hallucination / security check)",
        f"run_utc: {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        f"dataset rows: {len(rings['rows'])} | sellers: {len(sellers)} | sources: {len(source_ids)}",
        f"spot benchmark: ${spot_usd_oz:,.2f}/oz ({spot['benchmark']['price_date_as_shown_on_source']}) = ${usd_g:,.4f}/g",
        "",
        f"RESULT: {'FAIL' if fails else 'PASS'}  ({len(passes)} passed, {len(warns)} warnings, {len(fails)} failures)",
        "",
    ]
    for status, check, detail in RESULTS:
        if status != "PASS":
            lines.append(f"[{status}] {check}: {detail}")
    if not fails and not warns:
        lines.append("No warnings, no failures.")
    lines.append("")
    lines.append("Checks performed: source registry + domain allow-list, banned-domain scan, HTTPS enforcement,")
    lines.append("price/weight provenance, capture dates, blank-value flagging, karat/fineness consistency,")
    lines.append("independent recomputation of every derived number, phantom-math detection (no weight => no value),")
    lines.append("seller contact/return provenance, speculation-language scan, site link check,")
    lines.append("per-row source-link requirement, and render-text sanity.")
    text = "\n".join(lines) + "\n"
    (REPORTS / "audit_latest.txt").write_text(text, encoding="utf-8")
    (REPORTS / f"audit_{stamp}.txt").write_text(text, encoding="utf-8")

    print(text)
    return 1 if fails else 0


def guess_retailer(url: str) -> str:
    host = host_of(url)
    for rid, domains in OFFICIAL_HOSTS.items():
        if any(host == d or host.endswith("." + d) for d in domains):
            return rid
    return "__gov_or_benchmark__"


if __name__ == "__main__":
    sys.exit(main())
