# T10 match-key-poll incremental port

## Outcome

One complete caller, menus.match_key_poll 0791:9372, now runs in Rust. Its six-slot
delay-table loop, all key/quick-mode branches and 15 literal guest-call sites retain
the accepted oracle's memory/register/flag/stack/observer behavior. Nondefault
variants stay Python. This ports the caller, not its transitive callee closure.
Accepted 2cbeb36f/state-v2/private T07 inputs are unchanged.

The reference drive uses 17 native bodies / 1,633,521 native guest entries and
1,470,164 Python entries out of 3,103,685 total. Exactly 76,928 Python entries moved
to Rust. This remains a partial port; counts do not measure whole-code completion.

## All measured outcomes

Three quiet simultaneous preserved-T09/candidate/plain CPython/PyPy rounds,
distinct physical cores with rotated assignments and launch order, original
guards. Every raw event/result/record/full-memory output agrees. No sample is
removed. Every round faster: True.

| Round | T09 CPU s | Candidate CPU s | CPython CPU s | PyPy CPU s | Candidate/T09 |
| --- | --- | --- | --- | --- | --- |
| 1 | 72.953917 | 66.999287 | 145.676135 | 54.672967 | 0.918378200 |
| 2 | 77.499185 | 75.600570 | 154.964614 | 57.960385 | 0.975501488 |
| 3 | 74.425872 | 69.259857 | 147.907297 | 57.950121 | 0.930588459 |

Median candidate/T09 ratio **0.930588459**, **6.94% less CPU**.
Median paired CPython speed **2.136x**; candidate/PyPy CPU **1.225x**.
Still slower than PyPy.
This is three rounds on one host/reference fixture. The earlier pilot ratio
0.94387837 is diagnostic evidence, not a substitute for these samples.
Owner-approved incremental acceptance has no arbitrary per-step 5% minimum;
all fidelity, full measurement reporting and exact-head CI requirements remain.

## Passing proof and closed bindings

- Public 32 each CPython/PyPy, Rust 11 and 20 lifetime cases pass.
- 54,568 normal full-state comparisons across 17 native bodies: 52,472 prior 16-body
  cases plus 2,096 new caller cases (eight actual RAM entry captures/500 authored
  cases/four tap-listener combinations). Every scoped body/return control caught.
- 1,066 caller error comparisons plus 328 existing speaker observer cases agree.
  All 15 return sites and 12 external boundaries covered; live-return AX, saved-BP,
  speed-loop, alias/wrap and copy-pointer reload mutations exercised.
- Exact ordered 831 events/result/records/full memory/553 stretches/full IO/site/
  listener digest agree, including 158,092,780 IO observations.
- Four positive-denial sealed lifecycle checks pass, 11 independently attested Rust
  machines; strict ALL75/75 and exact-source F40 40/40 identical, 75-machine backend
  attestation with all 17 native bodies.
- Authoritative **validation-v3.json** binds 165 recursive evidence files.
  post-exit-audit-v3.json rehashes baseline/candidate/private-input/harness/prefix/
  observer/current-proof/historical-failure source bindings. Actual-host
  process-closure-v1.json proves supervisor exit and 40 empty process groups:
  24 canonical, 12 timing, 2 pilot, 2 failed historical preflight groups.

## External scope and preserved failures

Ten callees are registered ports; 0791:1A04 and 16D6:0945 are unregistered external
guest targets in this pin. Test-only authored near/far ABI entries allow the
caller's continuations to be compared, not their implementations. Separate
public cases remove those doubles and preserve actual unknown-guest refusal.
Production never installs these doubles, implements new Match hooks or expands
the admitted input domain. Full drive/lifecycle/family use actual services/callees.

Initial borrow-check build failure and exact Rust source are retained. Preflight
v1 omitted the two unregistered boundaries: both backends refused equally and
ordinary equality assertions hid later branches. Explicit successful-positive
and 15-return/12-target coverage checks caught this. V2 all comparisons agreed,
but test-source edits after startup invalidated source_unchanged. That run is
rejected/preserved; exact prior bytes are reconstructed/SHA-verified. V3 runs
with source frozen, passes both controls and full bindings; runtime binaries
never changed for the harness corrections. Old failed jobs/receipts stay historical,
not accepted. This is why the final producer/validator revision is v3.

Source/adapter/extension baseline: .cache/T10-baseline/engine, metadata
baseline-snapshot-v1.json; candidate binaries: .cache/T10-artifacts,
artifact-archive-v1.json. No original game bytes/states/tables committed or
oracle semantic fix/model review launched. Existing #6/later A700/ref-121,
owner-run engine-milestone review and goal2 integration/save-load/cancellation/
playtest remain separate. Live exact-head CI/merge/stop state stays in PR #27/
checkpoint #1. No next task is part of this increment.
