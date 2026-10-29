# T02 evidence and resume

## M1: bridge-only machine equal (2026-10-29)

- Oracle remains pristine at `d3cf46a3e87f0ba04916867b5b231c4646a0c2bd`.
- `taps-bridge-v1.json`, produced by `run_receipt_v1.py --backend rust --native 0
  --mode taps --out out/T02/taps-bridge-v1.json`: E034-03's drive with every routine
  bridged, equals `../T01/dev-taps-python-d3cf46a3.json` on events, result, full
  memory, stretches and ordered taps (`compare-bridge-v1.log`). 831 events,
  553 stretches, tap hash `76ac2f951bbed7bff94c4cfd1a2413de7207b47f027b141d35caf498f9f46647`.
  `goal2rust.native_calls` is empty. Both oracle and implementation source hashes
  were stable during the run. CPU time here is diagnostic, not the paired timing.
- `tests-before-v1.log`: new machine tests fail before implementation.
  `tests-dev-v3.log`: synthetic machine differentials pass, including 144 nested
  call combinations and listener/site reentrancy and error cleanup.
- Real match smoke: save/load at event 60 with five live frames reconstructed
  identical frame state and full machine snapshot. Formal lifecycle checks remain.
- `mutant-v1.json`: incrementing a pushed guest-call return IP is caught by the
  machine differential (`PortError: no registered port/return at 0791:0111`).
- **M2 pending**: `differential-v1.json` exposes native listener-value truncation
  for stack flushes wider than eight bytes (26D7, 2B51, 2BE5), despite equal memory.
  Fix `write_native` to retain arbitrary-width Python integers, then rerun into a
  new receipt. Do not weaken its full-stack listener coverage.

All harness commands use `PYTHONHASHSEED=0` and
`PYTHONPATH=engine/python:.cache/goal2-archaeology/runtime` from the repository root.
`run_family_v1.sh` is append-only and resumable; `paired_v1.sh` starts CPython,
PyPy, and the Rust machine together. No family or timing run has started at M1.
Original game bytes and save images remain private in the ignored oracle cache.
