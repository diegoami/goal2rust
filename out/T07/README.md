# T07 state-v2 compatibility refresh

## Validation complete

All required gates pass; see [assessment.md](assessment.md). Authoritative
post-writer ledger: **validation-v2.json**. The original historical-result
assumption/failed diagnostic is preserved; the identity-aware revision retains
every fresh-v2 gate and checks the complete historical result. All producer
and child groups have exited. Live merge/stop status is in PR #21 / checkpoint #1.
Do not restart completed producers or overwrite receipts. All invocation and
in-progress commands below are historical; future artifacts need new evidence.

Task #20 / PR #21, contract docs/tasks/T07.md. Accepted oracle PR640 merge
2cbeb36fdd3feb369324aaa88e6e4d2aa3b3d99c. Old e0270981 clone preserved under
.cache/goal2-archaeology-T06. T06's private inputs, receipts and archived binaries
remain historical; never overwrite them or relabel state-v1 as v2.

Input-audit-v1.json binds freshly extracted private .cache/T07-tables and
.cache/T07-state-v2-v1.json, verified against the registered source and manifest.
Two differing code-data bytes are carried; all translated routines/helpers and
machine/dispatcher files are unchanged. New public tests fail on the old pin;
22 public tests pass on CPython/PyPy. Upstream unit-v1 preserves an optional
registered-fixture skip; after placing that private fixture in the expected
ignored cache, unit-v2 passes all11 tests and read-map-v2 verifies it too.
Initial stale-local-origin fetch failure is preserved in preflight-v1.log;
accepted commits were fetched explicitly from official GitHub.

## Source/binary/input bindings and resume

Producers hash the exact engine/test/oracle/harness/proof sources and private
state/table inputs, including the installed interpreter extension. Native code
and measured extensions are reused unchanged from T06; copies are preserved by
digest under .cache/T07-artifacts. Nothing of the original enters tracked output.

Read checkpoint #1 and inspect every live process group before resuming.
.cache/T07-supervisor.lock guards the supervisor; jobs-v1.jsonl and
supervisor-v1.log append commands/PIDs/exits/progress. Never duplicate groups,
edit bound sources/rebuild during runs, or overwrite a completed/failed receipt.
Choose fresh versioned evidence and preserve all failures/default limits.

Historical candidate invocation, only if incomplete and no live group remains:

```sh
PYTHONHASHSEED=0 .venv/bin/python -u -B out/T07/supervise.py >> out/T07/supervisor-v1.log 2>&1
```

Stages: one ALL75 run supplies an exact F40 source-line selection, with separate
unchanged strict ALL/F40 comparisons; four positively sealed lifecycle checks
and independent Rust attestation; fresh per-call/full-frame legacy-seven proofs
and all three preserved tree suites, with body/return controls; equivalent
state-v2 ordered drives; full entry profile; quiet simultaneous CPython/PyPy/Rust
CPU. Only after all19 producers and supervisor exit, run the supplemental audit
and seal an exclusive ledger with validate.py.

V2 full-memory, records and tap hashes can differ from historical v1 because
the code-data overlay/schema changed. Compare every field between equivalent
fresh v2 machines, documenting the input delta; old receipts stay untouched.
No speed claim from schema changes/cProfile. Existing #6 limits remain; A700 and
owner-run engine-milestone review stay later gates, known ref-121 preserved.

## Historical result digest diagnostic

Fresh-v2 Python/Rust ordered results agree exactly. The old-v1 result digest
changed because it includes image_sha256. The preserved failed diagnostic is
historical-result-check-v1.log; the exact identity-continuity proof is
historical-result-bridge-v1.json, using independently reconstructed image hashes
and no omitted result keys. See contract-audit.md. Do not modify the frozen
original validate.py or canonical receipts. After all writers exit: run the
original validator and retain its expected result_sha256 failure in
validator-original-v1.log, run post-exit-audit.txt, then validate-v2.txt into the
exclusive validation-v2.json. That final ledger binds both validator versions.
