# T25 text-cell rendering chunk

Status: the 87 per-body stages, fresh ordered drive, lifecycle, full profile,
ALL75/exact-source F40 and strict10/20/30/60 prefixes pass. The complete first
timing campaign passes all quality gates: paired median1.66% less CPU than
saved T24, with all three rounds improving. Final ledger/CI/merge status lives
in checkpoint #1.
PR #59 stays draft and unmerged; checkpoint #1 owns live status.

## Translation and source contract

At accepted oracle `2cbeb36fdd3feb369324aaa88e6e4d2aa3b3d99c`, T25 translates
six connected display exports: text_cells_forward (214B:00FF),
text_cells_backward (214B:0123), string_at_attr (214B:01A3),
string_at_set_attr (214B:0205), string_forward_attr (214B:026D) and
string_forward_set_attr (214B:02C8). Four callers retain the already native
bounded-string-copy guest23E4:0644. All14 owned body/helper function code
objects and eight actual near/far guest returns are inventoried.

The implementation preserves live byte reads, overlap propagation, offset
wraps, contiguous word writes across offsetFFFF, captured source segment,
cached AX high byte, pending DS push and late DF storage. Callers retain their
original temporary across the copy guest and resume with fresh registers.
Attribute writes precede position reads; live SS, far-pointer word ordering,
captured destination/source SS and actual near/far calls follow the source.
No invented DS pop or use of sent guest values is introduced. Nondefault
variants stay Python. See contract.md for the exact source order.

## Preserved inputs, artifact and attempts

Actual accepted T24 source/tests/adapter/both interpreter artifacts are saved
in `.cache/T25-baseline` (75 files); `.cache/T24-baseline` is the older T23
comparator. Before builds, T24's852 primary/281 evidence bindings and its
one-source/four-input supplemental audit were checked. Both final interpreter
builds/installs and94-test public preflights preceded archive/freeze.

The primary freeze binds1083 concrete files, including65 explicit producer/
audit sources. Genuine source capture completed with49 pure-oracle inputs,
48 exclusive private shards and two actual drive prefixes. The rejected
inventory and development branch-label/provenance epochs remain preserved;
neither is substituted for canonical proof. Private memory stays ignored.

The first controller retained a copied scoped-write wrapper whose OUT still
named T24. Its startup freeze assertion failed before exercising a routine.
The original58-attempt journal,57 successes and failed log remain immutable.
A separately sealed continuation binds six additive sources/121 inputs;
the corrected wrapper changes ONLY OUT to T25, retaining all four selectors,
640 comparisons and assertions. Completed proofs were verified and reused.
No production/binary change, rebuild or capture rerun followed the freeze.

For the owner's shutdown, the second controller stopped at an empty boundary
after all87 M2 stages passed. The winddown receipt records every then-started
group stopped and preserves the journal prefix hash. The owner resumed on
2026-11-04 using the same sealed controller, a new protected log and the same
append-only resumed journal. Final accounting must include all three controller
epochs and retain the original pre-proof failure separately from successes.

## Completed proof results

| Proof | Result |
| --- | ---: |
| Fresh prior63 / new6 normal comparisons | 180,984 / 20,576 |
| Combined normal comparisons | 201,560 |
| Real-state schedules:6 ×8 ×4 ×3 | 576 |
| New body controls198–203 | 12,576 |
| AX/CX/DX/SI/DI/ES/EFLAGS controls204–245 | 88,032;2,096 each |
| Eight real return controls246–253 | 1,280;160 each |
| Positive source branch pairs / distinct condition outcomes | 1,600 /10 |
| New errors / distinct reached selectors | 27,360 /171 |
| Nondefault variants | 192 |
| All-inventory scoped closure | 12,576;all14 code objects witnessed |
| Live callback matrices | Nine;1,280 each |
| Public CPython / PyPy | 94 /94 tests |
| Rust / GC / supplemental observer | 11 /20 /328 |

Error selection explicitly samples early/middle/last write ordinals. This
bounded selector coverage is not an exhaustive fault-coverage percentage.
Owned default Python code has zero observed execution inside native lifetimes;
positive source/outside/nondefault witnesses establish the scope controls.
Every prior proof, control, error, branch, variant and closure gate is retained.

The fresh Rust drive matches Python's831 events, result, records, full memory
and complete ordered IO/listener/site/write trace. Original-file and Unicorn
denial remain active. Instrumented runtime is diagnostic, not a speed result.

## Fresh remaining-work profile

The complete profile matches the fresh state-v2 drive outcome. It observes
69 native bodies out of422 registered match-engine bodies (16.35% by count),
2,699,104 native and404,581 Python entries out of3,103,685 total:86.96% native
fixture entry frequency. T25 moves10,810 entries from Python on this fixture.
These are neither source-line/test coverage nor whole-game progress measures.

The largest remaining Python entry counts are handle_player_at_ball(57,791),
energy_chance_branch/offside_call(36,198 each), pass_receiver_destination
(35,723), challenge_duel(35,193) and near_player_zone(16,064). The complete
profile also retains lower-frequency routines with material self time, such as
quick listing1771:0BC4(162 entries). Entry counts and cProfile self times do not
establish exact crossing costs or uninstrumented gains. Select a following
bounded closure separately after T25's acceptance gates complete.

## Integrated fidelity

Independent native attestation verifies11 lifecycle and75 family machines,
each campaign collectively reaching all69 native bodies. All75 records
completed under unchanged guards, with no errors. F40 is selected byte for
byte from the complete ALL output; all immutable prefixes and both full
comparisons pass. The original1083 bindings and additive6/121 remain unchanged.

## Complete timing campaign

All three simultaneous four-arm rounds completed on the same archived
artifacts. The first whole campaign passed the three quiet-start observations,
every arm's start/end load, continuous five-second load samples and independent
known-idle runner observations. No campaign or sample was rejected or replaced.
Original guards remain unchanged, and all four arms match events, result,
records and full memory. CPU seconds below are uninstrumented match-drive CPU,
not wall time or a multi-fixture result.

| Round | Saved T24 CPU s | T25 CPU s | CPython CPU s | PyPy CPU s |
| --- | ---: | ---: | ---: | ---: |
| 1 | 36.705729543 | 35.619759681 | 151.792752982 | 53.650808263 |
| 2 | 36.126758854 | 35.947045565 | 136.326302704 | 51.937113824 |
| 3 | 33.293700908 | 32.739525082 | 128.278609037 | 49.056564564 |

| Round | T25 / saved T24 | Saved T24 / PyPy | T25 / PyPy | CPython / T25 |
| --- | ---: | ---: | ---: | ---: |
| 1 | 0.970414159 | 0.684159861 | 0.663918417 | 4.261476055 |
| 2 | 0.995025480 | 0.695586570 | 0.692126360 | 3.792420227 |
| 3 | 0.983354935 | 0.678679830 | 0.667383160 | 3.918157295 |
| Median of per-round ratios | 0.983354935 | 0.684159861 | 0.667383160 | 3.918157295 |

T25 uses1.66% less CPU than saved T24 at the paired median. Every round
improves, by2.96%,0.50% and1.66%, respectively. In the same campaign, saved
T24 uses31.58% less CPU than PyPy and T25 uses33.26% less, at independent
ratio medians. The CPython/T25 CPU-speed ratio is3.92 at its per-round median.
Each median is selected independently; dividing the median PyPy columns does
not measure the incremental change. Historical standalone PyPy ratios are
not substituted for this campaign's saved baseline. Every raw sample remains
in performance-v1.json and its12 individual receipts.

This is a modest improvement on one fixed fixture, not a general performance
claim. No positive magnitude threshold applies to this translation task.
Final post-writer accounting must retain92 successful logical stages,93
physical canonical attempts(including the original pre-proof failure),12 timing
groups and all three controller epochs. The six README audits/final-v2 ledger,
exact-head CI/squash/mainCI and merged binding audit remain mandatory.
