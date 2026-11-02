# T18 player-destination subtree

All 15 remaining default Python bodies below `update_player_destination` are
native together. The combined artifact preserves all 41 real guest return sites
and source-inline work, with existing native descendants as closure boundaries.
Nondefault variants still execute Python. This remains a partial engine port.

The accepted oracle is unchanged at `2cbeb36fdd3feb369324aaa88e6e4d2aa3b3d99c`,
using the private T07 state-v2 and tables. No original bytes are committed.
Actual accepted T17 source, adapter, tests and CPython/PyPy binaries were saved
before builds in `.cache/T18-baseline`; its 50 files remain hash-bound.

## Fidelity

The final combined artifact passes 81,624 fresh prior-28-body normal comparisons
and all corresponding controls, errors, branches and observer checks. New proofs
pass 41,440 full-state individual/integrated/ABI comparisons, 44,480 injected-error
comparisons across 278 reached selectors, 3,200 positive source-branch pairs and
320 variant comparisons. Scoped execution checks prove zero owned Python body or
helper execution during 31,440 native lifetimes, with positive outside/variant
witnesses. All 31,440 body controls, 20,960 output/flag controls and 6,560
comparisons across 41 individually reached return controls behave as declared.

Two 1,280-case live-observer matrices cover prior T17 and new T18 captured versus
live pointer, stack, SS, register, flag and local semantics. Public CPython and
PyPy each pass 60 tests; Rust passes 11 tests and GC parity passes 20 cases. The
legacy supplemental observer matrix passes 328 comparisons.

Exact reference/native drives agree on all 831 events, 553 stretches, result,
records, full memory and ordered 158,092,780 IO observations, with digest
`096f56c262844705a0fcf7348fa4563c40e7d3ff4554b05c5224ffb0a7080ea9`.
All four sealed lifecycle checks pass. Strict ALL75 and exact-source F40 pass;
10/20/30/60-record strict prefix snapshots are preserved. Independent Rust
attestations cover 11 lifecycle machines and 75 family machines.

## Translation progress

The complete profile confirms 43 native registered non-stub bodies out of 422
(10.19% by equal-weight routine count), and 2,405,625 native guest entries out of
3,103,685 (77.51% on this reference fixture). Python entries fall to 698,060;
276,061 entries move to native. These are neither source-line, CPU-time nor
global test coverage percentages. Guest entries are not exact FFI counts.

## Preserved rejected attempts and bindings

The first preflight archive raced PyPy installation and combined the new CPython
library with historical PyPy. It was rejected before canonical producers; v1
bytes remain preserved. `artifact-archive-v2.json` is authoritative.

The original canonical destination proof stopped at its outside-helper positive
witness: `pitch` was missing from the proof ownership set. Equality and the
zero-inside assertion passed. The rejected v1 log remains unchanged. A versioned
proof adds ownership tracking and proves the outside witness on all 120 actual
entry inputs, retaining every assertion and case. No production semantic fix or
rebuild was needed. All 401 original bindings remain unchanged; the explicit v2
freeze binds 409 sources, binaries and inputs, including recovery drivers.

Generated profile/text outputs are excluded from the executable source allowlist.
Final audits retain both controller ledgers and every rejected outcome. No
source-stability override, reduced corpus or selectively repeated timing headline
is used. See [final ledger](validation-final-v3.json), [post-exit audit](post-exit-audit-v3.json)
and [process closure](process-closure-v3.json).

The initial timing campaign is rejected because round 3 plain CPython hit the
unchanged 60-second dispatch guard. All 11 completed samples and every log remain
preserved in `cpu-*-v1` and `timing-disposition-v1.json`; no complete v1 summary
was produced. The replacement runs all three four-arm rounds with identical
production artifact, inputs, guards and quiet criteria. It does not substitute
only the missing CPython arm. The final explicit v3 freeze contains 417 inputs,
retaining all 409 prior bindings and adding versioned timing/audit tooling.

### Rejected timing campaign: every sample

CPU seconds below are retained diagnostic outcomes, not a completed timing gate.
The third plain-CPython arm timed out and has no completed CPU receipt.

| Round | Saved T17 | T18 | Plain CPython | PyPy |
| --- | ---: | ---: | ---: | ---: |
| 1 | 51.419830 | 41.947517 | 181.631356 | 55.324275 |
| 2 | 57.858912 | 44.690649 | 160.546367 | 67.434682 |
| 3 | 55.290846 | 45.172163 | dispatch timeout | 62.401821 |

## Complete replacement timing campaign

Source: [all four-arm samples and ratios](performance-v2.json), with individual
`cpu-*-v2.json` receipts. Each round starts after three observations with both
1-minute and 5-minute host load below 4. Four arms launch together on distinct
physical cores, with assignments and launch order rotated. The 60-second
per-dispatch guard is unchanged. Every outcome from both campaigns is retained.

CPU seconds:

| Round | Saved T17 | T18 | Plain CPython | PyPy |
| --- | ---: | ---: | ---: | ---: |
| 1 | 46.336241 | 36.441490 | 162.903568 | 46.452946 |
| 2 | 53.808447 | 43.962363 | 147.658609 | 58.733379 |
| 3 | 46.956567 | 37.297552 | 131.176871 | 48.751780 |

| Round | T18 / saved T17 | Saved T17 / PyPy | T18 / PyPy | CPython / T18 |
| --- | ---: | ---: | ---: | ---: |
| 1 | 0.786458 | 0.997488 | 0.784482 | 4.470277 |
| 2 | 0.817016 | 0.916148 | 0.748507 | 3.358750 |
| 3 | 0.794299 | 0.963176 | 0.765050 | 3.517037 |
| Median of per-round ratios | 0.794299 | 0.963176 | 0.765050 | 3.517037 |

T18 uses **20.57% less CPU than saved T17**, improving in all three rounds
(range 18.30%–21.35% less).
In this same campaign saved T17 uses 3.68% less CPU than PyPy at the median,
and T18 uses **23.49% less**, improving on PyPy in all three rounds. Paired
plain-CPython/T18 CPU speed is 3.517×. Summaries
use medians of per-round ratios, not ratios of medians or historical PyPy gaps.
No per-translation 5% floor is introduced.

This demonstrates a measured gain for this bounded tree on one reference fixture.
It does not prove a general PyPy advantage, source-line completion, portable
application performance or UI-thread/GIL safety. Runtime and state remain partly
Python. Engine A700/ref-121/owner review and application/worker/save-load/
cancellation/ABI/packaging/playtest gates remain separate.

## Final closure

The host audit verifies all 83 recorded process groups and all three controllers
have exited, including rejected proof/timing attempts and both sets of 12 timing
children. Original sources, binaries, private inputs, the 50-file baseline and
preserved archives match their bindings. Final validation binds 417 inputs and
all completed/rejected evidence. CI, merge and stop status live in checkpoint #1
and [PR #45](https://github.com/diegoami/goal2rust/pull/45). No next task is included.
