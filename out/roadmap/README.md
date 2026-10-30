# Roadmap preparation, 2026-10-30

Owner-authorized continuation: [roadmap](../../docs/roadmap.md),
[T03 / #8](../../docs/tasks/T03.md), [T04 / #9](../../docs/tasks/T04.md).
This directory is preparation evidence, not completion of either task.
T02's accepted oracle remains d3cf46a3, and its production sources are unchanged.

## Post-T02 diagnostic profile

`profile-T02-v1.json`, `.prof`, `.txt`, `.log` record the Rust machine on the
old accepted oracle. Events (831), result and full memory equal T02's receipt;
all source/extension hashes stayed unchanged during the run. The .prof contains
function names/counts/times only; JSON holds hashes and counts, no game state.

- 3,103,685 guest entries, 880,504 native and **2,223,181 Python** entries.
- Candidate `0791:2956`: 184,872 entries, 369,744 Python calls/resumptions.
- Callee `1771:3216`: 233,587 entries, all still Python.
- Moving both would remove 418,459 current Python guest entries (18.8% of
  remaining entries in this drive). This is an entry-count opportunity, not
  a predicted speedup or an exact count of foreign-function transitions.
- `0791:2FB1` has 5,147 actual guest entries and 298,641 calls/resumptions;
  it is the largest registered body by profiled self time and remains a
  subsequent caller-tree candidate, after availability and its dependencies.
- Register access, flush/store and memory IO remain prominent. cProfile's
  327.599 CPU seconds includes instrumentation; compare no speed ratio with
  T02's uninstrumented CPU receipts. Rust internals are not separately resolved.

The old recommendation's first bounded caller/callee pair is still supported.
Confirm it after the accepted oracle update rather than treating this one
drive as the final implementation choice. `docs/tasks/T04.md` inventories the
two bodies and the native-continuation work they require.

Reproduce into a new name (never overwrite a receipt):

```sh
PYTHONHASHSEED=0 .venv/bin/python -B out/roadmap/profile_machine_v1.py \
  --out out/roadmap/profile-T02-v2.json
```

## Sealed T80b preview

Both real-drive producers finished successfully. `compare-seal-preview-v1.json`
records equality on input state, all 831 events, result, full memory and returned
state. Both replay checks pass on events/result/records, and returned records
roundtrip through Image.from_state. Source manifests agree between backends
and stayed unchanged; Rust independently records 880,504 native calls across
exactly seven addresses. The plain backend records no native calls. These are
separate processes, avoiding the adapter's process-wide backend interference.

The isolated ignored clone `.cache/goal2-archaeology-seal-preview` is pristine
at merged T80b `b46000bc5ef790696cfa3dc6eb905f2b28e5f057`. It does not replace
the accepted oracle. Original tables remain only in this ignored upstream
clone; private state is `.cache/seal-preview-state-v1.json`, never tracked.
`upstream-audit-v1.json` records the seven audited source files (machine,
frames/runtime, geometry/entrypoints and attributes) as byte-identical to the
accepted pin. Runtime changes are limited to check/image/Match, the port-module
exclusion list, and the new tables loader. Repeat this audit at the final pin.

`synthetic-preview-v1.log`: all six Rust synthetic machine tests pass against
this preview. `state-contract-preview-v1.log`: all three upstream public
state-contract tests pass (module bytes omitted, wrong tables refused,
mutated tables refused). These tests use the preview's own fixtures/tables.

`seal_preview_v1.py` separately drives Python and Rust from the same state and
tables with the upstream denial bootstrap active: importing Unicorn and
opening `.sav`, `.exe`, `.dat` raise. It verifies a saved first-event checkpoint
replays to the same events/result/records and roundtrips records through
Image.from_state. Match.load does not restore a tables object: pass tables
explicitly to records_after(tables), as allowed by upstream's API.

Commands (prepare once; state stays private; choose fresh output names):

```sh
PYTHONHASHSEED=0 .venv/bin/python -B out/roadmap/seal_preview_v1.py --prepare
PYTHONHASHSEED=0 .venv/bin/python -B out/roadmap/seal_preview_v1.py \
  --backend python --out out/roadmap/seal-preview-python-v2.json
PYTHONHASHSEED=0 .venv/bin/python -B out/roadmap/seal_preview_v1.py \
  --backend rust --out out/roadmap/seal-preview-rust-v2.json
```

One drive/one replay boundary is not T03 acceptance. Full sealed lifecycle,
ordered taps, differential/mutants, F40/ALL and fresh paired CPU must run after
the accepted pin is chosen. Archaeology #627 and #628 were still open at the
last inspection; selecting that pin and beginning T04 depend on them.
No diagnostic process remains active. Do not restart completed producers;
check issue #1 and upstream PR state, then continue T03 when its dependencies
are accepted. No T04 production translation or oracle-pin change was made here.
