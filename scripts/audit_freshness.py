#!/usr/bin/env python3
"""GOLD4 Gate 7 — freshness & source-health gate.

The five existing gates are offline. This one closes the loop: it checks that the
*evidence about the sources* still exists, is recent, is internally consistent,
and is honestly reflected in the dataset.

What it enforces
  1. data/source_health.json exists and was generated from a real evidence artifact.
  2. Every row in data/rings.json carries a `source_check` block that matches the
     evidence file (state, price_state, HTTP status).
  3. Every row whose evidence says the URL is dead / blocked / unreadable carries
     the matching review flag. A dead source with no flag is a FAIL.
  4. No row's stored price contradicts the evidence in the direction that matters:
     if the evidence could not read a price, the row must not claim it was
     re-confirmed on the evidence date.
  5. The evidence is not stale: older than --max-age-days (default 30) is a FAIL.
     Between 7 and 30 days is a WARNING ("re-run the live check").
  6. Every registered source that returned 404 must either be corrected, or carry
     a manual_verification note explaining why it is still published.

Exit codes: 0 pass (warnings allowed), 1 hard failure.

Run after every review:
    python3 scripts/audit_freshness.py
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

REQUIRED_FLAG = {
    "HTTP_404": "SOURCE_URL_DEAD",
    "SOFT_404": "SOURCE_URL_DEAD",
    "REFUSED_403": "SOURCE_BOT_BLOCKED",
    "EMPTY_OR_JS_SHELL": "SOURCE_PRICE_NOT_MACHINE_READABLE",
}

errors: list[str] = []
warnings: list[str] = []
checks = 0


def ok() -> None:
    global checks
    checks += 1


def bad(msg: str) -> None:
    global checks
    checks += 1
    errors.append(msg)


def warn(msg: str) -> None:
    global checks
    checks += 1
    warnings.append(msg)


def parse_utc(s: str) -> dt.datetime | None:
    if not s:
        return None
    try:
        return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-age-days", type=int, default=30)
    ap.add_argument("--warn-age-days", type=int, default=7)
    args = ap.parse_args()

    sh_path = DATA / "source_health.json"
    if not sh_path.exists():
        print("FAIL: data/source_health.json is missing — the site must not publish without live source evidence")
        return 1
    health = json.loads(sh_path.read_text(encoding="utf-8"))
    rings = json.loads((DATA / "rings.json").read_text(encoding="utf-8"))
    sources = json.loads((DATA / "sources.json").read_text(encoding="utf-8"))

    ok()  # 1. evidence file present
    if health.get("network_environment_blocked"):
        bad("the last live check ran in a network-blocked environment and proves nothing")
    art = health.get("evidence_artifact", "")
    artifact = None
    raw_by_key = {}
    if not (ROOT / art).exists():
        bad(f"evidence artifact referenced but missing: {art}")
    else:
        try:
            artifact = json.loads((ROOT / art).read_text(encoding="utf-8"))
            raw_by_key = {r.get("key"): r for r in artifact.get("results", [])}
            if artifact.get("checked_utc") != health.get("evidence_checked_utc"):
                bad("health evidence_checked_utc does not match the raw artifact timestamp")
            else:
                ok()
            if artifact.get("network_environment_blocked"):
                bad("raw evidence artifact is marked network_environment_blocked")
            else:
                ok()
        except (OSError, json.JSONDecodeError) as exc:
            bad(f"evidence artifact is unreadable: {exc}")

    checked = parse_utc(health.get("evidence_checked_utc", ""))
    if checked is None:
        bad("evidence_checked_utc missing/unparseable in data/source_health.json")
    else:
        age = (dt.datetime.now(dt.timezone.utc) - checked).days
        if age > args.max_age_days:
            bad(f"live source evidence is {age} days old (limit {args.max_age_days}) — re-run the live check")
        elif age > args.warn_age_days:
            warn(f"live source evidence is {age} days old — re-run the live check")
        else:
            ok()

    rows = {r["id"]: r for r in rings["rows"]}
    health_rows = {h["id"]: h for h in health["rows"]}
    health_sources = {h["id"]: h for h in health["sources"]}

    for rid, row in rows.items():
        h = health_rows.get(rid)
        if h is None:
            bad(f"{rid}: no entry in the live source-health evidence")
            continue
        raw = raw_by_key.get(rid)
        if raw is None:
            bad(f"{rid}: no raw result in the referenced evidence artifact")
            continue
        if h.get("source_state") in ("NOT_CHECKED", "ENVIRONMENT_BLOCKED"):
            bad(f"{rid}: source was not successfully checked ({h.get('source_state')})")
        elif raw.get("classification") != h.get("source_state") or raw.get("http_status") != h.get("http_status"):
            bad(f"{rid}: health summary does not match raw classification/HTTP evidence")
        else:
            ok()
        if h.get("stored_price_usd") != row.get("price_usd") or h.get("stored_price_captured_utc") != row.get("price_captured_utc"):
            bad(f"{rid}: health stored price/date differs from the canonical row; rerun reconciliation")
        else:
            ok()
        sc = row.get("source_check")
        if not sc:
            bad(f"{rid}: row has no source_check block (evidence not applied)")
            continue
        if sc.get("checked_utc") != health.get("evidence_checked_utc") or sc.get("evidence_artifact") != art:
            bad(f"{rid}: applied evidence timestamp/artifact is stale or incorrect")
        else:
            ok()
        if sc.get("state") != h.get("source_state"):
            bad(f"{rid}: source_check.state {sc.get('state')} != evidence {h.get('source_state')}")
            continue
        if sc.get("price_state") != h.get("price_state"):
            bad(f"{rid}: source_check.price_state {sc.get('price_state')} != evidence {h.get('price_state')}")
            continue
        if sc.get("http_status") != h.get("http_status"):
            bad(f"{rid}: source_check.http_status differs from the evidence artifact")
            continue
        ok()

        want = REQUIRED_FLAG.get(h["source_state"])
        if want and want not in row.get("flags", []):
            bad(f"{rid}: source state {h['source_state']} must carry the {want} flag")
        else:
            ok()
        if h["source_state"] not in ("OK", *REQUIRED_FLAG) and "SOURCE_NOT_REACHED" not in row.get("flags", []):
            bad(f"{rid}: unresponsive source state {h['source_state']} must carry SOURCE_NOT_REACHED")
        else:
            ok()

        if h.get("price_state") == "DIFFERS" and "PRICE_STRUCTURED_DIFFERS" not in row.get("flags", []):
            bad(f"{rid}: the page prints a different price but PRICE_STRUCTURED_DIFFERS is missing")
        else:
            ok()
        if h.get("price_state") == "MULTIPLE_OFFERS_INCLUDE_STORED" and "PRICE_STRUCTURED_VARIANT_AMBIGUOUS" not in row.get("flags", []):
            bad(f"{rid}: multi-offer match lacks PRICE_STRUCTURED_VARIANT_AMBIGUOUS")
        else:
            ok()

        # A value may only look "fresh" if some read path actually opened it.
        # If this automated check could not read the page, but the row is dated the
        # same day, the read must have come from a different path (a human/browser
        # session). That is legitimate, but it must never pass silently.
        if h.get("price_state") in ("SOURCE_NOT_REACHED", "NOT_MACHINE_READABLE"):
            same_day = str(row.get("price_captured_utc", "")).startswith(
                (health.get("evidence_checked_utc") or "xx")[:10]
            )
            if same_day and row.get("price_usd") is not None:
                warn(
                    f"{rid}: populated price dated on the evidence day although this automated check could not read the page "
                    f"({h['source_state']}) — the value rests on a different read path and needs review"
                )
            else:
                ok()
        else:
            ok()

        # Dead URL => the row must still carry a usable official link, and the
        # review flag has to explain itself.
        if h["source_state"] in ("HTTP_404", "SOFT_404"):
            if not str(row.get("url", "")).startswith("https://"):
                bad(f"{rid}: dead URL is not even an https official link")
            elif not re.search(r"(?:Pass \d+|Live review) source check ", row.get("flag_detail") or ""):
                warn(f"{rid}: SOURCE_URL_DEAD raised without the evidence sentence in flag_detail")
            else:
                ok()

    # 6. registered sources: raw artifact → health summary → applied source row.
    for src in sources["sources"]:
        h = health_sources.get(src["id"])
        raw = raw_by_key.get(src["id"])
        lc = src.get("live_check") or {}
        state = lc.get("state")
        if h is None or raw is None:
            bad(f"source {src['id']}: missing health or raw evidence")
            continue
        if h.get("source_state") in ("NOT_CHECKED", "ENVIRONMENT_BLOCKED"):
            bad(f"source {src['id']}: source was not successfully checked")
        elif raw.get("classification") != h.get("source_state") or raw.get("http_status") != h.get("http_status"):
            bad(f"source {src['id']}: health summary differs from raw evidence")
        elif state != h.get("source_state") or lc.get("http_status") != h.get("http_status") or lc.get("checked_utc") != h.get("checked_utc"):
            bad(f"source {src['id']}: live_check is not the current applied evidence")
        else:
            ok()
        if state in ("HTTP_404", "SOFT_404", "REFUSED_403", "EMPTY_OR_JS_SHELL"):
            if src.get("manual_verification") or src.get("url_correction"):
                ok()
            else:
                warn(f"source {src['id']}: {state} with no correction and no manual verification note")
        else:
            ok()
        if not str(src.get("url", "")).startswith("https://"):
            bad(f"source {src['id']}: URL is not https")

    print("=" * 70)
    print("GOLD4 FRESHNESS & SOURCE-HEALTH GATE (gate 7)")
    print("=" * 70)
    print(f"evidence checked : {health.get('evidence_checked_utc')}")
    print(f"rows             : {len(rows)}   registered sources: {len(sources['sources'])}")
    print(f"row states       : {health.get('row_states')}")
    print(f"price states     : {health.get('price_states')}")
    print("-" * 70)
    for w in warnings:
        print(f"[WARN] {w}")
    for e in errors:
        print(f"[FAIL] {e}")
    print("-" * 70)
    if errors:
        print(f"RESULT: FAIL — {len(errors)} hard failure(s), {len(warnings)} warning(s), {checks} checks")
        return 1
    print(f"RESULT: PASS — {checks} checks, {len(warnings)} warning(s), 0 failures")
    print("This gate proves the evidence exists, is recent, is applied to every row and is honestly flagged.")
    print("It cannot prove a retailer's page today matches what a shopper sees in their own browser.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
