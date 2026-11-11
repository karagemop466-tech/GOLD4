#!/usr/bin/env bash
# Session 4fe4a9c3 (re-read of 2026-11-11): full rebuild in dependency order, then every gate. Idempotent.
set -euo pipefail
cd "$(dirname "$0")/../.."
export GOLD4_SOURCE_CHECK_PASS="Re-read 2026-11-11 (4fe4a9c3)" GOLD4_SOURCE_CHECK_SESSION="arena/4fe4a9c3-gold4"
python3 scripts/session_4fe4a9c3/apply_reread.py >/dev/null
python3 scripts/build_source_health.py >/dev/null
python3 scripts/apply_source_health.py >/dev/null
python3 scripts/compute.py | tail -1
python3 scripts/generate_site.py | tail -1
python3 scripts/build_site.py | tail -1
python3 scripts/build_pass20.py | tail -1
python3 scripts/session_8a2b9dfb/readiness.py | tail -1
python3 scripts/session_4fe4a9c3/build_page.py
python3 scripts/session_4fe4a9c3/run_gates.py >/dev/null || true
python3 scripts/session_4fe4a9c3/docs.py
python3 scripts/gen_verification.py | tail -1
python3 scripts/build_site.py | tail -1
python3 scripts/build_pass20.py | tail -1
python3 scripts/session_4fe4a9c3/build_page.py
python3 scripts/session_4fe4a9c3/selfcheck.py | tee reviews/reread-4fe4a9c3/selfcheck.txt | tail -2
python3 scripts/session_4fe4a9c3/run_gates.py
