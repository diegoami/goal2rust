# T11 ball draw-state incremental port

One complete caller, display.draw_ball_state 0791:8F10, and inline grid_cell now run
in Rust. Captured record pointers, live grid/coordinate/ZF/AX observations, signed-
byte coordinates with unsigned word MUL/highDX/unchanged flags, all previous/current
glyph/occupancy writes, stack and callback order and variant fallback match the
accepted 2cbeb36f/state-v2 oracle. Both registered callees and nested multiply remain
actual delegated source bodies; no transitive callee/hardware implementation claim.

The reference drive has 18 native bodies/1,712,715 native guest entries and 1,390,970
Python entries of 3,103,685 total. 79,194 entries moved from Python. This is a partial
port, not a whole-code completion percentage.

## Complete paired measurements

Three quiet simultaneous saved T10/candidate/plainCPython/PyPy rounds, distinct
physical cores, rotated assignments/launch order, original guards; every raw
output agrees, every sample retained. All rounds faster: True.

| Round | T10 CPU s | Candidate CPU s | CPython CPU s | PyPy CPU s | Candidate/T10 |
| --- | --- | --- | --- | --- | --- |
| 1 | 64.828324 | 62.093232 | 139.704149 | 52.559177 | 0.957810231 |
| 2 | 62.519736 | 59.608601 | 138.533304 | 50.890404 | 0.953436542 |
| 3 | 63.861963 | 61.325874 | 138.076040 | 49.511726 | 0.960287966 |

Median ratio **0.957810231: 4.22% less CPU** than saved T10.
Median paired CPython speed **2.252x**; candidate/PyPy CPU **1.181x**.
Still slower than PyPy.
No arbitrary per-increment 5% minimum. This is one host/reference fixture; the
0.96407507 pilot is diagnostic, not acceptance. No speculation about sample variation.

## Fidelity and closed evidence

- Public 35 each CPython/PyPy, Rust 11, 20 lifetime cases pass.
- 56,664 normal full-state comparisons across 18 bodies: 54,568 previous 17-body
  cases plus 2,096 new caller cases (eight actual RAM captures/500 authored cases/
  four tap-listener combinations). 352 new and 1,066 key-poll error cases plus 328
  speaker observer cases agree. Every scoped body/return control caught; no-call
  cases stay equal under return 13. Both returns/targets/nested multiply and all 4
  write sites/path outcomes covered with REAL delegated callees, positive success,
  captured-argument/savedBP/pointer/ZF/AX mutations, alias/wrap/sentinels, pauses,
  direct done/errors/variants. No test doubles or missing callee workarounds needed.
- Exact ordered 831 events/result/records/full memory/553 stretches and full IO/
  site/listener digest identical (158,092,780 IO observations).
- Four positive-denial sealed lifecycle checks pass with 11 attested Rust machines;
  strict ALL75/75 and exact-source F40 40/40 identical, 75-machine backend attestation
  and all 18 native bodies observed. No original guards raised or corpus reduced.
- Authoritative **validation-v1.json**, 145 recursive evidence files,
  with post-exit-audit-v1.json. Actual-host process-closure-v1.json proves supervisor
  exit and 41 empty experiment groups (27 canonical/12 timing/2 pilot). Full source/
  binary/private-input/baseline/archive/harness/prefix/proof/observer rehash passes.

Preserved source/adapter/extension baseline: .cache/T11-baseline/engine,
baseline-snapshot-v1.json; candidate binaries: .cache/T11-artifacts,
artifact-archive-v1.json. Baseline fails only the new native-coverage assertion;
all behavioral tests already pass. The implementation's first build and all
current proof bindings pass. No overwritten historical receipt, original game
bytes/state/tables in git, oracle semantic fix or automatic model review.
Existing #6/laterA700/ref-121/owner-run engine-milestone review and goal2 integration/
save-load/cancellation/playtest remain separate. Live CI/merge/stop state PR #29/
checkpoint #1. No next task included.
