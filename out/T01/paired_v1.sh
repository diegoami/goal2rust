#!/bin/bash
# T01 Done-when 2: the untapped drive at d3cf46a3 with and without the Rust routines, started together on one quiet
# machine, each composed with its source hashes into out/T01/cpu-{python,rust}-<v>.json (new files).
#   paired_v1.sh <v>        e.g. v1
set -euo pipefail
G2R=/home/diego/projects/goal2rust
V=$1
RAW=$G2R/out/T01/raw
mkdir -p "$RAW"
uptime > "$RAW/load-before-$V.txt"
"$G2R/out/T01/run_receipt.sh" pristine cpu "raw/cpu-python-$V" > "$RAW/cpu-python-$V.log" 2>&1 & P1=$!
"$G2R/out/T01/run_receipt.sh" spike cpu "raw/cpu-rust-$V" rust > "$RAW/cpu-rust-$V.log" 2>&1 & P2=$!
wait $P1; wait $P2
uptime > "$RAW/load-after-$V.txt"
cd "$G2R/out/T01"
/home/diego/.local/bin/python3.12 -B compose_receipt_v1.py "raw/cpu-python-$V.json" "cpu-python-$V.json" --clone "$G2R/.cache/goal2-archaeology"
GOAL2_PORT_OVERRIDES=goal2rust_overrides /home/diego/.local/bin/python3.12 -B compose_receipt_v1.py "raw/cpu-rust-$V.json" "cpu-rust-$V.json" --clone "$G2R/.cache/goal2-archaeology-spike" --rust
/home/diego/.local/bin/python3.12 -B compare_receipts.py "cpu-python-$V.json" "cpu-rust-$V.json"
