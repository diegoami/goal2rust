# T23 Pascal string-write chunk

Status: all T23 fidelity and final selected quiet-measurement gates pass.
Exact-head CI, merge, main CI and merged audit status live in checkpoint #1.
Performance is mixed: two selected rounds improve and one regresses.

## Translation and source semantics

At accepted oracle `2cbeb36fdd3feb369324aaa88e6e4d2aa3b3d99c`, the three complete
caller/helper trees are runtime.sys_str_store `23E4:062A`, sys_str_store_max
`23E4:0644` and sys_str_concat `23E4:06B7`, with shared `_copy_forward` and
`str_concat`. There are zero guest calls or applicable guest-return controls.
The first/third exports read four input words but return with `retf 4`; the
bounded export uses `retf 10`. No enter/leave or invented flags/guest call appears.
Nondefault variants remain Python.

The implementation preserves the source's conditional read-ahead snapshot for
copies longer than eight bytes with no offset wrap and disjoint linear ranges.
Other copies read each byte live immediately before its write, retaining overlap
propagation and segment-offset wrap. Unmasked helper-entry offsets such as65536
remain meaningful to that predicate. Concatenation keeps the wrapped intermediate
length write before saturation; captured lengths survive callbacks. Its AX read
occurs after those writes, while assignment captures AX before its length write.
DF is cleared at the late flag store, preserving other live flag bits.

A pure untapped `Host::read_snapshot` captures one checked source block without
Python callbacks while borrowed; `Regs::cld` caches the DF mask until `store`.
Existing body/bridge paths retain their behavior. Contract:contract.md and
inventory-v1.json; all seven inventoried source body/helper code objects are
included in the first canonical scoped-closure probe.

## Comparator and artifact preservation

Before builds, all661 accepted T22 primary input/source/artifact bindings,
230 evidence hashes and two supplemental source bindings were verified.
Actual accepted T22 source/tests/adapter/CPython/PyPy artifacts are preserved in
.cache/T23-baseline(71 files). Historical.cache/T22-baseline is T21, not this
comparison's baseline. Both final interpreter builds/installs and both83-test
public preflights completed before candidate archive-v1 copied the two binaries
into.cache/T23-artifacts. freeze-v1 binds731 concrete files, including53 explicitly
allowlisted proof sources; generated reports are excluded. Private T07 state-v2,
tables and new eight-per-body captures remain ignored. No original bytes in git.

## Completed per-body evidence

| Proof | Result |
| --- | ---: |
| Fresh prior56 normal |164,312|
| New3 normal |6,288|
| Combined normal |170,600|
| Real-state schedules:3×8×4×3 |288|
| New body controls170–172 |6,288|
| AX/SI/DI/EFLAGS output controls173–184 |25,152:2,096 each|
| Guest-return controls |0 applicable:zero guest calls|
| Positive source branch/copy-mode pairs |480|
| Error comparisons |12,000|
| Error execution rows/distinct positively reached selectors |75 /75|
| Nondefault variants |48|
| All-inventory scoped closure |6,288|
| Seven live callback matrices |1,280 each|
| Public CPython /PyPy |83 /83 tests|
| Rust /GC /supplemental observer |11 /20 /328|

Every owned source/helper function has positive source witnesses. Native default
lifetimes execute zero owned Python code, with positive outside and nondefault
probes. All original prior56 controls/errors/branches/variants/closure assertions
remain. T22 offside replay now includes all14 inventoried bodies/helpers in its
canonical probe; shared source witnesses remain exactly s8=16,768,s16=176,064,
with zero native-lifetime owned calls. Its former additive proof is preserved.

The new live matrix positively distinguishes captured bulk data from later source
mutations, live overlap/wrapped reads, eight-versus-nine boundary behavior,
concat/store captured lengths versus AX timing, late flags and live SS arguments
with restoration before return. Branch evidence includes zero/eight/nine lengths,
forward/backward overlap, both wraps, unmasked65536, max-high-byte handling,
exact255 and unsigned saturation. Each selected program/ordinal error is reached;
ordinal controls sample early, middle and last-byte writes without claiming an
exhaustive global error or branch percentage.

## Complete full-match evidence

Exact ordered Rust/reference drive matches 831 events,553 stretches,result,
records and full memory. Ordered observers match158,092,780 IO,114,492 listener
enters/leaves,81,134 site enters/leaves and4 writes,digest
`096f56c262844705a0fcf7348fa4563c40e7d3ff4554b05c5224ffb0a7080ea9`.
All four sealed lifecycle gates pass with11 independently attested Rust machines
and all59 bodies. All75 admitted corpus records complete without errors; strict
ALL and exact-source F40 comparisons pass. Independent family attestation counts
75 Rust machines/all59 bodies. Immutable10/20/30/60 snapshots/comparisons pass.

The full profile confirms59/422 registered nonstub bodies(13.98% equal-weight
count),2,610,122 native/493,563 Python entries of3,103,685 total:
84.09751634% native fixture entry frequency.16,532 entries moved. These are
not source-line,CPU-time,global test coverage or whole-port completion.

## Rejected original performance campaign

All three complete v1 four-arm rounds remain preserved. The third CPython arm
started quiet but ended at load19.886/11.277(1/5-minute averages), after the
Rust/PyPy arms had ended. Its243.729 CPU seconds reflect late interference;
the campaign is rejected for quiet-host performance acceptance. No arm or round
was selectively replaced. The original v1 validator checks pre-round quietness
only; its immutable pass ledger is historical fidelity/binding evidence, not
the final performance selection. See rejected-performance-v1.json.

| Round | Saved T22 CPU s | T23 CPU s | CPython CPU s | PyPy CPU s |
| --- | ---: | ---: | ---: | ---: |
| 1 | 32.105415422 | 32.947827319 | 130.105894326 | 51.185619996 |
| 2 | 32.530788156 | 32.174328488 | 130.916722591 | 51.945380090 |
| 3 | 36.546153115 | 34.840682145 | 243.729066469 | 50.936311046 |

| Round | Saved T22 / PyPy | T23 / PyPy | T23 / saved T22 |
| --- | ---: | ---: | ---: |
| 1 | 0.627235060 | 0.643693040 | 1.026238935 |
| 2 | 0.626249882 | 0.619387681 | 0.989042391 |
| 3 | 0.717487238 | 0.684004818 | 0.953333776 |
| Median of per-round ratios | 0.627235060 | 0.643693040 | 0.989042391 |

The full three-round campaign was repeated on the SAME unchanged artifact and
saved baseline. After all original writers/controller exited, the
performance-resume-inputs-v2 manifest sealed two additive measurement/validation
sources and five immutable input hashes before execution. All731 primary
bindings and53 canonical proof sources stayed fixed. No production change,
rebuild or original receipt edit occurred.

## Selected complete quiet repeat(v2)

The repeat retained the original three pre-round quiet observations, added every
arm's before/after max1/5-minute load<4, and sampled total load every5 seconds
with a ceiling8(accounting for up to4 owned arms plus the original pre-round
budget). All three complete rounds pass all quality checks. Physical cores and
launch order rotate. Every output matches the original reference.

| Round | Saved T22 CPU s | T23 CPU s | CPython CPU s | PyPy CPU s |
| --- | ---: | ---: | ---: | ---: |
| 1 | 31.084269851 | 30.548661189 | 126.945715982 | 45.051140862 |
| 2 | 30.285107941 | 31.198123932 | 134.533105879 | 45.921156182 |
| 3 | 31.601463782 | 31.404579839 | 132.363025611 | 47.766040015 |

| Round | Saved T22 / PyPy | T23 / PyPy | T23 / saved T22 |
| --- | ---: | ---: | ---: |
| 1 | 0.689977418 | 0.678088515 | 0.982769141 |
| 2 | 0.659502296 | 0.679384548 | 1.030147358 |
| 3 | 0.661588521 | 0.657466682 | 0.993769784 |
| Median of per-round ratios | 0.661588521 | 0.678088515 | 0.993769784 |

The median paired T23/T22 CPU ratio is0.993769784072, or0.62%
less CPU. Rounds1 and3 improve; round2 uses3.01% more CPU. This does not
establish a repeatable speed gain. The predeclared incremental translation
contract requires full fidelity and complete measurements, without an arbitrary
5% floor or an all-round speed gate. No such criterion was added or removed
after seeing the result.

Same-campaign saved T22/PyPy median0.661588521 means
33.84% less CPU; T23/PyPy median
0.678088515 means32.19% less.
CPython/T23 median speed ratio:4.214768237.
Each median is computed independently from its column; do not divide independent
medians or compare historical standalone PyPy gaps as a trend. The mixed paired
outcome and all raw samples take precedence over a single headline percentage.

## Final ledger and process closure

validation-final-v2 selects performance-v2 and preserves/rechecks the original
fidelity ledger plus every original evidence hash.731 primary bindings,
263 complete evidence hashes,two additive source bindings and five supplemental
input hashes pass. The original v1 ledger/rejection/source manifest are all
bound into final evidence. The baseline-input audit maps all661 accepted T22
primary bindings to the actual saved snapshot/unchanged inputs,checks230 old
evidence hashes and its two supplemental sources,older source/profile/archive
bindings and all original before/after native-presence witnesses. New repeat
receipts independently confirm56 baseline versus59 candidate native bodies.

All82 original canonical+12 original timing groups/controller exited; the
repeat's12 arms and measurement process also exited:107 checked process groups.
Both closure checks use the actual host namespace. The final selected validator
and merged-audit template retain every original source/corpus/control guard,
artifact and receipt. No original data enters git. CI/merge/stop status lives in
checkpoint #1/PR #55. No following task is selected here.

## Limits

One fixture's performance is not broad workload/adoption evidence. The hybrid
still invokes Python and retains interpreter-dependent/GIL state; UI-thread
safety and GIL release are not established. Engine A700/ref-121/owner milestone
review,issue6 and application pipe/worker/save-load/cancellation/platform ABI/
loading/packaging/playtest gates remain separate. Upstream T159 supplies the
engine-pipe contract; this task does not integrate Rust into the application.
Goal2's UI foundation and archaeology's static T118a/F039(PROPOSED) findings do
not change the controlled2cbeb36f engine semantics or justify skipping gates.
