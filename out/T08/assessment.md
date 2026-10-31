# T08: repeatable common-bridge performance gain

All fidelity and repeatability gates pass. PR #23 / checkpoint #1 hold live
merge and stop/resume status. The accepted source remains archaeology
2cbeb36fdd3feb369324aaa88e6e4d2aa3b3d99c, state/2. No guest routine or input
format was added; the twelve native bodies are unchanged. T07 historical
receipts, source and measured binaries remain intact.

## Measured result

The candidate used less CPU than the exact preserved old Rust implementation
in every quiet simultaneous round. Median paired candidate/baseline ratio is
**0.732669**, or **26.73% less CPU**, passing the
predeclared <=0.95 threshold. All raw event/result/record/full-memory outputs and
553-stretch counts agree across all four arms in every round. No sample is omitted.

| Round | Old Rust baseline CPU s | Candidate CPU s | Plain CPython CPU s | Plain PyPy CPU s | Candidate reduction |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 94.202 | 69.019 | 140.652 | 47.150 | 26.73% |
| 2 | 94.596 | 68.661 | 140.988 | 46.943 | 27.42% |
| 3 | 94.483 | 69.503 | 140.098 | 48.871 | 26.44% |

Median paired candidate speed against CPython is **2.038x**.
Median candidate/PyPy CPU ratio is **1.463x**. The candidate remains
slower than PyPy; this is a demonstrated improvement over the old hybrid, not a
PyPy win or proof about a fully native engine. Earlier different-time one-pair
ratios do not replace the simultaneous preserved-source comparison.

All correctness jobs ended before timing. Each round starts after three
observations with both 1m/5m load below 4; each arm is pinned to a separate physical
core, with old/candidate core assignments and launch order exchanged in round 2.
Topology, enforced taskset commands, start times and all 12 child exits are in
performance-v1.json. Default 60-second stretch guards stay unchanged. Three
samples provide a repeatability check, not a general hardware timing distribution.

## Selection and mechanism

T07 cProfile identifies common bridge work across remaining Python bodies:
20.3m bounds checks, 11.8m word reads,9.6m register writes and 5.8m write_as calls.
An authored-memory primitive benchmark selected narrower read/write paths. The
first whole-drive pilot also matched outputs at 84.571 old / 63.338 candidate CPU
seconds. Both were diagnostics; full fidelity and the independent three-round
gate determine acceptance. contract.md records the exact operation boundaries.

Immutable Python attribute names are interned and common register/bank names
use static matching. Mutable tap/handler/span/error VALUES are always fetched
again. Exact builtin-int fixed-image own-memory reads use bound Rust methods;
generic/invalid/non-exact/resized cases use original helpers. Small exact-int
writes mask their width and use the existing listener-before-write path, keeping
owned bytes across callbacks. Huge/custom/wide inputs retain the original path.
No callback, site or observable guest entry is removed. GOAL2RUST_FAST=0 is an
ablation flag for the new read/write paths; baseline comparisons use the actual
old source/adapter/extension, not that flag. Fast counters prove paths executed.

The new profile preserves 3,103,685 guest entries: 1,350,794 native across 12 bodies
and 1,752,891 Python entries. Python memory-view u16/u8 method calls drop from
11,838,009/8,161,101 to zero. This mechanism evidence establishes neither a
whole-port completion percentage nor speed by itself; uninstrumented paired
receipts establish the measured gain above.

## Exact fidelity and closed evidence

| Gate | Result |
| --- | --- |
| Public/callback/error/numeric parity | All 24 tests pass on CPython and PyPy; covers dynamic taps/listeners, reentrant registration, exceptions before commit, aliases/high halves, widths 0..16, negative/huge values and fallback/resized reads. |
| Rust/lifetime | Rust 11 tests pass; 20 registered-port/callable cycles collected. |
| Full body/frame/boundary differential | 40,024/40,024 equal across all 12 bodies/continuations, 500 random/eight real captures per legacy body and all three tree suites; all known body/return controls caught. Retained-input/AX-after-capture mutations preserved. |
| Ordered sealed drive | All 831 events, result, returned state, full memory, 553 stretches and complete IO/site/listener stream equal. Fast usage: 11,838,009 word reads, 8,161,101 byte reads, 5,501,462 writes. |
| Sealed lifecycle | All four checks pass under positive original-file/Unicorn denial, with 11 independently attested Rust machines and fast-path execution. |
| ALL/F40 | Unchanged strict comparators: ALL 75/75 and exact-source F40 40/40 identical, zero failures/raised limits. Independent attestation covers 75 Rust machines and fast-path execution. |
| Final ledger | validation-v1.json binds raw source/binary/input/output hashes after all 17 canonical producers, 12 performance children and supervisor exited. Every process group empty. Supplemental audit verifies old baseline/archive bytes, oracle/harness, prefixes, public/GC/proof counts and all rounds. |

The pre-change snapshot .cache/T08-baseline/engine contains the exact T07
source/adapter/extension; baseline-snapshot-v1.json records its hashes. Baseline
receipt extension paths are independently checked. Candidate artifacts remain
in .cache/T08-artifacts, metadata artifact-archive-v1.json. Final index hashes
118 recursive evidence files. No original bytes/state/tables/checkpoints are tracked.

## Preserved attempts and limits

The failing-before optimized-path API test and first compile's receiver typo
are retained; the typo was corrected before tests/pilot/full proofs. No equality
assertion, guard, performance threshold or round was weakened/discarded. The pilot
and primitive timings remain separate from confirmation results.

Non-reference numeric extension objects retain existing Rust fallback behavior;
this does not claim new oracle support or resolve #6. Existing factory-isolation
and allocator/coverage limits remain. A700 and owner-run engine-milestone review
remain later gates, known ref-121 noncompletion preserved. Most match logic and
the surrounding game remain unported. No later task or automatic model review
started. Read README.md/checkpoint before new runs; never restart completed
producers or silently reuse these receipts after a source/binary/input change.
