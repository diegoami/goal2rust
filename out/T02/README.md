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

## M2: seven routines native and equal (2026-10-29)

- Fixed native listener delivery to construct the integer from **all** coalesced
  stack bytes, rather than folding into u64. The v1 failed differential is kept.
- `differential-v2.json`: 28,224/28,224 equal. Per routine: 500 random inputs and
  four real inputs captured from the drive, each in four tap/listener modes and
  both bare-body and whole-frame execution. Full memory, every register, result,
  exception and ordered taps/listeners are compared. Real inputs live only in RAM;
  receipts contain counts/hashes. All seven have four captured real inputs.
- `taps-rust-v1.json` equals the original Python receipt on every required field
  (`compare-rust-v1.log`), including the same ordered hash as M1. Its native call
  map has exactly the seven T01 entries, totalling 880,504 calls; all remaining
  bodies run through the bridge. Source hashes before/after are equal.
- `tests-v2.log`: synthetic tests now cover all seven native full frames and
  >64-bit listener values, and poison their Python bodies to prove they are not
  called. `mutant-v2.json` rechecks the return-IP mutant on the corrected source.
- F40 is running with two workers, append-only in `family-F40-rust-v1.jsonl`.
  Resume with `out/T02/run_family_v1.sh`; the original family runner skips records
  already appended. Compare only once all 40 have completed; preserve any errors.
- The unmodified `original_match.check --engine port --no-unicorn` is running
  into `check-rust-v1.json` for its engine, interactive save/load, goal consistency,
  and knockout replay checks. CPU receipts wait until these validation runs finish
  and the machine is quiet. No T03 work is authorized here.

Additional M2 validation: `tests-v3.log` adds recursion with five live frames
sharing a return address and a stop before resume; it agrees with the oracle.
`wheel-tests-v3.log` and `wheel-tests-pypy-v3.log` pass the six synthetic tests
from separately built/installed CPython 3.12 and PyPy 3.11 wheels. `engine/README.md`
documents the per-event API. The production sources and CPython extension still
hash exactly as in the native M2 taps receipt.

The proposed next-subtree order is drafted in `next-subtrees.md` with generated
profile/call-edge evidence in `profile-subtrees-v2.json`. Generator resumptions
are distinguished from the actual dispatched call counts in the T01 top-40
call table. M3's paired timing gate is still pending; do not infer speed from the
tapped validation runs.

Final gate orchestration (supervised):

```sh
.venv/bin/python -u -B out/T02/finish_v1.py >> out/T02/finish-v1.log 2>&1
```

It waits for F40 and the existing check run, refuses failed records/checks,
records `compare.py`'s exit status, verifies the M2 source/extension hashes, and
requires three quiet load observations before starting the paired CPU runs.
It preserves existing records and refuses incomplete timing attempts. A partial
supervisor log can be appended to on resume. It neither publishes nor starts
another task. The kit check itself is the unmodified standard producer; if
interrupted before its JSON report, preserve its log and rerun the command with
stdout appended (or use a new receipt version if the completed report failed).

## Mid-run recovery checkpoint (2026-10-29)

F40 has 20 completed records with no runner errors; its **final comparison is
pending**, not inferred from completion. The partial append-only family receipt
and log are pushed for recovery. Before resuming either producer in a new
session, check whether the existing runner is still active; do not run two
producers against the same output. Current sessions: family 17713, kit check
33178, final-gate supervisor 57926. The supervisor is waiting for both producers.
The production implementation and extension still match M2. CI passed on
`c40369f`; any subsequent final head must have its own passing CI.

## Lifecycle checks passed (2026-10-29)

`check-rust-v1.json`: the unchanged kit's engine, interactive save/load, goal
consistency, and knockout checks all pass, with Unicorn imports positively
refused. The interactive straight/resumed/expected digests agree, as do the
knockout straight/extra-time-resumed/shootout-order-resumed/expected digests.
F40 is still running (24 completed records at this checkpoint, no runner errors);
its final comparison and paired CPU receipts remain pending.
