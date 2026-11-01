# Engine roadmap

[designed: owner, 2026-10-30] Adopt the upstream sealing contract, refresh the
oracle and evidence, profile the Rust machine, then translate complete hot call
trees. This follows the owner's approval of the upstream assessment. T02 is
complete; its historical receipts and Done-when remain unchanged.

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
six-slot delay-table and key/quick branches; its15 literal guest-call sites and12
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

Upstreams rechecked before T11: archaeology2a411f50 unchanged; goal2 advances
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
observer/ordered/lifecycle/ALL75/F40/profile/artifact/closure proof and3 quiet
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
private state-v2, actual T14 baseline preserved. Full prior21-body regression,
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
baseline. Full prior22-body and new proof/controls/errors/source branch traces,
ordered/lifecycle/ALL75/F40/profile, closed artifact ledger and three quiet paired
four-arm outcomes; all outcomes retained, no 5% floor. No artificial guest-return
control, callee-frame or separate registered 86D0 implementation claim.

## 3. Engine milestone and goal2 adoption

Keep per-subtree proofs. Before an engine milestone, additionally run the
admitted ALL 75 and the explicit A700 corpus with its own strict oracle and
comparison script. A700 is excluded from ALL upstream. Preserve ref-121 as
the known noncompletion in both arms (archaeology#623); do not call it a pass
or replace it. T79's 699 equal completed matches prove the Python port, not Rust.

The owner runs the milestone review from a prompt naming the PR and requesting
the full report as a PR comment and its URL. Goal2 adoption separately requires
application fidelity, save/load, cancellation and native lifecycle/playtest.
The hybrid Rust engine has not beaten PyPy. T08 demonstrates a 26.73% median
CPU reduction against the preserved hybrid baseline in three simultaneous rounds;
the candidate still uses about 1.46x PyPy CPU (out/T08/assessment.md).

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
