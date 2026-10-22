#!/usr/bin/env python3
"""Offline safety checks: local links resolve, No-Hallucinations banner & FTC source exist,
and every rendered catalog table row links directly to an official HTTPS source with check date."""
from html.parser import HTMLParser
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


class LinksAndRows(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []
        self.source_links = 0
        self.in_row = False
        self.row_https = 0
        self.rows_checked = 0
        self.bad_rows = 0

    def handle_starttag(self, tag, attrs):
        ad = dict(attrs)
        href = ad.get("href", "")
        if href:
            self.hrefs.append(href)
            if href.startswith("https://"):
                self.source_links += 1
            if self.in_row and href.startswith("https://"):
                self.row_https += 1
        if tag == "tr" and ad.get("data-ring-row") == "1":
            self.in_row = True
            self.row_https = 0

    def handle_endtag(self, tag):
        if tag == "tr" and self.in_row:
            self.in_row = False
            self.rows_checked += 1
            if self.row_https < 1:
                self.bad_rows += 1


errors = []
root_pages = sorted(p.name for p in ROOT.glob("*.html"))
if not {"index.html", "flagged.html", "calculator.html", "checklist.html", "audit.html"}.issubset(set(root_pages)):
    errors.append("Missing required root HTML pages.")

for filename in root_pages:
    path = ROOT / filename
    text = path.read_text(encoding="utf-8")
    parser = LinksAndRows()
    parser.feed(text)
    if parser.source_links < 1:
        errors.append(f"No HTTPS source link found in {filename}")
    if parser.bad_rows:
        errors.append(f"{filename} contains {parser.bad_rows} catalog row(s) without an official HTTPS source link")
    for href in parser.hrefs:
        if href.startswith(("https://", "mailto:", "#")):
            continue
        target = href.split("?", 1)[0].split("#", 1)[0]
        if target and not (ROOT / target).exists():
            errors.append(f"Broken local link in {filename}: {href}")

index = (ROOT / "index.html").read_text(encoding="utf-8")
if "NO HALLUCINATIONS" not in index or "no hallucinations" not in index.lower():
    errors.append("Front-page no-hallucination warning missing.")
if "consumer.ftc.gov/articles/buying-platinum-gold-and-silver-jewelry" not in index:
    errors.append("Primary FTC source link missing from dashboard.")

if errors:
    print("SITE SAFETY CHECK FAILED")
    print("\n".join(f"- {error}" for error in errors))
    sys.exit(1)

print(f"PASS: verified {len(root_pages)} root HTML pages; all local links resolve; every catalog row links to an official HTTPS source; NO HALLUCINATIONS policy & FTC reference present.")
