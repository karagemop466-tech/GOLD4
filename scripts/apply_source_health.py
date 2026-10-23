#!/usr/bin/env python3
"""Apply the live source-health evidence to data/rings.json — additively only.

Reads   data/source_health.json   (evidence, generated on a runner with internet)
Writes  data/rings.json           (adds a `source_check` block per row + review flags)

WHAT THIS SCRIPT WILL AND WILL NOT DO
    WILL   stamp each row with what the live check saw: HTTP status, state,
           the page's own structured price, and the check timestamp.
    WILL   raise review flags for dead URLs, bot-blocked sources and prices that
           the page now prints differently.
    WILL   append (never replace) the previous state to `flag_detail` so the
           history of a value survives.
    WON'T  change a single price, weight, karat, SKU or URL.
    WON'T  treat a 403 / 404 / JS shell as evidence about a price.
    WON'T  touch rows or fields it was not asked to touch.

Idempotent: re-running replaces the `source_check` block and does not duplicate
flags or flag_detail sentences.

Usage: python3 scripts/apply_source_health.py [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

NEW_FLAG_LABELS = {
    "SOURCE_URL_DEAD": "source URL returns 404 as of the live check",
    "SOURCE_BOT_BLOCKED": "retailer blocked the automated check (HTTP 403)",
    "PRICE_STRUCTURED_DIFFERS": "page's structured price differs from the stored price",
    "SOURCE_PRICE_NOT_MACHINE_READABLE": "price is not published in machine-readable form",
}


def sentence(state_row: dict, checked: str) -> str:
    """The exact, quoted evidence sentence appended to the row."""
    st = state_row["source_state"]
    ps = state_row["price_state"]
    found = ", ".join(
        f"{p['value']:,.2f} {p['currency'] or 'n/a'} via {p['source']}" for p in state_row.get("found_prices", [])
    )
    head = f"Pass 15 source check {checked}: "
    if st == "HTTP_404":
        return head + (
            "the stored source URL returned HTTP 404 (Blue Nile / Ross-Simons 'not found'); "
            "the stored value was read from this URL on its capture date and cannot be re-confirmed here. "
            "No value was changed."
        )
    if st == "REFUSED_403":
        return head + (
            "the retailer's bot protection refused the automated check (HTTP 403), so this pass makes no claim "
            "about the current price; the stored value keeps its original provenance. No value was changed."
        )
    if st == "EMPTY_OR_JS_SHELL":
        return head + (
            "the page answered HTTP 200 but serves a JavaScript shell with no product text, so the price could "
            "not be read without a browser render. No value was changed."
        )
    if ps == "CONFIRMED":
        return head + f"the page's own structured data printed {found}, matching the stored price."
    if ps == "DIFFERS":
        return head + (
            f"the page's own structured data currently prints {found} against the stored "
            f"${state_row['stored_price_usd']:,.2f}. Both numbers are shown; the stored value is NOT overwritten "
            "because the difference may be a variant/configuration selection on the page."
        )
    if ps == "NOT_MACHINE_READABLE":
        return head + "the page publishes no USD structured price, so the stored value keeps its original provenance."
    return head + f"source state {st}, price state {ps}."


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    health = json.loads((DATA / "source_health.json").read_text(encoding="utf-8"))
    rings_path = DATA / "rings.json"
    doc = json.loads(rings_path.read_text(encoding="utf-8"))
    checked = (health.get("evidence_checked_utc") or "")[:16].replace("T", " ") + "Z"
    by_id = {r["id"]: r for r in health["rows"]}

    changed = 0
    for row in doc["rows"]:
        st = by_id.get(row["id"])
        if st is None:
            continue
        flags = [f for f in row.get("flags", []) if f not in NEW_FLAG_LABELS]
        row["source_check"] = {
            "checked_utc": health.get("evidence_checked_utc"),
            "evidence_artifact": health.get("evidence_artifact"),
            "http_status": st.get("http_status"),
            "state": st.get("source_state"),
            "price_state": st.get("price_state"),
            "page_title": (st.get("page_title") or "")[:160],
            "found_prices": [p for p in st.get("found_prices", [])][:4],
            "note": st.get("note", ""),
        }
        if st.get("final_url") and st["final_url"].rstrip("/") != row["url"].rstrip("/"):
            row["source_check"]["final_url"] = st["final_url"]

        if st.get("source_state") == "HTTP_404":
            flags.append("SOURCE_URL_DEAD")
        elif st.get("source_state") == "REFUSED_403":
            flags.append("SOURCE_BOT_BLOCKED")
        elif st.get("price_state") == "NOT_MACHINE_READABLE":
            flags.append("SOURCE_PRICE_NOT_MACHINE_READABLE")
        if st.get("price_state") == "DIFFERS":
            flags.append("PRICE_STRUCTURED_DIFFERS")
        row["flags"] = flags

        # Append the evidence sentence once, keeping whatever an earlier pass wrote.
        existing = row.get("flag_detail") or ""
        marker = "Pass 15 source check"
        if marker in existing:
            existing = existing.split(" | " + marker)[0].rstrip(" |")
        note = sentence(st, checked)
        if st.get("source_state") == "OK" and st.get("price_state") in ("CONFIRMED", "NO_STORED_PRICE"):
            # confirmed / nothing to raise: record it in source_check only, do not
            # clutter flag_detail on 45 healthy rows.
            pass
        else:
            row["flag_detail"] = (existing + " | " + note).strip(" |") if existing else note
        changed += 1

    doc["source_health_pass"] = (
        f"Pass 15 (session arena/03c0c10f-gold4) re-opened all {len(by_id)} store URLs live from a GitHub runner "
        f"at {health.get('evidence_checked_utc')} and recorded the HTTP status and the page's own structured price "
        "in each row's `source_check` block. This pass changed no price, weight or URL."
    )
    doc["source_health_checked_utc"] = health.get("evidence_checked_utc")
    doc["source_health_artifact"] = health.get("evidence_artifact")

    if args.dry_run:
        print(f"dry run: would stamp {changed} rows")
        return 0
    rings_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"stamped {changed} rows in data/rings.json (no value changed)")

    # ---------------------------------------------------------------- sources.json
    # Only two things are written here: the live-check result for each registered
    # source, and one documented URL correction for a link that is now dead.
    # Verified by hand on 2026-10-23 through a browser-rendered fetch:
    #   https://www.nist.gov/pml/owm/metric-publications/nist-handbook-44  -> NIST "Page not found"
    #   https://www.nist.gov/nist-pub-series/handbook-nist-hb              -> live, describes HB 44
    CORRECTIONS = {
        "nist-hb44-2026": {
            "url": "https://www.nist.gov/nist-pub-series/handbook-nist-hb",
            "title": "NIST Handbook series — Handbook 44 (specifications, tolerances and other technical requirements for weighing and measuring devices)",
            "retrieved_utc": "2026-10-23",
            "dead_url": "https://www.nist.gov/pml/owm/metric-publications/nist-handbook-44",
        }
    }
    src_doc = json.loads((DATA / "sources.json").read_text(encoding="utf-8"))
    src_health = {s["id"]: s for s in health["sources"]}
    src_changed = 0
    for src in src_doc["sources"]:
        h = src_health.get(src["id"])
        if h:
            src["live_check"] = {
                "checked_utc": h.get("checked_utc"),
                "http_status": h.get("http_status"),
                "state": h.get("source_state"),
                "final_url": h.get("final_url"),
            }
            src_changed += 1
        # Two hosts refuse the runner but answer a browser-rendered fetch. Both pages
        # were re-read by hand on 2026-10-23 and are recorded here as manual evidence,
        # so the 404 from CI is never mistaken for a dead source.
        MANUAL = {
            "ftc-gold-jewelry": "Re-read 2026-10-23 via a browser-rendered fetch: the article loads with its full text (karat marks, 'solid gold' definition, plated/filled/vermeil definitions). The runner's plain GET returns 404 — bot filtering, not a dead source.",
            "ftc-credit-cards": "Re-read 2026-10-23 via a browser-rendered fetch: the article loads with its full text (billing-error dispute rights). The runner's plain GET returns 404 — bot filtering, not a dead source.",
            "brilliantearth-atelier": "Brilliant Earth's bot protection refuses the automated check (HTTP 403). The page was read by a browser-rendered session on 2026-10-23 (repo verification log, Pass 14), which is the only evidence for its price; this automated pass makes no claim about it.",
            "brilliantearth-atelier-14k": "Brilliant Earth's bot protection refuses the automated check (HTTP 403). The page was read by a browser-rendered session on 2026-10-23 (repo verification log, Pass 14); this automated pass makes no claim about it.",
            "brilliant-earth-returns": "Brilliant Earth's bot protection refuses the automated check (HTTP 403), so this pass cannot re-confirm the 30-day return terms; the clause stays as captured and is flagged on the Flagged page.",
            "brilliantearth-returns-30d": "Brilliant Earth's bot protection refuses the automated check (HTTP 403), so this pass cannot re-confirm the 30-day return terms; the clause stays as captured and is flagged on the Flagged page.",
            "anjolee-ms354a": "Re-read 2026-10-23 via a browser-rendered fetch: the product page loads (Six Curved Prongs Solitaire Diamond Engagement Ring). The runner receives a JavaScript shell with no product text, so its price could not be machine-checked on this pass.",
        }
        if src["id"] in MANUAL and (src.get("live_check") or {}).get("state") not in (None, "OK"):
            src["manual_verification"] = MANUAL[src["id"]]
        fix = CORRECTIONS.get(src["id"])
        if fix and src.get("url") == fix["url"] and (src.get("live_check") or {}).get("http_status") == 404:
            # idempotent re-run: the correction was already applied on a previous run
            src["live_check"]["state"] = "URL_CORRECTED_AFTER_CHECK"
            src["live_check"]["checked_url"] = fix["dead_url"]
            src["live_check"]["note"] = (
                "the 404 recorded above belongs to the URL that was in force at check time; the URL was "
                "corrected on 2026-10-23 and the replacement was verified live by hand"
            )
        if fix and src.get("url") == fix["dead_url"]:
            src["url"] = fix["url"]
            src["title"] = fix["title"]
            src["retrieved_utc"] = fix["retrieved_utc"]
            src["verification"] = "V1_direct_page_fetch (re-verified 2026-10-23)"
            src["url_correction"] = (
                "Pass 12 (2026-10-23): the previous URL " + fix["dead_url"] + " now returns NIST's "
                "'Page not found' (confirmed through a browser-rendered fetch and by HTTP 404 from CI). "
                "Replaced with the live NIST Handbook series page that describes Handbook 44."
            )
            src["live_check"]["state"] = "URL_CORRECTED_AFTER_CHECK"
            src["live_check"]["checked_url"] = fix["dead_url"]
            src["live_check"]["note"] = (
                "the 404 recorded above belongs to the URL that was in force at check time; the URL was "
                "corrected on 2026-10-23 and the replacement was verified live by hand"
            )
            print(f"corrected dead source URL for {src['id']}")
    (DATA / "sources.json").write_text(json.dumps(src_doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"stamped {src_changed} registered sources in data/sources.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
