# T06: native effective skill tree

All unchanged task gates pass. PR #19 / checkpoint #1 hold live merge and
stop/resume status. Accepted oracle remains
e0270981883f02ce46a31391e7070079977bbfef; T05 evidence and archived binaries
are preserved. Goal2's newer adoption/table-policy documentation was audited;
its exception does not amend goal2rust's private-input rule. No original bytes,
state, saves or tables are committed here.

## Implementation and selection

Effective skill 0791:278A and its only guest callee 1771:3A06 now execute as a
native caller continuation and native leaf. This is an approved roadmap
prerequisite for later contest trees. The refreshed T05 profile records 23,342
starts in each body. The hotter keyboard poll reaches a much larger menu closure.
The source inventory and exact register/stack contract are in contract.md.

The caller retains off/seg/element/base in explicit Rust continuation fields.
It consumes the dispatcher's captured AX, preserving Python semantics when
callbacks overwrite guest arguments/base or change AX after capture. The callee
reproduces immediate Mem.Frame writes and SP/BP updates with distinct instruction
sites. The source's inline keeper membership operation retains its five pushed
words and register effects. All guest boundaries, variants, callbacks, suspension,
replay and completion behavior remain observable. Nondefault variants stay Python.

## Artifact-bound correctness

| Gate | Result |
| --- | --- |
| Public tests | 19 pass on CPython and PyPy; 11 Rust tests pass. Includes direct leaf bodies, retained state, captured AX, errors, pauses/replay, variants and completion callbacks. |
| Differential | 6,224/6,224 full-state/body/frame/boundary comparisons equal: eight real captures per routine, 500 synthetic inputs per routine, tap/listener/continuation and direct-leaf-body modes. |
| Mutated callback inputs | 400 executed saved-argument/base mutations and 144 AX-after-capture mutations agree with Python. |
| Body control5 | Retained leaf local-word corruption caught in all 6,224 comparisons. |
| Root-return control6 | Saved 27EB IP corruption caught in all 2,096 caller comparisons; the 4,128 isolated leaf comparisons remain equal, as expected. |
| Ordered drive | All 831 events, result, returned records, full memory, 553 stretches and complete IO/site/listener stream equal. |
| Sealed lifecycle | Engine, interactive save/load, goals and knockout/replay pass under positive original-file/Unicorn denial. Independent attestation: 11 Rust machines, 487,636 executions of each new body. |
| F40 | Strict unchanged comparator: 40/40 expected IDs identical, zero failures, original guards. Independently attested all 40 Rust machines, 1,732,351 executions of each new body. |
| Final ledger | validation-v1.json binds canonical source/binaries and recursive evidence after all 11 producers and supervisor exited; every producer process group empty. |

The complete stream retains
`afcb5ec2ad3800a7d969f8cda6a513577d3e39feff886a441a48cbd814d0f191`:
158,092,780 IO calls, 114,492 listener pairs, 81,134 site pairs, four writes.
The supplemental post-exit audit verifies the pristine pinned oracle/harness,
10/20/30-match prefixes and line hashes, old/new archives, public proof counts,
controls and executed callback-mutation counts. Its immutable source is
post-exit-audit.txt, result post-exit-audit-v1.json. Measured extensions are
preserved by digest under ignored .cache/T06-artifacts; see artifact-archive-v1.json.

## Profile and scope

Total guest entries remain 3,103,685. Native entries rise to **1,350,794 across
12 default bodies**. Remaining Python entries fall from 1,799,575 to
**1,752,891**, removing 46,684 (2.59% of T05's remaining entries). Both new bodies
have zero Python calls/resumptions, formerly 70,026 combined. These are diagnostic
counts, not exact FFI crossings or an uninstrumented speed estimate.

The profile has 422 registered non-stub routine addresses: 12 default bodies native,
410 remaining on the bridge. Native bodies account for 43.5% of guest entries in
this reference drive. This is execution frequency; body sizes vary, core execution
machinery is a separate port, and surrounding-game translation remains ahead.
There is no defensible whole-port completion percentage from these counts.

## Quiet paired performance

All correctness producers finished before three quiet observations (both 1m/5m
load below 4), then plain CPython/PyPy/Rust drives started together. Outputs and
source bindings agree; default 60-second stretch guards remain unchanged.

| Backend | CPU seconds |
| --- | ---: |
| Plain CPython | 139.233 |
| Plain PyPy | 46.582 |
| Rust machine, twelve native bodies, CPython bridge | 93.558 |

Rust is **1.488x CPython speed** and uses **2.008x PyPy CPU** in this
pair. It has not beaten PyPy. One pair is not a distribution, and the different-time
T05 receipts do not establish a controlled incremental speed change. No speed
claim comes from cProfile or entry counts; the measured outcome is retained.

## Limits and handoff

Baseline native-root/direct-leaf assertions fail before implementation; that
expected log is preserved. The first production implementation passed the new
public tests; no equality or Done-when assertion was weakened. All controls,
logs and receipts remain immutable. Do not restart completed producers or
silently reuse these receipts after a source or binary change.

This accepts one subtree. ALL75/A700 and owner-run review remain later engine-
milestone gates, preserving known ref-121 noncompletion. T03's ALL75 is not
relabelled as proof of this artifact. Existing #6 isolation/allocator/coverage
limits remain; compare backend factories in separate processes. No later native
tree or oracle update started and no automatic model review was launched.
