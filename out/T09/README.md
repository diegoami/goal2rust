# T09 speaker/noise state

## V1 stopped: fidelity passes, performance gate missed

All experiments have exited. All fidelity checks pass, but the three-round median
CPU gain is 4.28%, below the unchanged 5% requirement. PR #25 stays draft/unmerged,
task #24 open; main unchanged. See assessment.md. No accepted validation-v1.json.
Diagnostic closed rejection ledger: rejected-validation-v1.json (acceptance=false,
do_not_merge=true), with real-host rejected-process-closure-v1.json. Do not restart
v1 producers or overwrite any receipt, round, source binding or archived artifact.
A further candidate requires fresh versioned proof; success-path helper scripts
remain historical/unexecuted for this rejected candidate. Live stop/resume state
is in issue #1. Commands below are historical, not an instruction to rerun v1.

Task #24, contract docs/tasks/T09.md and contract.md. Read checkpoint issue #1
and recheck live jobs before resuming. Never overwrite completed receipts,
rejected attempts, preserved baselines or private inputs. No original data in git.

The rejected register-descriptor prototype is retained as source .txt, microbench
and compiled artifact hashes. No prototype factory is active in production.
A four-body speaker/RNG state tree is the selected candidate. Existing hardware
omission stubs remain ordinary observable calls. Accepted 2cbeb36f/state-v2,
private .cache/T07-state-v2-v1.json and .cache/T07-tables are unchanged.
Preserved T08 source/adapter/binary baseline: .cache/T09-baseline/engine,
indexed by baseline-snapshot-v1.json. The single pilot is diagnostic only.

Historical/resume command, only when incomplete and no matching process group:

```sh
PYTHONHASHSEED=0 .venv/bin/python -u -B out/T09/supervise.py >> out/T09/supervisor-v1.log 2>&1
```

The exclusive lock .cache/T09-supervisor.lock, jobs-v1.jsonl and supervisor-v1.log
record starts/exits. Read all groups; do not duplicate or modify bound .py/Rust
sources, extension binaries or inputs while a producer runs. Use new versioned
outputs after any change. New tree: eight real RAM captures per body, 500 authored
cases per body, callbacks, direct bodies, pauses and three scoped controls.
Existing 12-body proofs/controls, exact ordered drive, sealed lifecycle, strict
ALL75/F40 and profile precede three quiet simultaneous baseline/candidate/plain
CPython/PyPy rounds on rotated physical cores. Every candidate must improve and
median CPU ratio must be <=0.95. No failed or slow round discarded. After all
writers and groups exit, post-exit-audit.txt and validate.py close a fresh ledger.
Existing #6 / later A700 and owner-run engine review remain separate gates.
