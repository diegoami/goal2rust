# T03: accepted sealed-engine compatibility

All three unchanged Done-when gates in `docs/tasks/T03.md` / `docs/roadmap.md`
pass locally. The accepted oracle is
`e0270981883f02ce46a31391e7070079977bbfef`, the merged T80d handover including
T80c's sealed family. Final-head CI and merge are tracked in PR #14 / issue #8.
The owner requested wind-down after T03; T04 has not begun.

## Result and implementation

The existing Rust machine works with the upstream `Image.from_state(state,
tables)` input and `records_after()` output. After checkpoint load, callers
supply `records_after(tables)` explicitly because upstream does not serialize
the tables object. The build/API guide now shows this route and worker isolation.

No production Rust routine, dispatcher, frame or adapter code changed. The
seven translated bodies and their machinery are unchanged in the new oracle;
CI/provenance now select the accepted sealed source. T01/T02 translation-origin
pins, receipts and failures remain historical, not re-labelled as new proof.
The old oracle is preserved separately. Tables were generated locally from
the owner's registered executable; tables, states, images and checkpoints stay
in ignored cache and are never shipped or committed here.

## Correctness gates

| Gate | Fresh evidence and result |
| --- | --- |
| Public API | Authored synthetic data exercises invalid state/table binding/module bytes, Rust records output and checkpoint roundtrip; final test fails on the old oracle's missing API. All 10 public tests pass on CPython and PyPy; Rust tests pass. |
| Per-call/body/full-frame differential | `differential-v1.json`: **28,224/28,224 equal**, 500 random plus four real captures per routine, four tap/listener modes, body and whole frame. |
| Body control | `body-mutant-v1.json`: omitted dead stack byte caught in **3,720/4,032** cases for 0791:2B51. Raw differences remain private; committed values are hashes. |
| Machine control | `machine-mutant-v1.json`: incremented saved return IP caught at 0791:0111 by the full-frame differential. |
| Ordered state-input drive | `compare-taps-v1.json`: **831 events**, result, returned state, full memory, **553 stretches** and complete ordered taps equal. Rust records **880,504 native calls** across exactly seven addresses. |
| Sealed lifecycle | `check-v1.json`: engine, interactive save/load, goals and knockout including extra-time/shootout replay all pass under positive Unicorn/original-file denial. Straight/resumed/expected digests agree. |
| Lifecycle identity | Independent sidecar records **11 Rust machines / 18,256,225 native calls**. |
| ALL / F40 | Strict unchanged comparators: **ALL 75/75 identical, F40 40/40 identical, 0 fail**, exit 0. F40 source lines are selected byte-for-byte from the same fresh ALL run with line hashes. No recovery, missing IDs or relaxed limits. |
| Family identity | Independent sidecars account for **75 Rust machines / 99,434,036 native calls** across two workers. |
| Artifact closure | `validation-v2.json`: all source/extension manifests rehashed, comparisons and controls checked, selection/progress-line provenance verified, all producers exited, and recursive evidence hashes recorded. |

The ordered stream hash is
`afcb5ec2ad3800a7d969f8cda6a513577d3e39feff886a441a48cbd814d0f191`.
It contains 158,092,780 IO calls, 114,492 listener enter/leave pairs and 81,134
site enter/leave pairs. This producer also extracts records_after, adding a
full-memory read; the comparison is between equivalent new state-input runs,
not against historical image-input memory/tap hashes.

## Paired performance

Three drives started together after three quiet observations with both 1m/5m
load below 4, after every family/lifecycle producer finished. Default CPU-mode
guards were unchanged. Events/result/records/full memory/stretches agree across
all three interpreters/backends; source and extension manifests stayed unchanged.

| Backend | CPU seconds |
| --- | ---: |
| Plain CPython 3.12 | 193.296 |
| Plain PyPy 3.11 | 82.009 |
| Rust machine, seven native bodies, CPython bridge | 159.681 |

Rust is **1.211 times as fast as plain CPython** in this pair, and uses
**1.947 times plain PyPy's CPU**. It has not beaten PyPy. This is one paired
drive, not a distribution or an incremental speed comparison with T02's different
day/input/producer. T03 changes compatibility and proof coverage; most routine
bodies still run through Python. No speed gain from sealing is claimed.

## Evidence finality and limits

The initial `validation-v1.json` snapshot preceded the supervisor's final log
banner. It is retained unchanged. `validation-v2.json`, written after every
writer exited, is the authoritative final index; the sole changed old-index
file is proved to differ only by that final banner. Both measured extension
builds are preserved in ignored `.cache/T03-artifacts` by digest, so a later
T04 rebuild need not destroy the measured binaries.

The first public-test attempt exposed a missing sys import in the new helper;
it was corrected and its failure log retained. Raw logs retain original
whitespace; source-only whitespace checks pass. No production defect or
acceptance exception was introduced to obtain these results.

Coverage remains finite: seven native bodies, four real captures each, one
ordered fixture, one paired timing, and the admitted ALL 75. A700's larger
699-completed-match corpus remains an engine-milestone gate, not a Rust result
established here; preserve its known ref-121 noncompletion. Process-wide adapter
coexistence and other review #6 limits remain as documented. Tournament
continuation, board display fidelity and initial-career state are still outside
the sealed match-engine contract.

Next task is T04 (#9): refresh the profile on the accepted sealed input, confirm
the provisional 0791:2956 → 1771:3216 tree, then implement native caller
continuations with the full per-call/frame/tap/family/lifecycle/timing gates.
The old-pin profile supports that candidate but does not waive the refresh.
