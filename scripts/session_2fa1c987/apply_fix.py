#!/usr/bin/env python3
"""One-shot documented correction for scripts/generate_site.py.

Session arena/2fa1c987-gold4, Pass 21 companion task 77/80.

WHAT IT CHANGES AND WHY
-----------------------
`scripts/generate_site.py` writes eight published pages (dashboard, solitaires,
three-stone-halo, bands, checklist, standards, audit, coordination). Three
facts on those pages were HARDCODED and had drifted away from the single source
of truth:

  1. the spot ribbon printed
         "CROSS-CHECK QUOTES · 2026-10-22 (benchmark: WGC $4,024.45/oz, 22 Oct)"
     but data/gold_spot.json -> prior_captures marks $4,024.45 status=superseded
     and the ACTIVE benchmark is $3,996.31/oz. A reader was shown a superseded
     benchmark as the benchmark.
  2. the ribbon claimed "5 Automated Audit Gates Passing" while
     .github/workflows/pages.yml runs nine gates / twelve command invocations.
  3. the "Zero Invented Data" bullet asserted the benchmark driving every
     derived value is "$4,024.45/oz read on 2026-10-23" — again superseded.
  (plus: the hero called a 2026-10-22 quote "live", and the melt calculator
   rendered pre-filled placeholder numbers in the result panel with no label
   saying they were an example.)

This script replaces each hardcoded value with the same value READ FROM
data/gold_spot.json (or counted from .github/workflows/pages.yml), so the next
benchmark move can never silently desynchronise these pages again. It changes
NO number in data/**, and it does not touch any price, weight, karat or URL.

It is idempotent: running it twice leaves the file unchanged (each replacement
is guarded by a check for the original string).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GEN = ROOT / "scripts" / "generate_site.py"


# --------------------------------------------------------------------------
# helpers that will live inside generate_site.py
# --------------------------------------------------------------------------
HELPERS = '''
# ---------------------------------------------------------------------------
# Live facts read from data/** at build time (session arena/2fa1c987-gold4).
#
# These were hardcoded here until 2026-11-11, and drifted: the ribbon presented
# a SUPERSEDED WGC reading as the benchmark while data/gold_spot.json had
# already moved on. Everything below is now derived, so a future benchmark move
# cannot desynchronise these pages again.
# ---------------------------------------------------------------------------

def load_spot_facts() -> dict:
    """Benchmark + dated cross-check quotes, straight from data/gold_spot.json."""
    spot = json.loads((ROOT / "data" / "gold_spot.json").read_text(encoding="utf-8"))
    bench = spot["benchmark"]
    consts = spot.get("constants", {})
    per_g = consts.get("spot_usd_per_gram")
    if per_g is None:
        per_g = bench["value_usd_per_oz"] / consts.get("troy_ounce_grams", 31.1034768)
    quotes = {}
    for key, value in spot.items():
        if key.lower().startswith("cross_check") and isinstance(value, list):
            for entry in value:
                if not isinstance(entry, dict):
                    continue
                name = str(entry.get("publisher", "")).lower()
                if "kitco" in name:
                    quotes.setdefault("kitco", entry)
                elif "jm bullion" in name or "jmbullion" in name:
                    quotes.setdefault("jmbullion", entry)
    return {
        "benchmark_oz": bench["value_usd_per_oz"],
        "benchmark_per_g": per_g,
        "benchmark_date": bench.get("price_date_as_shown_on_source", ""),
        "benchmark_retrieved": bench.get("retrieved_utc", ""),
        "benchmark_url": bench.get("source_url", "https://www.gold.org/goldhub/data/gold-prices"),
        "kitco": quotes.get("kitco", {}),
        "jmbullion": quotes.get("jmbullion", {}),
    }


def gate_counts() -> tuple[int, int]:
    """Count the CI gates and command invocations in .github/workflows/pages.yml.

    Returns (distinct_gate_numbers, command_invocations). Derived rather than
    hardcoded so the ribbon cannot drift from the pipeline again.
    """
    workflow = ROOT / ".github" / "workflows" / "pages.yml"
    if not workflow.exists():
        return 0, 0
    gates: set[int] = set()
    invocations = 0
    in_gate_step = False
    in_run_block = False
    for raw in workflow.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("- name:"):
            name = line[len("- name:"):].strip()
            m = re.match(r"Gate (\d+)", name)
            in_gate_step = bool(m)
            in_run_block = False
            if m:
                gates.add(int(m.group(1)))
            continue
        if in_gate_step and line.startswith("run:"):
            rest = line[len("run:"):].strip()
            if rest and rest != "|":
                invocations += 1
                in_run_block = False
            else:
                in_run_block = True
            continue
        if in_run_block:
            if line.startswith(("- name:", "- uses:", "- if:")):
                in_run_block = False
                continue
            if line and not line.startswith("#"):
                invocations += 1
    return len(gates), invocations

'''


def apply() -> int:
    src = GEN.read_text(encoding="utf-8")
    original = src
    changes: list[str] = []

    # 1. insert the helpers after the esc() helper
    anchor = '''def esc(val: object) -> str:
    return html.escape(str(val), quote=True)
'''
    if "def load_spot_facts()" not in src:
        assert anchor in src, "esc() anchor not found"
        src = src.replace(anchor, anchor + HELPERS, 1)
        changes.append("inserted load_spot_facts() + gate_counts() helpers")

    # 2. render_shell: derive the ribbon facts
    anchor = '''def render_shell(active_href: str, title: str, description: str, body_html: str, catalog: dict) -> str:
    counts = catalog["counts"] if "counts" in catalog else catalog["meta"]["counts"]'''
    new = '''def render_shell(active_href: str, title: str, description: str, body_html: str, catalog: dict) -> str:
    counts = catalog["counts"] if "counts" in catalog else catalog["meta"]["counts"]
    _spot = load_spot_facts()
    _gates, _gate_cmds = gate_counts()
    _bench = f"${_spot['benchmark_oz']:,.2f}/oz"
    _bench_g = f"${_spot['benchmark_per_g']:,.4f}/g"
    _kitco_oz = f"${_spot['kitco'].get('value_usd_per_oz', 0):,.2f}/oz"
    _kitco_g = f"${_spot['kitco'].get('value_usd_per_gram', 0):,.2f}/g"
    _jmb_oz = f"${_spot['jmbullion'].get('value_usd_per_oz', 0):,.2f}/oz"
    _jmb_g = f"${_spot['jmbullion'].get('value_usd_per_gram', 0):,.2f}/g"'''
    if "_spot = load_spot_facts()" not in src:
        assert anchor in src, "render_shell anchor not found"
        src = src.replace(anchor, new, 1)
        changes.append("render_shell: derive spot facts + gate counts")

    # 3. the ribbon + the gate-count claim
    old_ribbon = '''        <span class="spot-pill">CROSS-CHECK QUOTES · 2026-10-22 (benchmark: WGC $4,024.45/oz, 22 Oct)</span>
        <span class="mono" style="margin-left:0.45rem;">
          Kitco: <strong>$4,024.60/oz</strong> (<strong>$129.39/g</strong>) <a href="https://www.kitco.com/charts/gold" target="_blank" rel="noopener noreferrer">[Source ↗]</a>
          · JM Bullion: <strong>$4,039.76/oz</strong> (<strong>$129.88/g</strong>) <a href="https://www.jmbullion.com/charts/gold-price/" target="_blank" rel="noopener noreferrer">[Source ↗]</a>
        </span>'''
    new_ribbon = '''        <span class="spot-pill">BENCHMARK IN FORCE: WGC <strong>{_bench}</strong> · source date {_spot["benchmark_date"]} · retrieved {_spot["benchmark_retrieved"]} <a href="{_spot["benchmark_url"]}" target="_blank" rel="noopener noreferrer">[Source ↗]</a></span>
        <span class="mono" style="margin-left:0.45rem;">
          Dated cross-checks ({_spot["kitco"].get("retrieved_utc", "2026-10-22")}, not the benchmark):
          Kitco: <strong>{_kitco_oz}</strong> (<strong>{_kitco_g}</strong>) <a href="https://www.kitco.com/charts/gold" target="_blank" rel="noopener noreferrer">[Source ↗]</a>
          · JM Bullion: <strong>{_jmb_oz}</strong> (<strong>{_jmb_g}</strong>) <a href="https://www.jmbullion.com/charts/gold-price/" target="_blank" rel="noopener noreferrer">[Source ↗]</a>
          · benchmark = <strong>{_bench_g}</strong>
        </span>'''
    if old_ribbon in src:
        src = src.replace(old_ribbon, new_ribbon, 1)
        changes.append("ribbon: superseded hardcoded benchmark -> derived benchmark")

    old_gates = '<a href="audit.html">5 Automated Audit Gates Passing ✓</a>'
    new_gates = '<a href="audit.html">{_gates} Automated Audit Gates / {_gate_cmds} command invocations Passing ✓</a>'
    if old_gates in src:
        src = src.replace(old_gates, new_gates, 1)
        changes.append("ribbon: hardcoded '5 gates' -> counted from pages.yml")

    # 4. hero: a 2026-10-22 quote is not "live"
    old_hero = '''          With live fine gold trading at <strong>$4,024.60/oz ($129.39/g)</strong> on <span class="mono">2026-10-22</span>,'''
    new_hero = '''          With the <strong>dated cross-check quote</strong> of <strong>{_kitco_oz} ({_kitco_g})</strong> on <span class="mono">{_spot["kitco"].get("retrieved_utc", "2026-10-22")}</span> — a captured quote, not a live price; the benchmark in force for every derived value on the canonical dashboard is <strong>{_bench}</strong>, source date {_spot["benchmark_date"]} —'''
    if old_hero in src:
        src = src.replace(old_hero, new_hero, 1)
        changes.append("hero: 'live fine gold trading' -> dated cross-check wording")

    # 5. "Zero Invented Data" bullet: benchmark sentence derived
    old_zero = '''The gold benchmark driving every derived value is the World Gold Council panel <span class="mono">$4,024.45/oz</span> read on <span class="mono">2026-10-23</span> ('Data as of 22 October, 2026');'''
    new_zero = '''The gold benchmark driving every derived value on the canonical dashboard is the World Gold Council panel <span class="mono">{_bench}</span> ({_bench_g}) retrieved <span class="mono">{_spot["benchmark_retrieved"]}</span>, source date '{_spot["benchmark_date"]}';'''
    if old_zero in src:
        src = src.replace(old_zero, new_zero, 1)
        changes.append("policy bullet: superseded benchmark -> derived benchmark")

    # 6. KPI card: label the Kitco quote as a cross-check, show the benchmark
    old_kpi = '''        <div class="kpi-label">24K Gold Spot (2026-10-22)</div>
        <div class="kpi-value">$4,024.60/oz</div>'''
    new_kpi = '''        <div class="kpi-label">24K Gold Spot — cross-check quote ({_spot["kitco"].get("retrieved_utc", "2026-10-22")})</div>
        <div class="kpi-value">{_kitco_oz}</div>'''
    if old_kpi in src:
        src = src.replace(old_kpi, new_kpi, 1)
        changes.append("KPI card: labelled as a dated cross-check quote")

    old_kpi_sub = '''        <div class="kpi-sub"><span class="mono">$129.39/g</span> <a href="https://www.kitco.com/charts/gold" target="_blank" rel="noopener noreferrer">Kitco ↗</a> · <span class="mono">$129.88/g</span> <a href="https://www.jmbullion.com/charts/gold-price/" target="_blank" rel="noopener noreferrer">JM Bullion ↗</a></div>'''
    new_kpi_sub = '''        <div class="kpi-sub"><span class="mono">{_kitco_g}</span> <a href="https://www.kitco.com/charts/gold" target="_blank" rel="noopener noreferrer">Kitco ↗</a> · <span class="mono">{_jmb_g}</span> <a href="https://www.jmbullion.com/charts/gold-price/" target="_blank" rel="noopener noreferrer">JM Bullion ↗</a></div>
        <div class="kpi-sub">Benchmark in force: <span class="mono">{_bench} = {_bench_g}</span> · WGC, source date {_spot["benchmark_date"]} <a href="{_spot["benchmark_url"]}" target="_blank" rel="noopener noreferrer">↗</a></div>'''
    if old_kpi_sub in src:
        src = src.replace(old_kpi_sub, new_kpi_sub, 1)
        changes.append("KPI card: benchmark in force now shown")

    # 7. the calculator result panel ships pre-filled placeholders; label them
    old_results = '''        <div class="calc-results" aria-live="polite">
          <div class="result-box primary">'''
    new_results = '''        <div class="calc-results" aria-live="polite">
          <p class="small" style="margin:0 0 .5rem"><strong>Pre-filled example only.</strong> The figures below are an
          illustration loaded with the default inputs above; they are replaced as soon as you enter your own values and
          are <em>not</em> a quote, a valuation or a measured result for any listed ring.</p>
          <div class="result-box primary">'''
    if old_results in src and "Pre-filled example only" not in src:
        src = src.replace(old_results, new_results, 1)
        changes.append("calculator: pre-filled example now labelled as an example")

    if src == original:
        print("NO CHANGES — already applied or an anchor did not match.")
        return 1

    GEN.write_text(src, encoding="utf-8")
    print(f"Patched {GEN.relative_to(ROOT)}")
    for c in changes:
        print(f"  - {c}")
    return 0


if __name__ == "__main__":
    sys.exit(apply())
