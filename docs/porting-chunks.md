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

## T22 validated outcome and current upstream boundary

[T22](tasks/T22.md) closes8CF5/8E24/90C5 with all four far sites. All fidelity,
strict ALL75/F40, lifecycle, source/baseline and process-closure gates pass;
[assessment](../out/T22/assessment.md). The post-writer all-inventory scope proof
adds shared s8/s16 to the canonical motion-helper set on the same artifact:
6,288 comparisons/64 variants, positive source witnesses and zero native-lifetime
owned Python calls. Two additive proof/audit sources are separately sealed;
all661 primary bindings and every canonical receipt remain fixed.

Profile:56 native bodies(13.27% equal-weight count),2,593,590 native entries
(83.56% fixture frequency),510,095 Python. Timings are mixed: two faster rounds,
one1.24% slower, paired median1.01% less CPU than T21. Same-campaign T21/PyPy
0.691683 and T22/PyPy0.694602 are independent medians from different rounds.
No repeatable gain or global LOC/test-coverage claim; all samples remain.

Upstreams rechecked at goal2`185886f39ef51a4d9c5f9a68cf4f5ce62c85ab78`
and archaeology`26fe704d58b483e5a8a2acbb4dca4ee4a16581aa`.
Goal2[T159/#545](https://github.com/diegoami/goal2/pull/545) now provides the
long-lived engine process and bounded binary-header/payload pipe protocol,
ready/open/match/ack/pause/answer/cancel/quit messages, stderr isolation, death/
restart, input-EOF shutdown and cancel/close deadlines. T160 routes watched and
competitive matches onto it next. Rust adoption must test this actual protocol,
restart/game replay, cancellation/EOF and target ABI/loading; T22 does not wire
Rust into the application or release the GIL.
Archaeology's new T118a-c documents the route(b) write-set/post-match-news scope;
only task docs changed, not the selected engine semantics. Keep controlled
2cbeb36f/private T07 inputs for this accepted comparison. Whole-game Track B
and UI/protocol Track A still proceed independently of Rust translation.

## T23 selected chunk: Pascal string writes

The full T22 profile selects three hot exports sharing runtime._copy_forward:
23E4:062A assignment,0644 bounded assignment and06B7 concatenation. All complete
caller/helper trees move together; no registered guest callee remains below them.
The shared helper's eager read-ahead branch and bytewise live overlap/wrap branch
are distinct observable semantics. This coherent helper-connected chunk moves
16,532 fixture entries; no speed forecast. [Task](tasks/T23.md),
[inventory](../out/T23/inventory-v1.json). The broader commentary/duel roots reach
larger closures through helper-dispatched call tables, so their literal-call
counts alone are insufficient to seal a complete tree.

T23 includes every inventory helper in its first closure probe. It also replays
T22 offside closure with shared s8/s16 in the canonical OWNED set and positive
source witnesses, preserving the prior additive proof's assertions. Baseline is
actual accepted T22, preserved before builds; historical .cache/T22-baseline is
T21. Accepted oracle/upstream heads are unchanged from T22. The current accepted
counts and mixed T22 measurements remain until T23's full combined campaign.

## Upstream progress during T23 validation

Goal2 main`b755eb67f04fac41f7fafd7d7e342088ce3db8c8` merged the
[T162 UI foundation](https://github.com/diegoami/goal2/pull/544): shared theme,
VGA font, screen stack, data import and original-help presentation. T163(start/
new game) andT165(squad/tactics) are the next UI work. The owner explicitly
leaves Python-route bulletins awaiting Track B's news port and the assistant
awaiting its port. These are whole-game/UI dependencies, not a reason to change
this engine translation or claim those features exist here.

Archaeology main`4f40e9995a3e167bf1da146c6a77139615613d14` merged
[T118a/#642](https://github.com/diegoami/goal2-archaeology/pull/642), the static
played-fixture write-set inventory/listing checks and proposed F039 findings.
Post-match news/sacking work is split into T118b1/b2, followed by behavioral
corroboration T118c. The changed files are findings/specs/static annotations/
task docs/write-set tests; selected runtime/original_match/port code is unchanged.
The controlled2cbeb36f engine pin/private T07 inputs stay fixed throughout T23.
Rust translation, application pipe/ABI adoption, Track A UI and Track B native
whole-game rules continue as separate gates. No original screenshots/help/game
assets are copied into this repository.

## T23 final result

[T23](tasks/T23.md) translates062A/0644/06B7 and all seven inventoried source
body/helper functions; zero registered guest calls. Full prior56/new3 fidelity,
ordered drive,lifecycle,strict ALL75/F40 and all source/error/callback/control/
variant/closure assertions pass.59 bodies(13.98% count),2,610,122 native entries
(84.10% fixture frequency),493,563 Python;no LOC/global test/CPU coverage claim.

The first full timing campaign is retained but rejected because the third
CPython arm ended under external load. A separately sealed full three-round
repeat on the unchanged artifact passes pre/post/per-round sampled quietness.
Its result remains mixed:two faster rounds,one3.01% slower;paired median0.62%
less CPU than saved T22. Same-campaign independent T22/PyPy0.661589 and
T23/PyPy0.678089 medians are retained alongside all raw rows. No repeatable
speed claim or cherry-picked arm. Final-v2 ledger binds731 primary inputs,
263 evidence hashes and two additive measurement/audit sources;107 process
groups/controller stopped. Original v1 sources/receipts/ledger remain unchanged.

## T24 selected chunk and upstream dependency update

The full T23 profile selects the complete keyboard-service chunk214B:0723,
08DD,0983 and0993,with nine owned body/helper functions in total. The wait/clear caller's
only guest,08DD at098A,is included. This cohesive kit-service path moves78,172
fixture entries;prediction63 bodies/2,688,294 native/415,391 Python,no speed
forecast. The actual per-port memory view/kit callbacks remain the semantic API;
no BIOS prologue or automatic-answer policy is invented. [Task](tasks/T24.md).

Upstreams rechecked at goal2`4368facda28d807500eb382854e2cc3f3d157d54`
and archaeology`ddc888b9dc3b13921928e50770c649c24a1d45d7`.
Goal2[T163/#553](https://github.com/diegoami/goal2/pull/553) merges the new-window
start/new-game screens. Its process now serializes local gates per computer
after two WSL crashes;independent tasks still coordinate the shared host. The
owner's first-key-poll choice concerns animation/RNG during post-match news in
the NEW whole-game harness,not this pinned match-engine service behavior.
Archaeology plansT119-T123:a route harness,then silent path,route_fixture/news,
and sealed route handover;T118c's behavioral corroboration folds intoT119.
These task docs do not change selected runtime/original_match/port semantics.
Keep controlled2cbeb36f/private T07 inputs and Rust-in-parallel scope. No original
screens/help/game assets copied. Application/route/UI/ABI/GIL gates remain apart.

## Upstream whole-season dependency update during T24

Rechecked goal2 `e44a66fe2f3724086ba0e722d5c6468394cf62e8` and archaeology
`8298428759ce47f848981d30e90333bbf98493e7`. Goal2's
[T170 season plan](https://github.com/diegoami/goal2/blob/e44a66fe2f3724086ba0e722d5c6468394cf62e8/docs/tasks/T170.md)
depends on upstream T123 **and T124**. This commit adds the task contract;
it does not implement a season on the Python route. New qualifier-viewing and
fixtures/history work is also planned; T164 desk/team-info UI is implemented.
The changed-file comparison contains no selected match-engine runtime changes.

Archaeology split the route harness into
[T119a](https://github.com/diegoami/goal2-archaeology/blob/8298428759ce47f848981d30e90333bbf98493e7/docs/tasks/T119a.md)
(harness) and T119b (recorded runs, incorporating T118c). Its proposed
`Match(tail=False)` split must retain the existing default behavior. The harness
owns first-poll answers and ordered writes/RNG/key-site records; that future
policy does not replace T24's pinned kit callbacks.

[T124](https://github.com/diegoami/goal2-archaeology/blob/8298428759ce47f848981d30e90333bbf98493e7/docs/tasks/T124.md)
adds the previously missing round-end scope: stage dispatch, six builders and
remaining stage-news helpers. It must split into bounded builder tasks and prove
draw order as well as the calendar. Yearly ageing/retirement remains separate.
The new merged archaeology work is static sacking/write-set evidence and task
design, not changes to the selected runtime port. The controlled T24 artifact
and oracle stay fixed. Broader whole-game adoption must include these upstream
dependencies; the current 422-body match-engine denominator is not a whole-game
completion estimate. Select the next native chunk separately from T24's fresh
profile, after T24 completes all acceptance and merge gates.

## T24 final result and pause

[T24](tasks/T24.md) moves the four complete keyboard-service exports and all
nine owned body/helper functions, retaining the wait/read real guest at098A
and generic kit callbacks. All prior59/new4 per-body/error/branch/variant/helper/
callback/control proofs, ordered drive, lifecycle and strict ALL75/F40/prefixes
pass. Full profile:63 bodies(14.93% count),2,688,294 native/415,391 Python entries,
86.62% native fixture entry frequency. No CPU/LOC/global-test/whole-port coverage
claim follows from those counts.

The entire original timing campaign is retained/rejected for external load in
round one. Its full replacement on the same artifact passes all quiet-start,
arm-endpoint and continuous-load checks. Selected result:1.00% MORE CPU than
saved T23 at the paired median;one1.50% faster round,two1.00%/2.55% slower.
Same-campaign independent T23/PyPy0.623213354 and T24/PyPy0.629437938 medians
remain beside all raw values. No repeatable gain or selectively replaced sample.
This translation task has no positive magnitude or all-round speed gate.

Final ledger binds852 primary files/281 evidence hashes. A separately sealed
one-source/four-input profile-reference audit verifies the unchanged historical
comparator and all profile observations against fresh Python/Rust receipts.
All111 canonical/timing groups,controller and three capture PIDs exited. Final
CI/merge/mainCI/merged-binding status lives in checkpoint#1. The owner requests
a pause after this task;no T25 is selected or started. A later task must inventory
a complete bounded tree from the fresh profile,including dynamic helper callees.

## T25 selected text-cell closure and upstream update

The owner resumed after T24. [T25](tasks/T25.md) selects four connected Pascal
text callers and their forward/backward cell-writing callees,six exports and
14 owned functions in total. Existing native0644 closes the remaining guest
boundary;all eight real return sites remain. The fixed fixture predicts10,810
moved entries,not a speed result. This tree is bounded even though the hotter
duel/contest roots still fan out through larger unported helper-dispatched trees.

Upstream snapshots:goal2 e1735b657a6812d86851ab38069819bf91b24e89 and
archaeology9e77f0066216d0cddfbf76aed2dfa53866a97d9d. Goal2's T160 pipe-based
watched/competitive matches and new-window pitch/boards are implemented;save/
quit/load work is planned separately. Archaeology's T119a route harness and
Match(tail=False) are merged,but T119c must preserve competitive fixture round
bytes and name table-read key sites;T121 now depends on that correction. No
controlled pin refresh or adoption into T25's default-match semantics follows.

Goal2's shared-host runner rule now caps each runner at six gate jobs and
requires checking IT13 runner activity before a local gate. T25 honors that
admission rule and records independent runner observations during timings;
a busy/unknown runner state rejects an entire timing campaign. Continuous
five-second load monitoring remains separate from network queries. No unrelated
process/runner is stopped or reconfigured. Original source/corpus/quality guards
and the quiet-IT13 preference remain.

## T25 resume dependency check (2026-11-04)

Live main heads are goal2 `8893411ffb24bfddac617ba36b7d68fc0bb7ba1f` and
archaeology `04021dd06e4afdeac99cc358273f6041a30ed6c4`. Since T25 selection,
goal2 added save/quit UI and management extras, plus watched-match qualifier
handling. Archaeology now includes T119c's competitive route fixture/key-policy
correction and its E040 evidence. Route proofs can disable the write-recording
listener with `record_writes=False`; the Prover still checks memory itself.
T120's silent-fixture proof runner and the explicitly edited input needed to
reach BB2F are now specified; that task contract is not a completed port proof.

These updates advance later whole-game dependencies. They do not refresh
T25's accepted `2cbeb36f` oracle, change its default-match contract, or alter
the frozen artifact. Complete T25's remaining full-match/profile/timing gates
before selecting the next chunk from the full profile. The paused M2 receipts
and separately sealed continuation remain intact; checkpoint #1 records the
owner-authorized restart and current controller identity.

## T25 final validation

All prior63/new6 fidelity proofs,all14-owned closure,ordered drive,lifecycle,
strict ALL75/F40/prefixes and full profile pass. The fresh profile confirms69
native bodies(16.35% count),2,699,104 native/404,581 Python entries,86.96%
native fixture entry frequency. These are not source-line/test/CPU coverage.
The first complete quiet four-arm campaign passes all load/runner gates and
uses1.66% less CPU than saved T24 at the paired median;all three rounds improve.
Same-campaign independent T24/PyPy0.684159861 and T25/PyPy0.667383160 remain
beside all raw values in the [assessment](../out/T25/assessment.md).

Final-v2 binds1083 primary files/277 evidence hashes and additive6sources/121
inputs. All105 physical canonical/timing groups and three controller epochs
are stopped. The original pre-proof wrapper failure remains reconciled,not
counted as a proof pass. Exact-head CI/merge/mainCI/merged-audit status remains
in checkpoint#1. The owner authorized merging and continuing;select the next
complete bounded closure from the full remaining profile after T25 acceptance.

## T26 selected offside/commentary closure

The owner authorized merging T25 and continuing. T25 is accepted atd300f98,
with green exact-head/mainCI and a completed merged binding audit. Full-profile
selection closes56D9 through26A0/2B0F/1EB5,ratings/ring/new-line checks,
1829 rendering,0018 byte fill and1C86 wrap arithmetic:ten bodies,25 actual guest
returns,31 owned code objects. Resolve frame.go via SITES and display's tuple
loops;include both local word closures. Existing native2BE5 and T23/T25 string/
text routines are the only guest boundaries. Prediction45,569 moved fixture
entries,79 bodies/2,744,673 native/359,012 Python entries,is not a speed result.

Latest upstream heads are goal2b3d8dc3bd2f7e6316ff56f1f8d163c4ff6426504 and
archaeology65de2fc06d5c909c01da9deeedfffcbef0d398e2. The match-day UI and pipe
prompts now include set-piece/extra-time/shoot-out decisions;later application
adoption must retain those protocol/behavior gates. Whole-game T124 now has a
T124t legal-eleven harness dependency before stage builders. These are separate
from the pinned2cb default-match Rust task. The owner clarified shared-runner
admission:check before STARTING a local gate;never stop a gate already running
because a runner becomes busy. T26 retains strict independent runner/load timing
quality and whole-campaign rejection/repetition. No original guard is raised.

## T26 final validation

All92 M2 stages,prior69/new10 proofs and all ten live matrices pass on one
fixed artifact. Ordered/lifecycle/strict ALL75/F40/10/20/30/60 and independent
backend attestation pass. Full profile79 bodies/422(18.72% count),2,744,673
native/359,012 Python entries,88.43% native fixture frequency. This confirms
45,569 moved entries;it is not source-line/test/CPU coverage or whole-game
progress. The complete first quiet timing campaign passes all checks,with
paired median1.57% less CPU than saved T25,two faster and one3.69% slower
round. Repeatable improvement is not established;all raw values/ratios and
same-campaign independent T25/PyPy0.677809344,T26/PyPy0.668069969 remain in
the [assessment](../out/T26/assessment.md).

Final-v1 and all five post-writer audits bind1647 primary files/283 evidence
hashes,accepted T25 1083/277+6/121,baseline77/all42 artifacts,capture49/80 and
preserved development epochs. All109 canonical/timing groups/controller are
stopped. Final exact-head CI/squash/mainCI/merged audit and completion stay in
checkpoint#1. Select a following bounded closure separately from the fresh
full profile;no T27 is selected here.

## T27 selected quick-result strength closure

The owner continued after accepted T26d2f5a19. Full-profile selection chooses
quick.listing_1771_0BC4,the highest remaining registered-body self-time,with
manager bonus,foot/position/player strength and bit-test callees:seven bodies,
12 actual returns,27 owned code objects including Rec.__init__/lin/u8. Resolve
quick._call popped-word semantics,attributes.gcall SENT/liveDX semantics and
helper-dispatched membership returns explicitly. Native3216/08DF are the only
guest boundaries. Higher player-at-ball/contest roots reach restarts,substitution
and menus;they are not truncated into an apparently small partial closure.

Prediction18,250 moved entries,86 native bodies/2,762,923 native/340,762 Python
entries is fixture frequency,not speed or code/test/whole-game progress. Actual
T26 baseline79 files is preserved before builds;50 pure-oracle inputs yield56
genuine entry shards. Latest upstream change is goal2's UI kit/palette correction;
archaeology remains65de2fc0. No accepted-pin/default-engine policy change follows.

## T29 selected near-player-zone path and upstream dependencies

After accepted T28,select44C1 from the fresh FULL profile:one body/six actual
owned helper functions/onefar4500 return/native2BE5 onlyboundary. Its source
Frame-style lifetime and SENT direction value differ from Regs-based533B;
retain repeatedargumentreads,cached physicalpointer,liveSS and AX-before-local
read order. Explicitly exclude the uncalled positioning.w8 namecollision with
Frame.w8;all actualsix require positive source/outside/nondefault witnesses.
Prediction16064movedentries is not a speed claim. ActualT28(84files) is saved
before builds with its3061primary/338evidence+5supplemental ledger/mergedaudit.

Upstreams goal2c951855b/archaeology953b57ee advance pipe-only application,
independentmenu navigation/commentarypause,best-twenty assistant,newsroute/
speakerABI and captain/stopped-substitution fixes. Later adoption/pinrefresh
must explicitly assess these contracts and their original-backed proofs.
Keep2cb/privateT07 for this controlled task;no mid-campaign source refresh.
