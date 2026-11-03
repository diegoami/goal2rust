# T23 Pascal string-write chunk

Status: all per-body/inherited fidelity and exact ordered full-drive proofs pass.
Sealed lifecycle and full profile also pass. ALL75/F40, timings and final audits
remain pending.
No T23 speed result is claimed.

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

## Remaining gates and limits

The full ordered Rust/reference drive matches831 events,553 stretches, result,
records and full memory. Ordered observers match158,092,780 IO,114,492 listener
enters/leaves,81,134 site enters/leaves and4 writes, digest
`096f56c262844705a0fcf7348fa4563c40e7d3ff4554b05c5224ffb0a7080ea9`.
The native drive independently observes all59 bodies and2,610,122 native entries.
Instrumentation elapsed/CPU time is no uninstrumented performance claim.

All four sealed lifecycle gates pass with11 independently attested Rust machines
and all59 bodies. The full profile confirms59 bodies,2,610,122 native entries
and493,563 Python of3,103,685 total(84.09751634% native fixture frequency).

Strict ALL75/exact-source
F40 with10/20/30/60 immutable prefix comparisons, independent backend attestation
and full profile remain. Three quiet simultaneous rotated saved-T22/candidate/
CPython/PyPy rounds must retain every outcome, including regressions. Report raw
CPU seconds and medians of per-round ratios, with baseline/PyPy alongside
candidate/PyPy; no arbitrary incremental5% floor or pilot-only speed claim.
Final source/input/binary/evidence/archive/baseline and actual-host shutdown
audits, exact-head CI/squash/mainCI/merged bindings/checkpoint complete the task.

Routine counts and fixture guest-entry frequency are not source-line, CPU-time,
global test coverage or whole-port completion. The hybrid still invokes Python,
holds interpreter-dependent state and does not establish GIL-release/UI-thread
safety. Engine A700/ref-121/owner milestone review,issue6 and application pipe/
worker/save-load/cancellation/platform ABI/loading/packaging/playtest gates remain
separate. Upstream T159 provides the engine-pipe contract; this task does not
integrate Rust into the application. Select any following task separately from
the fresh remaining-work profile.
