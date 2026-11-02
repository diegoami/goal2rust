# T17 marking-target closure

Read docs/tasks/T17.md, contract.md, inventory-v1.json and live checkpoint #1
before implementation/builds/producers. Status belongs in GitHub issue #41.

Accepted pin 2cbeb36f / private T07 state-v2 and tables. The actual T16 baseline
was preserved before any T17 build in .cache/T17-baseline/engine, bindings and
PyPy extension; baseline-snapshot-v1.json binds every copied file. The old
.cache/T16-baseline is T15 and must never be used as T17's baseline.

M1 receipts are exclusive-create and immutable. inventory.py reproduces literal
registered inbound/outbound sites without executing the engine. contract.md
seals helper ownership, observer/ABI/error/control and case requirements.

Implement/prove all five bodies on one branch, pushing resumable milestones.
Development preflight runs are not final receipts. Freeze the combined artifact
before canonical proof/ALL75/F40/profile/timing producers; bind every source,
input and binary. Preserve completed outputs and rejected epochs. Never build
or edit bound sources/inputs during a measured run. Production changes after
freeze require a fresh epoch and all required proofs, not selectively rerun wins.
No original data in git. Exact-head CI and complete Done-when precede merge.

The concrete final proof selectors/counts/control IDs are sealed in
proof-plan-v1.json (supplements the M1 contract). captures-v1.json is earlier
input provenance, not a final-artifact fidelity receipt; the immutable private
capture bytes are rebound in every canonical producer's source/input ledger.
Development preflight logs are labelled preflight; they do not replace canonical
receipts. Both extensions are archived in .cache/T17-artifacts and bound in
artifact-archive-v1.json. No runtime semantic correction was made during preflight.

Canonical resume (only while every freeze binding still matches):
PYTHONHASHSEED=0 .venv/bin/python -u -B out/T17/supervise.py
The supervisor skips completed, source-verified receipts, appends jobs-v1.jsonl,
preserves strict ALL prefixes and waits for quiet before guarded family/check
and final three-round timings. An incomplete JSONL is handled only by the source
family.py documented append/resume behavior; do not overwrite completed lines.
After all producers exit, run process-closure.txt on the actual host, then
post-exit-audit.txt and validate.py with a new validation output. Run final
public CPython/PyPy/Rust/GC and observer-matrix-v2.txt on the frozen artifact;
completed receipts are never overwritten. Canonical original guards remain.
