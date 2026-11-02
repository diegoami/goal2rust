# Port complete, bounded call trees

[owner-approved, after T16] Recalibrate the next work around connected native
subtrees. The default unit is a complete execution path with its remaining
Python callees, rather than one registered routine per full validation campaign.
The engine-first / whole-game-later objective and accepted oracle are unchanged.

## Current baseline

T16 is accepted on main `b3ad14188454ef200b7cfa06500227b0de0a5723`.
Figures below come from `out/T16/profile-after-v1.json` at accepted oracle
`2cbeb36fdd3feb369324aaa88e6e4d2aa3b3d99c`. The data and formulas are recorded in
[the planning snapshot](plans/post-T16-baseline.json).

| Measure | T16 value | Interpretation |
| --- | --- | --- |
| Native registered non-stub bodies | 23 / 422 (5.45%) | Equal-weight routine count, not source-line coverage |
| Native guest entries | 1,979,912 / 3,103,685 (63.79%) | Frequency on one fixture, not code or CPU coverage |
| Remaining Python guest entries | 1,123,773 | Fixture-specific starts, not exact bridge transitions |
| Ported source-line share | Not reported | Requires an explicit mapping/counting method |
| Global test line/branch coverage | Not reported | Targeted fidelity/branch proofs do not establish a global percentage |

The accepted proofs remain evidence of behavior for their bound artifacts. Do not
rename an entry-frequency percentage as code coverage or infer a completion date
from any of these counts. Keep global test coverage distinct from translation
coverage; no new coverage percentage is invented for this plan.

## Select and bound each chunk

1. Recheck checkpoint, live heads/checks and the full remaining-work profile.
2. Select a hot root; inventory its literal/dynamic guest targets and inline
   helpers. Follow remaining Python callees to a finite native closure. An
   existing native subtree can be a boundary; an unported default-path callee
   must be included or the candidate replaced with a smaller genuinely closed tree.
3. Bound by semantics and dependency shape, not a fixed number of bodies or a
   whole-module quota. A large module with unrelated services is not a closure.
   Seal exact ownership, variants, ABI and observable/error contracts before builds.
4. Implement and prove constituent bodies in resumable milestones on one branch.
   Preserve real guest boundaries and source-inline invocations, even when a
   native helper already exists at the same historical address.
5. Freeze the whole bundle and its baseline, sources, binaries and private inputs.
   Run all required per-body/integrated proofs and the full campaign once for the
   combined artifact. Production changes after freeze require a new bound epoch
   and fresh required receipts, preserving old ones. Local preflight cases during
   development do not replace final artifact-bound proofs.

This batches the expensive full campaign; it does not drop prior-body regression,
controls, errors, callbacks, lifecycle, ALL75/F40, profiling or paired timings.
The oracle is never changed to make a candidate pass.

## Immediate work: T17 marking-target closure

[T17](tasks/T17.md) ports five currently Python bodies together: marking-target
selection, its zone test, holder/half queries and the registered random draw.
All remaining registered guest callees of that root are then native under the
default variants. This is a larger unit than another isolated marking caller.

On the unchanged reference fixture, the five new bodies account for 149,652
entries. Expected after faithful replacement: 28 native bodies, 2,129,564 native
entries and 974,121 Python entries. These are coverage predictions, not speed
forecasts or acceptance substitutes; confirm them with the new full profile.

Prove both individual bodies and the integrated root using actual callees. In
instrumented proof runs, assert that no default-path Python routine or inline
helper owned by the selected subtree executes while that subtree is active.
Scope that assertion to its actual frame lifetime: shared helpers used elsewhere
and intentional nondefault Python variants remain valid. Guest entry counts alone
are insufficient to prove that a native wrapper does not delegate work to Python.

## Decide the following chunk from evidence

After T17, inspect the new profile and scoped execution/boundary observations.
The next likely region is destination/positioning: `update_marking_destination`,
`set_destination_from_post`, `position_group`, depth adjustment and their
remaining geometry/random dependencies. This is a candidate region, not a sealed
T18 scope or permission to port the entire module without an inventory.

If common dispatch/bridge work dominates instead, define a separate measured
optimization task with its own predeclared criteria. Native-to-native calls still
use common dispatch machinery today; batching routines in a PR does not itself
remove Python object construction, observers or every foreign-function boundary.
Measure actual paths rather than treating guest-entry counts as FFI counts. Do
not silently combine a broad dispatcher redesign with the T17 translation.

## Performance reporting and adoption

Use [same-campaign performance reporting](performance-reporting.md). Preserve the
previous accepted hybrid and compare saved baseline, candidate, plain CPython and
PyPy together on one quiet host, with rotated physical cores and every outcome
retained. Report baseline/PyPy and candidate/PyPy side by side. No new 5% floor is
introduced for translations; explicit optimization contracts keep their own gates.
A fidelity success is not a speed win when measurements regress.

The engine milestone still requires the explicit A700 corpus in addition to ALL75,
its known ref-121 noncompletion preserved, and the owner's review. Goal2 adoption
then requires worker/application parity, save/load, cancellation, lifecycle and
playtesting, with a predeclared representative performance set before claiming a
broader PyPy advantage. A single-fixture win is not general adoption evidence.

Goal2 at `1d274622c85054e595a8d0da11925d8780d4b148` now runs engine tests under
PyPy child processes ([PR #502](https://github.com/diegoami/goal2/pull/502)) and
retries transient half-time IPC read refusals ([PR #504](https://github.com/diegoami/goal2/pull/504)).
Later Rust integration must respect those process/IPC contracts and verify the
chosen backend independently; it does not replace their test routing prematurely.
A Rust adoption task must explicitly test its worker interpreter and native-extension
ABI on each target platform. A portable pure-Python worker smoke test does not
prove the Rust extension loads; original/Unicorn reference runs remain isolated
under their supported interpreter.

The upstream [T147 portable build](https://github.com/diegoami/goal2/blob/1d274622c85054e595a8d0da11925d8780d4b148/docs/tasks/T147.md)
plans to bundle CPython 3.13 for the UI and PyPy 3.11 for workers; [T153 first-run import](https://github.com/diegoami/goal2/blob/1d274622c85054e595a8d0da11925d8780d4b148/docs/tasks/T153.md)
serves the owner's playtest using the private data folder. Those are upstream
plans, not completed Rust milestones. Do not block goal2's playable build on this
port or bundle original data here. Independent public whole-game distribution
still needs the remaining original-game dependencies removed.
