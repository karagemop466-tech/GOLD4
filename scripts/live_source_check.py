#!/usr/bin/env python3
"""
GOLD4 — LIVE source-health check (Pass 15, session arena/03c0c10f-gold4).

WHY THIS EXISTS
---------------
Every other check in this repo (audit.py, check_site.py, verify.py,
verify_a0be79d4.py, audit_hallucinations.py) is OFFLINE. They prove that a
stored value is internally consistent and carries a source URL. They cannot
prove the source URL still resolves, or that the page still prints the number
it printed when it was captured. A row can therefore keep `price_verification:
V1_direct_page_fetch` long after the link rotted — which is precisely what
happened to BN-22 before this pass.

This script is the ONLINE half. It re-opens every official URL in the dataset
and records, for each one, the raw evidence:

  * HTTP status, final URL after redirects, byte count, page title
  * whether the response is a soft-404 ("cannot be found", "page not found")
  * the price-looking snippets actually printed on the page (raw text, with
    surrounding context) — NOT a guess at "the price"
  * gram-weight-looking snippets, karat/solid-gold wording occurrences

It never writes a value into data/*.json. It produces an evidence artifact
(`reports/live_source_check_<UTC>.json`) that a human or a later pass reviews.
Nothing in this file infers, interpolates or completes a value.

SECURITY / ANTI-HALLUCINATION POSTURE
-------------------------------------
* Read-only GETs, no auth, no cookies, no JS, no form posts.
* Requests are restricted to the hostnames already registered in
  data/sources.json (same allow-list posture as audit.py). No third-party,
  marketplace, blog or price-comparison host can be probed.
* If the *environment* blocks outbound TLS (sandboxed runners do), the run is
  marked `network_environment_blocked` and the artifact is written with
  statuses recorded as `ENVIRONMENT_BLOCKED` — never as \"unreachable\", so a
  blocked sandbox can never be mistaken for a dead source.
* Exit codes: 0 = artifact written; 3 = blocked environment (artifact written
  with the block recorded); 4 = dataset could not be read.

USAGE
    python3 scripts/live_source_check.py                # check every row URL + registered source
    python3 scripts/live_source_check.py --limit 8      # smoke test
    python3 scripts/live_source_check.py --only BN-22   # single row
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import socket
import ssl
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
REPORTS = ROOT / "reports"

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0 Safari/537.36 GOLD4-source-health/1.0"
)

SOFT_404_MARKERS = (
    "page you're looking for cannot be found",
    "page you are looking for cannot be found",
    "page not found",
    "404 not found",
    "we couldn't find that page",
    "we could not find that page",
    "this page is no longer available",
    "sorry, this page does not exist",
)

PRICE_RE = re.compile(r"(?:\$|USD\s?)\s?(\d{1,3}(?:,\d{3})+(?:\.\d{2})?|\d{4,}(?:\.\d{2})?|\d{1,3}\.\d{2})")
WEIGHT_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(?:gr\b|g\b|grams?\b)", re.I)
KARAT_RE = re.compile(r"\b(?:10|14|18|22|24)\s?[kK](?:t|arat)?\b|\b(?:10|14|18)K\b")

MAX_SNIPPETS = 12


def utcnow() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def stamp() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def norm_host(url: str) -> str:
    m = re.match(r"https?://([^/]+)", url or "")
    return (m.group(1) if m else "").lower().removeprefix("www.")


def allowed_hosts(sources: dict) -> set[str]:
    hosts = {norm_host(s.get("url", "")) for s in sources.get("sources", [])}
    hosts.discard("")
    return hosts


def host_ok(url: str, allowed: set[str]) -> bool:
    h = norm_host(url)
    return any(h == a or h.endswith("." + a) for a in allowed)


def strip_html(html: str) -> str:
    html = re.sub(r"(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>", " ", html)
    html = re.sub(r"(?s)<[^>]+>", " ", html)
    html = (
        html.replace("&nbsp;", " ")
        .replace("&#x27;", "'")
        .replace("&#39;", "'")
        .replace("&quot;", '"')
        .replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&ndash;", "-")
        .replace("&mdash;", "-")
    )
    return re.sub(r"\s+", " ", html).strip()


def title_of(html: str) -> str:
    m = re.search(r"(?is)<title[^>]*>(.*?)</title>", html)
    return strip_html(m.group(1))[:160] if m else ""


def meta_content(html: str, prop: str) -> str:
    for pat in (
        rf'<meta[^>]+(?:property|name)=["\']{re.escape(prop)}["\'][^>]*content=["\']([^"\']*)',
        rf'<meta[^>]+content=["\']([^"\']*)["\'][^>]*(?:property|name)=["\']{re.escape(prop)}["\']',
    ):
        m = re.search(pat, html, re.I)
        if m:
            return m.group(1).strip()
    return ""


def offer_signals(html: str) -> dict:
    """Availability / currency / validity signals the page itself publishes.

    Why this exists: several rows are stored price-blank because the item was
    sold out when it was captured (for example BN-26). A price string alone
    cannot tell you whether the item is buyable, so the runner also records the
    *page's own* availability wording. It never decides anything by itself and
    it never rewrites a stored value — it is the evidence a later pass needs
    before it may record a price at all.
    """
    sig: dict[str, list[str]] = {}
    for m in re.finditer(r'(?is)<script[^>]+type=[\"\']application/ld\+json[\"\'][^>]*>(.*?)</script>', html):
        raw = m.group(1)
        for key in ("availability", "priceCurrency", "priceValidUntil", "itemCondition"):
            for v in re.findall(r'\"%s\"\s*:\s*\"([^\"]{1,120})\"' % key, raw):
                sig.setdefault(key, []).append(v)
    for prop in ("product:availability", "og:availability", "product:price:currency"):
        v = meta_content(html, prop)
        if v:
            sig.setdefault(prop, []).append(v)
    return {k: sorted(set(v))[:6] for k, v in sig.items()}


def structured_prices(html: str) -> list[dict]:
    """Prices published by the page itself in schema.org JSON-LD or price meta tags.

    This is the page's own machine-readable claim, not our guess. We keep the
    currency, the schema.org type and the product name so the claim can be tied
    to the exact item rather than to a "from" banner.
    """
    out: list[dict] = []
    for m in re.finditer(r'(?is)<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html):
        raw = m.group(1).strip()
        try:
            blob = json.loads(raw)
        except Exception:
            continue
        stack = [blob]
        while stack:
            node = stack.pop()
            if isinstance(node, list):
                stack.extend(node)
                continue
            if not isinstance(node, dict):
                continue
            typ = node.get("@type")
            types = typ if isinstance(typ, list) else [typ]
            price = node.get("price")
            if price is not None and any(t in ("Offer", "AggregateOffer", "Product") for t in types if t):
                out.append(
                    {
                        "source": "json-ld",
                        "type": ",".join(str(t) for t in types if t),
                        "price": str(price),
                        "currency": str(node.get("priceCurrency") or ""),
                        "name": str(node.get("name") or "")[:120],
                        "sku": str(node.get("sku") or node.get("mpn") or "")[:60],
                        "low": str(node.get("lowPrice") or ""),
                        "high": str(node.get("highPrice") or ""),
                    }
                )
            for v in node.values():
                if isinstance(v, (dict, list)):
                    stack.append(v)
    for prop in ("product:price:amount", "og:price:amount", "product:sale_price:amount"):
        val = meta_content(html, prop)
        if val:
            out.append(
                {
                    "source": f"meta:{prop}",
                    "type": "meta",
                    "price": val,
                    "currency": meta_content(html, "product:price:currency") or meta_content(html, "og:price:currency"),
                    "name": meta_content(html, "og:title")[:120],
                    "sku": "",
                    "low": "",
                    "high": "",
                }
            )
    return out[:10]


def context(text: str, m: re.Match, pad: int = 70) -> str:
    a = max(0, m.start() - pad)
    b = min(len(text), m.end() + pad)
    return ("…" if a else "") + text[a:b] + ("…" if b < len(text) else "")


def fetch(url: str, timeout: int) -> dict:
    """One read-only GET. Returns an evidence dict; never raises."""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    started = time.time()
    rec: dict = {"url": url, "checked_utc": utcnow()}
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read(3_000_000)
            charset = r.headers.get_content_charset() or "utf-8"
            html = raw.decode(charset, errors="replace")
            rec.update(
                {
                    "http_status": r.status,
                    "final_url": r.geturl(),
                    "bytes": len(raw),
                    "content_type": r.headers.get("Content-Type", ""),
                    "elapsed_ms": int((time.time() - started) * 1000),
                }
            )
    except urllib.error.HTTPError as e:
        body = b""
        try:
            body = e.read(200_000)
        except Exception:
            pass
        html = body.decode("utf-8", errors="replace")
        rec.update(
            {
                "http_status": e.code,
                "final_url": url,
                "bytes": len(body),
                "elapsed_ms": int((time.time() - started) * 1000),
                "error": f"HTTPError {e.code}",
            }
        )
    except (urllib.error.URLError, socket.timeout, ssl.SSLError, ConnectionError, TimeoutError) as e:
        reason = getattr(e, "reason", e)
        kind = "TLS/SSL" if isinstance(reason, ssl.SSLError) else type(reason).__name__
        rec.update(
            {
                "http_status": None,
                "connection_error": str(reason)[:200],
                "error_kind": kind,
                "elapsed_ms": int((time.time() - started) * 1000),
            }
        )
        return rec

    text = strip_html(html)
    rec["title"] = title_of(html)
    rec["text_chars"] = len(text)
    low = text.lower()
    rec["soft_404"] = any(m in low for m in SOFT_404_MARKERS)

    # Raw price-looking strings, with context. Evidence, not a decision.
    seen: set[str] = set()
    prices = []
    for m in PRICE_RE.finditer(text):
        val = m.group(1)
        if val in seen:
            continue
        seen.add(val)
        prices.append({"text": m.group(0).strip(), "context": context(text, m)})
        if len(prices) >= MAX_SNIPPETS:
            break
    rec["price_snippets"] = prices

    weights = []
    seen_w: set[str] = set()
    for m in WEIGHT_RE.finditer(text):
        want = m.group(1)
        if want in seen_w:
            continue
        seen_w.add(want)
        weights.append({"text": m.group(0).strip(), "context": context(text, m)})
        if len(weights) >= 6:
            break
    rec["weight_snippets"] = weights

    rec["og_title"] = meta_content(html, "og:title")[:160]
    rec["canonical"] = meta_content(html, "og:url") or (
        (re.search(r'(?is)<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)', html) or [None, ""])[1]
        if re.search(r'(?is)<link[^>]+rel=["\']canonical["\']', html)
        else ""
    )
    rec["structured_prices"] = structured_prices(html)
    rec["offer_signals"] = offer_signals(html)
    rec["karat_mentions"] = sorted({m.group(0) for m in KARAT_RE.finditer(text)})[:8]
    for phrase in ("solid gold", "gold plated", "gold-plated", "vermeil", "gold filled",
                   "gold-filled", "gold overlay", "gold tone", "gold-tone"):
        n = low.count(phrase)
        if n:
            rec.setdefault("phrase_counts", {})[phrase] = n
    rec["hallmark_word_on_page"] = bool(re.search(r"\bhallmark", low))
    return rec


def classify(rec: dict) -> str:
    """Evidence-based label. No inference beyond what the response proves."""
    if rec.get("http_status") is None:
        return "ENVIRONMENT_BLOCKED" if rec.get("_env_blocked") else "NO_RESPONSE"
    s = rec["http_status"]
    if s in (401, 403, 429):
        return f"REFUSED_{s}"
    if s >= 400:
        return f"HTTP_{s}"
    if rec.get("soft_404"):
        return "SOFT_404"
    if rec.get("text_chars", 0) < 400:
        return "EMPTY_OR_JS_SHELL"
    return "OK"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--only", default="")
    ap.add_argument("--timeout", type=int, default=30)
    args = ap.parse_args()

    try:
        rings = json.loads((DATA / "rings.json").read_text())["rows"]
        sources = json.loads((DATA / "sources.json").read_text())
    except Exception as e:  # pragma: no cover
        print(f"FAIL: cannot read dataset: {e}")
        return 4

    allowed = allowed_hosts(sources)
    targets: list[tuple[str, str, str]] = []  # (key, url, kind)
    for r in rings:
        if args.only and r["id"] != args.only:
            continue
        targets.append((r["id"], r["url"], "ring"))
    for s in sources["sources"]:
        targets.append((s["id"], s["url"], "source"))

    if args.limit:
        targets = targets[: args.limit]

    print("=" * 72)
    print("GOLD4 LIVE SOURCE HEALTH CHECK — read-only evidence collection")
    print("=" * 72)
    print(f"targets        : {len(targets)} ({sum(1 for t in targets if t[2]=='ring')} row URLs, "
          f"{sum(1 for t in targets if t[2]=='source')} registered sources)")
    print(f"allow-listed   : {len(allowed)} hostnames from data/sources.json")
    print(f"checked_utc    : {utcnow()}")

    results = []
    refused_allowlist = []
    for key, url, kind in targets:
        if not url.lower().startswith("https://"):
            refused_allowlist.append({"key": key, "url": url, "why": "not https"})
            continue
        if not host_ok(url, allowed):
            refused_allowlist.append({"key": key, "url": url, "why": "host not in sources.json allow-list"})
            continue
        rec = fetch(url, args.timeout)
        rec.update({"key": key, "kind": kind})
        results.append(rec)
        label = classify(rec)
        print(f"  {key:<26} {label:<18} {str(rec.get('http_status')):<5} "
              f"{str(rec.get('bytes','')):>8}B  {(rec.get('title') or rec.get('connection_error',''))[:52]}")
        time.sleep(0.4)

    conn_fail = [r for r in results if r.get("http_status") is None]
    env_blocked = bool(results) and len(conn_fail) == len(results)
    if env_blocked:
        for r in results:
            r["_env_blocked"] = True
            r["classification"] = "ENVIRONMENT_BLOCKED"
    else:
        for r in results:
            r["classification"] = classify(r)

    summary: dict = {}
    for r in results:
        summary[r["classification"]] = summary.get(r["classification"], 0) + 1

    artifact = {
        "artifact": "GOLD4 live source health check",
        "schema": 1,
        # Deliberately not a hard-coded session/pass: this script is run by the
        # workflow on whichever branch is being published, and an artifact that
        # names the wrong session is a provenance bug (Pass 17 fixed that).
        "session": os.environ.get("GOLD4_EVIDENCE_SESSION")
        or os.environ.get("GITHUB_HEAD_REF")
        or os.environ.get("GITHUB_REF_NAME")
        or "local-run",
        "pass": "auto (recorded in data/verification_log.json by the reviewing pass)",
        "checked_utc": utcnow(),
        "method": "read-only HTTPS GET of each URL, HTML stripped to text, raw price/weight snippets retained with context",
        "network_environment_blocked": env_blocked,
        "targets": len(targets),
        "allowlist_refused": refused_allowlist,
        "summary": summary,
        "results": results,
        "interpretation_rules": [
            "OK / SOFT_404 / HTTP_4xx are statements about THIS check at THIS timestamp only.",
            "A price snippet is raw page text, not a confirmed price; a later pass must reconcile it line by line.",
            "the classification OK does not by itself prove the price is unchanged — compare price_snippets with the stored value",
        ],
    }

    REPORTS.mkdir(exist_ok=True)
    out = REPORTS / f"live_source_check_{stamp()}.json"
    out.write_text(json.dumps(artifact, indent=1, ensure_ascii=False))
    latest = REPORTS / "live_source_check_latest.json"
    latest.write_text(json.dumps(artifact, indent=1, ensure_ascii=False))

    print("-" * 72)
    for k, v in sorted(summary.items(), key=lambda kv: -kv[1]):
        print(f"  {k:<22} {v}")
    if refused_allowlist:
        print(f"  allow-list refusals     {len(refused_allowlist)}")
    print(f"artifact: {out.relative_to(ROOT)}")
    if env_blocked:
        print("RESULT: NETWORK ENVIRONMENT BLOCKED — nothing can be concluded about the sources.")
        print("        This run is recorded as ENVIRONMENT_BLOCKED, not as unreachable URLs.")
        return 3
    print("RESULT: evidence collected (this is not a pass/fail verdict; review the artifact).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
