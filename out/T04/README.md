# T04 native availability tree

## Validation complete

All unchanged gates pass; see [assessment.md](assessment.md). The authoritative
post-writer index is `validation-v1.json`, with the additional
`post-exit-audit-v1.json`. No producer or child process remains active. Live
merge/checkpoint status is in PR #15 / issue #1.

Do not restart the completed producers or overwrite their receipts. A later
source or binary build needs fresh versioned evidence. The commands and
in-progress procedure below are historical; inspect checkpoint #1 and live
processes before resuming any interrupted future candidate.

Contract and source inventory: [contract.md](contract.md). Task: #9 and
`docs/tasks/T04.md`; the roadmap's Done-when is unchanged. Live status belongs
in checkpoint #1. T03 historical receipts and archived extensions are retained.

## Profile before translation

`profile_machine.py` refreshes the diagnostic from the sealed T03 state and
tables, denies original files/Unicorn and compares outcome/memory/records with
T03. It records all guest and native entries. Never overwrite a receipt:

```sh
PYTHONHASHSEED=0 .venv/bin/python -u -B out/T04/profile_machine.py \
  --out out/T04/profile-before-v2.json > out/T04/profile-before-v2.log 2>&1
```

The v1 log preserves an import-name collision: initially naming this producer
profile.py shadowed the standard library module imported by cProfile. Renaming
the producer fixes it; no match started in that failed attempt. cProfile timings
include instrumentation; no uninstrumented gain or exact FFI count is inferred.

## Public checks

`engine/tests/test_native_subtree.py` uses authored nonzero synthetic memory,
the actual registered Python routines and the Rust dispatcher. Baseline v2
has 400 expected native-count failures, with Python/bridge state equality.
v1 additionally contains the corrected test-helper done-registration mistake
explained in contract.md. Keep both logs.

## Private proof and resume discipline

`differential.py --out NEW.json` captures eight real states for each routine
in RAM from the sealed drive, plus 500 synthetic random/edge states; every
run compares full memory, all registers, errors and callbacks. `--mutant 1`
uses the existing corrupt-return control; `--mutant 2` is the callee body
control. Controls must find differences and normal runs must find none.
Only hashes/counts are persisted. `evidence.py` fingerprints the exact source
and interpreter extension and refuses source changes during a run.

All producers use exclusive receipts, not silent reruns. Read checkpoint #1,
inspect live processes and prior failures, and choose a new version before
restarting. Do not run completed T03 producers or overwrite their outputs.
Do not modify bound production/proof sources while producers are running.
The completed ordered drive, F40, lifecycle and quiet paired timings are
assessed above; public tests or a diagnostic profile alone do not complete T04.

## Initial implementation receipts

`differential-v2.json` expands the earlier v1 full-frame run to **3,224**
real/random/edge comparisons, including direct callee body return values.
`public-cpython-v4.log` and `public-pypy-v1.log` cover all 14 public tests,
including native caller suspension, direct completion callbacks and both
caller/callee variant fallback. `cargo-v1.log` covers the 11 Rust tests.
The baseline/native assertions and intermediate failed helper attempts remain.
The first native-suite attempt stopped twice because the test's pause counter
separated fresh/replay visits; counting the site once fixes the helper without
changing the production code or equality assertions. `public-cpython-v1.log`
preserves that failure. Later runs preserve the expanded suite.

The full gate supervisor uses `.cache/T04-supervisor.lock`; append-only
`jobs-v1.jsonl` binds producer process groups/commands, `supervisor-v1.log`
reports progress. Before resuming, inspect every job/process and failure;
never duplicate a live group. After it exits successfully, run the independent
post-writer audit (exclusive output):

```sh
PYTHONHASHSEED=0 .venv/bin/python -B out/T04/validate.py out/T04/validation-v1.json
```

The supervisor does not write the final index while its own log is open.
Measured source files and interpreter artifacts must stay unchanged throughout.
