#!/bin/bash
# T01: one drive receipt (goal2-archaeology's own producer, experiments/E036-match-port/out/T117/drive_receipt_v1.py)
# from a clone, into goal2rust/out/T01/<name>.json (new file; the producer refuses an existing one).
#   run_receipt.sh <pristine|spike> <cpu|taps> <name> [rust]      rust: the overrides on (GOAL2_PORT_OVERRIDES)
# Environment passed through: GOAL2RUST_ONLY, GOAL2RUST_MUTANT. PYTHONHASHSEED is 0 for every run.
set -euo pipefail
G2R=/home/diego/projects/goal2rust
case "$1" in
  pristine) ROOT=$G2R/.cache/goal2-archaeology ;;
  spike) ROOT=$G2R/.cache/goal2-archaeology-spike ;;
  *) echo "clone: pristine or spike" >&2; exit 2 ;;
esac
export PYTHONHASHSEED=0
export PYTHONPATH=runtime
if [ "${4:-}" = rust ]; then
  export PYTHONPATH=runtime:$G2R/bindings:$G2R/.venv/lib/python3.12/site-packages
  export GOAL2_PORT_OVERRIDES=goal2rust_overrides
fi
cd "$ROOT"
exec /home/diego/.local/bin/python3.12 -B experiments/E036-match-port/out/T117/drive_receipt_v1.py --mode "$2" --out "$G2R/out/T01/$3.json"
