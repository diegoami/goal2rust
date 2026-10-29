#!/usr/bin/env bash
# The three required timing receipts start together, on the same quiet machine.
set -euo pipefail
G2R=$(cd "$(dirname "$0")/../.." && pwd)
cd "$G2R"
unset GOAL2RUST_MACHINE GOAL2RUST_MACHINE_MUTANT GOAL2_PORT_OVERRIDES
export PYTHONHASHSEED=0 PYTHONPATH="$G2R/engine/python:$G2R/.cache/goal2-archaeology/runtime"
uptime > out/T02/load-before-v1.txt
.venv/bin/python -B out/T02/run_receipt_v1.py --backend python --mode cpu --out out/T02/cpu-python-v1.json > out/T02/cpu-python-v1.log 2>&1 & CP=$!
PYTHONPATH="$G2R/.cache/goal2-archaeology/runtime" .venv-pypy/bin/python -B out/T02/run_receipt_v1.py --backend python --mode cpu --out out/T02/cpu-pypy-python-v1.json > out/T02/cpu-pypy-python-v1.log 2>&1 & PP=$!
.venv/bin/python -B out/T02/run_receipt_v1.py --backend rust --mode cpu --out out/T02/cpu-rust-v1.json > out/T02/cpu-rust-v1.log 2>&1 & RS=$!
status=0
wait "$CP" || status=1
wait "$PP" || status=1
wait "$RS" || status=1
uptime > out/T02/load-after-v1.txt
if [ "$status" != 0 ]; then exit "$status"; fi
.venv/bin/python out/T01/compare_receipts.py out/T02/cpu-python-v1.json out/T02/cpu-rust-v1.json
.venv/bin/python out/T01/compare_receipts.py out/T02/cpu-pypy-python-v1.json out/T02/cpu-rust-v1.json
