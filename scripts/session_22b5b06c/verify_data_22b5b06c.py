#!/usr/bin/env python3
"""
verify_data.py — Anti-hallucination security checks for GOLD4 ring data.

Checks (run after every data change):
  1. Schema: every required field present on every row.
  2. Source: every row has an https:// URL on an OFFICIAL allow-listed domain.
  3. No fabricated values: weight_g / hallmark must be null unless notes cite the
     exact source detail; karat in data must appear in the product name/URL.
  4. Price sanity: numeric > 0 or null-with-flag; sale price <= list price.
  5. Timestamps: verified_at_utc present, parseable, not in the future.
  6. Duplicates: no duplicate product URLs or ids.
  7. Gold spot: numeric, sourced, timestamped; derived per-gram value recomputed.
  8. Flags: every B-SNIPPET / UNVERIFIED item must be listed for the Flagged page.

Exit code 0 = all checks passed (warnings allowed), 1 = hard failure.
Writes reports/verification_report.json and prints a summary.
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
REPORTS = ROOT / "reports"

OFFICIAL_DOMAINS = (
    "bluenile.com",
    "jamesallen.com",
    "brilliantearth.com",
    "api.gold-api.com",
    "kitco.com",
    "lbma.org.uk",
)

REQUIRED_FIELDS = [
    "id", "product", "retailer", "category", "metal_karat", "metal_color",
    "price_usd", "url", "source_type", "verified_at_utc",
    "verification_level", "flags",
]

KARAT_RE = re.compile(r"\b(\d{2})\s*[kK]\b")


def domain_of(url: str) -> str:
    m = re.match(r"https?://([^/]+)", url or "")
    return (m.group(1) if m else "").lower().removeprefix("www.")


def is_official(url: str) -> bool:
    d = domain_of(url)
    return any(d == dom or d.endswith("." + dom) for dom in OFFICIAL_DOMAINS)


def parse_ts(ts: str):
    ts = (ts or "").strip().replace("Z", "+00:00")
    # tolerate minute precision like 2026-10-22T23:15+00:00
    try:
        return datetime.fromisoformat(ts)
    except ValueError:
        return None


def main() -> int:
    errors, warnings, flagged = [], [], []
    rings_doc = json.loads((DATA / "rings.json").read_text())
    spot = json.loads((DATA / "gold_spot.json").read_text())
    rings = rings_doc["rings"]
    now = datetime.now(timezone.utc)

    seen_urls, seen_ids = {}, {}
    for r in rings:
        rid = r.get("id", "<missing-id>")
        # 1 schema
        for f in REQUIRED_FIELDS:
            if f not in r:
                errors.append(f"{rid}: missing required field '{f}'")
        # 2 source domain
        url = r.get("url", "")
        if not url.startswith("https://"):
            errors.append(f"{rid}: url missing or not https: {url!r}")
        elif not is_official(url):
            errors.append(f"{rid}: url domain not on official allow-list: {url}")
        # 6 duplicates
        if url in seen_urls:
            errors.append(f"{rid}: duplicate url with {seen_urls[url]}")
        seen_urls[url] = rid
        if rid in seen_ids:
            errors.append(f"{rid}: duplicate id")
        seen_ids[rid] = True
        # 3 karat consistency (name or url must contain the karat)
        k = str(r.get("metal_karat", ""))
        hay = (r.get("product", "") + " " + url).lower()
        if k and k.lower() not in hay:
            errors.append(f"{rid}: karat '{k}' not found in product name or URL — possible fabrication")
        # 3b weight/hallmark fabrication guard
        for field in ("weight_g", "hallmark"):
            if r.get(field) is not None:
                if not re.search(field.replace("_", "[ _]"), (r.get("notes") or ""), re.I):
                    errors.append(f"{rid}: '{field}'={r[field]!r} is non-null but notes do not cite the source detail — possible fabrication")
        # 4 price sanity
        p = r.get("price_usd")
        lp = r.get("list_price_usd")
        if p is None:
            if not r.get("flags"):
                errors.append(f"{rid}: price is null but row carries no explanatory flag")
            flagged.append({"id": rid, "why": "price null (not confirmed from live official source)", "url": url})
        elif not isinstance(p, (int, float)) or p <= 0:
            errors.append(f"{rid}: price_usd invalid: {p!r}")
        if lp is not None and p is not None and p > lp:
            errors.append(f"{rid}: sale price {p} exceeds list price {lp}")
        # price-vs-melt sanity when weight is known (none yet)
        if p and r.get("weight_g"):
            try:
                melt = float(r["weight_g"]) * (int(k.rstrip("kK")) / 24.0) * spot["price_usd_per_gram"]
                if p < melt * 0.8:
                    warnings.append(f"{rid}: price ${p} is suspiciously close to/below melt value ${melt:.0f} — red flag per checklist")
            except Exception:
                pass
        # 5 timestamps
        ts = parse_ts(r.get("verified_at_utc", ""))
        if ts is None:
            errors.append(f"{rid}: verified_at_utc unparseable: {r.get('verified_at_utc')!r}")
        elif ts > now:
            errors.append(f"{rid}: verified_at_utc is in the future: {r.get('verified_at_utc')}")
        # 8 flag levels
        lvl = r.get("verification_level")
        if lvl not in ("A-LIVE", "B-SNIPPET", "UNVERIFIED"):
            errors.append(f"{rid}: unknown verification_level {lvl!r}")
        if lvl == "B-SNIPPET":
            flagged.append({"id": rid, "why": "price from dated search snapshot of official page; live re-confirmation pending", "url": url})
        for fl in r.get("flags", []):
            if "UNVERIFIED" in fl or "PENDING" in fl or "SOLD OUT" in fl:
                flagged.append({"id": rid, "why": fl, "url": url})

    # 7 gold spot checks
    sp = spot.get("price_usd_per_troy_oz")
    if not isinstance(sp, (int, float)) or sp <= 0:
        errors.append(f"gold_spot: invalid price {sp!r}")
    if not is_official(spot.get("source_url", "")):
        errors.append(f"gold_spot: source_url not official: {spot.get('source_url')!r}")
    if parse_ts(spot.get("source_reported_updated_at", "")) is None:
        errors.append("gold_spot: source_reported_updated_at unparseable")
    if isinstance(sp, (int, float)):
        expected = round(sp / spot["troy_oz_in_grams"], 4)
        got = spot.get("price_usd_per_gram")
        if got is None or abs(got - expected) > 0.001:
            errors.append(f"gold_spot: per-gram {got!r} != recomputed {expected}")
    cc_status = str(spot.get("cross_check", {}).get("status", ""))
    if not cc_status.startswith("DONE"):
        flagged.append({"id": "GOLD-SPOT", "why": "single-source spot price; second-source cross-check pending", "url": spot.get("source_url")})
        warnings.append("gold_spot: cross-check PENDING (single source)")
    elif cc_status != "DONE":
        warnings.append(f"gold_spot: cross-check {cc_status} (completed via dated official snapshots, not a live fetch - see data/gold_spot.json)")

    REPORTS.mkdir(exist_ok=True)
    report = {
        "run_at_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "rows": len(rings),
        "a_live": sum(1 for r in rings if r.get("verification_level") == "A-LIVE"),
        "b_snippet": sum(1 for r in rings if r.get("verification_level") == "B-SNIPPET"),
        "errors": errors,
        "warnings": warnings,
        "flagged_for_review": flagged,
        "result": "FAIL" if errors else ("PASS_WITH_WARNINGS" if warnings else "PASS"),
    }
    (REPORTS / "verification_report.json").write_text(json.dumps(report, indent=2))

    print(f"verify_data: rows={report['rows']} A-LIVE={report['a_live']} B-SNIPPET={report['b_snippet']}")
    print(f"verify_data: errors={len(errors)} warnings={len(warnings)} flagged={len(flagged)} -> {report['result']}")
    for e in errors:
        print("  ERROR:", e)
    for w in warnings:
        print("  WARN:", w)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
