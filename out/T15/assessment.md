# T15 player sprite caller

The complete `motion.move_player_sprite` caller (0791:8537, retf 4) runs in Rust.
Five registered callee boundaries remain delegated. Immediate frame, captured
linear record and sentinel, live record/picture pointers/DS argument, signed
coordinate arithmetic, conditional reads and captured yield replies preserve the
source. Old-cell restoration, held sprite selection, keeper interception and ball
movement/clamps remain observable. Variants stay Python. No transitive callee or
hardware implementation claim. Same accepted 2cbeb36f and private T07 state-v2.

22 native bodies cover 1,904,131 guest entries, leaving 1,199,554 Python entries
of 3,103,685 total on the fixture. 75,943 entries moved; this is a partial port,
not a code-completion percentage.

## Every timing outcome

Three quiet simultaneous four-arm rounds use saved T14/candidate/plain CPython/
PyPy, distinct physical cores and rotated core/launch assignment. Raw outputs
agree and every sample is retained. No per-increment magnitude floor.

| Round | T14 CPU s | Candidate CPU s | CPython CPU s | PyPy CPU s | Candidate/T14 |
| --- | --- | --- | --- | --- | --- |
| 1 | 68.298596 | 65.625362 | 149.934165 | 60.896538 | 0.960859606 |
| 2 | 56.834864 | 54.180898 | 138.183820 | 52.044008 | 0.953303900 |
| 3 | 59.322741 | 58.356357 | 141.816364 | 56.204254 | 0.983709726 |

Median candidate/T14 **0.960859606**, **3.91% less CPU**. All three rounds improve. Paired CPython speed **2.430x**; candidate/PyPy CPU
**1.041x**. Still slower than PyPy.
The pilot is diagnostic only. One host/fixture; no broad workload claim or
comparison of absolute timings across historical campaigns.

## Fidelity and closure

47 public tests pass under each CPython and PyPy, with 11 Rust tests and 20 GC
checks. Fresh 22-body corpus: 65,048 normal full-state comparisons, 17,026 error
comparisons and 328 supplemental observer cases agree, with scoped controls
caught. The new caller contributes 2,096 positive comparisons (eight captured
RAM entries plus 500 authored inputs in four observer modes), 3,240 errors,
all five targets/returns and ten write sites, including signed/wrapping/linear
boundary arithmetic, captured versus live mutations, reply clobbers, waiting ABI,
pause/resume, direct done and variant fallback. Both controls differ in all
2,096 positive cases. Controlled ABI doubles scope the caller proof; full drive,
lifecycle and family tests execute actual source callees.

The exact ordered full drive agrees on 831 events, 553 stretches, result,
records, full memory and all callbacks. Four positive-denial lifecycle checks
and 11 independently attested Rust machines pass. Strict ALL75/75 and exact-source
F40 40/40 agree, with 75-machine Rust attestation and all 22 native bodies.

Authoritative `validation-v1.json` binds 165 evidence files
and 300 source/artifact/input hashes. Supplemental
`post-exit-audit-v1.json` and actual-host `process-closure-v1.json` pass. Supervisor
exited; all 53 groups are empty (39 canonical, 12 timing, two pilot). Baseline,
archives, pristine upstream harness and strict family prefixes are rehashed.
No source or binary changed during canonical proofs or measurements; completed
receipts remain preserved. Initial compile API mistake and an authored missing
clamp case were corrected before the canonical epoch; their logs are preserved.
All canonical proofs passed without runtime changes.

T14 baseline `.cache/T15-baseline/engine`, candidate `.cache/T15-artifacts`, with
hash manifests. No original bytes/state/tables committed, oracle semantic fix or
automatic review. Existing #6, A700/ref-121, owner-run engine milestone review,
application integration/save-load/cancellation/playtest remain separate. Live
merge/CI/stop status is in PR #37 and checkpoint #1. No next task included.
