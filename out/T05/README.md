# T05 native nearest-to-ball tree

Task #16 / docs/tasks/T05.md; full semantic inventory in contract.md. The
owner-authorized next tree is selected from T04's refreshed accepted-pin profile
(selection-v1.json). Historical T04 receipts and archived artifacts stay intact.

Same per-subtree gates as the approved roadmap. Source/artifact manifests cover
all engine/test/oracle and producer source. The accepted private state/tables
remain ignored under .cache/T03-*; no original bytes enter tracked output.
Public baseline fails only its native-root assertion; Python/bridge state already
agrees. Do not weaken equality, guards or the task's Done-when.

## Full-run/resume rules

Read checkpoint #1 and live heads/processes first. supervisor-v1.log and
jobs-v1.jsonl are append-only; .cache/T05-supervisor.lock guards the supervisor.
Check child process groups too before restarting an interrupted run. Completed
receipts use exclusive names and source/extension assertions. Never overwrite
or silently rerun a completed/failed attempt; choose fresh versioned outputs
and preserve failures. Never modify bound sources or rebuild while jobs run.

Historical invocation for this candidate, only while incomplete and no group
remains active:

```sh
PYTHONHASHSEED=0 .venv/bin/python -u -B out/T05/supervise.py >> out/T05/supervisor-v1.log 2>&1
```

Stages: strict F40 with two workers/default guards, four sealed lifecycle checks
with independent backend attestation, plain/Rust ordered drives, 8 real captures
and 500 authored synthetic inputs with full boundary/final-state equality, body
control3 and root-return control4, refreshed all-entry profile, three quiet-host
observations, simultaneous plain CPython/PyPy/Rust CPU drives. Only after every
producer and supervisor exits, seal a new exclusive post-writer ledger:

```sh
PYTHONHASHSEED=0 .venv/bin/python -B out/T05/validate.py out/T05/validation-v1.json
```

No performance claim comes from cProfile or guest-entry counts. ALL75/A700 and
owner-run engine-milestone review remain later gates; known ref-121 stays intact.
