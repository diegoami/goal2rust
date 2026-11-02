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
