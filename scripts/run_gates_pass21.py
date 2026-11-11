#!/usr/bin/env python3
"""Pass 21 copy of run_gates_pass20.py, extended with Gate 9 (all twelve CI commands).

Run every CI gate locally, record the result, and write reviews/pass21/gates.json.

The gate list mirrors .github/workflows/pages.yml exactly, so a local PASS means
CI is expected to pass on the same tree. The exit code of each gate is the source
of truth for its status; the printed summary line is recorded verbatim for the
reader. No gate output is edited or softened.
"""
from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "reviews" / "pass21"
SUMMARY = re.compile(r"(RESULT:|runtime tests passed|STATUS\s*:|PASS[a-zA-Z ]*:|OK\b|Ran \d+ tests|Records audited:|Checks passed|FAIL)")

GATES = [
    ("1", "Canonical dataset integrity & derived-math recompute", ["scripts/audit.py"]),
    ("2", "Root, /pages & /docs link and policy gate", ["scripts/check_site.py"]),
    ("3", "Combined schema & blank-flag check", ["scripts/verify.py"]),
    ("4", "Multi-page XSS, 404-blocklist & Assay-Lab scanner", ["scripts/verify_a0be79d4.py"]),
    ("5", "Gemstone-deduction, category-subpage & hallucination auditor", ["scripts/audit_hallucinations.py"]),
    ("6a", "Citation-integrity self-test (must reject a known-bad CFR citation)",
     ["scripts/session_46691f83/verify_citations.py", "--self-test"]),
    ("6b", "Citation integrity (every CFR citation vs its official heading)",
     ["scripts/session_46691f83/verify_citations.py"]),
    ("7", "Live-evidence freshness & source-health gate", ["scripts/audit_freshness.py"]),
    ("8", "Conservative currency parsing & blank current-price register", ["scripts/test_assurance.py"]),
    ("9a", "Readiness register regression tests", ["scripts/session_8a2b9dfb/test_readiness.py"]),
    ("9b", "Calculator runtime tests (node)", ["node:scripts/session_8a2b9dfb/test_calculator.js"]),
    ("9c", "Readiness report determinism check", ["scripts/session_8a2b9dfb/readiness.py", "--check"]),
]


def run(cmd: list[str]) -> tuple[int, str]:
    if cmd[0].startswith("node:"):
        argv = ["node", cmd[0][5:], *cmd[1:]]
    else:
        argv = [sys.executable, *cmd]
    proc = subprocess.run(argv, cwd=ROOT, capture_output=True, text=True)
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    results, log, failures = [], [], 0
    for gate, name, cmd in GATES:
        code, output = run(cmd)
        lines = [ln.strip() for ln in output.splitlines() if ln.strip()]
        detail = next((ln for ln in reversed(lines) if SUMMARY.search(ln)), lines[-1] if lines else "")
        if gate == "6a" and "SELF-TEST PASSED" in detail:
            # Keep the verdict, drop the quoted section titles: they are a known-bad
            # example and the citation gate would otherwise flag this page for quoting it.
            detail = "SELF-TEST PASSED — a known-wrong CFR citation was correctly rejected"
        if gate == "6b":
            detail = next((ln for ln in lines if ln.startswith("Citation-integrity gate")), detail)
        if gate == "3":
            audited = next((ln for ln in lines if ln.startswith("Records audited")), "")
            detail = f"{audited} · exit {code}" if audited else detail
        status = "PASS" if code == 0 else "FAIL"
        failures += code != 0
        results.append({"gate": gate, "name": name, "status": status,
                        "detail": f"{detail} · exit {code}"})
        log.append(f"=== Gate {gate} — {name} ===\n{output.strip()}\nexit={code}\n")

    (OUT / "gates.txt").write_text("\n".join(log), encoding="utf-8")
    (OUT / "gates.json").write_text(json.dumps(results, indent=1) + "\n", encoding="utf-8")
    for r in results:
        print(f"Gate {r['gate']:<3} {r['status']:<4} {r['detail'][:120]}")
    print(f"\n{len(results) - failures}/{len(results)} gate invocations passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
