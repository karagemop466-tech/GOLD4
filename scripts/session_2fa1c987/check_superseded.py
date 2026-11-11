#!/usr/bin/env python3
"""Superseded-benchmark check for the non-canonical surfaces.

Session arena/2fa1c987-gold4, Pass 21 companion task 78.

The generic scanner (scan_prose.py) can only ask "does this number exist
anywhere in data/**?". A superseded number does exist in data/** — it sits in
`prior_captures` with status `superseded` — so the generic scan reports it as
traceable even when a page presents it as the benchmark *in force*. That is a
false clean.

This script closes that hole. It reads data/gold_spot.json, separates the
ACTIVE benchmark from every SUPERSEDED reading, and then looks for superseded
readings on the published surfaces in a context that claims they are current
("benchmark", "in force", "driving every derived value", "spot", ...).

Like the scanner, it edits nothing. It exits 1 in --gate mode when a superseded
value is presented as current, so that once the backlog is cleared a later
integration can make it blocking.

USAGE
    python3 scripts/session_2fa1c987/check_superseded.py
    python3 scripts/session_2fa1c987/check_superseded.py --json out.json
    python3 scripts/session_2fa1c987/check_superseded.py --gate
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

SURFACES = [
    "dashboard.html", "solitaires.html", "three-stone-halo.html", "bands.html",
    "checklist.html", "standards.html", "audit.html", "flagged.html",
    "sellers.html", "calculator.html", "app.js",
    "categories/*.html", "docs/*.html", "assets/*.js", "static/*.js",
    "README.md", "AUDIT.md", "VERIFICATION.md",
]

# Words that make a sentence a claim about what is true NOW.
CURRENT_CLAIM = (
    "benchmark", "in force", "driving every derived value", "spot benchmark",
    "spot price", "gold spot", "per oz", "/oz", "per gram", "/g",
    "currently", "in effect", "used for all arithmetic", "the benchmark",
)

# Words that legitimately mark the number as history, not a current claim.
HISTORICAL_MARKER = (
    "prior_captures", "superseded", "no longer", "previously", "earlier",
    "was replaced", "old benchmark", "historical", "pass 1", "pass 2",
    "pass 3", "pass 4", "pass 5", "pass 6", "pass 7", "pass 8", "pass 9",
    "pass 10", "pass 11", "pass 12", "pass 13", "pass 14", "pass 15",
    "pass 16", "pass 17", "pass 18", "pass 19", "pass 20", "pass 21",
    "before this", "at the time", "used by", "pr #", "session arena/",
    "independent live spot reading", "additive integration",
)

# NOTE: an earlier draft excluded any line containing the word "cross-check".
# That silently swallowed the real finding, because the legacy pages print the
# benchmark inside a ribbon whose label begins "CROSS-CHECK QUOTES ...":
#     CROSS-CHECK QUOTES · 2026-10-22 (benchmark: WGC $4,024.45/oz, 22 Oct)
# The cross-check quotes (Kitco / JM Bullion / BullionVault) are *different*
# numbers that are legitimately published as dated cross-checks. So the
# exclusion is by VALUE, taken from data, never by keyword.
CROSS_CHECK_KEYS = (
    "cross_check_quotes", "bullionvault", "kitco", "jm_bullion", "jmbullion",
)


def strip_tags(html: str) -> str:
    html = re.sub(r"<script\b.*?</script>", " ", html, flags=re.S | re.I)
    html = re.sub(r"<style\b.*?</style>", " ", html, flags=re.S | re.I)
    html = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"&[a-zA-Z#0-9]+;", " ", html)


def cross_check_values() -> set[float]:
    """Dated cross-check quotes (Kitco / JM Bullion / BullionVault) from data/**.

    These are legitimately published as *cross-checks*, so a page that prints
    them next to their own date and link is not claiming they are the
    benchmark. They are excluded by VALUE, never by keyword.

    Only genuinely cross-check contexts count: the `cross_check_*` blocks in
    data/gold_spot.json, and BullionVault / Kitco / JM Bullion entries in the
    source registry. The active benchmark and the superseded WGC readings are
    deliberately NOT in this set — they are what this script is looking for.
    """
    out: set[float] = set()

    def add(value) -> None:
        try:
            out.add(round(float(value), 2))
        except (TypeError, ValueError):
            pass

    spot_path = ROOT / "data" / "gold_spot.json"
    if spot_path.exists():
        spot = json.loads(spot_path.read_text(encoding="utf-8"))
        for key, value in spot.items():
            if not key.lower().startswith("cross_check"):
                continue
            if isinstance(value, list):
                for entry in value:
                    if isinstance(entry, dict):
                        add(entry.get("value_usd_per_oz"))
            elif isinstance(value, dict):
                add(value.get("value_usd_per_oz"))

    for name in ("sources.json", "standards_and_spot.json"):
        path = ROOT / "data" / name
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue

        def walk(node) -> None:
            if isinstance(node, dict):
                blob = json.dumps(node).lower()
                if any(k in blob for k in ("kitco", "jmbullion", "bullionvault")):
                    add(node.get("value_usd_per_oz"))
                    add(node.get("usd_per_troy_oz"))
                    add(node.get("usd_per_gram"))
                for child in node.values():
                    walk(child)
            elif isinstance(node, list):
                for child in node:
                    walk(child)

        walk(data)
    return out


def load_spot() -> tuple[dict, list[dict]]:
    data = json.loads((ROOT / "data" / "gold_spot.json").read_text(encoding="utf-8"))
    active = data.get("benchmark", {})
    prior = list(data.get("prior_captures") or [])
    # prior_captures entries are either flat readings or full benchmark blocks.
    superseded = []
    for entry in prior:
        if not isinstance(entry, dict):
            continue
        if entry.get("status") == "superseded" or "value_usd_per_oz" in entry:
            superseded.append(entry)
    return active, superseded


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", dest="json_out")
    ap.add_argument("--gate", action="store_true")
    args = ap.parse_args()

    active, superseded = load_spot()
    cross_checks = cross_check_values()
    active_val = active.get("value_usd_per_oz")
    active_date = active.get("price_date_as_shown_on_source")

    print("=" * 70)
    print("GOLD4 SUPERSEDED-BENCHMARK CHECK (session arena/2fa1c987-gold4)")
    print("=" * 70)
    print(f"ACTIVE benchmark in data/gold_spot.json : {active_val} USD/oz"
          f"  (source date: {active_date})")
    print("superseded readings still present in prior_captures:")
    for s in superseded:
        print(f"  - {s.get('value_usd_per_oz')} USD/oz"
              f"  ({s.get('price_date_as_shown_on_source')})"
              f"  status={s.get('status')}")
    print(f"dated cross-check quote values (excluded by value): "
          f"{sorted(cross_checks)}")
    print()

    findings: list[dict] = []
    files: list[Path] = []
    for pattern in SURFACES:
        files += sorted(ROOT.glob(pattern))
    files = [f for f in files if f.is_file() and ".git" not in f.parts]

    for path in files:
        raw = path.read_text(encoding="utf-8", errors="replace")
        text = strip_tags(raw) if path.suffix.lower() in (".html", ".htm") else raw
        lines = text.splitlines()
        for lineno, line in enumerate(lines, 1):
            for s in superseded:
                val = s.get("value_usd_per_oz")
                if val is None:
                    continue
                try:
                    if float(val) in cross_checks:
                        continue
                except (TypeError, ValueError):
                    pass
                # Match the number in its common printed forms.
                forms = {f"{val:,.2f}", f"{val:.2f}", f"{val:,}", f"{val}"}
                if not any(form in line for form in forms):
                    continue
                ctx = " ".join(lines[max(0, lineno - 2):lineno + 2])
                low = ctx.lower()
                if any(m in low for m in HISTORICAL_MARKER):
                    continue
                if not any(m in low for m in CURRENT_CLAIM):
                    continue
                findings.append({
                    "file": str(path.relative_to(ROOT)),
                    "line": lineno,
                    "superseded_value_usd_per_oz": val,
                    "superseded_source_date": s.get("price_date_as_shown_on_source"),
                    "active_benchmark_usd_per_oz": active_val,
                    "official_link_in_context": "https://" in ctx,
                    "context": re.sub(r"\s+", " ", ctx)[:300],
                })

    print(f"files scanned : {len(files)}")
    print(f"FINDINGS      : {len(findings)} superseded reading(s) presented as current")
    print()
    by_file: dict[str, list[dict]] = {}
    for f in findings:
        by_file.setdefault(f["file"], []).append(f)
    for fname in sorted(by_file):
        print(f"\n{fname}")
        for f in by_file[fname][:8]:
            link = "link" if f["official_link_in_context"] else "NO-LINK"
            print(f"  L{f['line']:<5} superseded {f['superseded_value_usd_per_oz']} USD/oz"
                  f"  vs active {f['active_benchmark_usd_per_oz']}  [{link}]")
            print(f"        {f['context'][:200]}")
        if len(by_file[fname]) > 8:
            print(f"  ... {len(by_file[fname]) - 8} more")

    if args.json_out:
        Path(args.json_out).write_text(json.dumps({
            "scanner": "scripts/session_2fa1c987/check_superseded.py",
            "session": "arena/2fa1c987-gold4",
            "active_benchmark_usd_per_oz": active_val,
            "active_source_date": active_date,
            "superseded": superseded,
            "files_scanned": [str(f.relative_to(ROOT)) for f in files],
            "findings": findings,
        }, indent=2), encoding="utf-8")
        print(f"\nJSON written: {args.json_out}")

    if args.gate and findings:
        print("\nGATE MODE: failing — a superseded reading is presented as current.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
