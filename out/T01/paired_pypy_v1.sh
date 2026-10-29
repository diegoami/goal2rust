#!/bin/bash
# T01: the PyPy baseline. As paired_v1.sh, both runs under PyPy 3.11 (uv python find pypy3.11): the pristine clone,
# and the hook clone with the crate built for PyPy (maturin build -i pypy3.11, installed in .venv-pypy), at once.
#   paired_pypy_v1.sh <v>   -> out/T01/cpu-pypy-{python,rust}-<v>.json
set -euo pipefail
G2R=/home/diego/projects/goal2rust
V=$1
RAW=$G2R/out/T01/raw
export G2R_PY=$(uv python find pypy3.11)
export G2R_SITE=$G2R/.venv-pypy/lib/pypy3.11/site-packages
mkdir -p "$RAW"
uptime > "$RAW/load-before-pypy-$V.txt"
"$G2R/out/T01/run_receipt.sh" pristine cpu "raw/cpu-pypy-python-$V" > "$RAW/cpu-pypy-python-$V.log" 2>&1 & P1=$!
"$G2R/out/T01/run_receipt.sh" spike cpu "raw/cpu-pypy-rust-$V" rust > "$RAW/cpu-pypy-rust-$V.log" 2>&1 & P2=$!
wait $P1; wait $P2
uptime > "$RAW/load-after-pypy-$V.txt"
cd "$G2R/out/T01"
/home/diego/.local/bin/python3.12 -B compose_receipt_v1.py "raw/cpu-pypy-python-$V.json" "cpu-pypy-python-$V.json" --clone "$G2R/.cache/goal2-archaeology" --site "$G2R_SITE"
GOAL2_PORT_OVERRIDES=goal2rust_overrides /home/diego/.local/bin/python3.12 -B compose_receipt_v1.py "raw/cpu-pypy-rust-$V.json" "cpu-pypy-rust-$V.json" --clone "$G2R/.cache/goal2-archaeology-spike" --rust --site "$G2R_SITE"
/home/diego/.local/bin/python3.12 -B compare_receipts.py "cpu-pypy-python-$V.json" "cpu-pypy-rust-$V.json"
