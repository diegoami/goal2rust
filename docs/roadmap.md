# Engine roadmap

[designed: owner, 2026-10-30] Adopt the upstream sealing contract, refresh the
oracle and evidence, profile the Rust machine, then translate complete hot call
trees. This follows the owner's approval of the upstream assessment. T02 is
complete; its historical receipts and Done-when remain unchanged.

## Current plan after T28: complete native chunks

[owner-approved recalibration] T03-T16 are historical accepted increments. The
next default work unit is a complete bounded native execution tree with its
remaining Python callees. Keep individual proofs, then validate the whole frozen
bundle in one full campaign. See [chunk policy](porting-chunks.md).

1. **T17, validated in [PR #43](https://github.com/diegoami/goal2rust/pull/43):**
   [complete marking-target subtree](tasks/T17.md): 47C5,4438,2996,2C54 and
   214B:06B1, with existing native boundaries. All 28 native bodies and predicted
   entry counts are confirmed. [Results](../out/T17/assessment.md).
2. **T18, [PR #45](https://github.com/diegoami/goal2rust/pull/45):**
   [complete player-destination subtree](tasks/T18.md): all 15 remaining default
   bodies below 4B64, 41 real guest return sites and their inline helpers. The
   full profile confirms 43 native bodies and the predicted entry counts.
   [Results](../out/T18/assessment.md). Choose the following closed tree from
   the new full profile after this task is accepted; no next task is included.
3. **T19, [PR #47](https://github.com/diegoami/goal2rust/pull/47):**
   [complete depth-adjustment subtree](tasks/T19.md): five remaining default bodies
   below 474D and all 23 real guest sites. Full fidelity and paired measurements
   pass; [results](../out/T19/assessment.md). Select any following closed tree from
   its full remaining-work profile in a new session; no next task is included.
4. **T20, [PR #49](https://github.com/diegoami/goal2rust/pull/49):**
   [complete chase-gate subtree](tasks/T20.md): three bodies below 5729 and all
   five guest sites. Full fidelity and paired measurements pass;
   [results](../out/T20/assessment.md). Select the next closed tree from its full
   profile in a new session; no following scope or implementation is included.
5. **T21, [PR #51](https://github.com/diegoami/goal2rust/pull/51):**
   [complete ball-travel/multiply subtree](tasks/T21.md): both remaining default
   bodies and far8396. Full fidelity/paired measurements pass;
   [results](../out/T21/assessment.md). Owner requested winding down after this
   task; select any following scope in a new session from the full profile.
6. **T22, [PR #53](https://github.com/diegoami/goal2rust/pull/53):**
   [complete offside-line/display tree](tasks/T22.md),8CF5/8E24/90C5 and all four
   guest returns. Full prior53/new3, all-inventory helper closure, ordered drive,
   lifecycle and strict ALL75/F40 pass. Timings are mixed: two faster rounds,
   one1.24% slower, median1.01% less CPU than saved T21; no repeatable gain claim.
   [Assessment](../out/T22/assessment.md). No following task is included; select
   any next closed tree from the full T22 profile in a new session.
7. **T23,[PR #55](https://github.com/diegoami/goal2rust/pull/55):**
   [complete Pascal string-write chunk](tasks/T23.md):062A/0644/06B7 and shared
   copy/concat helpers,zero guest calls. Full fidelity,ordered/lifecycle,strict
   ALL75/F40 and all7-inventory closure pass. Entire first timing campaign
   rejected for late load; complete quiet repeat retained. Mixed result:two
   faster rounds,one3.01% slower,paired median0.62% less CPU than saved T22.
   [Assessment](../out/T23/assessment.md);no repeatable gain claim. Select any
   following closed tree separately from the full T23 remaining-work profile.
8. **T24, [PR #57](https://github.com/diegoami/goal2rust/pull/57):**
   [complete keyboard-service chunk](tasks/T24.md),0723/08DD/0983/0993 and all
   nine owned body/helper functions,including real far return098A. All fidelity/strict corpus
   and selected quiet-measurement gates pass;78,172 moved entries confirmed.
   Performance regresses at the paired median:1.00% more CPU than saved T23,
   one faster/two slower rounds. Entire loaded v1 and quiet replacement v2
   retained. [Assessment](../out/T24/assessment.md). Owner requests a pause
   after completion;no following task selected. The actual kit callback/stop
   boundary remains;the separate whole-game first-poll policy is not adopted.
9. **T25, [PR #59](https://github.com/diegoami/goal2rust/pull/59):**
   [Complete text-cell rendering chunk](tasks/T25.md): six connected display
   exports00FF/0123/01A3/0205/026D/02C8,all14 owned functions/eight guest returns,
   with existing native0644 boundary. Full fidelity/ALL75/F40/prefix/lifecycle
   and first quiet timing campaign pass. Profile confirms69 native bodies,
   +10,810 native entries. Paired median1.66% less CPU than saved T24,all three
   rounds improve. [Assessment](../out/T25/assessment.md) retains every raw CPU
   value and same-campaign PyPy ratios. CI/merge status remains in checkpoint#1.
10. **T26, [PR #61](https://github.com/diegoami/goal2rust/pull/61):**
   [Complete offside/commentary tree](tasks/T26.md),ten bodies/25 guest returns/
   31 owned code objects,including nested helpers and site-table/loop calls.
   Existing T23 strings/T25 text and2BE5 close the boundaries. All92 M2/strict
   corpus/lifecycle/ordered/profile gates pass;79 native bodies and45,569 moved
   entries confirmed. First complete quiet timing campaign passes,mixed result:
   paired median1.57% less CPU than saved T25,two faster/one3.69% slower round.
   [Assessment](../out/T26/assessment.md) retains all raw samples/ratios/limits.
   Final ledger/CI/merge status stays in checkpoint#1;no following task selected.
11. **T27,[PR #63](https://github.com/diegoami/goal2rust/pull/63):**
   [Complete quick-result strength tree](tasks/T27.md),seven bodies/12 returns/
   27 owned code objects. Full campaign and final2378/320 ledger/merged audit
   pass;86 native bodies and18250 moved entries confirmed. First quiet timing
   campaign has pairedmedian4.80% less CPU than savedT26,with one3.05% slower
   round. [Assessment](../out/T27/assessment.md);one fixture,mixed rounds.
12. **T28, [PR #65](https://github.com/diegoami/goal2rust/pull/65):**
   [Complete pass-receiver destination closure](tasks/T28.md),533B/six owned
   functions/one near return5367 through existing native045D. All107 canonical
   stages/final3061primary+338evidence+5supplemental ledger/merged audit pass.
   87 native bodies and35723 moved entries confirmed. Complete quietv2 paired
   median2.12% less CPU than savedT27;all rounds improve. Entire rejectedv1 and
   separately sealed post-writer audit correction preserved. [Assessment](../out/T28/assessment.md).
13. **T29, [issue #66](https://github.com/diegoami/goal2rust/issues/66):**
   [Complete near-player-zone path](tasks/T29.md),44C1/six actual ownedfunctions/
   one farreturn4500/native2BE5 boundary. Fifth by remaining selftime in FULL
   T28 profile;higher roots still pull in duel/state/delay/launch/restart paths.
   Preserve actualT28 before builds,seal50pure-oracle inputs/eight genuine shards.
   Prediction16064 moved entries is not performance or coverage evidence.
14. **Measure boundary cost:** if common native-to-native dispatch/bridge work is
   dominant, define a separate optimization task. A larger PR alone does not remove
   every Python boundary or common dispatch cost.
15. **Engine milestone and application adoption:** retain the larger A700 corpus,
   known ref-121 noncompletion and owner review, then worker/save-load/cancellation/
   playtest and representative performance gates. PyPy remains goal2's baseline.
16. **Whole game later:** tournament, board and career initialization still have
   original-game dependencies; a native match subtree does not remove those gates.

Current profile is **87/422 registered non-stub bodies (20.62%)**, while **90.17%**
of guest entries on the reference fixture are native (2,798,646 native, 305,039
Python). Neither is source-line, CPU-time or test coverage; no global line/branch
percentage is currently reported. Use the [current profile](../out/T28/profile-after-v1.json),
the historical [T16 planning snapshot](plans/post-T16-baseline.json) and
[same-campaign performance reporting](performance-reporting.md). Every new summary
shows saved-baseline/PyPy and candidate/PyPy together. No calendar completion date
or unmeasured general PyPy speed promise follows from these coverage counts.

## 1. T03: sealed-engine compatibility

Archaeology PRs #627 (sealed family) and #628 (handover) merged with passing
checks. T03 adopted their accepted handover commit; the current state-v2 pin is described
in T07 below. T03's evidence
and resume rules are in `out/T03/README.md`. Keep d3cf46a3 and all T01/T02
evidence available: an oracle update does not revalidate old receipts against
the new source.

Use the upstream contract unchanged: `Image.from_state(state, tables)`, the
per-event Match API, and `Match.records_after()`. Tables are generated locally
from the player's registered GOAL.EXE, validated against the upstream manifest;
no tables, executable bytes, states or saves are committed or shipped here.
Use the same boundary as goal2's planned worker (goal2#478); goal2 keeps its
PyPy 3.11 engine until Rust meets fidelity and performance gates.

T03 milestones: M1 audit and pin accepted source; M2 public contract tests and
sealed-child compatibility; M3 fresh artifact-bound real evidence and timings.
Done when:

1. Public tests exercise the new API through Rust, including invalid inputs,
   records output and save/load. A private sealed child denies Unicorn imports
   and original-file opens during execution, and passes the upstream lifecycle
   checks from state plus tables with an independently attested Rust backend.
2. Fresh per-call/full-frame differential, body and guest-return mutants,
   ordered drive and F40 pass for the exact artifact. State-input Python and
   Rust agree on events, result and records output. Compare full memory and
   ordered taps between equivalent state-input machines; do not compare the
   intentionally removed executable bytes with an image-input memory digest.
3. The admitted ALL family passes 75/75 from state. Fresh paired CPython,
   PyPy and Rust CPU receipts come from one quiet host, with source and
   extension hashes, default guards and every failure preserved.

Backend comparisons use separate processes while the process-wide adapter
limitation in #6 remains. T03 does not silently resolve unrelated review
findings. Any necessary production fix needs fresh artifact-bound evidence.

## 2. T04: first complete native hot subtree

Capture a fresh post-T02 profile, recording every guest entry (not just the top
40), native entries and remaining Python entries. cProfile's timings include
instrumentation and do not establish an uninstrumented speed gain or exact
foreign-function transition counts. An early profile against the old pin is
useful diagnostic evidence; confirm the choice after T03's oracle update.

The first candidate remains `0791:2956` to `1771:3216` (player availability).
Inventory literal and dynamic callees, inline helpers, return bytes and
suspensions before translating; replace the candidate if the fresh profile
supports a better bounded tree. Subsequent candidates are effective skill,
ball selection/possession, contests, positioning and movement.

T04 milestones: M1 selected tree and full caller/callee contract; M2 native
caller and callee equal per call/frame; M3 full drive/family/lifecycle proofs
and paired timings. Done when real captures plus random/edge states agree on
full memory, all registers, errors and ordered callbacks; body and caller/return
mutants are caught; ordered drive, F40 and lifecycle pass; and paired receipts
show the outcome against plain PyPy as well as CPython. Report regressions as
results, never omit them. Count remaining Python guest entries and re-profile
before selecting another tree. No performance claim rests on cProfile alone.

T04's implementation and measured outcome are in
[out/T04/assessment.md](../out/T04/assessment.md); its refreshed full profile
records 1,804,722 remaining Python guest entries. Use that evidence when
inventorying the next bounded tree. An entry-count reduction is not an
uninstrumented speed claim; the larger engine milestone below remains separate.

## 2a. T05: nearest-to-ball native tree

Continue the bounded-tree sequence with `0791:2FB1` after T04's refreshed
profile: highest remaining registered body self time and 298,641 Python
calls/resumptions from 5,147 starts. Its complete guest closure is already
native (2956 -> 3216 and 2BE5). Translate the loop as explicit native
continuations while preserving all guest boundaries and the live stack word
across the two direction calls. Contract and unchanged per-subtree gates:
[docs/tasks/T05.md](tasks/T05.md); evidence: [out/T05](../out/T05/README.md).
Report the paired performance outcome and remaining entries; a small entry
count can still represent many Python resumptions, and neither predicts speed.

## 2b. T06: effective skill native tree

Translate `0791:278A -> 1771:3A06` as a complete bounded prerequisite for
later contest trees. Retain the caller's captured scalars across its guest call,
consume the dispatcher's captured AX and reproduce the callee's distinct immediate
frame writes and the source's inline keeper-membership bytes. Contract/gates:
[tasks/T06.md](tasks/T06.md); proof and measured outcome in
[out/T06](../out/T06/README.md). Keep the accepted pin and private-input rule;
goal2's later table-policy exception is specific to goal2.

## 2c. T07: state-v2 compatibility refresh

Adopt accepted archaeology PR640 merge `2cbeb36fdd3feb369324aaa88e6e4d2aa3b3d99c`:
state/2 preserves differing code-data bytes and strictly checks overlay entries;
checkpoint tables survive load and extraction writes a loadable manifest.
Native Rust/adapter code remains unchanged. Regenerate private inputs from the
registered source; retain old state-v1 inputs, source clone, receipts and binaries.
Full compatibility gates and comparison boundary: [tasks/T07.md](tasks/T07.md),
[out/T07](../out/T07/README.md). Compare raw fresh-v2 machines exactly. Historical
result continuity accounts for the independently verified changed image identity
without omitting any result key. No speed claim follows from a schema refresh.

## 2d. T08: measured common-bridge performance

Use the full profile and authored primitive benchmarks to target common bridge
costs across remaining Python bodies. Preserve exact prior source/adapter/binary
for simultaneous baseline/candidate comparisons. Optimize immutable name/alias
lookup, common fixed-image reads and small writes while preserving dynamic
callbacks, fallback/error/numeric behavior and full guest semantics. No new
routine or source-pin change. Contract: [tasks/T08.md](tasks/T08.md),
[out/T08](../out/T08/README.md).

A candidate requires full fidelity plus three quiet simultaneous baseline,
candidate, CPython and PyPy rounds, rotated physical cores/launch order, every
candidate faster and median candidate/baseline CPU <=0.95. Preserve every round
and rejected attempt; a single pilot or faster primitive is insufficient. Report
PyPy outcomes explicitly; a smaller gap does not establish a PyPy win.

## 2e. T09: measured speaker/noise-state tree

Translate the bounded data-state closure 0791:94E8 -> 0791:94C9 -> 214B:0688,
plus 214B:1E8D, selected from T08's residual profile (205,799 Python entries).
Keep both omitted-hardware stubs as observable guest calls. An isolated register
descriptor prototype regressed writes and byte halves and was rejected; its
source/artifact/timings remain evidence. Contract: [tasks/T09.md](tasks/T09.md),
[out/T09](../out/T09/README.md). The original campaign used a 5% CPU target;
the owner-approved incremental acceptance amendment is recorded below.

Upstream rechecked 2026-10-31: archaeology main 2a411f50, goal2 main 721dbd1e.
Goal2 PR483 adopted the sealed kit (including its own table policy), and PR486
fixes cancellation after a job wrapper exits. This supports the adoption sequence;
retain the accepted 2cbeb36f pin/private table policy for the controlled T09
comparison. Goal2 integration/cancellation remains a separate adoption gate.

T09's fidelity proofs pass and all three rounds improve (median CPU gain 4.28%).
The owner authorized merging this incremental translation on 2026-11-01 and
removed the per-increment 5% minimum carried from T08. Fidelity, complete samples,
original guards, artifact binding and exact-head CI remain. See
[owner acceptance](porting-acceptance.md) and
[out/T09/assessment.md](../out/T09/assessment.md). Historical rejected receipts
remain intact; acceptance under the amended contract is recorded separately.
Goal2 main rechecked 2026-11-01 at d31bba36: PR488 caps automatic
CI batches while retaining full local/manual slow runs. This does not reduce
this port's strict ALL75/F40 gates or change the accepted semantic pin.

## 2f. T10: match key-poll native caller

Translate menus.match_key_poll0791:9372, the largest remaining registered Python
body self cost in the post-T09 profile (76,928 starts). One complete caller, all
six-slot delay-table and key/quick branches; its15 literal guest-call sites and 12
existing external callee bodies remain observable. This bounded increment does
not claim the transitive menu/service closure. Contract:[tasks/T10.md](tasks/T10.md),
[out/T10](../out/T10/README.md). Preserve actual T09 baseline before building.
Full per-caller and existing16-body proofs, ordered/lifecycle/ALL75/F40 evidence,
profile and three quiet paired four-arm rounds; retain all outcomes, no arbitrary
per-increment5% minimum. Same accepted2cbeb36f/state-v2, no original data in git.

T10's full caller/regression/ordered/lifecycle/ALL75/F40 proofs pass. Three paired
rounds each improve CPU: median 6.94% less than saved T09, with all samples retained;
Rust still uses 1.225x PyPy CPU on the reference fixture. 17 native bodies now cover
1,633,521 guest entries, leaving 1,470,164 Python entries (not code completion).
Current closed ledger: [out/T10/validation-v3.json](../out/T10/validation-v3.json),
assessment: [out/T10/assessment.md](../out/T10/assessment.md). Historical invalid
preflights remain preserved with exact source. Ten registered callees plus two
unregistered guests remain external; test ABI doubles never enter production.
No next task is included in this increment.

## 2g. T11: ball draw-state caller

Translate display.draw_ball_state0791:8F10 and inline grid_cell, largest remaining
Python body self cost after T10(79,194 starts). One complete caller, both registered
callee boundaries and nested source multiply remain delegated/observable. Preserve
captured record pointers, live grid/callback observations, unsigned-MUL signed-byte
address arithmetic and all previous/current picture writes. Contract:
[tasks/T11.md](tasks/T11.md),[out/T11](../out/T11/README.md). Same pin/state-v2;
actual T10 baseline preserved. Full old17-body/new caller/control/observer, ordered,
sealed lifecycle/ALL75/F40/profile/artifact proof and three quiet four-arm rounds,
all outcomes retained/reported, no arbitrary per-increment5% floor.

Upstreams rechecked before T11: archaeology 2a411f50 unchanged; goal2 advances
65c47459(PR490: CI scheduling/timeout and cancellation-test changes). No selected
engine semantic change or reason to alter the controlled accepted pin/full corpus.

T11 full fidelity and three-round measurements pass: all rounds improve, median
4.22% less CPU than saved T10. 18 native bodies/1,712,715 native guest entries,
1,390,970 Python entries remain (not a code-completion percentage). Accepted
ledger: [out/T11/validation-v1.json](../out/T11/validation-v1.json), all samples and
scope: [assessment](../out/T11/assessment.md). Actual registered delegated callees,
explicit positive success/branch coverage, no new hardware or callee implementation.

## 2h. T12: watched match sweep caller

Translate frame.watched_match_engine0791:9564, hottest remaining body after T11,
3494 starts/451,658 calls or resumptions. One complete22-player sweep, immediate
frame semantics, possession/holder/nested22-player logic, update/speaker/draw/key,
quick exit/wait decrement.17 static SITES rows/14 registered callees preserved;
no callee/hardware claim. Contract[tasks/T12.md](tasks/T12.md),
[out/T12](../out/T12/README.md). Captured BP/slot/k/rec versus live frame-stop/
SS/register/data semantics require explicit mutation/loop/site success coverage.
Full existing18-body/new caller/control/observer/ordered/lifecycle/ALL75/F40/
profile/artifact gates and three quiet rotated four-arm rounds, report all/no5%
minimum. Same2cbeb36f/private state-v2 inputs; actual T11 baseline preserved.

T12 full fidelity and three-round measurement gates pass: all rounds improve,
median 4.03% less CPU versus saved T11. 19 native bodies/1,716,209 native entries,
1,387,476 Python entries remain (not code-completion percentage). Closed proof:
[out/T12/validation-v1.json](../out/T12/validation-v1.json), all samples/scope in
[assessment](../out/T12/assessment.md). Initial wait-counter fixture gap retained
and resolved before source freeze, no runtime fix. No next task in this increment.

Final T12 upstream recheck: goal2 cee1de0f(PR491) includes the sealed-port match
route and PyPy 3.11 worker selection via GOAL2_ENGINE_PYTHON/auto-discovery, with
worker parity tests. This reinforces PyPy as the performance baseline; Rust
integration must preserve the worker/lifecycle/API boundary and remains separate.
No selected oracle routine semantic change: retain controlled 2cbeb36f pin/private
input policy. Archaeology main 2a411f50 remains unchanged.

## 2i. T13: play-state update caller

Translate contests.play_state_update0791:57AC, hottest remaining Python body after
T12(36,198 starts). One complete caller, finite four probes/two nearest-table
returns, keeper/candidate/destination/movement/holder branches;15 returns/14
registered callees remain explicit. Live own pointers/currentBP/actualAX/record/
flag/table semantics and None/True/False destination choice require exact tests.
Contract[tasks/T13.md](tasks/T13.md),[out/T13](../out/T13/README.md). Same pin/private
state-v2, T12 baseline preserved; full previous19-body/new caller/error/control/
observer/ordered/lifecycle/ALL75/F40/profile/artifact/closure proof and 3 quiet
rotated four-arm measured outcomes, no arbitrary5% floor. No callee/hardware claim.

T13 complete fidelity and measurements pass: all three rounds faster, median
5.27% less CPU than saved T12. 20 native bodies/1,752,407 native entries, 1,351,278
Python entries remain (not code-completion percentage). Closed current proof:
[out/T13/validation-v2.json](../out/T13/validation-v2.json), all samples/scope and
preserved failed error fixture in [assessment](../out/T13/assessment.md). No runtime
change for fixture correction. Existing callees remain delegated, no next task.

## 2k. T14: player-update caller

Translate motion.update_player0791:8AE9, hottest remaining Python body after T13
(75,781 starts). Immediate frame, finite11 handlers/5 fixed calls,16 registered
callee boundaries stay delegated. Preserve captured frame/linear rec/code/local
AXreply/kept versus live contents/conditional reads, integer0 versusNone, SENTAX
versus actual bank and exact observer/stack/ABI semantics. Contract:
[tasks/T14.md](tasks/T14.md),[out/T14](../out/T14/README.md). Full existing20-body/
new caller/control/error/observer/ordered/lifecycle/ALL75/F40/profile/artifact
closure,3 quiet rotated four-arm outcomes, no arbitrary5% floor; no callee/hardware
implementation claim, same2cbeb36f/private state-v2, actual T13 baseline preserved.

T14 accepted evidence: 21 native bodies, 1,828,188 native guest entries and
1,275,497 remaining Python entries in the measured fixture. All three paired
rounds improved; median CPU reduction versus T13 is 1.19%, with candidate/PyPy
CPU 1.056x. Strict ALL75 and F40 comparisons pass. See the
[assessment](../out/T14/assessment.md) and closed validation ledger.

Upstream rechecked 2026-11-01: archaeology remains `2a411f5`; goal2 is now
`51e70d3` (PR #494: CI/slow-runner infrastructure and job detachment fallback).
These changes do not alter the accepted oracle or this translation contract.

## 2l. T15: player sprite caller

Translate motion.move_player_sprite0791:8537, hottest remaining Python body in
T14's full profile (75,943 starts). Immediate frame, captured linear record and
sentinel, signed cell arithmetic, old background restoration / sprite draw,
holder/keeper/interception and ball movement/clamps; five registered guest-call
boundaries remain delegated. Preserve captured yield replies versus actual AX,
live pointers/record contents/DS argument and ordered observers. Contract:
[tasks/T15.md](tasks/T15.md), [out/T15](../out/T15/README.md). Same accepted pin and
private state-v2, actual T14 baseline preserved. Full prior 21-body regression,
new caller controls/errors/observers, ordered/lifecycle/ALL75/F40/profile/artifact
closure and three quiet rotated four-arm outcomes, all retained/no 5% floor.

T15 full fidelity and all three measured rounds pass: median 3.91% less CPU
than saved T14, with every outcome retained. The candidate uses 1.041x PyPy CPU
on this fixture and remains slower than PyPy. There are now 22 native bodies,
1,904,131 native guest entries and 1,199,554 remaining Python guest entries
(not a code-completion percentage). Accepted evidence:
[out/T15/validation-v1.json](../out/T15/validation-v1.json), complete samples and
scope in the [assessment](../out/T15/assessment.md). Strict ALL75/F40, exact
ordered callbacks, sealed lifecycle and independent backend attestation pass.
All 53 experiment groups are stopped. Upstreams remain archaeology `2a411f5`
and goal2 `51e70d3`; no roadmap change. No next task included in this increment.

## 2m. T16: player run-step and inline movement

Translate pilot.player_run_step 0791:8889, hottest remaining Python body after
T15 (75,781 starts). The source is a plain function: its movement, set tests,
attack/side/keeper/target and random helpers are inline, with no guest calls or
frame prologue. Preserve the nested parent-frame pointer, captured record and
deltas/random value, live content/pointers, seed writes, pitch/picture blocking
and unbounded source retry semantics. Contract: [tasks/T16.md](tasks/T16.md),
[out/T16](../out/T16/README.md). Same accepted pin/private state-v2 and saved T15
baseline. Full prior 22-body and new proof/controls/errors/source branch traces,
ordered/lifecycle/ALL75/F40/profile, closed artifact ledger and three quiet paired
four-arm outcomes; all outcomes retained, no 5% floor. No artificial guest-return
control, callee-frame or separate registered 86D0 implementation claim.

T16 full fidelity and all three measured rounds pass: median 5.03% less CPU
than saved T15, every outcome retained. Candidate/PyPy CPU is 1.073x on the
reference fixture (still slower than PyPy), with 2.627x paired CPython speed.
There are now 23 native bodies / 1,979,912 native guest entries, with 1,123,773
Python entries remaining (not a code-completion percentage). Closed evidence:
[out/T16/validation-v1.json](../out/T16/validation-v1.json), complete samples and
scope in the [assessment](../out/T16/assessment.md). Source branch traces and
all 13 write sites, strict ALL75/F40, ordered drive, sealed lifecycle and
independent backend attestation pass; all 56 experiment groups are stopped.

Upstream rechecked at completion: archaeology remains `2a411f5`; goal2 advances
to `0ea62a7` ([PR #499](https://github.com/diegoami/goal2/pull/499)), reporting
completed and still-running test modules promptly. This changes test reporting,
not the accepted oracle or worker API; no roadmap change. No next task included.

## 2n. T17: complete marking-target subtree

All five remaining Python bodies of the47C5 subtree are native together, with
13 real guest sites and unchanged inline/captured/live-state semantics. Contract:
[tasks/T17.md](tasks/T17.md), [evidence](../out/T17/README.md). Original source/
artifact/input bindings stayed fixed throughout measurements; variants use Python.

Fresh prior 23-body 67,144 normal comparisons, new 14,480 individual/integrated/ABI
comparisons,11,200 new errors,1120 source-branch comparisons,160 variants and all
body/output/13 return controls pass. An additional1280 live stack/pointer/SS/RNG
comparisons pass. Public 54 each CPython/PyPy,11 Rust,20GC, exact ordered full drive,
sealed lifecycle/independent backend attestations, strict ALL75/F40 and the full
profile pass. No new semantic fix, original data distribution or automatic review.

Profile:28 native bodies,2,129,564 native entries,974,121 Python entries. All three
paired rounds improve over saved T16; median7.82% less CPU. Same-campaign T16/PyPy
CPU 1.059106 versus T17/PyPy 0.974762; two rounds improve on PyPy and one uses 0.94%
more CPU. This is near parity on one fixture, with 2.52% less CPU at the median;
paired CPython speed2.861x. No general workload advantage or completion percentage.

A generated profile text report was initially classified as an input, causing a
metadata-only lifecycle wrapper rejection. The rejected receipt/report bytes are
preserved; source-clean check-v2 repeats all gates on the unchanged artifact.
Final validation explicitly checks that recovery, both ledgers,366 source/artifact/
input bindings,193 evidence hashes and actual-host closure of all 61 groups.
See [assessment](../out/T17/assessment.md) and [final ledger](../out/T17/validation-final-v2.json).
Live CI/merge/stop status remains checkpoint #1 /PR #43.

T17's profile identified geometry 2D10, positioning 42CB and 4A28 plus inline
Regs/direction work. T18 closes their common destination root and remaining
default dependencies. Broad dispatcher optimization remains separately measured.

## 2o. T18: complete player-destination subtree

All 15 remaining default bodies below 0791:4B64 are native together, preserving
41 real guest return sites, inline helpers and captured/live state semantics.
Fresh prior28 regressions and all new proofs, controls, errors, branches, variants
and live observers pass. Public60 each CPython/PyPy, Rust11, GC20, exact ordered
drive, sealed lifecycle, independent backend attestations and strict ALL75/F40
pass. Profile: 43 native bodies, 2,405,625 native entries, 698,060 Python entries.

All three complete paired rounds improve: median 20.57% less CPU than saved
T17. Same-campaign saved T17/PyPy 0.963176, T18/PyPy
0.765050; T18 uses 23.49% less CPU than PyPy on
this reference fixture. This is a partial port, not a general workload claim.
The initial mixed-interpreter preflight archive, outside-helper proof rejection
and incomplete timing campaign remain preserved. The full timing replacement
repeats every arm/round with unchanged guards and production bindings. Final
417-input/evidence ledger and actual-host closure of 83 groups:
[assessment](../out/T18/assessment.md), [validation](../out/T18/validation-final-v3.json).
Live CI/merge/stop status remains checkpoint #1 / PR #45. Finish T18 and wind down;
choose any later task from its complete profile in a new session.

## 2p. T19: complete depth-adjustment subtree

All five remaining default bodies below 474D are native with 23 guest return
sites and source-inline RNG/helpers preserved. Full prior43/new5 proofs, controls,
errors, branches, variants and three live matrices pass, alongside public65 each
CPython/PyPy, Rust11, GC20, exact ordered drive, lifecycle and strict ALL75/F40.
Final selector-count recovery retains all original comparisons and adds four
scoped post-return own-write checks: 20,160 comparisons across 122 distinct
selectors. Every rejected audit/preflight log remains preserved; runtime and
all original 466 bindings remain unchanged.

Profile: 48 native bodies, 2,508,808 native / 594,877 Python entries. All three
quiet paired rounds improve: median 6.78% less CPU than saved T18.
Same-campaign saved T18/PyPy 0.781398, T19/PyPy
0.739004; T19 uses 26.10% less CPU than PyPy on this
fixture. Partial engine port, no general workload or global coverage claim.
[Assessment](../out/T19/assessment.md), [final ledger](../out/T19/validation-final-v2.json).
All 75 recorded original/supplemental producer groups and the controller are
stopped. Live exact-head/main CI, merge and stop status remain checkpoint #1 /
PR #47. Finish T19 and wind down; no next task is started.

## 2q. T20: complete chase-gate subtree

All three default bodies 5729/2EB8/2EF0 are native, preserving five guest sites,
inline helpers and captured/live state. Prior48/new3 normal 147,832 pairs and
all required controls/errors/branches/variants/closure/four live matrices pass.
New error plan: 99 distinct selectors AND 99 execution rows, 15,840 comparisons.
Public70 each CPython/PyPy, Rust11, GC20, exact ordered drive, sealed lifecycle
and independently attested strict ALL75/F40 pass. Bounded fidelity pool before
guarded measurements; all 542 bound inputs fixed. No rejected canonical stage.

Profile:51 native bodies,2,542,617 native/561,068 Python entries. All three
paired rounds improve; median 4.16% less CPU than saved T19. Same-campaign
saved T19/PyPy 0.748274, T20/PyPy 0.717119
(28.29% less CPU on the reference fixture). This partial port has no global
coverage/general workload claim or arbitrary incremental 5% floor.
[Assessment](../out/T20/assessment.md), [final ledger](../out/T20/validation-final-v1.json).
All 80 recorded producer groups and controller are stopped. Live CI/merge/stop
status remains checkpoint #1 / PR #49. Finish T20 and wind down; no next task.

## 2r. T21: complete ball-travel and long-multiply subtree

835F/23E4:0279 are native together, preserving the one far guest return, captured
SENT/live DX and exact scratch/dead-stack/last-add flag semantics. Full prior51/
new2 normal154,024 comparisons and all controls/errors/branches/variants/closure/
five live matrices pass; positive six-flag/sign/min-word/sum-wrap/modulo32/
overflow witnesses. Public76 each/Rust11/GC20/observer328, exact ordered drive,
sealed lifecycle and independent strict ALL75/F40 attestations pass. Instrumented
draw-wrapper preflight correction/logs retained; separate native integration
added, no assertion drop or Rust semantic fix. All 598 bound inputs fixed.

Profile:53 native bodies,2,584,201 native/519,484 Python entries. All three paired
rounds improve; median 1.90% less CPU than saved T20. Same-campaign T20/PyPy
0.699125, T21/PyPy 0.686504 (31.35% less CPU on this
fixture). Modest gain below 5%; no arbitrary incremental floor, general workload
or global coverage claim. [Assessment](../out/T21/assessment.md),
[final ledger](../out/T21/validation-final-v1.json). All 85 recorded groups and
controller stopped. Live CI/merge/stop state remains checkpoint #1/PR #51.
Owner requested winding down for the day after this task; no next task started.

## 3. Engine milestone and goal2 adoption

Keep per-subtree proofs. Before an engine milestone, additionally run the
admitted ALL 75 and the explicit A700 corpus with its own strict oracle and
comparison script. A700 is excluded from ALL upstream. Preserve ref-121 as
the known noncompletion in both arms (archaeology#623); do not call it a pass
or replace it. T79's 699 equal completed matches prove the Python port, not Rust.

The owner runs the milestone review from a prompt naming the PR and requesting
the full report as a PR comment and its URL. Goal2 adoption separately requires
application fidelity, save/load, cancellation and native lifecycle/playtest.
T08 historically demonstrated26.73% less CPU than its saved hybrid baseline and
used 1.46x PyPy CPU (out/T08/assessment.md). T21 uses 31.35% less CPU than PyPy
on the reference fixture at the three-round median in its own campaign. Broader
adoption still needs its representative performance set and application gates.

Post-T16 upstream check: goal2 is now `1d274622` (archaeology remains `2a411f5`).
[PR #502](https://github.com/diegoami/goal2/pull/502) moves engine tests into PyPy
child processes; [PR #504](https://github.com/diegoami/goal2/pull/504) retries transient
half-time IPC read refusals. Preserve those worker/test contracts during later
Rust integration. Upstream T147 now plans a portable Windows folder with CPython
3.13 UI and PyPy 3.11 workers; T153 imports the owner's private data for playtesting.
These plans can proceed independently of Rust. They do not establish original-free
whole-game distribution or change this port's accepted pin/private-data policy.
See [adoption details](porting-chunks.md#performance-reporting-and-adoption).

## 4. Beyond the match engine

Tournament continuation remains original code under Unicorn (archaeology#427),
the board screen is outside the sealed fidelity comparison, and a fresh career's
initial state still originates in a savestate. Translate these boundaries only
with accepted upstream semantics and dedicated tasks. Sealing the match engine
does not establish an independent whole game.

Current accepted source checked 2026-10-31: state-v2 merge
`2cbeb36fdd3feb369324aaa88e6e4d2aa3b3d99c`, [PR #640](https://github.com/diegoami/goal2-archaeology/pull/640).
Historical handover e0270981 included PRs
[#624](https://github.com/diegoami/goal2-archaeology/pull/624),
[#625](https://github.com/diegoami/goal2-archaeology/pull/625),
[#626](https://github.com/diegoami/goal2-archaeology/pull/626),
[#627](https://github.com/diegoami/goal2-archaeology/pull/627),
[#628](https://github.com/diegoami/goal2-archaeology/pull/628), and
[goal2#478](https://github.com/diegoami/goal2/issues/478).

Latest upstream check (2026-11-02): goal2 `ed582f99`, archaeology `2a411f50`.
Goal2 PR #515 requires PyPy child processes for its engine tests; T154 / issue
#516 plans an application-boundary evaluation after the playable build. A future
Rust CPython module needs explicit API ownership, threading/GIL release and
portable target ABI/loading evidence; the current partial port still calls Python.
These integration requirements do not change the accepted oracle or T18 scope.

T19 final upstream check: goal2 `6bfdfbbd`, archaeology `2a411f50`. Portable
Windows CPython 3.13/PyPy 3.11 packaging is now merged (#510); core-save launch
routing (#519), released-versus-exited viewer behavior (#517) and replay timeout
diagnostics (#521) matter to later application adoption. T152's amended contract
(#522) retains EngineRuntimeMissing with no silent CPython fallback. These do
not change the pinned T19 oracle or supply Rust target ABI/GIL/application proof.
See [adoption update](porting-chunks.md#upstream-adoption-update-after-t19).

T20 final upstream check: goal2 `60fd39e6`, archaeology `2a411f50`. Owner m3
removes GOAL.EXE/Unicorn/recorded boot state after m2/ZIP playtest; GOAL.DAT is
read from the player's install first. Rust proceeds in parallel. First-run import
(#514) and the uninterrupted original playthrough T156 (#528) are merged. The
T156→T157→T158 design phase absorbs T154 into a measured technology/route/engine/
packaging evaluation, followed by the owner's decision. Preserve application,
GIL/threading and portable ABI gates; no original assets copied and no pin refresh
during this controlled campaign. See [adoption update](porting-chunks.md#upstream-plan-and-design-update-after-t20).

T21 final upstream check: goal2 `39d545bb`, archaeology `2a411f50`. Approved
original-faithful screen/flow design T157 (#530), optional checked help import
(#531) and play-next/captain-stop UX (#529) are now merged. Keep those contracts
for later application parity; they do not alter the accepted match-engine pin
or prove Rust GIL/thread/portable ABI adoption. T158/owner technology decision and
Rust-in-parallel m3 order remain. See [adoption update](porting-chunks.md#upstream-adoption-update-after-t21).

Upstream now approved the T158 long-lived PyPy engine process over a pipe, with
the Rust hybrid adopted inside it later after its gates. Track A owns UI/process
protocol; Track B owns native whole-game rules. See the [T22 upstream update](porting-chunks.md#t22-scope-and-upstream-adoption-update-2026-11-03).

During T24, goal2 `e44a66fe` adds the T170 whole-season task contract, dependent
on archaeology T123 **and the new T124 round-end ports**. Archaeology `82984287`
splits the route harness into T119a/b and adds stage dispatch/builders/news as
explicit missing scope. These are plans and static findings; no selected
match-engine runtime change appears in either upstream diff. Keep T24 frozen
and its oracle pinned. Future whole-game adoption requires the round-end proofs
as well as route continuation; the match-engine body/entry counts are not a
whole-game denominator. See the [dependency update](porting-chunks.md#upstream-whole-season-dependency-update-during-t24).

T25 resume upstream check (2026-11-04): goal2 `8893411f`, archaeology `04021dd0`.
Competitive route correction T119c and E040 evidence are now in archaeology;
T120's silent-fixture proof runner/input contract remains further work. Goal2
has advanced save/quit and management UI. Keep T25's oracle/artifact fixed and
finish its remaining M3 gates; select following scope only from the fresh full
profile. See the [resume dependency check](porting-chunks.md#t25-resume-dependency-check-2026-11-04).

T27 preparation upstream check (2026-11-04): goal2 `ec9429c6` contains the
original-kit UI correction; archaeology `d3375867` now merges
[T120 / PR #650](https://github.com/diegoami/goal2-archaeology/pull/650),
porting the silent fixture path (6970, D47E, B602, BB2F) with E040 proof and
falsifier records. This advances the later whole-game route dependency. The
upstream T124a ordering now follows T120 rather than waiting for T121.
These additions do not change T27's selected seven-body tree or authorize a
mid-campaign oracle refresh. Keep its controlled `2cbeb36f` pin and finish its
full fidelity/performance gates before merging. Later route adoption must assess
the new module and its dedicated proofs explicitly; a match-engine receipt does
not establish whole-game parity.

T27 resume dependency check (2026-11-05): goal2 `3fb3191d` adds T180's match
stop/bench UI and requires in-season ageing for T170. Archaeology `7032ce40`
merges T124a round-end framing, T124t legal-eleven harness and T121 fixture
routing/news. T122 is split into five proof slices; T124b into rankings/draw,
and required in-season ageing T124f now precedes sealed-season T123, while
sealed year rollover stays deferred. These advance later whole-game dependencies;
they do not replace T27's controlled `2cbeb36f` match pin or its full gates.

T27's complete seven-body strength closure now passes its full local canonical,
corpus and quiet timing campaign,with 86/422 bodies and 89.02% native fixture
entry frequency. Median CPU use is4.80% lower than saved T26 with one3.05%
slower round;one-fixture evidence only. Final ledgers pass;checkpoint#1 owns
exact-headCI/merge/mainCI/merged-audit status. No following scope is started.

T28 start dependency check(2026-11-05):goal2 `f19309df` adds T181 replay/saved
summaries,T148 native Qt scaling and explicit season terminal boundary before
deferred rollover;archaeology `174dfe4b` advances shared news primitives/result
columns(T122a/b). These affect later whole-game/application adoption;T28 retains
the accepted `2cbeb36f` pin and existing match family. No new adoption proof is
inferred from this native subtree.

T28 local campaign completes the six-function pass-receiver path through its
existing native keeper boundary:87/422 native bodies and90.17% native fixture
entry frequency. Accepted quiet timingv2 uses2.12% less CPU than saved T27 at
the paired median,all rounds improve;whole rejectedv1 remains preserved.
A separately sealed post-writer audit correction retains every historical/new
matrix gate and all frozen sources. Checkpoint#1 owns finalCI/merge/mainCI/
merged-audit status;following scope must come from the fresh full profile.

T29 start dependency check(2026-11-06):goal2 `c951855b` removes file journals
(T161),adds independent menu navigation and commentary reading pause(T184/185),
and requires best-twenty selection beforem3. Archaeology `953b57ee` merges
T122c/d/e news/route proofs,T125 original-backed best-twenty assistant,T123a
speaker ABI and captain-reentry/stopped-edit fixes(#659/#663). These are material
later application/whole-game and oracle-refresh dependencies. Before adopting a
new source pin,assess those behavior changes and regenerate its full receipts;
T29 deliberately retains accepted2cb/privateT07 and all current match gates.
No new application/adoption proof follows from this native chunk.
