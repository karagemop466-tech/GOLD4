#!/usr/bin/env python3
"""GOLD4 hallucination/security audit. Run after EVERY review. Exit 1 on hard failures."""
import json,re,sys,pathlib
root=pathlib.Path(__file__).resolve().parent.parent; flags=[]; fails=[]
data=json.loads((root/'data/rings.json').read_text())
for r in data['candidates']:
    if not r.get('source_url','').startswith('https://'): fails.append(f"{r['id']}: missing official source_url")
    for f in ('price','weight_g','karat'):
        if r.get(f) is not None:
            if not (r.get('price_date') and r.get('source_url')): fails.append(f"{r['id']}: {f} set without date+source")
        else: flags.append(f"{r['id']}.{f}: blank/UNVERIFIED (correct per policy)")
# scan published HTML for price-like numbers outside calculator example
for html in (root/'docs').glob('*.html'):
    t=html.read_text()
    for href in re.findall(r'href="([^"#]+)"',t):
        if not href.startswith(('http','mailto')) and not (root/'docs'/href).exists(): fails.append(f"{html.name}: broken internal link {href}")
    if html.name!='calculator.html':
        for m in re.findall(r'\$\s?\d[\d,]*\.?\d*',t): fails.append(f"{html.name}: possible unsourced price '{m}'")
out=["# AUDIT — hallucination/security check","Date: 2026-10-22","",f"HARD FAILURES: {len(fails)}"]+[f"- FAIL: {x}" for x in fails]+["",f"FLAGGED (blank/unverified, by design): {len(flags)}"]+[f"- {x}" for x in flags]+["","Rule: a value with no official source link + retrieval date must stay blank. Re-run after every review."]
(root/'AUDIT.md').write_text("\n".join(out)+"\n"); print("\n".join(out)); sys.exit(1 if fails else 0)
