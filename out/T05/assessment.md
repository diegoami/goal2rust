# T05: native nearest-to-ball tree

All unchanged task gates pass. PR #17 / checkpoint #1 hold live merge and
stop/resume status. Oracle remains e0270981883f02ce46a31391e7070079977bbfef;
T04's historical evidence and archived binaries remain intact.

## Implementation and selection

0791:2FB1 (`ball.find_nearest_to_ball`, near ret, no args) now runs as four
Rust continuation phases through the existing guest issue/return dispatcher.
Its closure was already native: availability 2956 -> 3216 and direction 2BE5.
All guest frames, three return sites, stack locals, the live word across two
direction calls, signed arithmetic, strict tie handling, sites, callbacks and
suspension/replay remain observable. Nondefault variants use the bridge.
Inventory: contract.md; source origin: PROVENANCE.md.

T04's refreshed profile selected this root for highest remaining registered
body self time and 298,641 Python calls/resumptions from 5,147 starts. T05's
profile preserves the 3,103,685 total guest entries and all match outputs,
records 1,304,110 native entries across ten bodies, and leaves **1,799,575**
Python guest entries. The root now has zero Python calls/resumptions.
The 5,147-entry reduction is 0.285% of T04's remaining entries; eliminating
repeated continuations is a separate diagnostic fact, not an exact FFI count.

The profile has 422 registered non-stub routine addresses, of which ten default
bodies are native. Native entries represent about 42% of this drive's calls,
not 42% of engine code. Most match logic and all surrounding-game translation
remain ahead; neither address counts nor call frequency give a whole-port
completion percentage. Core memory/register/dispatcher/frame machinery is Rust;
other bodies and kit/API callbacks still use Python.

## Artifact-bound correctness

| Gate | Result |
| --- | --- |
| Public tests | 16 pass on CPython and PyPy; 11 Rust tests pass. Boundary/final memory and registers, all continuation sites, pauses/replay, errors, variants and done callbacks included. |
| Differential | 2,128/2,128 equal: eight real captures x four tap/listener modes x four pauses (128), plus 500 authored random/edge inputs x four modes (2,000). Full state is observed at call/return boundaries and completion. |
| Body control3 | Skipping side0 is caught in all 2,128 comparisons. |
| Root-return control4 | Corrupting this root's saved return IP, while nested availability returns remain correct, is caught in all 2,128. |
| Nested errors | 20 authored error/valid-neighbor cases agree on errors, complete partial state and the two waiting native frames. |
| Ordered drive | All 831 events, result, returned records, full memory, 553 stretches and complete ordered IO/site/listener stream equal. |
| Sealed lifecycle | Engine, interactive save/load, goals and knockout/replay pass under upstream's positive original-file/Unicorn denial. Independent attestation: 11 Rust machines / 88,940 new-root entries. |
| F40 | Strict unchanged comparator: all 40 expected IDs identical, zero failures, original limits. Independent attestation: 40 Rust machines / 301,778 new-root entries. |
| Final ledger | validation-v1.json seals canonical source/binary bindings and recursive evidence after all 11 producers and supervisor exited; every producer process group empty. |

The complete stream retains hash
`afcb5ec2ad3800a7d969f8cda6a513577d3e39feff886a441a48cbd814d0f191`:
158,092,780 IO calls, 114,492 listener pairs, 81,134 site pairs and four writes.
The supplemental post-exit audit verifies the pristine pinned oracle/harness,
10/20/30-match source prefixes and line hashes, T04/T05 binary archives,
public proof counts and the nested-error evidence. Its immutable source is
post-exit-audit.txt; result post-exit-audit-v1.json. No original bytes are tracked.

## Quiet paired CPU

All correctness jobs finished before three quiet observations (both 1m/5m load
below 4), then plain CPython/PyPy/Rust drives started together. All outputs and
source bindings agree; default 60-second stretch guards remain.

| Backend | CPU seconds |
| --- | ---: |
| Plain CPython | 137.239 |
| Plain PyPy | 49.243 |
| Rust machine / ten native bodies / CPython bridge | 92.484 |

Rust is **1.484x CPython speed** and uses **1.878x PyPy CPU** in this
pair. It has not beaten PyPy. This is one pair, not a distribution or a controlled
incremental speed claim versus T04's different-time receipts. No speed gain is
inferred from cProfile or guest-entry counts.

## Limits and handoff

The baseline native-root assertion fails before translation, while bridge state
equality already passes; that log is retained. Production compiled and passed
the new public tests on its first implementation attempt. Mutant differences
are expected controls; all logs/receipts remain immutable. Measured artifacts
are archived by digest in ignored .cache/T05-artifacts; locations are in
artifact-archive-v1.json. Do not restart completed producers or overwrite receipts.

This accepts one subtree, not the full engine or game. ALL75/A700 and owner-run
review remain later engine-milestone gates, with known ref-121 noncompletion
preserved. Historical T03 ALL75 is not relabelled as proof of this artifact.
Existing #6 adapter/allocator limits remain; compare backends in separate workers.
No later tree or oracle upgrade started; no automatic model review launched.
