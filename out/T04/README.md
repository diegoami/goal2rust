# T04 native availability tree

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
Full ordered drive, F40, lifecycle and quiet paired timings remain required;
public tests or a diagnostic profile alone do not complete T04.
