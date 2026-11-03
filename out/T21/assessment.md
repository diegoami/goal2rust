# T21 ball-travel and long-multiply subtree

The complete default tree below motion.ball_travel 0791:835F is native, including
runtime.sys_long_mul 23E4:0279 and its flags helper. The far return 0791:8396 stays
a real guest boundary. Neither entry is long=True. The caller returns captured
SENT low AX while preserving live DX; the multiply captures all operands before
flush and preserves full scratch state, dead stack words and the last 16-bit
addition's six arithmetic flags. No dead caller-local write absent from the port
is invented. Nondefault variants stay Python. This remains a partial engine port.

Same accepted oracle `2cbeb36fdd3feb369324aaa88e6e4d2aa3b3d99c` and private
T07 state-v2/tables. The actual accepted T20 baseline was preserved before builds
under `.cache/T21-baseline`; baseline-snapshot-v1.json binds 58 files. Historical
`.cache/T20-baseline` is T19 and is not the comparator. No original bytes committed.

## Combined-artifact fidelity

Fresh prior 51 normal proofs pass 147,832 comparisons and all inherited controls,
errors, branches, variants, closure checks and four live matrices. T19's scoped
own-write 640 comparisons remain, establishing its 122 distinct selectors across
20,160 comparisons. T20's 99-row/99-distinct error plan is retained.

The new tree passes 6,192 full-state individual/integrated/ABI pairs, with at least
eight real entry states per body, 500 authored random/edge inputs in all four
observer modes and direct/entry/guest pause-replay schedules. The real-state
schedule count is 192 (2 bodies×8 captures×4 observers×3 schedules). It passes
6,720 error comparisons across 42 execution rows AND 42 distinct reached selectors,
480 positive arithmetic/branch pairs and 32 variants. Source witnesses cover both
outcomes of CF/PF/AF/ZF/SF/OF, signs, min-word abs, sum wrap, zero/nonzero,
32-bit overflow and the independent modulo32 product identity. Scoped execution
shows zero owned Python within 4,192 native lifetimes, with positive source/
outside/variant witnesses.

All 4,192 body controls, 6,288 full-output controls (AX/DX/EFLAGS 2,096 each) and
160 individually reached/detected return controls pass. Five refreshed live
matrices pass 1,280 comparisons each; the new matrix covers captured sum/live scale
and CX, captured SENT/live DX, live record SS, register arguments, captured
multiply inputs, final live flags, cached stack SS and captured record/live data.
Every scenario has positive mutation/effect witnesses, including a second cached-
SS write after a stack split and flags changing after scratch but before store.

Public CPython and PyPy each pass 76 tests, Rust 11, GC parity 20 and the supplemental
legacy observer matrix 328. Reference/native ordered drive agrees on 831 events,
553 stretches, full memory/result/records and 158,092,780 ordered IO observations
(114,492 listener enter/leave pairs, 81,134 site enter/leave pairs, four writes),
with digest `096f56c262844705a0fcf7348fa4563c40e7d3ff4554b05c5224ffb0a7080ea9`.

## Preserved instrumentation preflight correction

The first full public preflight had 75 tests and failed because observed/fault-
injection draw-state wrappers at the newly native travel/multiply addresses still
used default variant None. Native dispatch bypassed their instrumentation.
Rejected CPython/PyPy logs are preserved, with the original harness retained in
the pre-build baseline and its digest in preflight-v1.json.

The observed wrappers now carry explicit nondefault tags, retaining their trace
and fault assertions. A separate 32-case actual-native draw→membership/travel→
multiply integration check was added; public count is 76. No old assertion was
dropped and no Rust semantic correction was needed. Both interpreter installs
and successful public preflight finished before artifact-archive-v1 was copied.
Canonical proofs all bind the final combined artifact.

## Translation progress and fixed artifact

The full profile confirms 53 native registered non-stub bodies/422 (12.56%
equal-weight body count), 2,584,201 native entries/3,103,685 (83.26% fixture
frequency), 519,484 remaining Python entries and 41,584 entries moved. These are
not source-line, CPU-time or global test coverage. Guest entries are not exact
FFI counts.

Freeze-v1 binds 598 concrete sources/binaries/inputs, including final audit drivers.
An explicit allowlist excludes generated profile/text outputs; the exclusion
probe passes. Independent fidelity suites run in a bounded three-process pool,
all finished before guarded measurement stages. Every bound source/binary/private
input remains fixed, with completed/rejected historical receipts preserved.


## Corpus and lifecycle

Strict ALL75 and exact-source F40 pass, with all 75 records completed without
errors. Strict 10/20/30/60 prefixes are preserved. Independent attestation covers
75 family Rust machines and all 53 bodies. All four sealed lifecycle checks pass
(engine, interactive, goals, knockout), with 11 independently attested Rust machines.

## Same-campaign CPU measurements

Source: [all samples and ratios](performance-v1.json), with individual
`cpu-*-r*-v1.json` receipts. Each of three complete rounds starts after three
observations with 1-minute and 5-minute host load below 4. Four arms launch
together on distinct reported physical cores; assignments and launch order
rotate. Original dispatch guards remain. Every sample is retained, with no
selective arm replacement or timing campaign rerun.

CPU seconds:

| Round | Saved T20 | T21 | Plain CPython | PyPy |
| --- | ---: | ---: | ---: | ---: |
| 1 | 35.225888 | 34.500652 | 136.382265 | 51.265134 |
| 2 | 33.609398 | 32.970486 | 130.709078 | 48.013400 |
| 3 | 33.363619 | 32.761326 | 132.004513 | 47.721942 |

| Round | T21 / saved T20 | Saved T20 / PyPy | T21 / PyPy | CPython / T21 |
| --- | ---: | ---: | ---: | ---: |
| 1 | 0.979412 | 0.687131 | 0.672985 | 3.953034 |
| 2 | 0.980990 | 0.700000 | 0.686693 | 3.964427 |
| 3 | 0.981948 | 0.699125 | 0.686504 | 4.029279 |
| Median of per-round ratios | 0.980990 | 0.699125 | 0.686504 | 3.964427 |

T21 uses **1.90% less CPU than saved T20** at the paired median; all three
rounds improve (range 1.81%–2.06% less). This is a modest incremental gain,
below 5%; the owner-approved translation policy has no arbitrary magnitude floor.
In the same campaign saved T20 uses 30.09% less CPU than PyPy at the
median, and T21 uses **31.35% less**, with all three comparisons improving.
Paired plain-CPython/T21 CPU speed is 3.964×. Summaries are medians
of per-round ratios, not ratios of CPU medians or historical standalone PyPy gaps.

This is one reference fixture, not a general workload or application result. The
engine remains partly Python; this does not establish GIL release or thread
ownership. Engine A700/ref-121/owner milestone review and application API,
save/load, cancellation, target ABI/loading, packaging and playtest remain separate.

## Closed ledger and shutdown

Final validation verifies all **598** original source/binary/input bindings and
**214** evidence hashes. All 73 canonical producers and 12 timing children
have exited, with the controller gone: 85 recorded groups. No canonical stage
was rejected or needed a replacement, and no Rust semantic correction/rebuild,
assertion/corpus/guard reduction or overwritten receipt was needed. The earlier
instrumentation preflight rejection is retained explicitly above.

The baseline/input audit maps all 542 accepted T20 source/input bindings to
unchanged inputs or the saved pre-build snapshot, verifies its 202 evidence
hashes and older supplemental bindings, and checks historical T20/T19/T18/T17
profiles against inventory digests and accepted main. All three saved-baseline/
candidate drives reject/accept the new-two-body native-presence criterion
respectively, while outputs agree. The accepted comparator's identity is preserved.

[Final ledger](validation-final-v1.json), [baseline/input audit](baseline-input-audit-v1.json),
[post-exit audit](post-exit-audit-v1.json), [process closure](process-closure-v1.json).
Live exact-head/main CI, merge and stop state belong in checkpoint #1 and
[PR #51](https://github.com/diegoami/goal2rust/pull/51). The owner requested winding
down for the day after T21; no next task is started.
