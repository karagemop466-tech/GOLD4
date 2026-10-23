#!/usr/bin/env python3
"""Reconcile the latest live-source evidence artifact against the dataset.

Inputs
    reports/live_source_check_latest.json   (written by scripts/live_source_check.py
                                             on a GitHub runner with open internet)
    data/rings.json, data/sources.json

Output
    data/source_health.json   — per-row source state + price reconciliation

HARD RULES (anti-hallucination)
    * This script NEVER writes into data/rings.json. It produces a separate,
      clearly-labelled evidence file. A price that differs is reported as
      "DIFFERS" for review; it is not silently adopted.
    * A page that could not be fetched (404, 403 bot-block, JS-only shell, TLS
      failure) yields NO statement about its price. The stored value keeps its
      original provenance and is marked SOURCE_NOT_REACHED.
    * "CONFIRMED" requires exactly one distinct USD structured offer matching
      the stored amount. Missing currency is never assumed to be USD. If several
      variant offers include the stored amount, the result is explicitly
      MULTIPLE_OFFERS_INCLUDE_STORED, not an exact-variant confirmation.

Exit codes: 0 written; 4 inputs missing.
"""
from __future__ import annotations

import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
REPORTS = ROOT / "reports"


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def money(v) -> float | None:
    """Accept nonnegative finite numeric claims; never strip currency/sign text."""
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, str):
        v = v.strip()
        if not re.fullmatch(r"(?:[0-9]+|[0-9]{1,3}(?:,[0-9]{3})+)(?:\.[0-9]+)?", v):
            return None
        v = v.replace(",", "")
    try:
        value = float(v)
    except (TypeError, ValueError, OverflowError):
        return None
    return value if math.isfinite(value) and value >= 0 else None


def paginated_prices(rec: dict) -> list[dict]:
    """Structured price claims, de-duplicated by (price, currency)."""
    out, seen = [], set()
    for sp in rec.get("structured_prices") or []:
        price = money(sp.get("price"))
        if price is None:
            continue
        cur = (sp.get("currency") or "").upper()
        key = (round(price, 2), cur)
        if key in seen:
            continue
        seen.add(key)
        out.append({**sp, "value": round(price, 2), "currency": cur})
    return out


def reconcile(row: dict, rec: dict | None) -> dict:
    stored = row.get("price_usd")
    state = {
        "id": row["id"],
        "retailer": row["retailer"],
        "product_name": row["product_name"],
        "url": row["url"],
        "stored_price_usd": stored,
        "stored_price_captured_utc": row.get("price_captured_utc"),
        "stored_price_verification": row.get("price_verification"),
    }
    if rec is None:
        state.update(
            source_state="NOT_CHECKED",
            http_status=None,
            page_title=None,
            price_state="SOURCE_NOT_CHECKED",
            found_prices=[],
            note="this URL was not in the last evidence artifact",
        )
        return state

    cls = rec.get("classification")
    state.update(
        source_state=cls,
        http_status=rec.get("http_status"),
        checked_utc=rec.get("checked_utc"),
        page_title=rec.get("page_title") or rec.get("title") or rec.get("og_title"),
        final_url=rec.get("final_url"),
        soft_404=rec.get("soft_404"),
    )

    if cls == "EMPTY_OR_JS_SHELL":
        # The server answered 200, but the HTML carries no product text: the
        # price is rendered client-side. Reachable, not readable.
        state.update(
            price_state="NOT_MACHINE_READABLE",
            found_prices=[],
            note="the page answered 200 but serves a JavaScript shell with no product text; the price cannot be read without a browser render",
        )
        return state

    if cls != "OK":
        state.update(
            price_state="SOURCE_NOT_REACHED",
            found_prices=[],
            note={
                "HTTP_404": "the page returns 404 / a 'cannot be found' page — the stored price can no longer be checked at this URL",
                "REFUSED_403": "the retailer's bot protection refused the runner (HTTP 403) — no statement about the price is possible",
                "REFUSED_401": "HTTP 401 — no statement about the price is possible",
                "REFUSED_429": "rate-limited (HTTP 429) — no statement about the price is possible",
                "EMPTY_OR_JS_SHELL": "the server returns a JavaScript shell with no product text — price is rendered client-side",
                "NO_RESPONSE": "no HTTP response (connection/TLS failure)",
                "SOFT_404": "the page served a 'not found' body",
                "ENVIRONMENT_BLOCKED": "the checking environment had no outbound internet",
            }.get(cls, f"source state {cls}"),
        )
        return state

    prices = paginated_prices(rec)
    state["found_prices"] = [
        {"value": p["value"], "currency": p["currency"], "source": p["source"], "type": p["type"], "name": p.get("name", "")}
        for p in prices
    ]

    if stored is None:
        state.update(
            price_state="NO_STORED_PRICE",
            note="the dataset deliberately stores no price for this row"
            + (f"; the live page offered {prices[0]['value']:,.2f} {prices[0]['currency']}".replace("  ", " ") if prices else ""),
        )
        return state

    # Missing currency is not evidence of USD. Do not silently assume it.
    usd = [p for p in prices if p["currency"] == "USD"]
    if not usd:
        state.update(
            price_state="NOT_MACHINE_READABLE",
            note="the page publishes no USD structured price (JSON-LD / price meta); the stored value keeps its original provenance"
            if not prices
            else "structured data exists but has no explicit USD price (currency absent or non-USD); no currency is assumed and no conversion is performed",
        )
        return state

    values = sorted({p["value"] for p in usd})
    matches = [v for v in values if abs(v - float(stored)) < 0.005]
    if len(values) == 1 and matches:
        state.update(price_state="CONFIRMED", note="the page's single distinct USD structured offer prints the stored amount")
    elif matches:
        state.update(
            price_state="MULTIPLE_OFFERS_INCLUDE_STORED",
            note="multiple distinct USD variant offers are present and one equals the stored amount; without an exact variant/SKU match this is not a confirmation, and nothing is overwritten",
        )
    else:
        state.update(
            price_state="DIFFERS",
            note="the page's structured data prints a different amount than the stored value; both are shown, nothing is overwritten",
        )
    return state


def main() -> int:
    art_path = REPORTS / "live_source_check_latest.json"
    if not art_path.exists():
        print(f"FAIL: missing {art_path.relative_to(ROOT)} — run scripts/live_source_check.py first")
        return 4
    art = load(art_path)
    rings = load(DATA / "rings.json")["rows"]
    sources = load(DATA / "sources.json")["sources"]

    by_key = {r["key"]: r for r in art.get("results", [])}

    rows_out = [reconcile(r, by_key.get(r["id"])) for r in rings]
    src_out = []
    for s in sources:
        rec = by_key.get(s["id"])
        if rec is None:
            src_out.append({"id": s["id"], "publisher": s["publisher"], "url": s["url"], "tier": s["tier"],
                            "source_state": "NOT_CHECKED", "http_status": None})
            continue
        src_out.append(
            {
                "id": s["id"],
                "publisher": s["publisher"],
                "title": s.get("title", ""),
                "url": s["url"],
                "tier": s["tier"],
                "source_state": rec.get("classification"),
                "http_status": rec.get("http_status"),
                "checked_utc": rec.get("checked_utc"),
                "final_url": rec.get("final_url"),
            }
        )

    def count(items, field):
        out: dict[str, int] = {}
        for it in items:
            out[it[field]] = out.get(it[field], 0) + 1
        return dict(sorted(out.items(), key=lambda kv: (-kv[1], kv[0])))

    doc = {
        "schema_version": "1.0.0",
        "dataset": "GOLD4 live source health & price reconciliation",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "evidence_artifact": str(art_path.relative_to(ROOT)),
        "evidence_checked_utc": art.get("checked_utc"),
        "evidence_method": art.get("method"),
        "network_environment_blocked": art.get("network_environment_blocked"),
        "rules": [
            "Nothing here overwrites a stored value. DIFFERS is a review flag, not a correction.",
            "CONFIRMED means exactly one distinct USD schema.org/meta offer matches the stored amount; missing currency and multi-variant matches are not confirmed.",
            "A page that could not be fetched (404 / 403 bot-block / JS shell) says nothing about its price.",
            "No value is inferred, converted between currencies, or averaged.",
        ],
        "row_states": count(rows_out, "source_state"),
        "price_states": count(rows_out, "price_state"),
        "source_states": count(src_out, "source_state"),
        "rows": rows_out,
        "sources": src_out,
    }
    (DATA / "source_health.json").write_text(json.dumps(doc, indent=1, ensure_ascii=False), encoding="utf-8")

    print("source health reconciled")
    print(f"  evidence checked : {doc['evidence_checked_utc']}")
    print(f"  row source states: {doc['row_states']}")
    print(f"  price states     : {doc['price_states']}")
    print(f"  registry states  : {doc['source_states']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
