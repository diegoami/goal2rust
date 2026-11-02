# T19 depth-adjustment subtree

All five remaining default Python bodies below `adjust_depth_offset` are native
together: positioning 474D/4532/4649, geometry 2BB1 and entrypoints 214B:06FA.
All 23 real guest sites, near/far ABI and source-inline helpers remain observable.
Captured parent pointers, yielded values and frame BP remain distinct from live
stack words, SS, registers and record contents. The coin retains its RNG inline;
no registered random_n call or extra guest frame is introduced. Nondefault
variants stay Python. This remains a partial engine port.

Same accepted oracle `2cbeb36fdd3feb369324aaa88e6e4d2aa3b3d99c` and private
T07 state-v2/tables. The actual accepted T18 baseline was saved before builds
in `.cache/T19-baseline`; `baseline-snapshot-v1.json` binds its 54 files.
Historical `.cache/T18-baseline` is T17 and is not the comparator. No original
bytes are committed.

## Combined-artifact proofs

Fresh prior-43-body normal proofs pass 123,064 comparisons and all prior
controls/errors/branches/variants/observers. The new tree passes 16,480 full-state
individual/integrated/ABI comparisons, including eight actual entry captures per
body, authored random/edge inputs, four observer modes and direct/pause/replay
schedules. The initial error plan executes 19,520 comparisons across 122 rows (118 distinct
selector strings). Four additional scoped post-return write selectors add 640
comparisons: the combined result passes **20,160 error comparisons across 122
distinct selectors**, retaining every original row. It also passes 1,280 positive
source-branch pairs and 112 variants. Scoped
execution checks prove zero owned Python body/helper execution during 10,480
native lifetimes, with positive source/outside/variant witnesses.

All 10,480 new body controls, 4,192 output/flag controls and 3,680 comparisons
across 23 individually reached return controls pass; unreached paths stay equal.
Three refreshed live-observer matrices pass 1,280 cases each, retaining T17/T18
coverage and adding parent-pointer capture, live popped group/dead t6 words,
captured SENT versus actual AX, live record depth after a child return, fresh
SS/local result, captured slot/live AH and captured RNG seed/live DF.

Public CPython and PyPy each pass 65 tests; Rust passes 11 tests; GC parity passes
20 cases and the supplemental legacy observer matrix passes 328 comparisons.
The exact reference/native drive agrees on 831 events, 553 stretches, result,
records, full memory and ordered 158,092,780 IO observations (114,492 enter/leave
listener pairs, 81,134 enter/leave site pairs and four writes), with digest
`096f56c262844705a0fcf7348fa4563c40e7d3ff4554b05c5224ffb0a7080ea9`.

## Translation progress

The full profile confirms 48 native registered non-stub bodies of 422 (11.37%
by equal-weight routine count), and 2,508,808 native guest entries of 3,103,685
(80.83% on this fixture). There are 594,877 Python entries left; 103,183 entries
move to native. These figures are neither source-line, CPU-time nor global test
coverage. Guest-entry counts are not exact FFI transition counts.

## Retained preflight correction and immutable artifact

The first preflight SS-alias probe matched unrelated stack writes at a shared
guest-return address. Source and Rust produced the same error, but the probe
required a positive successful scenario. Its source/log are preserved as
`rejected_live_probe_v1.py` and `rejected-live-preflight-v1.log`. The corrected
probe targets the intended local-byte write and restores SS at the source's
actual return stack delta. All eight scenarios then pass before freeze and on
the canonical artifact. No Rust semantic correction or later rebuild was needed.

Both interpreter installations and preflight tests finished before the accepted
`artifact-archive-v1.json` was copied. `freeze-v1.json` binds 466 concrete source,
binary and input files. Explicit source/input allowlists exclude generated
profile/text outputs; the exclusion probe passes. Completed historical receipts,
private captures, saved baseline and accepted archive remain unchanged. No
assertion/corpus/guard/source-stability weakening or overwritten receipt is used.


## Full corpus and lifecycle

Strict ALL75 and exact-source F40 comparisons pass; all 75 records complete
without errors. Strict 10/20/30/60 prefixes are preserved. Independent attestation
covers 75 family Rust machines and all 48 bodies. All four sealed lifecycle
checks pass (engine, interactive, goals, knockout), with 11 independently attested
Rust machines and all 48 bodies.

## Final error-count audit and stronger recovery

The original final validator correctly rejected the claim that 122 error-plan
rows were 122 distinct selector keys. Four `write:PC` strings occur twice because
a guest-return stack write and a subsequent own write share the same PC:
4549, 4660, 46D4 and 46EE. All original 19,520 comparisons ran; the dictionary
contains 118 distinct keys. The rejected validator source, log and status remain
unchanged. No successful receipt was rewritten.

`proof-plan-v2.json` adds four distinct `post-return-write` selectors and 640
full-state source/Rust comparisons. They require the guest return to have fired
and the write width and frame-relative address to match the intended own write.
Positive witnesses prove the older selector stops before that return and the new
selector reaches the later write. All 640 comparisons pass, with 160/160 reached
for each group push and 10/160 reached for each conditional local-byte write.
The combined proof retains 126 execution rows, 20,160 comparisons and **122
distinct, independently reached selector keys**. Acceptance uses versioned
`validate_v2.py` and [validation-final-v2.json](validation-final-v2.json).

One supplemental launch omitted the required fixed hash seed and stopped at the
unchanged verifier before any comparison. Its rejection log is preserved; the
identical script passes with `PYTHONHASHSEED=0`. No runtime, binary, private input,
corpus or timing sample changed. The requirement remains 122 distinct selectors;
every original comparison and all other fidelity gates are retained. Supplemental audit/proof
sources are explicitly bound after all original writers exit, retaining every
one of the original 466 bindings.

## Same-campaign performance

Source: [all raw four-arm samples and ratios](performance-v1.json), with each
`cpu-*-r*-v1.json` receipt. Three rounds start after three observations with both
1-minute and 5-minute load below 4. Four arms launch together on distinct reported
physical cores, rotating core assignments and launch order. Dispatch guards
remain unchanged. Every round is retained; no campaign or timing arm is replaced.

CPU seconds:

| Round | Saved T18 | T19 | Plain CPython | PyPy |
| --- | ---: | ---: | ---: | ---: |
| 1 | 36.451555 | 33.979153 | 132.087327 | 45.294170 |
| 2 | 36.955123 | 34.950174 | 128.919263 | 47.293603 |
| 3 | 36.364155 | 33.811994 | 129.274389 | 46.656647 |

| Round | T19 / saved T18 | Saved T18 / PyPy | T19 / PyPy | CPython / T19 |
| --- | ---: | ---: | ---: | ---: |
| 1 | 0.932173 | 0.804774 | 0.750188 | 3.887305 |
| 2 | 0.945746 | 0.781398 | 0.739004 | 3.688659 |
| 3 | 0.929817 | 0.779399 | 0.724698 | 3.823329 |
| Median of per-round ratios | 0.932173 | 0.781398 | 0.739004 | 3.823329 |

T19 uses **6.78% less CPU than saved T18** at the median, with all three
rounds improving (range 5.43%–7.02% less). In the same campaign,
saved T18 uses 21.86% less CPU than PyPy at the median, and T19 uses
**26.10% less**, with all three comparisons improving. Paired plain-CPython/
T19 CPU speed is 3.823×. These are medians of per-round
ratios, not ratios of CPU medians or comparisons with historical standalone gaps.
No arbitrary per-translation 5% floor is introduced.

This is one reference fixture, not a general workload or application result. The
engine is still partly Python; this does not provide GIL release or UI-thread
safety. Engine A700/ref-121/owner milestone review and application save/load,
cancellation, API/thread ownership, portable ABI/loading and playtest gates remain.

## Closed evidence and shutdown

Final validation verifies all 466 original source/binary/input bindings unchanged,
explicit supplemental proof/audit bindings and 201 evidence hashes. The
post-writer audit maps all 417 accepted T18 source/input bindings to preserved
baseline files or unchanged historical inputs, and verifies all 230 old evidence
hashes. Historical T18/T17 profiles match their inventory digests and accepted
main. All three saved-baseline/candidate drives reject/accept the new five-body
native-presence criterion respectively, while outputs agree.

The original controller and all 74 original producer groups are stopped; the
additional scoped-error proof group is stopped too, for 75 recorded groups total.
See [process closure](process-closure-v2.json), [baseline/input audit](supplemental-audit-v1.json)
and [final ledger](validation-final-v2.json). Live exact-head/main CI, merge and
stop status remain in checkpoint #1 and [PR #47](https://github.com/diegoami/goal2rust/pull/47).
No next task is included.
