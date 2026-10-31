# T06 effective skill tree

Task #18 / draft PR #19; contract in docs/tasks/T06.md and contract.md.
Selection-v1.json binds T05's refreshed profile and the unchanged accepted oracle.
T05 receipts and archived extensions remain intact. No original bytes/state/tables
enter tracked output; private accepted inputs stay under .cache/T03-*.

Same per-subtree gates as the approved roadmap. Body control5 corrupts the leaf
retained local, root-return control6 changes only27EB IP. Tests include callbacks
that mutate saved guest arguments/base and AX after the dispatcher captures it.
Variants stay Python. Preserve all failures and original guards; no speed gain
is inferred from cProfile or routine/entry counts. ALL75/A700 and owner-run review
remain later engine-milestone gates; #6 limits and ref-121 remain unchanged.

## Immutable evidence and resume

Read checkpoint #1 and inspect every live process group before resuming.
Supervisor lock: .cache/T06-supervisor.lock; append-only jobs-v1.jsonl and
supervisor-v1.log bind commands/PIDs/exits/progress. Do not duplicate live groups,
modify bound source or rebuild while jobs run. Completed or failed receipts must
not be overwritten: choose fresh versioned evidence and preserve prior attempts.

Historical candidate invocation, only while incomplete and with no live group:

```sh
PYTHONHASHSEED=0 .venv/bin/python -u -B out/T06/supervise.py >> out/T06/supervisor-v1.log 2>&1
```

Stages: strict F40/two workers/default guards, four sealed lifecycle checks with
independent backend attestation, eight captures per routine and500 synthetic
states x body/frame/tap/listener/continuation variants, both controls, Python/Rust
ordered drives, all-entry profile, three quiet observations and simultaneous
CPython/PyPy/Rust CPU drives. Only after every writer exits seal an exclusive
ledger, after the supplemental post-exit audit:

```sh
PYTHONHASHSEED=0 .venv/bin/python -B out/T06/validate.py out/T06/validation-v1.json
```
