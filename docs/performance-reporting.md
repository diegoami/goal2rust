# Compare performance within a campaign

[owner-approved recalibration, after T16] Every new performance summary reports
the preserved baseline and candidate against PyPy from the same simultaneous
four-arm campaign. Historical standalone PyPy gaps are not a regression trend.

For each of three rounds, retain raw CPU seconds for saved hybrid, candidate,
plain CPython and PyPy, along with original guards, quiet-host observations,
rotated physical-core/launch assignment and artifact/source/input bindings.
Report these per-round ratios:

- Candidate / saved baseline: the incremental translation's measured CPU change.
- Saved baseline / PyPy and candidate / PyPy, side by side: the same-campaign gap.
- CPython / candidate: the paired CPU-speed ratio relative to plain CPython.

Summaries use the median of each set of per-round ratios, not a ratio of CPU
medians. Do not derive the incremental gain by dividing independently selected
median PyPy ratios. Keep every sample and regression, distinguish CPU from wall
time, and label a single pilot diagnostic. Profiling, entry counts and source-line
coverage do not establish an uninstrumented speed change or exact FFI counts.

## Example: accepted T16 campaign

Derived from unchanged `out/T16/performance-v1.json` and raw receipts; these
explanatory calculations do not rewrite those sealed artifacts.

| Round | Saved T15 / PyPy CPU | Candidate T16 / PyPy CPU | Candidate / T15 CPU |
| --- | --- | --- | --- |
| 1 | 1.144437 | 1.080196 | 0.943867 |
| 2 | 1.101435 | 1.072572 | 0.973795 |
| 3 | 1.125307 | 1.068666 | 0.949666 |
| Median of per-round ratios | 1.125307 | 1.072572 | 0.949666 |

In this campaign saved T15 used about 12.5% more CPU than PyPy, candidate T16
about 7.3% more, and T16 used 5.03% less CPU than T15. T15's earlier 4.1% PyPy
gap came from a different campaign and cannot establish a T16 regression.
Neither campaign proves a general PyPy win/loss across workloads.

Future receipts and summaries should expose both PyPy ratios explicitly. Existing
historical receipts remain immutable; explanatory reports can calculate missing
ratios from their raw same-round CPU values. No measurement is rerun just to
improve its headline. Fidelity and all predeclared task checks remain mandatory;
no new per-translation magnitude floor is introduced.

## T17 same-campaign result

Source: [all raw samples](../out/T17/performance-v1.json) and
[assessment](../out/T17/assessment.md). Every outcome is retained.

| Round | Saved T16 / PyPy | T17 / PyPy | T17 / saved T16 |
| --- | ---: | ---: | ---: |
| 1 | 1.095014 | 1.009414 | 0.921827 |
| 2 | 1.059106 | 0.974762 | 0.920363 |
| 3 | 1.045919 | 0.973971 | 0.931211 |
| Median of per-round ratios | 1.059106 | 0.974762 | 0.921827 |

T17 uses 7.82% less CPU than saved T16. Saved T16 uses 5.91% more CPU than PyPy
at the median in this campaign; T17 uses 2.52% less. Two PyPy comparisons improve
and one uses 0.94% more CPU. Treat this as near parity on the reference fixture;
a general advantage needs the later representative workload set. Historical
standalone PyPy ratios are not substituted for this campaign's saved baseline.

## T18 same-campaign result

Source: [complete replacement campaign](../out/T18/performance-v2.json) and
[assessment including rejected campaign samples](../out/T18/assessment.md).
The initial timing campaign is preserved after its third CPython arm hit the
unchanged dispatch guard. The replacement repeats all three four-arm rounds;
no missing-arm substitution or selective timing headline is used.

| Round | Saved T17 / PyPy | T18 / PyPy | T18 / saved T17 |
| --- | ---: | ---: | ---: |
| 1 | 0.997488 | 0.784482 | 0.786458 |
| 2 | 0.916148 | 0.748507 | 0.817016 |
| 3 | 0.963176 | 0.765050 | 0.794299 |
| Median of per-round ratios | 0.963176 | 0.765050 | 0.794299 |

T18 uses 20.57% less CPU than saved T17, with all three rounds improving.
Saved T17 uses 3.68% less CPU than PyPy at the median in this campaign; T18
uses 23.49% less, with all three PyPy comparisons improving. This is a
single-fixture result. Historical T17/PyPy ratios do not establish this change.

## T19 same-campaign result

Source: [all samples](../out/T19/performance-v1.json) and
[assessment](../out/T19/assessment.md). All three complete four-arm rounds are
retained with unchanged guards; no timing campaign or arm was replaced.

| Round | Saved T18 / PyPy | T19 / PyPy | T19 / saved T18 |
| --- | ---: | ---: | ---: |
| 1 | 0.804774 | 0.750188 | 0.932173 |
| 2 | 0.781398 | 0.739004 | 0.945746 |
| 3 | 0.779399 | 0.724698 | 0.929817 |
| Median of per-round ratios | 0.781398 | 0.739004 | 0.932173 |

T19 uses 6.78% less CPU than saved T18; all three rounds improve. In the
same campaign saved T18 uses 21.86% less CPU than PyPy at the median,
and T19 uses 26.10% less. This is one-fixture evidence; historical standalone
PyPy gaps are not substituted for the saved baseline.

## T20 same-campaign result

Source: [every raw sample](../out/T20/performance-v1.json) and
[assessment](../out/T20/assessment.md). All three complete four-arm rounds are
retained with unchanged guards; no campaign or timing arm was replaced.

| Round | Saved T19 / PyPy | T20 / PyPy | T20 / saved T19 |
| --- | ---: | ---: | ---: |
| 1 | 0.735671 | 0.699836 | 0.951290 |
| 2 | 0.760225 | 0.748328 | 0.984349 |
| 3 | 0.748274 | 0.717119 | 0.958364 |
| Median of per-round ratios | 0.748274 | 0.717119 | 0.958364 |

T20 uses 4.16% less CPU than saved T19, with all three rounds improving.
Same-campaign saved T19 uses 25.17% less CPU than PyPy at the median,
and T20 uses 28.29% less. This is one-fixture evidence and below a 5%
incremental reduction; the owner-approved translation policy has no such floor.
Historical standalone gaps are not substituted for the saved baseline.

## T21 same-campaign result

Source: [all raw samples](../out/T21/performance-v1.json) and
[assessment](../out/T21/assessment.md). All three complete four-arm rounds
retain unchanged guards and every outcome; no arm or campaign was replaced.

| Round | Saved T20 / PyPy | T21 / PyPy | T21 / saved T20 |
| --- | ---: | ---: | ---: |
| 1 | 0.687131 | 0.672985 | 0.979412 |
| 2 | 0.700000 | 0.686693 | 0.980990 |
| 3 | 0.699125 | 0.686504 | 0.981948 |
| Median of per-round ratios | 0.699125 | 0.686504 | 0.980990 |

T21 uses 1.90% less CPU than saved T20; all three rounds improve. Same-
campaign saved T20 uses 30.09% less CPU than PyPy at the median, and T21
uses 31.35% less. This modest incremental gain is below 5%, with no arbitrary
translation magnitude floor. Historical gaps do not establish this change; this
is one-fixture evidence.

## T22 same-campaign result

Sources:[all raw samples](../out/T22/performance-v1.json) and
[assessment](../out/T22/assessment.md). All three complete four-arm rounds and
the slower third candidate sample are retained.

| Round | Saved T21 / PyPy | T22 / PyPy | T22 / saved T21 |
| --- | ---: | ---: | ---: |
| 1 | 0.686521509 | 0.679584427 | 0.989895318 |
| 2 | 0.701939811 | 0.694601884 | 0.989546217 |
| 3 | 0.691682678 | 0.700229219 | 1.012356158 |
| Median of per-round ratios | 0.691682678 | 0.694601884 | 0.989895318 |

Paired median T22/T21 is1.01% less CPU; two rounds improve and round3
regresses1.24%. Repeatable improvement is not established. Same-campaign
T21 uses30.83% less CPU than PyPy and T22 uses
30.54% less, at their independent ratio medians.
The medians select different rounds; do not divide independent column medians.
Use every raw row and report the mixed outcome. The incremental translation's
predeclared criteria require fidelity and full measurement, without an arbitrary
5% floor. No regression or sample was discarded. One fixture only.

## T23 selected quiet repeat

Sources:[accepted v2 samples](../out/T23/performance-v2.json),
[rejected v1](../out/T23/rejected-performance-v1.json) and
[full assessment](../out/T23/assessment.md). The first entire campaign is retained
but rejected after late load contaminated its third CPython arm. All three rounds
were repeated on the unchanged artifact; every arm's load endpoints and sampled
load now pass the sealed quality checks.

| Round | Saved T22 / PyPy | T23 / PyPy | T23 / saved T22 |
| --- | ---: | ---: | ---: |
| 1 | 0.689977418 | 0.678088515 | 0.982769141 |
| 2 | 0.659502296 | 0.679384548 | 1.030147358 |
| 3 | 0.661588521 | 0.657466682 | 0.993769784 |
| Median of per-round ratios | 0.661588521 | 0.678088515 | 0.993769784 |

Selected paired median:0.62% less CPU than saved T22, with two faster
rounds and one3.01% slower. Repeatable improvement is not established.
Same-campaign T22 uses33.84% less CPU than
PyPy and T23 uses32.19% less at their
independent ratio medians. Each median may select a different row; do not divide
column medians or infer a trend from earlier campaigns' standalone PyPy gaps.
No sample was discarded or selectively replaced; full v1 and v2 raw seconds
are in the assessment. One fixture only; no arbitrary5% translation floor.

## T24 selected quiet campaign

Sources: [selected v2 samples](../out/T24/performance-v2.json),
[rejected complete v1](../out/T24/performance-v1.json) and
[full assessment with every raw CPU value](../out/T24/assessment.md). External
load contaminated original round one. Both entire three-round campaigns remain;
the replacement repeats all three rounds on unchanged artifacts and passes
quiet-start, every-arm endpoint and continuous-load checks.

| Round | Saved T23 / PyPy | T24 / PyPy | T24 / saved T23 | CPython / T24 |
| --- | ---: | ---: | ---: | ---: |
| 1 | 0.673806133 | 0.663699883 | 0.985001250 | 4.204833459 |
| 2 | 0.623213354 | 0.629437938 | 1.009987886 | 4.177058130 |
| 3 | 0.593283331 | 0.608433229 | 1.025535687 | 4.192077511 |
| Median of per-round ratios | 0.623213354 | 0.629437938 | 1.009987886 | 4.192077511 |

T24 uses **1.00% more CPU** than saved T23 at the paired median. Round one is
1.50% faster, rounds two and three are 1.00% and 2.55% slower: a mixed result
with a median regression. No repeatable gain is established or regression hidden.
Same-campaign saved T23 uses 37.68% less CPU than PyPy and T24 uses 37.06% less,
at independent ratio medians. Historical standalone gaps do not establish this
change. All raw samples, including rejected v1 and every slower round, remain.
The predeclared translation criteria impose fidelity and full measurement, with
no positive magnitude threshold or all-round speed-improvement gate. One fixture.

## T25 complete quiet campaign

Sources: [every raw sample](../out/T25/performance-v1.json) and
[assessment](../out/T25/assessment.md). All three simultaneous four-arm rounds
pass quiet-start, every-arm endpoint, continuous-load and independent idle-runner
checks. No campaign or sample was rejected or replaced.

| Round | Saved T24 / PyPy | T25 / PyPy | T25 / saved T24 | CPython / T25 |
| --- | ---: | ---: | ---: | ---: |
| 1 | 0.684159861 | 0.663918417 | 0.970414159 | 4.261476055 |
| 2 | 0.695586570 | 0.692126360 | 0.995025480 | 3.792420227 |
| 3 | 0.678679830 | 0.667383160 | 0.983354935 | 3.918157295 |
| Median of per-round ratios | 0.684159861 | 0.667383160 | 0.983354935 | 3.918157295 |

T25 uses1.66% less CPU than saved T24 at the paired median;all three rounds
improve(2.96%,0.50%,1.66%). Same-campaign saved T24 uses31.58% less CPU than
PyPy and T25 uses33.26% less,at independent ratio medians. Dividing independent
median PyPy columns does not measure the incremental change. All raw CPU seconds
remain in the assessment and receipts. This is one-fixture evidence;historical
standalone ratios do not establish a trend. No arbitrary5% translation floor.

## T26 complete quiet campaign

Sources:[every raw sample](../out/T26/performance-v1.json) and
[assessment](../out/T26/assessment.md). First complete simultaneous four-arm
campaign passes quiet starts,each endpoint,continuous load and independent
known-idle runners. No campaign or sample was rejected/replaced.

| Round | Saved T25 / PyPy | T26 / PyPy | T26 / saved T25 | CPython / T26 |
| --- | ---: | ---: | ---: | ---: |
| 1 | 0.677809344 | 0.667144082 | 0.984265101 | 4.323197245 |
| 2 | 0.655764641 | 0.679955027 | 1.036888822 | 4.033271266 |
| 3 | 0.697626772 | 0.668069969 | 0.957632356 | 4.256761994 |
| Median of per-round ratios | 0.677809344 | 0.668069969 | 0.984265101 | 4.256761994 |

T26 uses1.57% less CPU than saved T25 at the paired median. Rounds one/three
improve1.57%/4.24%;round two regresses3.69%. Mixed outcome,no repeatable gain
claim. Same-campaign saved T25 uses32.22% less CPU than PyPy and T26 uses33.19%
less,at independent ratio medians. Do not divide the median PyPy columns to
infer the paired change or compare historical standalone gaps as a trend.
Every raw CPU value and slower round is retained in the assessment. One fixture;
the task has no positive magnitude or all-round-improvement gate.
