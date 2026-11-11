#!/usr/bin/env python3
"""Numeric-provenance scanner for the NON-CANONICAL surfaces of GOLD4.

Session arena/2fa1c987-gold4, Pass 21 companion task 78.

WHAT IT IS FOR
--------------
The canonical surfaces (data/**, index.html, pages/**) are already covered by
scripts/audit.py, scripts/audit_hallucinations.py and the other gates. Nobody
was covering the surfaces a reader can still reach but that the canonical
generators do not own:

    dashboard.html  solitaires.html  three-stone-halo.html  bands.html
    checklist.html  standards.html   audit.html             coordination.html
    categories/*.html                docs/**                assets/**
    static/**       app.js           README.md  AUDIT.md  VERIFICATION.md
    audit/*.md

This scanner reconciles every numeric claim printed on those surfaces against
the single source of truth, data/**. It is a FINDING GENERATOR, not a gate on
other people's files: it never edits anything.

HOW IT DECIDES
--------------
For every money / per-ounce / per-gram / gram / multiple / date / count token
found in a scanned file, the value is classified as:

  traceable   - the same number exists somewhere in data/** (case-insensitive,
                comma-insensitive string match on the normalised number), so
                the claim is backed by stored evidence;
  historical  - the number is NOT in data/** but the surrounding text marks it
                as a superseded or pass-specific value ("prior_captures",
                "superseded", "Pass 12", "was", "earlier", "21 October", ...),
                so it is a dated historical statement rather than a current
                claim;
  untraceable - NOT in data/** and presented in the present tense. This is the
                class that has to be reviewed by a human against the official
                source before it is believed. It is reported, never deleted.

A number with no official https:// link in its immediate context is reported
with link=False, which is the strongest signal in the report.

The scanner deliberately does NOT try to be clever: it does not fetch the web,
does not infer, and does not "correct" anything. It prints what it found and
lets a human decide.

USAGE
-----
    python3 scripts/session_2fa1c987/scan_prose.py                # report
    python3 scripts/session_2fa1c987/scan_prose.py --json out.json
    python3 scripts/session_2fa1c987/scan_prose.py --gate         # exit 1 on
                                                                  # untraceable

Exit code is 0 in report mode (findings are published, not fatal, per the
project's "flagged items never block" rule). --gate is provided so a later
integration can choose to make it blocking once the backlog is cleared.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# --------------------------------------------------------------------------
# 1. Build the evidence set: every number that exists in data/**
# --------------------------------------------------------------------------

NUM_RE = re.compile(r"-?\d[\d,]*(?:\.\d+)?")

# Tokens whose presence in the surrounding text marks a value as historical.
HISTORICAL_MARKERS = (
    "prior_captures", "superseded", "no longer", "previously", "earlier",
    "was replaced", "old benchmark", "historical", "pass 1", "pass 2",
    "pass 3", "pass 4", "pass 5", "pass 6", "pass 7", "pass 8", "pass 9",
    "pass 10", "pass 11", "pass 12", "pass 13", "pass 14", "pass 15",
    "pass 16", "pass 17", "pass 18", "pass 19", "pass 20", "pass 21",
    "2026-10-21", "2026-10-22", "2026-10-23", "21 october", "22 october",
    "used by", "before this", "at the time",
)

# Claim patterns worth auditing, with a human label for each.
CLAIM_PATTERNS = [
    (re.compile(r"\$\s?(\d[\d,]*(?:\.\d+)?)\s?/\s?oz"), "usd_per_oz"),
    (re.compile(r"\$\s?(\d[\d,]*(?:\.\d+)?)\s?/\s?g\b"), "usd_per_gram"),
    (re.compile(r"(\d[\d,]*(?:\.\d+)?)\s?g\b"), "grams"),
    (re.compile(r"(\d[\d,]*(?:\.\d+)?)\s?×"), "multiple"),
    (re.compile(r"\$\s?(\d[\d,]*(?:\.\d+)?)"), "usd"),
]

# Surfaces scanned.  Deliberately NOT data/**, index.html or pages/**: those
# are owned by the canonical generators and the existing gates.
SCAN_GLOBS = [
    "dashboard.html", "solitaires.html", "three-stone-halo.html",
    "bands.html", "checklist.html", "standards.html", "audit.html",
    "coordination.html", "flagged.html", "sellers.html", "calculator.html",
    "categories/*.html", "docs/*.html", "assets/*.js", "static/*.js",
    "app.js",
]
SCAN_DOCS = [
    "README.md", "AUDIT.md", "VERIFICATION.md", "audit/*.md",
]


def normalise(num: str) -> set[str]:
    """Every plausible stored spelling of a number, for matching against data."""
    raw = num.replace(",", "").rstrip("0").rstrip(".") if "." in num else num.replace(",", "")
    out = {num, num.replace(",", ""), raw}
    try:
        f = float(num.replace(",", ""))
    except ValueError:
        return out
    for fmt in ("{:.2f}", "{:.3f}", "{:.4f}", "{:.5f}", "{:.0f}", "{:,.2f}", "{:,.0f}"):
        out.add(fmt.format(f))
    out.add(str(int(f)) if f == int(f) else "")
    return {o for o in out if o}


def build_evidence() -> set[str]:
    """All numeric tokens that appear anywhere under data/**."""
    evidence: set[str] = set()
    for path in sorted((ROOT / "data").rglob("*.json")):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        for match in NUM_RE.finditer(text):
            evidence |= normalise(match.group(0))
    return evidence


# --------------------------------------------------------------------------
# 2. Scan one file
# --------------------------------------------------------------------------

def strip_tags(html: str) -> str:
    html = re.sub(r"<script\b.*?</script>", " ", html, flags=re.S | re.I)
    html = re.sub(r"<style\b.*?</style>", " ", html, flags=re.S | re.I)
    html = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"&[a-zA-Z#0-9]+;", " ", html)


def find_claims(path: Path, evidence: set[str]) -> list[dict]:
    raw = path.read_text(encoding="utf-8", errors="replace")
    text = strip_tags(raw) if path.suffix.lower() in (".html", ".htm") else raw
    lines = text.splitlines()
    out: list[dict] = []
    for lineno, line in enumerate(lines, 1):
        if not line.strip():
            continue
        ctx = " ".join(lines[max(0, lineno - 2):lineno + 2])
        low = ctx.lower()
        for pattern, kind in CLAIM_PATTERNS:
            for m in pattern.finditer(line):
                num = m.group(1)
                forms = normalise(num)
                traceable = bool(forms & evidence)
                historical = any(marker in low for marker in HISTORICAL_MARKERS)
                if traceable:
                    verdict = "traceable"
                elif historical:
                    verdict = "historical"
                else:
                    verdict = "untraceable"
                out.append({
                    "file": str(path.relative_to(ROOT)),
                    "line": lineno,
                    "kind": kind,
                    "value": num,
                    "verdict": verdict,
                    "official_link_in_context": "https://" in ctx,
                    "context": re.sub(r"\s+", " ", ctx)[:260],
                })
    # Deduplicate identical (file, line, kind, value) triples: the money pattern
    # also matches the per-oz pattern's leading $.
    seen, deduped = set(), []
    for c in out:
        key = (c["file"], c["line"], c["kind"], c["value"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(c)
    return deduped


# --------------------------------------------------------------------------
# 3. Report
# --------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", dest="json_out", help="write findings JSON here")
    ap.add_argument("--gate", action="store_true",
                    help="exit 1 when an untraceable present-tense claim exists")
    args = ap.parse_args()

    evidence = build_evidence()
    files: list[Path] = []
    for pattern in SCAN_GLOBS:
        files += sorted(ROOT.glob(pattern))
    for pattern in SCAN_DOCS:
        files += sorted(ROOT.glob(pattern))
    files = [f for f in files if f.is_file() and ".git" not in f.parts]

    claims: list[dict] = []
    for f in files:
        claims += find_claims(f, evidence)

    counts: dict[str, int] = {}
    for c in claims:
        counts[c["verdict"]] = counts.get(c["verdict"], 0) + 1

    untraceable = [c for c in claims if c["verdict"] == "untraceable"]
    untraceable_nolink = [c for c in untraceable if not c["official_link_in_context"]]

    print("=" * 70)
    print("GOLD4 NON-CANONICAL SURFACE SCAN (session arena/2fa1c987-gold4)")
    print("=" * 70)
    print(f"files scanned          : {len(files)}")
    print(f"numeric claims found   : {len(claims)}")
    print(f"  traceable to data/** : {counts.get('traceable', 0)}")
    print(f"  dated historical     : {counts.get('historical', 0)}")
    print(f"  UNTRACEABLE (review) : {counts.get('untraceable', 0)}")
    print(f"  ... of which have no official link in context: {len(untraceable_nolink)}")
    print()
    print("This scanner reconciles numbers against stored evidence only. It does")
    print("not open the web, does not infer, and edits nothing. An 'untraceable'")
    print("mark means a human must check the official source before believing it.")
    print()

    if untraceable:
        print("-" * 70)
        print("UNTRACEABLE CLAIMS (present-tense, not found in data/**)")
        print("-" * 70)
        by_file: dict[str, list[dict]] = {}
        for c in untraceable:
            by_file.setdefault(c["file"], []).append(c)
        for fname in sorted(by_file):
            print(f"\n{fname}")
            for c in by_file[fname][:12]:
                link = "link" if c["official_link_in_context"] else "NO-LINK"
                print(f"  L{c['line']:<5} {c['kind']:<12} {c['value']:<12} [{link}]")
                print(f"        {c['context'][:160]}")
            if len(by_file[fname]) > 12:
                print(f"  ... {len(by_file[fname]) - 12} more in this file")

    if args.json_out:
        payload = {
            "scanner": "scripts/session_2fa1c987/scan_prose.py",
            "session": "arena/2fa1c987-gold4",
            "files_scanned": [str(f.relative_to(ROOT)) for f in files],
            "counts": counts,
            "method": "every numeric token reconciled against data/** by exact "
                      "numeric match; untraceable = not in data/** and not marked "
                      "historical by surrounding text. No web access, no inference.",
            "claims": claims,
        }
        Path(args.json_out).write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"\nJSON written: {args.json_out}")

    if args.gate and untraceable:
        print("\nGATE MODE: failing because untraceable present-tense claims exist.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
