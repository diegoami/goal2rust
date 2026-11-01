# T12 watched match sweep incremental port

One complete caller frame.watched_match_engine 0791:9564 now runs in Rust, including
its immediate Mem.Frame, 22-player sweep/nested loop, possession/holder/update/
speaker/draw/key flow, quick exit/wait decrement. Captured BP/DS/CS/slot/k/rec
remain distinct from live SS/stack-stop/register/ZF/memory. 17 static call sites/14
registered callees stay delegated/observable; no transitive callee/hardware claim.
Default variant only, others Python. Same 2cbeb36f/state-v2/private T07 inputs.

19 native bodies/1,716,209 native guest entries, 1,387,476 Python out of 3,103,685.
3494 Python entries moved; this is not a code-completion percentage. Generator
resumptions previously made this caller hot despite its relatively few starts.

## Complete measurements

Three quiet simultaneous saved T11/candidate/plainCPython/PyPy rounds, distinct
physical cores, rotated assignment/order, original guards, all outcomes retained
and all raw event/result/record/full-memory outputs identical. All rounds faster:
True. No arbitrary per-increment 5% floor.

| Round | T11 CPU s | Candidate CPU s | CPython CPU s | PyPy CPU s | Candidate/T11 |
| --- | --- | --- | --- | --- | --- |
| 1 | 72.311087 | 69.394922 | 154.263660 | 66.531917 | 0.959671957 |
| 2 | 69.032358 | 66.720488 | 148.497487 | 62.032187 | 0.966510350 |
| 3 | 64.932177 | 61.903104 | 145.225499 | 54.792929 | 0.953350203 |

Median **0.959671957 = 4.03% less CPU**; paired CPython speed **2.226x**,
candidate/PyPy CPU **1.076x**. Still slower than PyPy.
One host/reference fixture; pilot 0.97452040 diagnostic only, no speculative cause
of variance or comparisons with historical different-time absolute measurements.

## Fidelity and binding

Public 38 each CPython/PyPy, Rust 11, GC 20 pass. 58,760 full-state normal comparisons
across 19 bodies, 3306 error cases and 328 speaker observers agree; all scoped
body/return controls caught. New 2096 cases include 8 actual RAM captures/500 authored
inputs/four tap-listener combinations, 1888 errors, positive success/all 17 returns/
14 targets/12 writes, both 22 loops/early exits/underflow. CapturedBP/record/slot,
actualBP/local record/stop/play/returnAX/ZF mutations, near/far/full waiting ABI,
wrap/static-link/dead-push/frame/pause/direct done/variant/error observations match.
Controlled external ABI bodies test only caller continuations; actual full drives
use actual source callees. Initial fixture's full sweeps had wait 0 and missed 9703;
initial source/log retained, revised wait 1->FFFF before freeze covers it. No runtime
fix needed; first build and private proof epoch pass. Historical evidence retained.

Exact ordered 831 events/result/records/full memory/553 stretches/full IO-site-
listener digest (158,092,780 IO observations) identical. 4 positive-denial sealed
lifecycle checks/11 independent Rust machines, strict ALL75/75 and exact-source
F40 40/40 identical, 75-machine backend attestation/all 19 bodies. No guards raised.

Authoritative **validation-v1.json**, 153 evidence files, plus
post-exit-audit-v1.json and actual-host process-closure-v1.json: supervisor and 44
groups empty (30 canonical/12 timing/2 pilot). Full source/binary/input/baseline/
archive/harness/prefix/proof/observer binding rehash. Actual T11 baseline
.cache/T12-baseline/engine and candidate .cache/T12-artifacts, hash manifests.
No overwritten receipt/original game bytes/state/tables in git/oracle semantic fix/
automatic model review. Existing #6/laterA700/ref-121/owner-run engine milestone
review/goal2 integration/save-load/cancellation/playtest remain separate. Live
CI/merge/stop state PR #31/checkpoint #1. No next task included.
