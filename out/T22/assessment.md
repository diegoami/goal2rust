# T22 offside-line display tree

Status: all T22 fidelity, complete measurement and final audit gates pass.
Live exact-head CI, merge, main CI and merged binding audit status is in checkpoint #1.
Performance is mixed: two rounds improve and one regresses.

## Translation

At accepted oracle 2cbeb36fdd3feb369324aaa88e6e4d2aa3b3d99c, the complete tree is
motion.track_offside_line0791:8CF5, motion.move_sprite0791:8E24 and
motion.place_marker0791:90C5. Direction2BE5 was already native. Four real far
returns8D42/8DD0/8E17/9113 preserve the original guest/callback boundaries.
All inline record/cell/signed-byte/multiply helpers move with their owners.
Nondefault variants remain Python.

The tracking loop retains its captured first slot and direction, ten live player
rows per side, wrapped signed products and short-circuit marker selection. The
sprite retains separate live picture/background pointer reads, conditional old
cell restoration and captured-row AX/DX outputs. The marker retains live-SS
frame reads, its captured record pointer and captured AX/DX across callbacks.
No listing-only local writes, flag changes or new guest calls are invented.
Contract and helper inventory:contract.md and inventory-v1.json.

## Preserved comparator and artifact

Before builds, all 598 accepted T21 input/source/artifact and 214 evidence hashes
were checked. Actual accepted T21 source, tests, adapter and both interpreter
artifacts are preserved in.cache/T22-baseline, 69 bound files. Older
.cache/T21-baseline is T20 and is not the comparator. Both 81-test public
preflights completed before candidate archive-v1 copied both installed binaries
into.cache/T22-artifacts. freeze-v1 binds 661 concrete inputs/sources/binaries,
including 51 explicitly allowlisted proof sources; generated reports are excluded.
Private T07 state-v2/tables and new eight-per-body captures remain ignored.

An initial new-test fixture incorrectly entered near-returning8CF5 as a far
call. Its 129 failures, original harness and log are preserved in
rejected-offside-preflight-v1.log/rejected_offside_fixture_v1.py. The corrected
near entry passes with all assertions retained; no Rust semantic fix was needed.
Both complete public preflights and canonical public suites pass 81 tests each.

## Completed fidelity evidence

| Proof | Comparisons or result |
| --- | ---: |
| Fresh prior53 normal |154,024|
| New3 normal, actual and ABI-controlled callers |10,288|
| Combined normal |164,312|
| Real-state schedules:3×8×4×3 |288|
| New body controls161–163 |6,288|
| Separate sprite AX164/DX165 output controls |4,192:2,096 each|
| Four individual return controls166–169 |640, detection exactly when reached|
| Positive source branch/arithmetic/loop pairs |800|
| New error pairs |26,080|
| Error execution rows and distinct selectors |163 each, all positively reached|
| Nondefault variants |64|
| Scoped native-lifetime closure |6,288|
| Six callback matrices |1,280 each|
| Public CPython / PyPy |81 /81 tests|
| Rust / GC / supplemental observer |11 /20 /328|

Scoped checks find zero owned default Python body/helper executions inside native
lifetimes, with positive source/outside/nondefault probes. All prior controls,
error/branch/variant/closure assertions remain, including T19's supplemental
own-write selectors. Every source branch has positive witnesses; signed rows,
columns, cell-offset wrap, ten-player loop completion, high first slots and
marker arithmetic are explicitly observed. Each of the eight new live-callback
scenarios has positive mutation hits and effects; all five inherited matrices
remain. Normal, body/output/return controls have separate immutable receipts.

The exact full drive matches831 events,553 stretches, result, records and full
memory. Ordered observers match158,092,780 IO,114,492 listener enters/leaves,
81,134 site enters/leaves and 4 writes. Digest:
`096f56c262844705a0fcf7348fa4563c40e7d3ff4554b05c5224ffb0a7080ea9`.
The fresh full profile confirms 56 native bodies, 2,593,590 native entries and
510,095 Python entries of3,103,685 total(83.56485919% native fixture frequency).
All four sealed lifecycle gates pass;11 independently attested Rust machines
observe all 56 bodies.

## Full corpus, measurement and closure

All 75 admitted records complete without errors and strict ALL/exact-source F40
pass. Prefix10/20/30/60 line snapshots and strict comparisons are preserved.
Independent attestation identifies 75 Rust family machines and all 56 bodies.
The four lifecycle gates identify 11 Rust machines and all 56 bodies.

After every canonical writer/controller exited, the additive
shared_helper_closure.py expanded the in-memory probe set to all 14 inventoried
body/helper symbols, including shared mem.s8/mem.s16. All 6,288 scoped pairs
(96 real schedules+2,000 authored per body) pass exact full observations with
zero owned Python executions inside native lifetimes and positive outside/source
probes.64 nondefault probes also pass. Shared source witnesses: s8=16,768 and
s16=176,064. No production/canonical proof source or completed receipt changed.
The supplemental-source-inputs-v1 manifest seals both new proof/audit drivers
before execution; shared-helper-audit-v1 verifies their hashes and process exit.
The primary 661 bindings remain unchanged, with two separately bound additive
sources. Every original proof and receipt is retained.

Three complete quiet simultaneous four-arm rounds used the saved accepted T21
and combined T22 artifact on IT13, with rotated physical cores and launch order.
All outputs match. Every round and arm is preserved; none was replaced or rerun.

| Round | Saved T21 CPU s | T22 CPU s | CPython CPU s | PyPy CPU s |
| --- | ---: | ---: | ---: | ---: |
| 1 | 34.243726177 | 33.897704200 | 139.530337639 | 49.880048536 |
| 2 | 32.900132533 | 32.556201679 | 128.731062749 | 46.870304287 |
| 3 | 33.947988387 | 34.367455089 | 130.052128691 | 49.080292807 |

| Round | Saved T21 / PyPy | T22 / PyPy | T22 / saved T21 |
| --- | ---: | ---: | ---: |
| 1 | 0.686521509 | 0.679584427 | 0.989895318 |
| 2 | 0.701939811 | 0.694601884 | 0.989546217 |
| 3 | 0.691682678 | 0.700229219 | 1.012356158 |
| Median of per-round ratios | 0.691682678 | 0.694601884 | 0.989895318 |

The median paired T22/T21 ratio is0.989895317606, or1.01% less
CPU. Rounds 1 and 2 improve; round 3 uses1.24% more CPU. This campaign does
not establish a repeatable speed improvement. The predeclared translation
contract requires full fidelity and complete reported measurements; no all-round
speed gate or arbitrary5% magnitude minimum was introduced or removed.

Same-campaign T21/PyPy median0.691682678 means
30.83% less CPU; T22/PyPy median
0.694601884 means30.54% less.
The CPython/T22 median is3.954117990. Each column's
median is computed independently; here the three ratio medians select different
rounds. Do not divide those medians or compare a historical campaign's PyPy gap
as a trend. The mixed paired result and all raw samples take precedence over a
single headline percentage.

validation-final-v1 passes661 primary source/input/artifact bindings and 230
evidence hashes. post-exit and baseline-input audits pass, including all 598
accepted T21 bindings mapped to the saved snapshot/unchanged inputs,214 accepted
T21 evidence hashes, historical profiles and new-native before/after presence.
All 78 canonical+12 timing groups and controller exited. The additive proof's
separate group also exited; actual-host shared-helper audit checks all 91 groups
and controller. Historical artifact archives and every source/corpus guard are
preserved. Exact-head/main CI, merge and merged audit status live in checkpoint#1.
No next task is included.

## Limits

Routine count and reference-fixture entry frequency are distinct from source-line,
CPU-time, global branch/test coverage and whole-port completion. One fixture's
four-arm performance is not general workload/adoption evidence. Native-to-native
guests still use common dispatch; the hybrid invokes Python, retains GIL-related
state and does not establish UI-thread safety. Engine A700/ref-121/owner milestone
review, issue#6 and application protocol/worker/save-load/cancellation/target ABI/
loading/packaging/playtest gates remain separate. Upstream T158 now approves a
long-lived engine process, with Rust adopted inside it later; the controlled
oracle and Rust-in-parallel order are unchanged.
