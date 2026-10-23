#!/usr/bin/env python3
"""check_links.py — local link/asset integrity for the built site.
Parses every .html in the repo root and pages/, resolves local href/src targets,
and fails if any local file is missing. External links are listed for manual review
(they cannot be fetched from the sandbox network)."""
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parent.parent
HTML_FILES = [ROOT / "index.html"] + sorted((ROOT / "pages").glob("*.html"))

ATTR_RE = re.compile(r'(?:href|src)="([^"]+)"')

broken, external, checked = [], set(), 0
for f in HTML_FILES:
    text = f.read_text()
    for m in ATTR_RE.finditer(text):
        url = unquote(m.group(1)).strip()
        if not url or url.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        checked += 1
        parts = urlsplit(url)
        if parts.netloc:
            external.add(f"{parts.scheme}://{parts.netloc}{parts.path}")
            continue
        target = (f.parent / parts.path).resolve()
        if not target.exists():
            broken.append(f"{f.relative_to(ROOT)}: missing local target {url}")

print(f"check_links: files={len(HTML_FILES)} links={checked} external_unique={len(external)}")
for b in broken:
    print("  BROKEN:", b)
print("External domains referenced (manual review list):")
for u in sorted(external):
    print("  ", u)
if broken:
    sys.exit(1)
print("check_links: PASS — no broken local links")
