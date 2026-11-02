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

Full corpus/lifecycle, timings, final audits and merge status belong in
[checkpoint #1](https://github.com/diegoami/goal2rust/issues/1). No performance
conclusion before all three complete simultaneous rotated four-arm rounds.
