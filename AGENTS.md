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

Measured common-bridge performance task T08 is specified in
[docs/tasks/T08.md](docs/tasks/T08.md), with preserved baseline, exact fallback/
callback contract and repeatability/resume rules in [out/T08/README.md](out/T08/README.md).
Read those and checkpoint #1 before any run/build. Preserve every round, rejected
prototype and old baseline; no merge from a microbenchmark or single pilot.

T02 is complete. Its evidence and historical cross-computer experiment commands are in
[out/T02/README.md](out/T02/README.md). Read that before restarting its experiments;
keep the task's Done-when intact and consult the latest GitHub checkpoint for status.

Keyboard-service chunk T24 is specified in [docs/tasks/T24.md](docs/tasks/T24.md),
with source/capture/artifact and post-writer rules in [out/T24/README.md](out/T24/README.md).
Read those and checkpoint #1 before resuming any producer. Preserve both full timing
campaigns, the final validation-v1 ledger and the separately sealed profile-reference
audit (one supplemental source/four input receipts). Its historical capture source map
and genuine entry shards must remain intact. Never overwrite completed receipts or
rebuild a bound artifact during measurement. Current completion and pause/resume
authority remain in the live checkpoint; choose any next scope from the full profile.

Text-cell chunk T25 is specified in [docs/tasks/T25.md](docs/tasks/T25.md).
Read [out/T25/README.md](out/T25/README.md), inventory-v2 and checkpoint #1 before
resuming. The original freeze and separately sealed continuation must both remain
intact; preserve both raw job journals and the rejected pre-proof wrapper attempt.
Use the README's updated final-v2 audit sequence and live controller identity.
If a shutdown checkpoint exists, verify its stopped controller and all completed
receipts before restarting the same artifact. Never rerun completed capture or
overwrite receipts; current completion/stop/resume authority remains in checkpoint #1.

Offside/commentary tree T26 is specified in [docs/tasks/T26.md](docs/tasks/T26.md).
Read [out/T26/README.md](out/T26/README.md), contract.md, inventory-v1.json and
checkpoint #1 before producers/builds. Preserve accepted T25's final-v2 and
separately sealed continuation, and actual T25 baseline in `.cache/T26-baseline`
before builds. Genuine capture binds 49 pure-oracle inputs; never edit its bound
sources while its producer lives or overwrite completed shards/receipts. Inventory
includes all 31 code objects, both local word helpers, SITES and loop returns.
Current run/stop/resume authority stays in checkpoint #1.

T26's canonical candidate is now frozen:1647 primary bindings/72 explicit
sources,both artifacts archived after98-test interpreter preflights. Read its
updated README before resuming producers;never rebuild/install or edit bound
sources. Preserve all genuine capture/development epochs and every completed
canonical receipt. Use final_capture_audit.py after writers exit;the initial
capture-input audit belongs to the pre-implementation epoch. Live PID/journal
and completion status stay in checkpoint #1.

Quick-result strength tree T27 is specified in [docs/tasks/T27.md](docs/tasks/T27.md).
Read [out/T27/README.md](out/T27/README.md),contract.md,inventory-v1.json and
checkpoint #1 before producers/builds. Preserve accepted T26's1647/283 final
ledger/history and actual comparator in `.cache/T27-baseline` before builds.
Capture binds50 pure-oracle inputs;all56 genuine shards/eight per body are
complete. Never overwrite completed receipts or recapture. All27 owned code
objects include three Rec methods;_call/gcall/helper return bindings stay explicit.
Current run/stop/resume authority remains the live checkpoint.

Before resuming T27,read `out/T27/shutdown-checkpoint-v1.json` and the README's
callback retry notes,then the latest live checkpoint. Preserve the completed
279-selector/70-outcome proof plan and BOTH rejected live/preparation epochs.
`live-return-diagnosis-v1.json` corrects the old shutdown interpretation:both
identically named PortMachine classes reject the unchangedSS fixture equally.
The fixed return-hook fixture passes all8 scenarios/1280 pairs in developmentv3.
Preparationv3 was SIGKILLed during PyPy preflight;preserve its rejection/source/
artifact/log epoch. The new controller usesv4 receipts/journal andv2 preflight
logs;never restart consumedv2/v3,
duplicate a live controller,overwrite a receipt or edit its bound sources.

T27's canonical campaign and final validation-v1 are now complete:2378 primary
bindings/79 explicit sources,102 canonical plus12 timing groups;all writers and
preparation controllers stopped. Read README and live checkpoint before any
further action;never restart completed producers or alter frozen sources.
Final merge/mainCI/merged binding audit status remains in checkpoint#1.

T28 pass-receiver destination closure is specified in docs/tasks/T28.md.
Read out/T28/README.md,contract.md,inventory-v1.json and live checkpoint before
producers/builds. Preserve accepted T27's2378/320 final ledger/merged audit and
actual82-file comparator in.cache/T28-baseline. Capture binds50 pure-oracle
inputs;eight genuine entry shards required. Do not edit bound capture sources
while producer lives or overwrite completed receipts. Scope includes all six
owned body/helpers and actual near return5367;045D is the native boundary.

T28 development and preseal plan are complete:2416 differential pairs,106 public
tests each,Rust11;livev3 hasfour scenarios/640 pairs aftertwo preserved fixture
failures. Proof-plan-v1 seals22 reached selectors/eight branch outcomes. Never
rerun capture/plan or overwrite completed receipts. Prepared final controller
usespreparation-v1/107canonical groups. Read README/latest live checkpoint for
PID/admission/completion status;keep its bound sources fixed while it lives.
