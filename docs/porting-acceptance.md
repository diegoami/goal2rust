# Incremental port acceptance

[owner, 2026-11-01] The project replaces Python with Rust piece by piece while
preserving the accepted oracle's behavior. A correct incremental native subtree
need not improve whole-match CPU by 5% on its own. Continue to measure and report
performance against the preserved Rust baseline, CPython and PyPy, retain every
sample and regression, and require the fidelity/CI gates in its task contract.
An explicit optimization task can retain its own predeclared magnitude target;
T08's historical 5% optimization gate remains unchanged.

For T09 specifically, the owner authorized merging after its complete fidelity
proof and three faster rounds (median 4.28% less CPU). All existing fidelity,
original-guard, artifact/source/input binding and exact-head CI requirements
remain. Every candidate round must still improve; remove only the arbitrary
per-increment 5% minimum. Keep the historical failure and receipts, with separate
acceptance under the amended contract. This is an owner decision, not permission
for an implementer to silently relax future task requirements.

## Post-T16 batching and reporting

The owner requested recalibration around larger coherent chunks. Use complete
bounded native call trees with per-body and integrated proofs, then one full
campaign for the combined frozen artifact. See [chunk policy](porting-chunks.md).
This changes future task granularity, not any completed Done-when, preserved
receipt, oracle/private-data policy or fidelity/CI gate. Translation coverage
and [same-campaign performance](performance-reporting.md) are reported separately.
No new percentage speed floor is introduced; predeclared task criteria remain.
