# T09 speaker/noise incremental port

## Owner-approved incremental port

The owner clarified the incremental Python-to-Rust objective and explicitly
authorized merging T09 on 2026-11-01. The contract was amended on main in
981335f: a faithful native subtree need not deliver 5% whole-match improvement.
All three candidate rounds are faster; the median uses **4.28% less CPU**.
All fidelity, original-guard, complete-sample and exact-head CI gates remain.
See docs/porting-acceptance.md and docs/tasks/T09.md.

The original <=0.95 optimization gate failed and its validator/receipts remain
unchanged. Historical rejected-validation-v1.json still records that old outcome
and binds 150 evidence files. **owner-acceptance-v2.json** separately accepts the
same runtime artifact under the owner's amended incremental-port contract,
rehashing the original evidence and source/binary/input bindings. No samples,
failures or private data are removed. No new runtime or oracle change is made.
All experiment groups have exited; no experiment is restarted for this amendment.
Live exact-head CI/merge/checkpoint state is in PR #25 / issue #1.

## Every paired timing sample

Three quiet simultaneous preserved-T08/candidate/plain CPython/PyPy rounds,
distinct physical cores and rotated assignments/launch order, original guards.
Every raw output/result/record/full memory agrees. No round is discarded.

| Round | T08 CPU s | Candidate CPU s | CPython CPU s | PyPy CPU s | Candidate/T08 |
| --- | --- | --- | --- | --- | --- |
| 1 | 67.431070 | 66.254678 | 134.097425 | 47.926957 | 0.982554150 |
| 2 | 68.596781 | 65.661157 | 134.685213 | 48.492371 | 0.957204635 |
| 3 | 71.044258 | 65.452921 | 146.591200 | 49.177802 | 0.921297841 |

Median paired CPython speed: 2.051x. Candidate/PyPy CPU: 1.354x;
**still slower than PyPy**. The earlier pilot's 5.30% gain did not repeat at the
original 5% three-round target. The measurements alone do not establish why samples
vary. This is one host/reference fixture, not a broad workload claim.

## Candidate and passing fidelity evidence

Four data-state bodies: 0791:94E8 -> 0791:94C9 -> 214B:0688, plus 214B:1E8D.
Six literal guest-call sites match the pinned source; existing omitted-hardware
stubs 214B:1EBC/0791:0425 remain delegated observable calls. No new hardware code
or oracle semantic fix. Native continuation finish preserves the seed routine's
cached returned value after its store, including later frame-finish AX restoration.

- Public 27 tests each on CPython/PyPy, Rust 11, 20 lifetime cases pass.
- 52,472 full-memory/all-register/ordered callback/frame comparisons equal:
  previous 12-body 40,024 + new 4-body 12,448 (eight real RAM captures/body,
  500 authored cases/body). All body/return controls are caught in intended scopes;
  unaffected isolated cases remain equal. Seed/DF and later stack mutations covered.
- 328 observer comparisons equal: 252 error cases, 16 variant fallbacks, 60 live
  return/store cases, including actual AX changes and tone state after speed changes.
- Exact ordered 831 events/result/records/full memory/553 stretches/full IO-site-
  listener digest agree, including 158,092,780 IO observations.
- Four sealed lifecycle checks pass, 11 independently attested Rust machines/all 16
  native bodies; strict ALL75/75 and exact-source F40 40/40 identical, with independent
  attestation of all 75 Rust machines. No raised timeout or reduced corpus.
- Profile: 16 native bodies, 1,556,593 native / 1,547,092 Python guest entries out of
  3,103,685 total. Exactly 205,799 entries moved from Python. This is a partial port;
  entry counts are not a whole-port completion percentage or exact FFI crossing count.

M2 index: m2-proof-v1.json. Rejection audit rehashes the full source/binary/private-
input/baseline/rejected-archive/harness/prefix evidence. Accepted 2cbeb36f/state-v2
and private T07 inputs unchanged. Actual baseline: .cache/T09-baseline/engine;
candidate binaries: .cache/T09-artifacts, indexed by artifact-archive-v1.json.

## Preserved attempts and limits

The register-descriptor prototype regressed setters and byte halves and was
rejected; source/binary/microbench remain, no factory active. Supplemental observer
harness v1 expected final AX 1111 after its store callback. Both backends agreed;
generic finish restores cached returned AX 8000. Failed source/log/diagnosis retained;
v2 checks that value plus the observed mutation, no production/equality change.
The baseline's failing-before native/body tests are also retained.

Do not restart completed v1 producers or overwrite receipts/rounds/baselines.
Any further runtime change needs fresh versioned artifact-bound fidelity and
timing proofs under its explicit task contract. Success-path process-closure.txt,
post-exit-audit.txt and write-assessment.txt were not used to assert acceptance;
the original validator demonstrably rejects its original 5% gate, and
rejected-audit.txt closes that historical outcome. Owner acceptance is separate. No original bytes/state/tables committed, no automatic
model review launched. Existing #6, later A700/ref-121/owner-run engine review and
goal2 integration/save-load/cancellation/playtest gates remain separate.
