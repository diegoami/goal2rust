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
schedules. It passes 19,520 injected-error comparisons across 122 independently
reached selectors, 1,280 positive source-branch pairs and 112 variants. Scoped
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

The remaining full-corpus, lifecycle, timing, CI and merge status is recorded in
[checkpoint #1](https://github.com/diegoami/goal2rust/issues/1). No T19 performance
conclusion is accepted before the complete three-round four-arm campaign.
