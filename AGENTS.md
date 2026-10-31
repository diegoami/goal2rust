# goal2rust — agent entrypoint

Read [CLAUDE.md](CLAUDE.md). The oracle is a pinned clone of goal2-archaeology in the git-ignored
`.cache/goal2-archaeology` (see PROVENANCE.md for its commit), with its private reference image in
`.cache/goal2-archaeology/.cache/dl` (never committed). Resume from the latest checkpoint (issue
labelled `checkpoint` once the GitHub repository exists; until then `docs/checkpoints.md`), then
recheck live heads and checks.

The owner-approved next sequence is in [docs/roadmap.md](docs/roadmap.md): T03's
sealed-engine compatibility gates precede T04's first native call tree. Check
upstream dependencies and the latest checkpoint before starting either task.

T03's accepted-pin evidence, artifact bindings and experiment resume rules are
in [out/T03/README.md](out/T03/README.md). Read that before running its producers;
completed receipts must not be overwritten. T04's contract is in
[docs/tasks/T04.md](docs/tasks/T04.md), with artifact bindings and producer
rules in [out/T04/README.md](out/T04/README.md). Read those before running its
producers; preserve completed receipts. Live completion and stop/resume status
remain in the GitHub checkpoint.

The bounded tree T05 is specified in [docs/tasks/T05.md](docs/tasks/T05.md),
with full evidence, artifact bindings and producer rules in
[out/T05/README.md](out/T05/README.md). Read those and the live checkpoint before
resuming; never overwrite completed receipts or rebuild during a measured run.

Effective-skill tree T06 is specified in [docs/tasks/T06.md](docs/tasks/T06.md),
with proof/artifact/resume rules in [out/T06/README.md](out/T06/README.md).
Read those and the live checkpoint before its producers; preserve completed
receipts and keep bound sources/binaries fixed during measurements.

State-v2 compatibility refresh T07 is specified in [docs/tasks/T07.md](docs/tasks/T07.md),
with current pin, input/artifact and resume rules in [out/T07/README.md](out/T07/README.md).
Read those and checkpoint #1 before any producer/build. Preserve historical v1
receipts and use the documented final validation revision; never overwrite them.

T02 is complete. Its evidence and historical cross-computer experiment commands are in
[out/T02/README.md](out/T02/README.md). Read that before restarting its experiments;
keep the task's Done-when intact and consult the latest GitHub checkpoint for status.
