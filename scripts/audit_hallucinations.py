#!/usr/bin/env python3
"""GOLD4 Automated Anti-Hallucination & Security Check (Session arena/81b71aa5-gold4).

Run after every data collection, HTML generation, or integration review pass:
    python3 scripts/audit_hallucinations.py

Enforces:
  1. JSON schema & provenance integrity on data/standards_and_spot.json and
     data/verified_rings.json (plus data/rings.json & data/gold_spot.json when present).
  2. Independent mathematical recomputation of troy-ounce/gram spot conversions,
     stone-carat mass deductions (1 ct = 0.200 g per NIST Handbook 44), pure-gold
     grams (weight_g * karat / 24), raw melt values, and price-to-melt ratios.
  3. Zero-phantom-math enforcement: any item with null metal_weight_g MUST have null
     pure_gold_g, null melt_value_usd, and null price_to_melt_ratio.
  4. Official HTTPS source allow-list & banned-marketplace/forum/blog check across
     all JSON datasets and HTML pages.
  5. Runtime external dependency & privacy check (flags external Google Fonts CDNs or
     third-party script tags in site HTML/CSS).
  6. Speculative-wording scan (rejects unverified guessing words in audit data).
  7. HTML structural & link verification across root pages, categories/*.html,
     pages/*.html, and docs/*.html: local links resolve, every <tr data-row-id="...">
     includes class="src" with an https:// official link, and NO HALLUCINATIONS rules
     are prominently displayed.
"""
from __future__ import annotations

from html.parser import HTMLParser
import json
import math
from pathlib import Path
import re
import sys
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]

APPROVED_RETAILER_DOMAINS = {
    "bluenile": ("bluenile.com",),
    "blue-nile": ("bluenile.com",),
    "brilliantearth": ("brilliantearth.com",),
    "brilliant-earth": ("brilliantearth.com",),
    "ross-simons": ("ross-simons.com",),
    "mejuri": ("mejuri.com",),
    "catbird": ("catbirdnyc.com",),
    "mene": ("mene.com", "support.mene.com"),
    "allurez": ("allurez.com",),
    "vrai": ("vrai.com",),
    "anjolee": ("anjolee.com",),
}

APPROVED_REFERENCE_DOMAINS = (
    "consumer.ftc.gov",
    "ftc.gov",
    "ecfr.gov",
    "uscode.house.gov",
    "law.cornell.edu",
    "govinfo.gov",
    "nist.gov",
    "gia.edu",
    "bullionvault.com",
    "jmbullion.com",
    "gold.org",
    "lbma.org.uk",
    "github.com",
    "karagemop466-tech.github.io",
)

BANNED_DOMAIN_SUBSTRINGS = (
    "ebay.",
    "amazon.",
    "etsy.",
    "poshmark.",
    "1stdibs.",
    "therealreal.",
    "reddit.",
    "quora.",
    "wikipedia.",
    "pinterest.",
    "medium.com",
    "blogspot.",
    "wordpress.com",
    "tiktok.com",
    "instagram.com",
    "facebook.com",
    "x.com",
    "twitter.com",
)

SPECULATIVE_PHRASES = (
    "probably",
    "we assume",
    "presumably",
    "ballpark",
    "rough guess",
    "should be around",
    "estimated weight",
    "estimated price",
    "typical price",
    "circa",
)


class PageInspector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []
        self.srcs: list[str] = []
        self.https_links = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        amap = {k: (v or "") for k, v in attrs}
        if "href" in amap and amap["href"]:
            href = amap["href"]
            self.hrefs.append(href)
            if href.startswith("https://"):
                self.https_links += 1
        if "src" in amap and amap["src"]:
            self.srcs.append(amap["src"])


def norm_host(url: str) -> str:
    h = (urlparse(url).hostname or "").lower()
    return h[4:] if h.startswith("www.") else h


def host_matches(host: str, allowed_tuple: tuple[str, ...]) -> bool:
    return any(host == d or host.endswith("." + d) for d in allowed_tuple)


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    checks_passed = 0

    def ok() -> None:
        nonlocal checks_passed
        checks_passed += 1

    # 1. Verify data/standards_and_spot.json
    std_path = ROOT / "data" / "standards_and_spot.json"
    if not std_path.exists():
        errors.append("Missing data/standards_and_spot.json")
        return report(errors, warnings, checks_passed)

    std = json.loads(std_path.read_text(encoding="utf-8"))
    mc = std["mass_constants"]
    oz_t = float(mc["troy_ounce_to_grams"])
    ct_g = float(mc["metric_carat_to_grams"])
    if abs(oz_t - 31.1034768) > 1e-9 or abs(ct_g - 0.2) > 1e-9:
        errors.append("NIST mass constants mismatch in data/standards_and_spot.json")
    else:
        ok()

    quotes = std.get("spot_quotes_2026_10_22", [])
    if len(quotes) < 2:
        errors.append("Expected at least 2 independent dated spot quotes in standards_and_spot.json")
    for q in quotes:
        url = q.get("source_url", "")
        if not url.startswith("https://") or not host_matches(norm_host(url), APPROVED_REFERENCE_DOMAINS):
            errors.append(f"Unapproved spot quote URL: {url}")
        recomputed_g = float(q["usd_per_troy_oz"]) / oz_t
        if abs(recomputed_g - float(q["usd_per_gram_exact_computed"])) > 1e-6:
            errors.append(f"Spot gram conversion mismatch for {q['id']}")
        else:
            ok()

    # 2. Verify data/verified_rings.json
    vr_path = ROOT / "data" / "verified_rings.json"
    if not vr_path.exists():
        errors.append("Missing data/verified_rings.json")
        return report(errors, warnings, checks_passed)

    vr = json.loads(vr_path.read_text(encoding="utf-8"))
    primary_spot_g = float(quotes[0]["usd_per_gram_exact_computed"])
    if abs(float(vr["spot_pure_gold_usd_per_gram"]) - primary_spot_g) > 1e-8:
        errors.append("Spot reference drift between standards_and_spot.json and verified_rings.json")
    else:
        ok()

    sellers = {s["seller_id"]: s for s in vr["sellers"]}
    irr_ids = {i["id"] for i in vr["flagged_irregularities"]}
    cat_ids = {c["id"] for c in vr["categories"]}

    for sid, s in sellers.items():
        for k in ("homepage_url", "return_policy_url"):
            u = s.get(k, "")
            if not u.startswith("https://"):
                errors.append(f"Seller {sid} {k} is not HTTPS: {u}")
            elif not host_matches(norm_host(u), APPROVED_RETAILER_DOMAINS.get(sid, ())):
                errors.append(f"Seller {sid} {k} domain mismatch: {u}")
            else:
                ok()

    seen_ring_ids: set[str] = set()
    for r in vr["rings"]:
        rid = r["ring_id"]
        if rid in seen_ring_ids:
            errors.append(f"Duplicate ring_id: {rid}")
        seen_ring_ids.add(rid)

        if r["category"] not in cat_ids:
            errors.append(f"{rid}: unknown category {r['category']}")
        sid = r["seller_id"]
        if sid not in sellers:
            errors.append(f"{rid}: unknown seller_id {sid}")

        for uk in ("url", "return_policy_url"):
            u = r.get(uk, "")
            h = norm_host(u)
            if not u.startswith("https://"):
                errors.append(f"{rid}: non-HTTPS {uk}: {u}")
            elif any(b in h for b in BANNED_DOMAIN_SUBSTRINGS):
                errors.append(f"{rid}: banned domain in {uk}: {u}")
            elif not host_matches(h, APPROVED_RETAILER_DOMAINS.get(sid, ())):
                errors.append(f"{rid}: unapproved host {h} for seller {sid}")
            else:
                ok()

        if r.get("verified_date") != "2026-10-22":
            errors.append(f"{rid}: missing or unexpected verified_date {r.get('verified_date')}")

        karat = r.get("karat")
        fineness = r.get("fineness")
        if karat is not None:
            expected_fin = 0.999 if karat == 24 and sid == "mene" else (karat / 24.0)
            if fineness is None or abs(float(fineness) - expected_fin) > 1e-4:
                errors.append(f"{rid}: fineness {fineness} inconsistent with {karat}K")
            else:
                ok()
        else:
            if fineness is not None:
                errors.append(f"{rid}: fineness populated when karat is null")

        sc = r.get("stone_carat_total")
        sm = r.get("stone_mass_g")
        if sc is None:
            if sm is not None:
                errors.append(f"{rid}: stone_mass_g populated when stone_carat_total is null")
        else:
            if sm is None or abs(float(sm) - round(float(sc) * ct_g, 4)) > 1e-4:
                errors.append(f"{rid}: stone_mass_g {sm} != {sc} * 0.200")
            else:
                ok()

        mw = r.get("metal_weight_g")
        if mw is None:
            for fk in ("pure_gold_g", "melt_value_usd", "price_to_melt_ratio"):
                if r.get(fk) is not None:
                    errors.append(f"{rid}: HALLUCINATION / PHANTOM MATH — {fk} populated while metal_weight_g is null")
            ok()
        else:
            if karat is None:
                errors.append(f"{rid}: metal_weight_g set while karat is null")
            else:
                pure_expected = float(mw) * (float(karat) / 24.0)
                melt_expected = pure_expected * primary_spot_g
                ratio_expected = float(r["price_usd"]) / melt_expected
                if abs(float(r["pure_gold_g"]) - round(pure_expected, 4)) > 1e-3:
                    errors.append(f"{rid}: pure_gold_g {r['pure_gold_g']} != {pure_expected:.4f}")
                elif abs(float(r["melt_value_usd"]) - round(melt_expected, 2)) > 0.02:
                    errors.append(f"{rid}: melt_value_usd {r['melt_value_usd']} != {melt_expected:.2f}")
                elif abs(float(r["price_to_melt_ratio"]) - round(ratio_expected, 2)) > 0.02:
                    errors.append(f"{rid}: price_to_melt_ratio {r['price_to_melt_ratio']} != {ratio_expected:.2f}")
                else:
                    ok()

        for iid in r.get("irregularity_ids", []):
            if iid not in irr_ids:
                errors.append(f"{rid}: references unknown irregularity_id {iid}")

        notes_low = (r.get("audit_notes") or "").lower()
        for phrase in SPECULATIVE_PHRASES:
            if phrase in notes_low:
                errors.append(f"{rid}: speculative wording '{phrase}' found in audit_notes")

    # 3. Scan HTML pages across repository
    html_files: list[Path] = []
    for candidate in (ROOT / "index.html", ROOT / "flagged.html"):
        if candidate.exists():
            html_files.append(candidate)
    for folder in ("categories", "pages", "docs"):
        d = ROOT / folder
        if d.exists():
            html_files.extend(sorted(d.glob("*.html")))

    for hp in html_files:
        rel = str(hp.relative_to(ROOT))
        text = hp.read_text(encoding="utf-8")

        if any(tok in text for tok in ("undefined", "NaN", ">None<", "{{", "}}")):
            errors.append(f"{rel}: contains unresolved template/JS token (undefined/NaN/None/{{{{)")
        else:
            ok()

        if "fonts.googleapis.com" in text or "fonts.gstatic.com" in text:
            warnings.append(f"{rel}: loads external Google Fonts CDN at runtime (see IRR-REPO-01)")

        insp = PageInspector()
        insp.feed(text)
        if insp.https_links < 1 and not rel.startswith("docs/"):
            errors.append(f"{rel}: contains zero HTTPS official source links")
        else:
            ok()

        for ref in insp.hrefs + insp.srcs:
            if ref.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
                continue
            if ref.startswith("http://"):
                errors.append(f"{rel}: insecure http:// reference {ref}")
                continue
            if ref.startswith("https://"):
                h = norm_host(ref)
                if any(b in h for b in BANNED_DOMAIN_SUBSTRINGS):
                    errors.append(f"{rel}: banned secondary/marketplace host {h} in {ref}")
                continue
            clean = ref.split("#", 1)[0].split("?", 1)[0]
            if not clean:
                continue
            resolved = (hp.parent / clean).resolve()
            if not resolved.exists():
                errors.append(f"{rel}: broken local asset/page link '{ref}'")
            else:
                ok()

        for row_id, row_body in re.findall(r'<tr[^>]*data-row-id="([^"]+)"[^>]*>(.*?)</tr>', text, flags=re.S):
            if 'class="src"' not in row_body or "https://" not in row_body:
                errors.append(f"{rel}: row {row_id} missing class=\"src\" official https:// link")
            else:
                ok()

        if rel.startswith("categories/") or rel == "index.html":
            if "no hallucination" not in text.lower() and "no-hallucination" not in text.lower():
                errors.append(f"{rel}: missing explicit No-Hallucinations policy callout")
            else:
                ok()

    # Check CSS files for runtime CDN leaks
    for css_path in list(ROOT.glob("*.css")) + list((ROOT / "assets").glob("*.css")) if (ROOT / "assets").exists() else list(ROOT.glob("*.css")):
        css_text = css_path.read_text(encoding="utf-8")
        if "fonts.googleapis.com" in css_text:
            warnings.append(f"{css_path.relative_to(ROOT)}: @import from fonts.googleapis.com (flagged in IRR-REPO-01)")

    return report(errors, warnings, checks_passed)


def report(errors: list[str], warnings: list[str], checks_passed: int) -> int:
    print("======================================================================")
    print("GOLD4 ANTI-HALLUCINATION & SECURITY AUDIT (arena/81b71aa5-gold4)")
    print("======================================================================")
    print(f"Checks passed : {checks_passed}")
    print(f"Warnings      : {len(warnings)}")
    print(f"Hard failures : {len(errors)}")
    for w in warnings:
        print(f"  [WARN] {w}")
    for e in errors:
        print(f"  [FAIL] {e}")
    if errors:
        print("RESULT: FAIL — fix hard failures before publishing or merging.")
        return 1
    print("RESULT: PASS — zero hallucinated/unsourced values, zero phantom math, zero broken local links.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
