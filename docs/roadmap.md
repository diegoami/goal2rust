# Engine roadmap

[designed: owner, 2026-10-30] Adopt the upstream sealing contract, refresh the
oracle and evidence, profile the Rust machine, then translate complete hot call
trees. This follows the owner's approval of the upstream assessment. T02 is
complete; its historical receipts and Done-when remain unchanged.

## 1. T03: sealed-engine compatibility

Archaeology PRs #627 (sealed family) and #628 (handover) merged with passing
checks. PROVENANCE.md and CI pin their accepted handover commit; T03's evidence
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

## 3. Engine milestone and goal2 adoption

Keep per-subtree proofs. Before an engine milestone, additionally run the
admitted ALL 75 and the explicit A700 corpus with its own strict oracle and
comparison script. A700 is excluded from ALL upstream. Preserve ref-121 as
the known noncompletion in both arms (archaeology#623); do not call it a pass
or replace it. T79's 699 equal completed matches prove the Python port, not Rust.

The owner runs the milestone review from a prompt naming the PR and requesting
the full report as a PR comment and its URL. Goal2 adoption separately requires
application fidelity, save/load, cancellation and native lifecycle/playtest.
The current hybrid Rust engine has not beaten PyPy (T02: 107.394 versus 48.634
CPU seconds on the same drive).

## 4. Beyond the match engine

Tournament continuation remains original code under Unicorn (archaeology#427),
the board screen is outside the sealed fidelity comparison, and a fresh career's
initial state still originates in a savestate. Translate these boundaries only
with accepted upstream semantics and dedicated tasks. Sealing the match engine
does not establish an independent whole game.

Accepted source checked 2026-10-31: archaeology handover `e0270981883f02ce46a31391e7070079977bbfef`, PRs
[#624](https://github.com/diegoami/goal2-archaeology/pull/624),
[#625](https://github.com/diegoami/goal2-archaeology/pull/625),
[#626](https://github.com/diegoami/goal2-archaeology/pull/626),
[#627](https://github.com/diegoami/goal2-archaeology/pull/627),
[#628](https://github.com/diegoami/goal2-archaeology/pull/628), and
[goal2#478](https://github.com/diegoami/goal2/issues/478).
