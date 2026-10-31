# T08 Measured common bridge performance

## Validation complete

All fidelity and three-round performance gates pass; see [assessment.md](assessment.md).
Authoritative closed ledger: validation-v1.json, with post-exit-audit-v1.json.
No producer/child group remains active. Live merge/stop status is in PR #23 / #1.
Do not restart completed producers or overwrite any round/baseline/receipt.
Commands below are historical; future artifacts need fresh versioned proof.

Task #22; full implementation/observer/fallback/measurement contract in
contract.md and docs/tasks/T08.md. Existing accepted2cbeb36f/state-v2 inputs stay
under ignored .cache/T07-*. T07 receipts and binaries remain unchanged. Preserved
old source/adapter/extension baseline is .cache/T08-baseline/engine, hash-bound
in baseline-snapshot-v1.json. Candidate and baseline are separate processes.

Primitive diagnostics and the first whole-drive pilot are preserved; they do
not satisfy the three-round performance gate. First build receiver typo is
retained/corrected; baseline optimized-path API test fails as expected.

## Full run and resume

Read live checkpoint #1 and inspect ALL process groups before any resume.
.cache/T08-supervisor.lock guards the supervisor; jobs-v1.jsonl / supervisor-v1.log
append commands/PIDs/exits/progress. Never duplicate a live group or modify bound
source/inputs/binaries during runs. Completed/failed receipts use exclusive names;
choose fresh versioned evidence and preserve prior attempts and original guards.

Historical invocation, only while incomplete with no live group:

```sh
PYTHONHASHSEED=0 .venv/bin/python -u -B out/T08/supervise.py >> out/T08/supervisor-v1.log 2>&1
```

Stages: ALL75/two workers with exact F40 source selection and both strict
comparators; four positively sealed lifecycle checks plus backend/fast-path
attestation; all12-body fresh proofs and controls; equivalent ordered drives;
full profile; then three quiet four-arm baseline/candidate/CPython/PyPy rounds
with recorded/rotated physical-core assignments and launch order. performance.py
retains all samples and rejects a candidate unless every round improves and
median candidate/baseline CPU <=0.95. No microbenchmark-only merge or PyPy-win claim.

After every canonical producer, performance child and supervisor exits, run the
supplemental post-exit audit and seal a new exclusive ledger with validate.py.
Existing #6 limits and later A700/owner-run engine-milestone review remain, ref-121
preserved. No original bytes/state/tables/checkpoints are committed here.
