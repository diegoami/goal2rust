# T16 player run-step and inline movement

The complete `pilot.player_run_step` body (0791:8889, ret 2) and its inline
movement/random/set/attack/side/keeper/target helpers run in Rust. The accepted
source is a plain function with no guest calls or frame prologue. No callee
frames, guest returns, register assignments or retry cap are invented. Parent
frame/linear record, captured dx/dy/random value, live contents/pointers, signed
arithmetic, pitch/picture blocking and every seed/movement write preserve source.
Variants stay Python; 86D0 is an inline helper, not a separately registered native
body. Same accepted 2cbeb36f / private T07 state-v2. No hardware claim.

23 native bodies cover 1,979,912 guest entries, leaving 1,123,773 Python entries
of 3,103,685 total on the fixture. 75,781 entries moved. This remains a partial
port, not a code-completion percentage.

## Every timing outcome

Three quiet simultaneous saved T15/candidate/plain CPython/PyPy rounds use
separate physical cores and rotated launch/core assignment. Every raw output
agrees and every sample is retained; no per-increment magnitude floor.

| Round | T15 CPU s | Candidate CPU s | CPython CPU s | PyPy CPU s | Candidate/T15 |
| --- | --- | --- | --- | --- | --- |
| 1 | 57.634325 | 54.399139 | 136.981814 | 50.360430 | 0.943867034 |
| 2 | 52.135412 | 50.769203 | 134.600600 | 47.334061 | 0.973795003 |
| 3 | 53.854225 | 51.143519 | 134.340239 | 47.857348 | 0.949665871 |

Median candidate/T15 **0.949665871**, **5.03% less CPU**. All three rounds improve. Paired CPython speed **2.627x**; candidate/PyPy
CPU **1.073x**. Still slower than PyPy.
The pilot is diagnostic only. One host/fixture; no broad workload or historical
absolute timing comparison.

## Fidelity and closure

50 public tests pass under each CPython/PyPy, with 11 Rust tests and 20 GC cases.
Fresh 23-body corpus: 67,144 normal full-state comparisons and 19,586 error
comparisons agree, with scoped controls detected. The new body contributes 2,096
positive comparisons (eight actual RAM entries and 500 authored inputs in four
observer modes), 2,560 error comparisons, all 13 write sites, both coin choices/
axis orders, offside adjustment, all four steps and retries. All five observer
mutation classes are positive. Body24 and position25 controls differ in all
2,096 cases. There is no guest-return control because no guest call exists.

An additional 160 traced source/native comparisons require every source offside
skip and movement acceptance/rejection branch, including both holders, to be
reached. Source-line/return tracing changes no source bytes and is excluded from
timings. The 328 supplemental speaker observers also agree (488 supplemental
comparisons total). Capture/live pointer/delta/seed behavior, full memory/all
registers/ordered observers/errors, direct done, entry pause and variants agree.
Initial synthetic stack/record overlap and an unreachable retry mutation were
corrected before canonical freeze; logs are preserved. The corrected saved T15
baseline fails only the new native-coverage assertion. First runtime build and
canonical private epoch pass without runtime changes.

Exact ordered full drive agrees on 831 events, 553 stretches, result, records,
full memory and callback digest. Four positive-denial sealed lifecycle checks /
11 independently attested machines, strict ALL75/75 and exact-source F40 40/40
agree, with 75 independently attested Rust machines / all 23 bodies. Baseline,
archives, pristine oracle harness and strict completed prefixes are rehashed.

Authoritative `validation-v1.json` binds 169
evidence files and 324 source/artifact/input hashes.
Supplemental post-exit-audit and actual-host process-closure receipts pass.
Supervisor exited; all 56 groups are empty (42 canonical, 12 timing, two pilot).
Bound sources, binaries and private inputs stayed fixed throughout canonical
proofs/measurements; every completed receipt is preserved.

Actual T15 baseline `.cache/T16-baseline/engine`, candidate `.cache/T16-artifacts`,
with hash manifests. No original bytes/state/tables committed, oracle semantic
change or automatic review. Existing #6, A700/ref-121, owner-run engine milestone
review and application integration/save-load/cancellation/playtest remain
separate. Live merge/CI/stop status: PR #39 / checkpoint #1. No next task included.

Upstream at completion: archaeology 2a411f5 unchanged; goal2 0ea62a7 (PR #499)
improves test-progress reporting only. No accepted oracle or roadmap change.
