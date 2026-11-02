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
