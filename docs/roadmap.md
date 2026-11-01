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
