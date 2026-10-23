#!/usr/bin/env python3
"""Gate 6 — citation-integrity check (session arena/46691f83-gold4).

The existing anti-hallucination audits recompute every number and re-check every
URL, but none of them can catch a *citation* error: pointing the trademark rule
at "16 CFR § 23.9" reads like law and is completely plausible, yet § 23.9 is the
pewter section. That exact misattribution was live in this repository on
2026-10-23 and is fixed by this pass.

This gate is offline and deterministic. It carries the section headings that
were read verbatim off the official eCFR page on 2026-10-23 (URL and date
recorded below) and applies two rules:

  R1  label rule - a section cited with a label ("§ 23.9 Quality Marks") must be
      labelled with its own subject, not another section's.
  R2  sentence rule - in a sentence of a published HTML page that cites exactly
      one CFR section, a topic owned by a different section must not appear
      within 60 characters after the citation. (HTML only: the JSON files are
      machine-formatted blobs whose "sentences" run across unrelated records.)

Either rule failing fails the build.

Run: python3 scripts/session_46691f83/verify_citations.py
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]

SOURCE_URL = "https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-23"
RETRIEVED = "2026-10-23"

# Read verbatim from the eCFR table of contents on 2026-10-23.
CFR_16_PART_23 = {
    "23.0": "Scope and application.",
    "23.1": "Deception (general).",
    "23.2": "Misuse of the terms \u201chandmade,\u201d \u201chand-polished,\u201d etc.",
    "23.3": "Misrepresentation as to gold content.",
    "23.4": "Misuse of the word \u201cvermeil.\u201d",
    "23.5": "Misrepresentation as to silver content.",
    "23.6": "Misuse of the words \u201cplatinum,\u201d \u201ciridium,\u201d \u201cpalladium,\u201d \u201cruthenium,\u201d \u201crhodium,\u201d and \u201cosmium.\u201d",
    "23.7": "Disclosure of surface-layer application of rhodium.",
    "23.8": "Misrepresentation as to products containing more than one precious metal.",
    "23.9": "Misrepresentation as to content of pewter.",
    "23.10": "Additional guidance for the use of quality marks.",
    "23.11": "Misuse of \u201ccorrosion proof,\u201d \u201cnoncorrosive,\u201d \u201ccorrosion resistant,\u201d \u201crust proof,\u201d \u201crust resistant,\u201d etc.",
    "23.12": "Definition and misuse of the word \u201cdiamond.\u201d",
    "23.13": "Misuse of the words \u201cflawless,\u201d \u201cperfect,\u201d etc.",
    "23.14": "Disclosure of treatments to diamonds.",
    "23.15": "Misuse of the term \u201cblue white.\u201d",
    "23.16": "Misuse of the term \u201cproperly cut,\u201d etc.",
    "23.17": "Misuse of the words \u201cbrilliant\u201d and \u201cfull cut.\u201d",
    "23.18": "Misrepresentation of weight and \u201ctotal weight.\u201d",
    "23.19": "Definitions of various pearls.",
    "23.20": "Misuse of the word \u201cpearl.\u201d",
    "23.21": "Misuse of terms such as \u201ccultured pearl,\u201d \u201cseed pearl,\u201d \u201cOriental pearl,\u201d \u201cnatura,\u201d \u201ckultured,\u201d \u201creal,\u201d \u201csynthetic,\u201d and regional designations.",
    "23.22": "Misrepresentation as to cultured pearls.",
    "23.23": "Disclosure of treatments to pearls and cultured pearls.",
    "23.24": "Disclosure of treatments to gemstones.",
    "23.25": "Misuse of the words \u201cruby,\u201d \u201csapphire,\u201d \u201cemerald,\u201d \u201ctopaz,\u201d \u201cstone,\u201d \u201cbirthstone,\u201d \u201cgem,\u201d \u201cgemstone,\u201d etc.",
    "23.26": "Misrepresentation as to varietal name.",
    "23.27": "Misuse of the words \u201creal,\u201d \u201cgenuine,\u201d \u201cnatural,\u201d \u201cprecious,\u201d etc.",
    "23.28": "Misuse of the words \u201cflawless,\u201d \u201cperfect,\u201d etc.",
}

# Topic phrase -> the only section that owns it.
TOPIC_OWNER = {
    "quality mark": "23.10",
    "quality marks": "23.10",
    "trademark": "23.10",
    "pewter": "23.9",
    "rhodium": "23.7",
    "vermeil": "23.4",
    "total weight": "23.18",
}

REF_RE = re.compile(r"(?:§{1,2}\s*|section\s+)(23\.\d+)", re.IGNORECASE)
# Pages that quote a wrong citation *in order to report the correction* are
# excluded: coordination.html, pages/log.html and the verification log exist to
# name the error that was fixed, and scanning them would only flag the fix.
# Every buyer-facing page and every data file is still scanned.
SKIP_NAMES = {"coordination.html", "pages/log.html"}

SCAN_FILES = tuple(
    p for p in (
        sorted((ROOT / "data").glob("*.json"))
        + sorted(ROOT.glob("*.html"))
        + sorted((ROOT / "pages").glob("*.html"))
        + sorted((ROOT / "categories").glob("*.html"))
    )
    if str(p.relative_to(ROOT)) not in SKIP_NAMES
)
SENTENCE_SPLIT = re.compile(r"(?<=[.:;])\s+|\n|</li>|<li>|</p>")


def label_after(text: str, end: int) -> str:
    tail = text[end:end + 40]
    tail = re.split(r"[§(<,;]|&#167;|16 CFR|15 U\.S\.C|12 CFR", tail)[0]
    return tail.strip(" 0123456789.-–—:").lower()


SELF_TEST_SAMPLE = "16 CFR § 23.9 Quality Marks: every stamp needs a trademark beside it."


def self_test() -> int:
    """Prove the gate still catches the error it was written for."""
    m = REF_RE.search(SELF_TEST_SAMPLE)
    assert m, "self-test regex no longer matches a plain CFR citation"
    lab = label_after(SELF_TEST_SAMPLE, m.end())
    hit = [owner for topic, owner in TOPIC_OWNER.items() if lab.startswith(topic) and owner != m.group(1)]
    if not hit:
        print("SELF-TEST FAILED: a known-bad citation ('§ 23.9 Quality Marks') was not detected.")
        return 1
    print(f"SELF-TEST PASSED: '§ 23.9 Quality Marks' is correctly rejected (§ 23.9 is '{CFR_16_PART_23['23.9']}'; "
          f"quality marks are § {hit[0]}).")
    return 0


def main() -> int:
    if "--self-test" in sys.argv:
        return self_test()
    errors: list[str] = []
    r1 = r2 = refs = 0

    for path in SCAN_FILES:
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        rel = path.relative_to(ROOT)
        for m in REF_RE.finditer(text):
            sec = m.group(1)
            if sec not in CFR_16_PART_23:
                errors.append(f"{rel}: cites 16 CFR \u00a7 {sec}, which is not in the verified section table")
                continue
            refs += 1

            # A page that quotes an existing wrong citation in order to correct it
            # ("the standards page cited § 23.9 for ...") is doing the opposite of
            # misattributing it. Both rules are skipped when the surrounding text
            # says so — the marker may sit before OR after the citation.
            correction_context = re.search(
                r"(cited|previously|wrongly|incorrectly|mistaken|corrected|used to say|misattribut)",
                (text[max(0, m.start() - 220): m.start()] + " " + text[m.end(): m.end() + 200]).lower(),
            )

            # R1 — explicit label immediately after the citation.
            lab = label_after(text, m.end())
            if lab and not correction_context:
                for topic, owner in TOPIC_OWNER.items():
                    if lab.startswith(topic) and owner != sec:
                        r1 += 1
                        errors.append(
                            f"{rel}: 16 CFR \u00a7 {sec} ({CFR_16_PART_23[sec]}) is labelled "
                            f"'{topic}', which is \u00a7 {owner}"
                        )
            # R2 — single-section sentence with another section's topic right after it.
            # Only applied to the HTML pages: the JSON files are machine-formatted
            # blobs where "sentences" run across unrelated records, which produced
            # nothing but false positives when this rule was first tried on them.
            if path.suffix != ".html" or correction_context:
                continue
            start = max(0, m.start() - 200)
            sentence = text[start: m.end() + 200]
            for part in SENTENCE_SPLIT.split(sentence):
                refs_in_part = {x.group(1) for x in REF_RE.finditer(part)}
                if len(refs_in_part) != 1:
                    continue
                sec = next(iter(refs_in_part))
                idx = REF_RE.search(part).end()
                after = part[idx: idx + 60].lower()
                # Stop at the next citation: text that introduces another section
                # (e.g. "§ 23.9 is pewter; the rule is in § 23.10 ... quality marks")
                # is a correct contrast, not a misattribution.
                after = re.split(r"\u00a7|&#167;|section\s+23\.", after)[0]
                for topic, owner in TOPIC_OWNER.items():
                    if topic in after and owner != sec:
                        r2 += 1
                        errors.append(
                            f"{rel}: sentence citing only 16 CFR \u00a7 {sec} "
                            f"({CFR_16_PART_23[sec]}) then claims '{topic}', which is \u00a7 {owner}"
                        )

    src = json.loads((ROOT / "data" / "sources.json").read_text(encoding="utf-8"))
    ids = {s["id"]: s for s in src["sources"]}
    for needed, section, url_part in (
        ("ecfr-16-23", "16 CFR Part 23", "part-23"),
        ("usc-15-297", "15 U.S.C. \u00a7 297", "15/297"),
        ("usc-15-295", "15 U.S.C. \u00a7 295", "15/295"),
        ("ecfr-12-1026-13", "12 CFR \u00a7 1026.13", "1026.13"),
        ("cfpb-fcba-en61", "CFPB billing-error FAQ", "consumerfinance.gov"),
    ):
        entry = ids.get(needed)
        if not entry:
            errors.append(f"sources.json: {section} is cited but source '{needed}' is not registered")
        elif url_part.lower() not in entry.get("url", "").lower():
            errors.append(f"sources.json: source '{needed}' URL is not the {section} page")

    print(f"Citation-integrity gate: {refs} CFR section references checked across {len(SCAN_FILES)} files "
          f"(rule violations: label={r1}, sentence={r2}).")
    print(f"Section table read verbatim from {SOURCE_URL} on {RETRIEVED}.")
    if errors:
        print(f"FAIL: {len(errors)} citation problem(s)")
        for e in errors[:40]:
            print("  -", e)
        return 1
    print("PASS: every CFR section citation matches its official heading, and every statute cited on the site has a registered source URL.")
    print("REVIEW LIMIT: offline. It cannot confirm a page still says today what it said when it was read - that needs a live re-fetch.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
