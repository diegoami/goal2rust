# Port complete, bounded call trees

[owner-approved, after T16] Recalibrate the next work around connected native
subtrees. The default unit is a complete execution path with its remaining
Python callees, rather than one registered routine per full validation campaign.
The engine-first / whole-game-later objective and accepted oracle are unchanged.

## Historical planning baseline after T16

T16 is accepted on main `b3ad14188454ef200b7cfa06500227b0de0a5723`.
Figures below come from `out/T16/profile-after-v1.json` at accepted oracle
`2cbeb36fdd3feb369324aaa88e6e4d2aa3b3d99c`. The data and formulas are recorded in
[the planning snapshot](plans/post-T16-baseline.json).

| Measure | T16 value | Interpretation |
| --- | --- | --- |
| Native registered non-stub bodies | 23 / 422 (5.45%) | Equal-weight routine count, not source-line coverage |
| Native guest entries | 1,979,912 / 3,103,685 (63.79%) | Frequency on one fixture, not code or CPU coverage |
| Remaining Python guest entries | 1,123,773 | Fixture-specific starts, not exact bridge transitions |
| Ported source-line share | Not reported | Requires an explicit mapping/counting method |
| Global test line/branch coverage | Not reported | Targeted fidelity/branch proofs do not establish a global percentage |

The accepted proofs remain evidence of behavior for their bound artifacts. Do not
rename an entry-frequency percentage as code coverage or infer a completion date
from any of these counts. Keep global test coverage distinct from translation
coverage; no new coverage percentage is invented for this plan.

## Select and bound each chunk

1. Recheck checkpoint, live heads/checks and the full remaining-work profile.
2. Select a hot root; inventory its literal/dynamic guest targets and inline
   helpers. Follow remaining Python callees to a finite native closure. An
   existing native subtree can be a boundary; an unported default-path callee
   must be included or the candidate replaced with a smaller genuinely closed tree.
3. Bound by semantics and dependency shape, not a fixed number of bodies or a
   whole-module quota. A large module with unrelated services is not a closure.
   Seal exact ownership, variants, ABI and observable/error contracts before builds.
4. Implement and prove constituent bodies in resumable milestones on one branch.
   Preserve real guest boundaries and source-inline invocations, even when a
   native helper already exists at the same historical address.
5. Freeze the whole bundle and its baseline, sources, binaries and private inputs.
   Run all required per-body/integrated proofs and the full campaign once for the
   combined artifact. Production changes after freeze require a new bound epoch
   and fresh required receipts, preserving old ones. Local preflight cases during
   development do not replace final artifact-bound proofs.

This batches the expensive full campaign; it does not drop prior-body regression,
controls, errors, callbacks, lifecycle, ALL75/F40, profiling or paired timings.
The oracle is never changed to make a candidate pass.

## Validated chunk: T17 marking-target closure

[T17](tasks/T17.md) ports marking-target selection, its zone test, holder/half
queries and the full-word registered random draw together. All remaining default
guest callees close through native bodies. Variants stay Python. Per-body,
actual integrated and scoped Python-execution proofs pass on the combined artifact.

The profile confirms 28 native bodies,2,129,564 native entries and 974,121 Python
entries of 3,103,685: exactly149,652 entries moved. This is6.64% equal-weight body
count and 68.61% entry frequency on one fixture. Global LOC/test coverage remains
unreported. See [assessment](../out/T17/assessment.md) and the
[closed ledger](../out/T17/validation-final-v2.json).

T17 uses 7.82% less CPU than saved T16 at the paired median. Same-campaign saved
T16/PyPy 1.059106 and T17/PyPy 0.974762 show the gap closing to near parity: two
rounds use less CPU than PyPy, one0.94% more. This is one-fixture evidence.

## Validated scope: T18 player-destination closure

[T18](tasks/T18.md) ports all 15 remaining default bodies below
`positioning.update_player_destination` (0791:4B64), including marking destination,
post destination, position group, geometry queries, random table/energy helpers,
long extrema, byte clamp and membership. All 41 real guest return sites remain
observable. The helper inventory follows functions passed to inline `invoke`;
scoped execution checks prove zero owned Python execution during native lifetimes.

The profile confirms 43 native bodies, 2,405,625 native guest entries and 698,060
Python entries of 3,103,685: 276,061 entries moved. This is 10.19% equal-weight body
count and 77.51% entry frequency on one fixture. Global LOC/test coverage remains
unreported. See [evidence](../out/T18/README.md).

The complete three-round campaign uses 20.57% less CPU than saved T17.
Same-campaign saved T17/PyPy is 0.963176 and T18/PyPy
0.765050: 23.49% less CPU at the median on this
fixture, with all rounds improving. The failed earlier timing campaign is retained
and the complete replacement uses unchanged guards. [Assessment](../out/T18/assessment.md).

## Validated scope: T19 depth-adjustment closure

[T19](tasks/T19.md) closes all five remaining default bodies below 474D, including
attack/defend depth steps, slot side and the inline-RNG coin. All 23 guest sites
and captured/live semantics remain explicit. Full prior43/new5 proofs, controls,
three live matrices, ordered drive, lifecycle and strict ALL75/F40 pass. A final
selector-count audit retained all original rows and added four scoped own-write
selectors: 20,160 comparisons across 122 distinct selectors, with no runtime
change or timing rerun. [Assessment](../out/T19/assessment.md).

The profile confirms 48 native bodies (11.37% equal-weight count), 2,508,808
native guest entries (80.83% fixture frequency) and 594,877 Python entries. Global
LOC/test coverage remains unreported. All three paired timing rounds improve: median
6.78% less CPU than saved T18. Same-campaign saved T18/PyPy
0.781398 and T19/PyPy 0.739004 show 26.10% less
CPU than PyPy on this fixture. No general workload advantage is claimed.

## Validated scope: T20 chase-gate closure

[T20](tasks/T20.md) closes three remaining default bodies below 5729, including
both goal-strip queries and their inline helpers. It preserves five guest sites
and the distinction between live AX and SENT, captured point/parent DI and fresh
pointers. The larger hot roots still fan out into many unported services; this
smaller tree is fully closed. [Assessment](../out/T20/assessment.md).

Full prior48/new3 proofs, controls, 99 distinct error selectors/99 execution rows,
four live matrices, ordered drive, lifecycle and strict ALL75/F40 pass. Independent
fidelity jobs share a bounded three-process pool before measurement stages; all
542 bound sources/binaries/inputs remain fixed. No rejected canonical stage or
replacement timing campaign was needed.

The profile confirms 51 native bodies (12.09% equal-weight count), 2,542,617
native entries (81.92% fixture frequency) and 561,068 Python entries. All three
paired rounds improve, median 4.16% less CPU than saved T19. Same-campaign
saved T19/PyPy 0.748274 and T20/PyPy 0.717119
show 28.29% less CPU than PyPy on this fixture. No global LOC/test coverage
or general workload claim. No new per-translation 5% floor.

## Validated scope: T21 ball-travel/multiply closure

[T21](tasks/T21.md) closes the two-body 835F/23E4:0279 tree, preserving the real
far8396 return, register arguments, scratch/dead stack/last-add flags and captured
SENT/live DX. Both entries remain non-long. Full prior51/new2 proofs, all output
controls, positive arithmetic witnesses, five live matrices, ordered drive,
lifecycle and strict ALL75/F40 pass. [Assessment](../out/T21/assessment.md).

Profile: 53 native bodies (12.56% equal-weight count), 2,584,201 native entries
(83.26% fixture frequency), 519,484 Python entries. All three paired rounds
improve: median 1.90% less CPU than saved T20. Same-campaign T20/PyPy
0.699125, T21/PyPy 0.686504 means 31.35% less CPU than
PyPy on this fixture. No general workload or global LOC/test-coverage claim.
The owner-approved no-arbitrary-5%-floor policy applies to this modest gain.

Older observed draw-state wrappers now explicitly use nondefault tags, retaining
all trace/fault assertions; a separate actual-native integration test was added.
Rejected preflight logs/original harness are preserved. No Rust semantic fix or
canonical rejection occurred. All 598 frozen bindings stayed fixed.

## Decide the following chunk from evidence

After T21 is accepted, inspect its complete remaining Python profile and scoped
execution/boundary observations before sealing the next closed tree. No next task
is included in T21.

If common dispatch/bridge work dominates instead, define a separate measured
optimization task with its own predeclared criteria. Native-to-native calls still
use common dispatch machinery today; batching routines in a PR does not itself
remove Python object construction, observers or every foreign-function boundary.
Measure actual paths rather than treating guest-entry counts as FFI counts. Do
not silently combine a broad dispatcher redesign with the T17 translation.

## Performance reporting and adoption

Use [same-campaign performance reporting](performance-reporting.md). Preserve the
previous accepted hybrid and compare saved baseline, candidate, plain CPython and
PyPy together on one quiet host, with rotated physical cores and every outcome
retained. Report baseline/PyPy and candidate/PyPy side by side. No new 5% floor is
introduced for translations; explicit optimization contracts keep their own gates.
A fidelity success is not a speed win when measurements regress.

The engine milestone still requires the explicit A700 corpus in addition to ALL75,
its known ref-121 noncompletion preserved, and the owner's review. Goal2 adoption
then requires worker/application parity, save/load, cancellation, lifecycle and
playtesting, with a predeclared representative performance set before claiming a
broader PyPy advantage. A single-fixture win is not general adoption evidence.

Goal2 at `1d274622c85054e595a8d0da11925d8780d4b148` now runs engine tests under
PyPy child processes ([PR #502](https://github.com/diegoami/goal2/pull/502)) and
retries transient half-time IPC read refusals ([PR #504](https://github.com/diegoami/goal2/pull/504)).
Later Rust integration must respect those process/IPC contracts and verify the
chosen backend independently; it does not replace their test routing prematurely.
A Rust adoption task must explicitly test its worker interpreter and native-extension
ABI on each target platform. A portable pure-Python worker smoke test does not
prove the Rust extension loads; original/Unicorn reference runs remain isolated
under their supported interpreter.

The upstream [T147 portable build](https://github.com/diegoami/goal2/blob/1d274622c85054e595a8d0da11925d8780d4b148/docs/tasks/T147.md)
plans to bundle CPython 3.13 for the UI and PyPy 3.11 for workers; [T153 first-run import](https://github.com/diegoami/goal2/blob/1d274622c85054e595a8d0da11925d8780d4b148/docs/tasks/T153.md)
serves the owner's playtest using the private data folder. Those are upstream
plans, not completed Rust milestones. Do not block goal2's playable build on this
port or bundle original data here. Independent public whole-game distribution
still needs the remaining original-game dependencies removed.

## Evidence input/output lesson

Keep generated reports in an output directory excluded from input/source globs.
Bind executable proof sources explicitly. T17's broad root *.txt matcher included
a newly generated profile view, correctly rejecting the first lifecycle receipt's
source stability. Its unchanged bytes and rejection remain preserved; source-clean
check-v2 repeats every lifecycle gate on the same binary. Final drivers explicitly
account for rejected and accepted attempts. Never suppress source_unchanged or
edit a completed receipt to repair classification. Supplemental proof sources can
be added and bound after canonical writers exit, with every original binding
retained and no production change.

## Upstream application boundary, checked 2026-11-02

Goal2 main is `ed582f99d5b7a56d53ccb7ae89394581d7fa7b83`; archaeology
main remains `2a411f50422ecd1f5d8cf96d05f1873e6257e684`. Goal2
[PR #515](https://github.com/diegoami/goal2/pull/515) requires PyPy child processes
for its engine tests. Our declared CPython/PyPy fidelity and four-arm measurements
remain required.

Goal2's planned [T154 evaluation, issue #516](https://github.com/diegoami/goal2/issues/516)
will assess a long-lived PyPy engine over a pipe after the playable build, and a
future Rust CPython module. Its suggested Rust thread assumes GIL release; this
partial port still invokes Python bodies/callbacks and holds interpreter-dependent
state, so T18 does not provide that thread/API guarantee. A separate integration
task must establish API ownership, threading/GIL release, cancellation, target ABI
and portable ZIP loading, with Windows/Linux measurements. Keep the accepted
oracle fixed and let the playable goal2 build proceed independently.

## Upstream adoption update after T19

Goal2 main is now `6bfdfbbd00107cddbb519a48629c41ac51ca6d6c`; archaeology
remains `2a411f50422ecd1f5d8cf96d05f1873e6257e684`. Since T19 began, goal2
merged [portable Windows packaging #510](https://github.com/diegoami/goal2/pull/510),
bundling CPython 3.13 for the UI and PyPy 3.11 for workers. Rust extension ABI
and portable ZIP loading need explicit target-platform proof; current Linux
CPython 3.12/PyPy tests do not supply it.

[Core-save launch/resume #519](https://github.com/diegoami/goal2/pull/519) and
[viewer lifecycle #517](https://github.com/diegoami/goal2/pull/517) add adoption
contracts: preserve core-save routing and distinguish a released viewer from an
unexpectedly exited viewer, retaining the designed resumable stop. Replay timeout
[diagnostics #521](https://github.com/diegoami/goal2/pull/521) and the
[T152 contract correction #522](https://github.com/diegoami/goal2/issues/522)
do not change this pinned engine translation. T152 now matches the existing owner
policy: missing PyPy/explicit engine runtime raises EngineRuntimeMissing, with
no silent CPython fallback. T154's API/threading/GIL evaluation stays separate.
These updates strengthen later adoption checks and do not change T19's oracle.

## Upstream plan and design update after T20

Goal2 main is `60fd39e6dfb6072b95e7b23aff470c9d472c94c6`; archaeology
remains `2a411f50422ecd1f5d8cf96d05f1873e6257e684`. The owner-approved
[m3 plan #509](https://github.com/diegoami/goal2/issues/509) removes GOAL.EXE,
Unicorn and the recorded boot-state dependency after m2 and the ZIP playtest.
GOAL.DAT comes from the player's install first and is replaced later; goal2rust
continues in parallel and does not change that order.

Goal2 merged [first-run data import #514](https://github.com/diegoami/goal2/pull/514)
and [T156 original playthrough #528](https://github.com/diegoami/goal2/pull/528).
The uninterrupted reference spans a new career, watched match, save/quit/reload
and round-two quick match. It is useful to later whole-game fidelity; it does
not replace this port's admitted engine corpus or larger engine milestone gates.
Only references are recorded here; no original renders or game data are copied.

The owner's design phase starts from T156, then T157 screen design and
[T158 technology evaluation](https://github.com/diegoami/goal2/blob/60fd39e6dfb6072b95e7b23aff470c9d472c94c6/docs/tasks/T158.md).
T158 absorbs T154 and measures toolkit, route, engine-boundary and portable
packaging options on Linux/Windows, including the Rust hybrid as a CPython module.
Its prototypes and owner decision are pending. A hybrid speed result provides
neither GIL release nor in-process UI-thread safety; preserve explicit API, worker,
save/load, cancellation and target-extension ABI/loading gates. This does not
change the accepted engine oracle or authorize an application redesign here.

## Upstream adoption update after T21

Goal2 main is `39d545bbed8550cc9a203a743f72e8c27640b806`; archaeology
remains `2a411f50422ecd1f5d8cf96d05f1873e6257e684`. Goal2 merged the
[owner-approved T157 screen/flow design #530](https://github.com/diegoami/goal2/pull/530):
follow the original, with tagged departures for DOS limits or playtest problems.
[Optional checked GOAL.HLP import #531](https://github.com/diegoami/goal2/pull/531)
serves original help on F1, while old data folders without it remain valid.
[Play-next UX #529](https://github.com/diegoami/goal2/pull/529) makes the desk
control primary and preserves captain-stop Q/C choices. These are later
application parity contracts, not engine semantic changes or a Rust adoption.
No original help, renders or game data are copied here. T158's measured technology/
engine-boundary/packaging evaluation and the owner decision remain separate,
alongside explicit GIL/threading/ABI/save/load/cancellation/playtest gates.
The controlled engine pin and Rust-in-parallel m3 order are unchanged.

## T22 scope and upstream adoption update, 2026-11-03

T22 selects the complete8CF5/8E24/90C5 offside-line/display tree from T21's
full remaining-work profile. Direction2BE5 is already native. All four guest
sites remain observable;9,389 entries are predicted to move, with no speed
forecast. [Task](tasks/T22.md), [inventory](../out/T22/inventory-v1.json).

Upstream goal2 at`c81565c341ea4678680230e6c38324b83677e7f2` now records the
owner-approved[T158 technology choice](https://github.com/diegoami/goal2/pull/532):
PySide6 Essentials with the pitch inside the window, grow the Python route and
retain the Core as test oracle, use one long-lived PyPy engine process over a
pipe, then adopt the Rust hybrid inside that process once its gates pass.
Track A(T159-T169) owns UI/protocol; Track B(T170-T175 plus upstream ports) owns
native whole-game rules. This repository continues Rust translation in parallel.
T158's independent30-match/platform probes are useful adoption evidence, bound
to T20; they do not revalidate T22 or replace its exact artifact/corpus gates.
The hybrid still invokes Python and holds interpreter-dependent state; no UI
thread/GIL-release guarantee follows. Explicit worker/protocol/save-load/cancel/
ABI/loading/representative performance and owner engine milestone gates remain.
Archaeology main2a411f50 is unchanged; controlled oracle2cbeb36f stays fixed.
