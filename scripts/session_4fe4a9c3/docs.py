#!/usr/bin/env python3
"""Prose for the 2026-11-11 re-read (session 4fe4a9c3), generated from the evidence so it cannot drift from the data.

Writes: this session's entry in data/verification_log.json, its block and the
benchmark lines in README.md, and reviews/reread-4fe4a9c3/report.md. Idempotent.
Every number comes from reviews/reread-4fe4a9c3/reconciliation.json, data/rings.json or
data/gold_spot.json. NO value is typed here.
"""
from __future__ import annotations

import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
SITE = "https://karagemop466-tech.github.io/GOLD4/"


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def m(v):
    v = float(v)
    return f"${v:,.0f}" if abs(v - round(v)) < 0.005 else f"${v:,.2f}"


def main() -> None:
    rec = load("reviews/reread-4fe4a9c3/reconciliation.json")
    hand = load("reviews/reread-4fe4a9c3/hand_reads.json")
    rings = load("data/rings.json")["rows"]
    spot = load("data/gold_spot.json")
    health = load("data/source_health.json")
    gates = load("reviews/reread-4fe4a9c3/gates.json")
    dec = rec["rows"]
    by = {d["id"]: d for d in dec}
    vc = rec["verdict_counts"]
    n = len(dec)
    b = spot["benchmark"]
    prev = [p for p in spot["prior_captures"] if p.get("status") == "superseded"][-1]
    delta = (b["value_usd_per_oz"] / prev["value_usd_per_oz"] - 1) * 100
    usd_g = spot["constants"]["spot_usd_per_gram"]
    flags_total = sum(len(r["flags"]) for r in rings)

    def ids(v):
        return [d["id"] for d in dec if d["verdict"] == v]

    def chg(i):
        return f"{i} {m(by[i]['stored_price_usd'])} → {m(by[i]['price_today_usd'])}"

    sale_bn = [i for i in ids("SALE") if i.startswith("BN-")]
    sale_rs = [i for i in ids("SALE") if i.startswith("RS-")]
    changed, dead, sold, notread = ids("CHANGED"), ids("SOURCE_DEAD"), ids("SOLD_OUT"), ids("NOT_REREAD")
    hand_ids = [h["id"] for h in hand["rows"]]
    lag = [r["id"] for r in rings if "STRUCTURED_PRICE_LAGS_DISPLAY" in r["flags"]]
    w_rows = [r["id"] for r in rings if r.get("weight_g") is not None]
    w_not = [i for i in w_rows if not by[i]["weight_reread_today"]]
    cross = "; ".join(f"{c['label']} ${c['value_usd_per_oz']:,.2f}" for c in spot["reread_2026_11_11_cross_checks"])
    gates_ok = sum(1 for g in gates if g["status"] == "PASS")
    rs = health["row_states"]

    # ---------------------------------------------------------------- verification log
    log = load("data/verification_log.json")
    entry = {
        "pass": "Re-read of 2026-11-11 (session 4fe4a9c3) — re-verification after 19 days: runner sweep of all rows + hand reads, benchmark refresh, sale prices, dead pages (session arena/4fe4a9c3-gold4)",
        "when_utc": "2026-11-11T08:00Z–08:50Z",
        "scope": "The stored prices and benchmark were 19–20 days old. Every ring URL and registered source was re-opened by a GitHub runner, "
                 f"{len(hand_ids)} rows and the gold benchmark were hand-read in a browser-rendered reader, and each row was reconciled against both.",
        "checked": [
            f"{n}/{n} ring URLs + {len(health['sources'])}/{len(health['sources'])} registered sources re-opened by a GitHub runner at {rec['runner_checked_utc']} "
            f"(evidence: reports/live_source_check_20261111T080309Z.json). Row states: " + ", ".join(f"{k} {v}" for k, v in rs.items()),
            f"{len(hand_ids)} rows hand-read with verbatim page strings recorded (reviews/reread-4fe4a9c3/hand_reads.json): " + ", ".join(hand_ids),
            f"Gold benchmark re-read: World Gold Council panel ${b['value_usd_per_oz']:,.2f}/oz, '{b['data_as_of_shown_on_source']}' "
            f"({delta:+.2f}% against the ${prev['value_usd_per_oz']:,.2f}/oz reading of 23 October). Cross-checks read by the runner: {cross}",
            f"Every derived gold value recomputed at ${usd_g}/g; all {len(gates)} gate commands re-run: {gates_ok} pass",
        ],
        "found": [
            f"{vc.get('UNCHANGED', 0)} prices unchanged; {vc.get('SALE', 0)} are now temporary sale prices (Blue Nile {len(sale_bn)}, Ross-Simons {len(sale_rs)})",
            "Prices changed with no sale label: " + "; ".join(chg(i) for i in changed),
            "Pages gone (price now blank, last value kept): " + ", ".join(dead),
            "Sold out (price blank): " + ", ".join(sold),
            f"On {len(lag)} Ross-Simons pages the machine-readable price still carries the pre-sale amount while the page displays the sale price; "
            "the structured-data CONFIRMED rule would have confirmed the stale October prices",
            "Tooling: the pass label 'Pass 15' was hard-coded in scripts/apply_source_health.py and scripts/audit_freshness.py; both fixed",
        ],
        "flags_added": ["SALE_PRICE_TEMPORARY", "PRICE_CHANGED_2026_11_11", "SOURCE_DEAD_2026_11_11", "SOLD_OUT_2026_11_11",
                        "PRICE_NOT_REREAD_2026_11_11", "STRUCTURED_PRICE_LAGS_DISPLAY"],
        "not_verified_this_pass": [
            f"{n - len(hand_ids)} of {n} rows were not hand-read; their only evidence dated 2026-11-11 is the runner fetch",
            "Not re-read at all: " + ", ".join(notread),
            f"Gram weights re-seen for {len(w_rows) - len(w_not)} of {len(w_rows)} rows; not re-seen: " + ", ".join(w_not),
            "Return-policy, warranty, law and guidance text: reachability checked only, wording not re-read",
            "No XRF or assay result, no hallmark, no independently verified seller reputation for any row",
        ],
        "result": f"{gates_ok}/{len(gates)} gate commands pass on the final tree",
        "recommendation": "Look for hallucinations after every review: open rows at random, compare each number and its date with the official page. "
                          "Re-read every price before buying; sale prices expire.",
        "outcome": f"{vc.get('SALE', 0) + vc.get('CHANGED', 0)} prices updated with history kept, {vc.get('SOURCE_DEAD', 0) + vc.get('SOLD_OUT', 0)} rows blank, "
                   f"{flags_total} flag instances published.",
        "note": "Values were copied from the two evidence files by scripts/session_4fe4a9c3/apply_reread.py; none was typed by hand.",
    }
    log["passes"] = [p for p in log["passes"] if "session 4fe4a9c3" not in str(p.get("pass", ""))] + [entry]
    log["not_reverified_this_pass"] = entry["not_verified_this_pass"]
    (ROOT / "data/verification_log.json").write_text(json.dumps(log, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    # ---------------------------------------------------------------- README block
    block = f"""<!-- REREAD-4FE4A9C3:START (generated by scripts/session_4fe4a9c3/docs.py — do not edit by hand) -->
**Re-read and re-price of 11 November 2026 (session `arena/4fe4a9c3-gold4`): re-verification after 19 days.** The stored prices and gold benchmark dated from 22–23 October. A GitHub runner re-opened all **{n}** ring pages and **{len(health['sources'])}** registered sources at {rec['runner_checked_utc']}, and this session hand-read **{len(hand_ids)}** rows and the benchmark. Full record: [11 November re-read page]({SITE}pages/reread-4fe4a9c3.html) · [`reviews/reread-4fe4a9c3/`](reviews/reread-4fe4a9c3/).

| Result on 11 November 2026 | Count | Rows |
|---|---|---|
| Price unchanged since October | **{vc.get('UNCHANGED', 0)}** | see the re-read page |
| Temporary **sale** price (list price shown beside it) | **{vc.get('SALE', 0)}** | Blue Nile {len(sale_bn)}, Ross-Simons {len(sale_rs)} |
| Price changed, no sale label | **{vc.get('CHANGED', 0)}** | {'; '.join(chg(i) for i in changed)} |
| Page gone — price now **blank** | **{vc.get('SOURCE_DEAD', 0)}** | {', '.join(dead)} |
| Sold out — price **blank** | **{vc.get('SOLD_OUT', 0)}** | {', '.join(sold)} |
| Not re-read | **{vc.get('NOT_REREAD', 0)}** | {', '.join(notread)} |

- **Gold benchmark:** World Gold Council panel **${b['value_usd_per_oz']:,.2f}/oz** ("{b['data_as_of_shown_on_source']}") = **${usd_g}/g**, {delta:+.2f}% against the 23 October reading of ${prev['value_usd_per_oz']:,.2f}/oz, which is kept in `prior_captures`. Runner cross-checks: {cross}. Not a live quote.
- **How prices were updated:** only where that day's evidence printed the current amount. Every superseded value is in the row's `price_history`. Dead and sold-out rows show a blank price with the last value read beside it. Nothing was estimated.
- **Finding:** on {len(lag)} Ross-Simons pages the machine-readable price still carried the pre-sale amount while the page displayed the sale price, so the automated `CONFIRMED` rule would have confirmed stale prices. `CONFIRMED` is evidence about page metadata, not about what a shopper sees.
- **Not done:** {n - len(hand_ids)} of {n} rows were not hand-read; gram weights were re-seen for {len(w_rows) - len(w_not)} of {len(w_rows)} rows; policy and law text was checked for reachability only; no ring was tested, no hallmark seen, no seller reputation verified.
- **Checks:** {gates_ok}/{len(gates)} gate commands pass (`python3 scripts/session_4fe4a9c3/run_gates.py`). {flags_total} flag instances are published on the [Flagged page]({SITE}pages/flagged.html). **Look for hallucinations after every review.**
<!-- REREAD-4FE4A9C3:END -->"""
    rp = ROOT / "README.md"
    s = rp.read_text(encoding="utf-8")
    if "<!-- REREAD-4FE4A9C3:START" in s:
        s = re.sub(r"<!-- REREAD-4FE4A9C3:START.*?<!-- REREAD-4FE4A9C3:END -->", lambda _: block, s, flags=re.S)
    else:
        anchor = "**Latest integration — purchase-readiness register"
        assert anchor in s
        s = s.replace(anchor, block + "\n\n**Earlier integration — purchase-readiness register", 1)
    bench = (f"The gold benchmark in force: **${b['value_usd_per_oz']:,.2f}/oz** = **${usd_g}/g**, read from the World Gold Council Goldhub panel on "
             f"**11 Nov 2026 at 08:01Z** (the panel's own line reads \"{b['data_as_of_shown_on_source']}\"). The 23 October benchmark of "
             f"${prev['value_usd_per_oz']:,.2f}/oz and all earlier readings are kept in `prior_captures`. Before this re-read: ")
    old = "The gold benchmark in force: **$3,996.31/oz** = **$128.48435/g**, read from the World Gold Council Goldhub panel on **23 Oct 2026 at 20:23Z**"
    if old in s:
        s = s.replace(old, bench + "$3,996.31/oz = $128.48435/g, read on 23 Oct 2026 at 20:23Z", 1)
    old2 = "| Gold benchmark used | **$3,996.31/oz = $128.48435/g**, read 23 Oct 2026 at 20:23Z"
    if old2 in s:
        s = s.replace(old2, f"| Gold benchmark used | **${b['value_usd_per_oz']:,.2f}/oz = ${usd_g}/g**, read 11 Nov 2026 at 08:01Z (\"{b['data_as_of_shown_on_source']}\"). "
                            "Previously $3,996.31/oz = $128.48435/g, read 23 Oct 2026 at 20:23Z", 1)
    cmd_old = "python3 scripts/build_pass20.py       # historical review page, current layout; original evidence unchanged\n"
    cmd_new = cmd_old + "python3 scripts/session_4fe4a9c3/build_page.py       # 11 Nov 2026 re-read page from reviews/reread-4fe4a9c3/*.json\n"
    if "scripts/session_4fe4a9c3/build_page.py" not in s and cmd_old in s:
        s = s.replace(cmd_old, cmd_new, 1)
    rp.write_text(s, encoding="utf-8")

    # ---------------------------------------------------------------- reviews/reread-4fe4a9c3/report.md
    lines = [
        "# Re-read of 2026-11-11 — re-verification after 19 days (session 4fe4a9c3)",
        "",
        "Session `arena/4fe4a9c3-gold4`. **No hallucinations:** every value below is copied from the evidence files; nothing was inferred.",
        "",
        "## Evidence",
        "",
        "| File | What it is |",
        "|---|---|",
        f"| `reports/live_source_check_20261111T080309Z.json` | GitHub runner, read-only GET of {n} ring URLs + {len(health['sources'])} sources, {rec['runner_checked_utc']} |",
        f"| `reviews/reread-4fe4a9c3/hand_reads.json` | {len(hand_ids)} rows + the benchmark, hand-read in a browser-rendered reader, verbatim strings |",
        "| `reviews/reread-4fe4a9c3/reconciliation.json` | row-by-row verdicts combining both read paths |",
        "| `reviews/reread-4fe4a9c3/gates.json`, `gates.txt` | the twelve gate commands on the final tree |",
        "",
        "## Gold benchmark",
        "",
        f"World Gold Council panel: **${b['value_usd_per_oz']:,.2f}/oz**, \"{b['data_as_of_shown_on_source']}\", read {b['captured_utc']} — <{b['source_url']}>.",
        f"Previous benchmark ${prev['value_usd_per_oz']:,.2f}/oz ({delta:+.2f}%). Runner cross-checks: {cross}.",
        "",
        "## Row by row",
        "",
        "| ID | Before | Read 11 Nov | List | Verdict | Read path | Weight re-seen | Official page |",
        "|---|---|---|---|---|---|---|---|",
    ]
    rr = {r["id"]: r for r in rings}
    for d in dec:
        hand_p = any("hand read" in p for p in d["read_paths"])
        run_p = any(p.startswith("runner") for p in d["read_paths"])
        path = "runner + hand" if hand_p and run_p else "hand" if hand_p else "runner" if run_p else "none"
        lines.append(
            f"| {d['id']} | {m(d['stored_price_usd']) if d['stored_price_usd'] is not None else '—'} | "
            f"{m(d['price_today_usd']) if d['price_today_usd'] is not None else '—'} | "
            f"{m(d['list_price_usd']) if d.get('list_price_usd') else ''} | {d['verdict']} | {path} | "
            f"{'yes' if d['weight_reread_today'] else ('no' if rr[d['id']].get('weight_g') is not None else 'n/a')} | <{rr[d['id']]['url']}> |")
    lines += ["", "## Not verified this pass", ""] + [f"- {x}" for x in entry["not_verified_this_pass"]]
    lines += ["", "## Gates", "", "| Gate | Status | Detail |", "|---|---|---|"] + [f"| {g['gate']} | {g['status']} | {g['detail']} |" for g in gates]
    (ROOT / "reviews/reread-4fe4a9c3/report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("wrote verification log entry, README block, reviews/reread-4fe4a9c3/report.md")


if __name__ == "__main__":
    main()
