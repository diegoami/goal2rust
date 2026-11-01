# T14 player-update incremental port

One complete caller motion.update_player 0791:8AE9 now runs in Rust, finite 11
handlers+5 fixed calls/16 registered delegated boundaries. Captured frameBP,
off/seg/LINEAR record+code addresses/localAX/kept versus live contents and
conditional reads match source. Captured yieldAX is used after 2CEC/2AD4/869F,
not actual bank changes after capture. Fatigue returns integer 0; normal return None
leaves Sprite AX/DX. Exact immediate frame/stack/write/observer/flag/ABI and variant
fallback; no callee/hardware implementation claim. Same 2cbeb36f/private state-v2.

21 native bodies/1,828,188 native guest entries, 1,275,497 Python of 3,103,685 total;
75,781 moved. Partial port, not a code-completion percentage.

## Every paired measurement

Three quiet simultaneous saved T13/candidate/plainCPython/PyPy rounds, distinct
physical cores/rotated assignment+launch/original guards. Every raw output agrees,
every sample retained; all rounds faster: True. No arbitrary 5%
per-increment floor or broad workload claim.

| Round | T13 CPU s | Candidate CPU s | CPython CPU s | PyPy CPU s | Candidate/T13 |
| --- | --- | --- | --- | --- | --- |
| 1 | 57.316421 | 56.963344 | 163.004059 | 53.941406 | 0.993839860 |
| 2 | 63.893773 | 62.240639 | 149.893834 | 58.494388 | 0.974126833 |
| 3 | 71.153535 | 70.305155 | 158.217184 | 68.299580 | 0.988076768 |

Median **0.988076768 = 1.19% less CPU** versus T13. Paired CPython speed
**2.408x**, candidate/PyPy CPU **1.056x**.
Still slower than PyPy.
Pilot 0.99941269 was essentially tied and diagnostic only, not proof of gain.
One host/fixture, no speculative explanation for sample variation or historical
different-time absolute timing comparisons.

## Fidelity and closure

Public 44 each CPython/PyPy, Rust 11/GC20 pass. 62,952 normal full-state comparisons
across 21 bodies, 13,786 error cases and 328 speaker observers agree; every scoped
control caught. New 2096 cases (8 actual RAM entries/500 authored/four tap-listener
modes)/6720 errors, positive/all 16 dispatch+return/target/6 writes/value0/None/path
coverage. Captured args/BP/state/code/SENT/kept versus live play/counter/fatigue/
record contents/conditional rereads, linear64K crossing/farptr-span/basewrap,
static-link/dead-stack/full waiting ABI/pause/direct done/variant/errors match.
Controlled registered ABI bodies test caller only; actual admitted tests use actual
source callees. First runtime build/private proof epoch pass, baseline fails only
new native-coverage assertion; no runtime/test/source-binding fix or overwritten
historical receipt. Existing previous failures remain preserved.

Exact ordered 831 events/result/records/full memory/553 stretches/full callback
digest identical (158,092,780 IO observations). 4 positive-denial lifecycle checks/
11 Rust machines; strict ALL75/75/exact-sourceF40 40/40 identical, 75-machine backend
attestation/all 21 bodies. Authoritative **validation-v1.json**, 157
recursive evidence files, post-exit-audit-v1.json and actual-host process-closure-
v1.json. Supervisor exited/50 empty groups (36 canonical/12 timing/2 pilot), full
source/binary/input/baseline/archive/harness/prefix/proof/observer binding rehash.
Actual T13 baseline .cache/T14-baseline/engine/candidate .cache/T14-artifacts, manifests.
No original bytes/state/tables committed, oracle semantic fix or automatic review.
Existing #6/A700/ref-121/owner-run engine milestone review and goal2 integration/
save-load/cancellation/playtest remain separate. Live CI/merge/stop PR #35/
checkpoint #1, no next task included.
