# T20 chase-gate subtree

The complete default chase-gate tree is native: contests.chase_ball_gate
0791:5729 and geometry.in_own_goal_strip 0791:2EB8 / in_opposing_goal_strip
0791:2EF0. All five guest boundaries and source-inline direction/goal-strip
helpers remain explicit. The gate resumes with fresh Regs and reads live AX,
ignoring SENT; captured point/parent DI and refreshed parent pointers remain
separate. Both leaves preserve inline call/return words, queued writes, scratch
registers and flags. Nondefault variants remain Python. This is a partial port.

Same accepted oracle `2cbeb36fdd3feb369324aaa88e6e4d2aa3b3d99c` and private
T07 state-v2/tables. The actual accepted T19 baseline was saved before builds
under `.cache/T20-baseline`; its 56 files are bound by baseline-snapshot-v1.json.
Historical `.cache/T19-baseline` is T18 and is not the comparator. No original
bytes are committed.

## Combined-artifact fidelity

Fresh prior48 normal proofs pass 139,544 comparisons and all corresponding
controls/errors/branches/variants/closure checks, including T19's additional
640 scoped own-write comparisons and its 122 distinct selector requirement.
The new tree passes 8,288 full-state individual/integrated/ABI pairs, including
eight actual entry states per body, four observer modes and direct/entry-pause/
guest-pause-replay schedules. Positive source branches pass 640 pairs; variants
pass 80 comparisons. Scoped execution checks prove zero owned Python execution
inside 6,288 native lifetimes, with positive source/outside/variant witnesses.

The new error plan has 99 execution rows AND 99 distinct selector strings, all
independently reached, across 15,840 comparisons. Read/write ordinal selectors
exercise repeated observable events without counting duplicate PC labels as
distinct selectors. All 6,288 body controls, 4,192 output/flag controls and 800
comparisons across five individually reached return controls pass; unreached
return-control paths stay equal.

Four live matrices pass 1,280 comparisons each, retaining T17/T18/T19 and adding
live parent pointers, actual AX after captured SENT, cached AL and stack SS at
final local flush, captured leaf word/far pointer, live direction/flags, captured
point followed by a fresh pointer, and captured parent DI across far-pointer
reads. Every scenario has positive mutation and effect witnesses.

Public CPython and PyPy each pass 70 tests; Rust passes 11 tests; GC parity passes
20 cases; the supplemental legacy observer matrix passes 328 comparisons.
Reference/native ordered drives agree on 831 events, 553 stretches, full memory,
result, records and 158,092,780 ordered IO observations (114,492 listener enter/
leave pairs, 81,134 site enter/leave pairs and four writes), with digest
`096f56c262844705a0fcf7348fa4563c40e7d3ff4554b05c5224ffb0a7080ea9`.

## Translation progress

The full profile confirms 51 native registered non-stub bodies out of 422
(12.09% equal-weight routine count), 2,542,617 native guest entries out of
3,103,685 (81.92% on this fixture), and 561,068 remaining Python entries.
Exactly 33,809 entries move to native. These measures are neither source-line,
CPU-time nor global test coverage, and guest entries are not exact FFI counts.

## Artifact and campaign

Both interpreter installations and passing preflight finished before the accepted
artifact-archive-v1 snapshot. Freeze-v1 binds 542 source/binary/input files,
including prior proof metadata, profile inputs and final audit drivers. An explicit
source/input allowlist excludes generated reports; its exclusion probe passes.
Independent fidelity jobs use a three-process pool; every M2 writer exits before
the native ordered drive and guarded corpus/profile/timing stages. No bound source,
artifact, private input, assertion, corpus or guard changed during the campaign.
No completed historical receipt is overwritten.

Full corpus/lifecycle, timing, final audit and merge status belong in
[checkpoint #1](https://github.com/diegoami/goal2rust/issues/1). Performance needs
all three complete simultaneous rotated four-arm rounds before a conclusion.
