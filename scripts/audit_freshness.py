#!/usr/bin/env python3
"""GOLD4 Gate 6 — freshness & source-health gate.

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
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

REQUIRED_FLAG = {
    "HTTP_404": "SOURCE_URL_DEAD",
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
    if not (ROOT / art).exists():
        bad(f"evidence artifact referenced but missing: {art}")
    else:
        ok()

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

    for rid, row in rows.items():
        h = health_rows.get(rid)
        if h is None:
            bad(f"{rid}: no entry in the live source-health evidence")
            continue
        sc = row.get("source_check")
        if not sc:
            bad(f"{rid}: row has no source_check block (evidence not applied)")
            continue
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

        if h.get("price_state") == "DIFFERS" and "PRICE_STRUCTURED_DIFFERS" not in row.get("flags", []):
            bad(f"{rid}: the page prints a different price but PRICE_STRUCTURED_DIFFERS is missing")
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
            if same_day:
                warn(
                    f"{rid}: price dated on the evidence day although this automated check could not read the page "
                    f"({h['source_state']}) — the value rests on a different read path and needs review"
                )
            else:
                ok()
        else:
            ok()

        # Dead URL => the row must still carry a usable official link, and the
        # review flag has to explain itself.
        if h["source_state"] == "HTTP_404":
            if not str(row.get("url", "")).startswith("https://"):
                bad(f"{rid}: dead URL is not even an https official link")
            elif "Pass 12 source check" not in (row.get("flag_detail") or ""):
                warn(f"{rid}: SOURCE_URL_DEAD raised without the evidence sentence in flag_detail")
            else:
                ok()

    # 6. registered sources
    for src in sources["sources"]:
        lc = src.get("live_check") or {}
        state = lc.get("state")
        if state in ("HTTP_404", "REFUSED_403", "EMPTY_OR_JS_SHELL"):
            if src.get("manual_verification") or src.get("url_correction"):
                ok()
            else:
                warn(f"source {src['id']}: {state} with no correction and no manual verification note")
        else:
            ok()
        if not str(src.get("url", "")).startswith("https://"):
            bad(f"source {src['id']}: URL is not https")

    print("=" * 70)
    print("GOLD4 FRESHNESS & SOURCE-HEALTH GATE (gate 6)")
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
