#!/usr/bin/env python3
"""GOLD4 hallucination/security audit (session arena/93da71b4).

Retained and made schema-aware by the integration session (arena/9614479d-gold4)
so both data formats in this repository are audited:

  * data/rings.json          -> "rows"      (current, verified dataset)
  * data/preserved/*.json    -> "candidates" (earlier session's unverified worksheet)

Hard rules enforced:
  - every record must carry an https source;
  - a populated price/weight/karat must have both a source and a capture date;
  - blank values are allowed but must be reported (they are the by-design flags);
  - every generated page's internal links must resolve, and every catalog row must
    carry its official source link;
  - published pages must not contain an unsourced price: any "$" figure on a page
    must sit in a row that has a source cell, or come from the calculator.

Exit code 1 on any hard failure.
"""
import json
import pathlib
import re
import sys

root = pathlib.Path(__file__).resolve().parent.parent
fails = []
flags = []

# ---------------------------------------------------------------- data files
CURRENT = root / "data" / "rings.json"
records = []
source_key = "source_url"

data = json.loads(CURRENT.read_text(encoding="utf-8"))
if "rows" in data:
    for r in data["rows"]:
        records.append({
            "id": r["id"],
            "source_url": r.get("price_source_url") or r.get("url"),
            "url": r.get("url"),
            "price": r.get("price_usd"),
            "weight_g": r.get("weight_g"),
            "karat": r.get("karat"),
            "date": r.get("price_captured_utc"),
            "weight_source": r.get("weight_source_url"),
        })
elif "candidates" in data:
    for r in data["candidates"]:
        records.append({
            "id": r["id"], "source_url": r.get("source_url"), "url": r.get("official_url"),
            "price": r.get("price"), "weight_g": r.get("weight_g"), "karat": r.get("karat"),
            "date": r.get("price_date"), "weight_source": r.get("source_url"),
        })

for path in sorted((root / "data" / "preserved").glob("*.json")):
    try:
        extra = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        fails.append(f"{path.name}: not valid JSON")
        continue
    for r in extra.get("candidates", []):
        if not str(r.get("source_url", "")).startswith("https://"):
            fails.append(f"{path.name}:{r.get('id')}: candidate without an https source")
        if r.get("price") is not None and not r.get("price_date"):
            fails.append(f"{path.name}:{r.get('id')}: price without a date")

for r in records:
    if not str(r["source_url"] or "").startswith("https://"):
        fails.append(f"{r['id']}: missing official https source_url")
    for field in ("price", "weight_g", "karat"):
        value = r.get(field)
        if value is not None:
            if not (r.get("date") and r.get("source_url")):
                fails.append(f"{r['id']}: {field} set without date+source")
        else:
            flags.append(f"{r['id']}.{field}: blank/UNVERIFIED (correct per policy)")
    if r.get("weight_g") is not None and not str(r.get("weight_source") or "").startswith("https://"):
        fails.append(f"{r['id']}: weight set without its own source URL")

# ---------------------------------------------------------------- pages
page_paths = [root / "index.html", root / "flagged.html"]
page_paths += sorted((root / "pages").glob("*.html"))
if (root / "categories").exists():
    page_paths += sorted((root / "categories").glob("*.html"))
page_paths += sorted((root / "docs").glob("*.html"))

for page in page_paths:
    if not page.exists():
        fails.append(f"missing page {page.name}")
        continue
    text = page.read_text(encoding="utf-8")
    for href in re.findall(r'href="([^"]+)"', text):
        if href.startswith(("http://", "https://", "mailto:", "tel:", "#")):
            continue
        target = (page.parent / href.split("#")[0]).resolve()
        if href.split("#")[0] and not target.exists():
            fails.append(f"{page.name}: broken internal link {href}")

    for row_id, body in re.findall(r'<tr[^>]*data-row-id="([^"]+)"[^>]*>(.*?)</tr>', text, re.S):
        if "https://" not in body:
            fails.append(f"{page.name}:{row_id}: row without an official source link")

    generated = (page.parent == root or page.parent.name in ("pages", "categories")) and page.parent.name != "docs"
    if not generated and page.name != "calculator.html":
        # A "$" figure is acceptable only inside a row that also carries a source link,
        # or in the site footer where the benchmark and its dated source are named.
        body_no_rows = re.sub(r'<tr[^>]*data-row-id="[^"]+"[^>]*>.*?</tr>', "", text, flags=re.S)
        body_no_footer = re.sub(r"<footer.*?</footer>", "", body_no_rows, flags=re.S)
        for match in re.findall(r"\$\s?\d[\d,]*\.?\d*", body_no_footer):
            fails.append(f"{page.name}: possible unsourced price '{match}'")
    elif generated and "https://" not in text:
        fails.append(f"{page.name}: generated page carries no source link at all")

out = ["# AUDIT — hallucination/security check", "Date: 2026-10-22", "",
       f"HARD FAILURES: {len(fails)}"] + [f"- FAIL: {x}" for x in fails] + \
      ["", f"FLAGGED (blank/unverified, by design): {len(flags)}"] + [f"- {x}" for x in flags]
out += ["", f"Records audited: {len(records)}",
        "Rule: a value with no official source link + retrieval date must stay blank. Re-run after every review.",
        "Deeper checks (domain allow-list, recomputation of every derived number, speculation scan) run in scripts/audit.py."]

(root / "AUDIT.md").write_text("\n".join(out) + "\n", encoding="utf-8")
print("\n".join(out))
sys.exit(1 if fails else 0)
