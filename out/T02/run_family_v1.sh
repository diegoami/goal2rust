#!/usr/bin/env bash
# Append-only/resumable F40. Run from any directory; at most two family workers.
set -euo pipefail
G2R=$(cd "$(dirname "$0")/../.." && pwd)
export PYTHONHASHSEED=0 GOAL2RUST_MACHINE=1 GOAL2RUST_NATIVE=1
export PYTHONPATH="$G2R/out/T02:$G2R/engine/python:$G2R/.cache/goal2-archaeology/runtime:$G2R/.venv/lib/python3.12/site-packages"
cd "$G2R/.cache/goal2-archaeology"
exec "$G2R/.venv/bin/python" -B experiments/E036-match-port/family.py --family F40 --engine port --no-unicorn --workers 2 --out "$G2R/out/T02/${1:-family-F40-rust-v1.jsonl}"
