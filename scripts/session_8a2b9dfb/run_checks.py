#!/usr/bin/env python3
"""Run the twelve Pages gate commands and retain their actual combined output.

No retailer request is made; this is code/data/site assurance, not live recapture.
The canonical generators must already have run. A failed command is logged and
returns failure immediately. Historical other-session reports are never edited.
"""
from __future__ import annotations

from datetime import datetime, timezone
import pathlib
import shlex
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
LOG = ROOT / "reports" / "readiness-checks-8a2b9dfb.txt"
COMMANDS = [
    ["python3", "scripts/audit.py"],
    ["python3", "scripts/check_site.py"],
    ["python3", "scripts/verify.py"],
    ["python3", "scripts/verify_a0be79d4.py"],
    ["python3", "scripts/audit_hallucinations.py"],
    ["python3", "scripts/session_46691f83/verify_citations.py", "--self-test"],
    ["python3", "scripts/session_46691f83/verify_citations.py"],
    ["python3", "scripts/audit_freshness.py"],
    ["python3", "scripts/test_assurance.py"],
    ["python3", "scripts/session_8a2b9dfb/test_readiness.py"],
    ["node", "scripts/session_8a2b9dfb/test_calculator.js"],
    ["python3", "scripts/session_8a2b9dfb/readiness.py", "--check"],
]


def main() -> int:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("w", encoding="utf-8") as log:
        log.write("Final combined-tree Pages assurance — session 8a2b9dfb\n")
        log.write("Started UTC: " + datetime.now(timezone.utc).isoformat() + "\n")
        log.write("Scope: current working-tree code/data/artifacts; publication revision is recorded in COORDINATION.md.\n")
        log.write("Nine gates / twelve commands. No new retailer reads, physical tests or purchase approvals.\n")
        log.write("Automated passes detect defined failures; they cannot prove absence of all hallucinations.\n")
        for number, command in enumerate(COMMANDS, 1):
            label = shlex.join(command)
            log.write(f"\n===== {number}/{len(COMMANDS)}: {label} =====\n")
            log.flush()
            result = subprocess.run(command, cwd=ROOT, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, text=True, check=False)
            log.write(result.stdout)
            log.write(f"\nEXIT CODE: {result.returncode}\n")
            log.flush()
            print(f"{'PASS' if result.returncode == 0 else 'FAIL'} {number}/{len(COMMANDS)} {label}", flush=True)
            if result.returncode:
                print(f"Stopped on failure; actual output: {LOG.relative_to(ROOT)}", file=sys.stderr)
                return result.returncode
        log.write("\nRESULT: all twelve commands passed. Factual and purchase-readiness gaps remain unverified.\n")
    print(f"Saved actual output: {LOG.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
