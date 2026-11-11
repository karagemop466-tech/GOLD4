#!/usr/bin/env python3
"""Run every Pages CI command, retaining actual output and exit statuses."""
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import tempfile
import sys

ROOT = Path(__file__).resolve().parents[2]
COMMANDS = [
    ['python3', 'scripts/audit.py'],
    ['python3', 'scripts/check_site.py'],
    ['python3', 'scripts/verify.py'],
    ['python3', 'scripts/verify_a0be79d4.py'],
    ['python3', 'scripts/audit_hallucinations.py'],
    ['python3', 'scripts/session_46691f83/verify_citations.py', '--self-test'],
    ['python3', 'scripts/session_46691f83/verify_citations.py'],
    ['python3', 'scripts/audit_freshness.py'],
    ['python3', 'scripts/test_assurance.py'],
    ['python3', 'scripts/session_8a2b9dfb/test_readiness.py'],
    ['node', 'scripts/session_8a2b9dfb/test_calculator.js'],
    ['python3', 'scripts/session_8a2b9dfb/readiness.py', '--check'],
    ['python3', 'scripts/session_a2f26a30/test_source_security.py'],
    ['python3', 'scripts/session_a2f26a30/test_review.py'],
    ['python3', 'scripts/session_a2f26a30/build_review.py', '--check'],
]


def main():
    path = ROOT / 'reports/current-a2f26a30-checks.txt'
    path.write_text('Started ' + datetime.now(timezone.utc).isoformat() + '\n'
                    'Automated software checks only; not external factual verification or an assay.\n')
    failures = 0
    for command in COMMANDS:
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        failures += result.returncode != 0
        with path.open('a') as log:
            log.write('\n$ ' + ' '.join(command) + '\n' + result.stdout + result.stderr + '\nexit=' + str(result.returncode) + '\n')
        print(('PASS' if result.returncode == 0 else 'FAIL') + ' ' + ' '.join(command), flush=True)
    with tempfile.TemporaryDirectory() as tmp:
        command = ['python3', 'scripts/session_a2f26a30/stage_pages.py', str(Path(tmp) / 'site')]
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        failures += result.returncode != 0
        with path.open('a') as log:
            log.write('\n$ ' + ' '.join(command) + '\n' + result.stdout + result.stderr + '\nexit=' + str(result.returncode) + '\n')
        print(('PASS' if result.returncode == 0 else 'FAIL') + ' actual public-artifact staging and HTML local-file links', flush=True)
    summary = f'{len(COMMANDS)+1-failures}/{len(COMMANDS)+1} command invocations passed'
    with path.open('a') as log:
        log.write('\n' + summary + '\nCompleted ' + datetime.now(timezone.utc).isoformat() + '\n')
    print(summary)
    return bool(failures)


if __name__ == '__main__':
    sys.exit(main())
