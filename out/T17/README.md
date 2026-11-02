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
