#!/usr/bin/env bash
# Pass 21: full rebuild in dependency order, then every gate. Idempotent.
set -euo pipefail
cd "$(dirname "$0")/.."
export GOLD4_SOURCE_CHECK_PASS="Pass 21" GOLD4_SOURCE_CHECK_SESSION="arena/4fe4a9c3-gold4"
python3 scripts/pass21_apply.py >/dev/null
python3 scripts/build_source_health.py >/dev/null
python3 scripts/apply_source_health.py >/dev/null
python3 scripts/compute.py | tail -1
python3 scripts/generate_site.py | tail -1
python3 scripts/build_site.py | tail -1
python3 scripts/build_pass20.py | tail -1
python3 scripts/session_8a2b9dfb/readiness.py | tail -1
python3 scripts/build_pass21.py
python3 scripts/run_gates_pass21.py >/dev/null || true
python3 scripts/pass21_docs.py
python3 scripts/gen_verification.py | tail -1
python3 scripts/build_site.py | tail -1
python3 scripts/build_pass20.py | tail -1
python3 scripts/build_pass21.py
python3 scripts/pass21_selfcheck.py | tee reviews/pass21/selfcheck.txt | tail -2
python3 scripts/run_gates_pass21.py
