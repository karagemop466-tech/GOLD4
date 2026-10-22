#!/usr/bin/env python3
"""Offline safety checks: local links resolve and product table has no unsupported rows."""
from html.parser import HTMLParser
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []
        self.source_links = 0
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        href = attrs.get("href", "")
        if href:
            self.hrefs.append(href)
            if href.startswith("https://"):
                self.source_links += 1

errors = []
for filename in ("index.html", "flagged.html"):
    path = ROOT / filename
    if not path.exists():
        errors.append(f"Missing page: {filename}")
        continue
    text = path.read_text(encoding="utf-8")
    parser = Links()
    parser.feed(text)
    if parser.source_links < 1:
        errors.append(f"No HTTPS source link found in {filename}")
    for href in parser.hrefs:
        if href.startswith(("https://", "mailto:", "#")):
            continue
        target = href.split("#", 1)[0]
        if target and not (ROOT / target).exists():
            errors.append(f"Broken local link in {filename}: {href}")

index = (ROOT / "index.html").read_text(encoding="utf-8")
# The sole tbody row is the explicit empty state: reject accidental additions until
# each candidate has been reviewed against its own official source.
tbody = re.search(r"<tbody>(.*?)</tbody>", index, re.S)
if not tbody or "No verified products yet" not in tbody.group(1):
    errors.append("Product table is no longer the reviewed empty state; verify each row and source manually.")
if "NO HALLUCINATIONS" not in index or "no hallucinations" not in index.lower():
    errors.append("Front-page no-hallucination warning missing.")
if "consumer.ftc.gov/articles/buying-platinum-gold-and-silver-jewelry" not in index:
    errors.append("Primary FTC source link missing from dashboard.")
if errors:
    print("SITE SAFETY CHECK FAILED")
    print("\n".join(f"- {error}" for error in errors))
    sys.exit(1)
print("PASS: local links resolve; source links exist; product table remains explicitly empty; no-hallucination warning and FTC reference present.")
print("REVIEW LIMIT: this offline check does not establish source availability, product authenticity, or live gold prices.")
