# Owner-run T02 milestone review prompt

Review goal2rust PR #5, "T02: run the match dispatcher, frames and guest calls in
Rust". Resolve `gh pr view 5 --json headRefOid` once at the start, record that
exact SHA, and review its diff against `main`. If the PR head changes, identify
the review as stale. Read `AGENTS.md`, `CLAUDE.md`, `docs/tasks/T02.md`,
`PROVENANCE.md`, `out/T02/assessment.md` and the latest checkpoint issue #1 first.

The oracle is pristine at `d3cf46a3e87f0ba04916867b5b231c4646a0c2bd`; its Python
port is semantic authority. Check Rust against that source, not an assumption
about what the original ought to do. Private images stay in the ignored cache;
do not put original bytes or live memory into a report or git.

Review the full machine, bridge and bindings, including ownership of memory and
registers, near/far calls, argument cleanup, return bytes, suspended/recursive
frames, replay, callback ordering/reentrancy/errors, stop semantics and save/load.
Only T01's seven bodies may be native. Examine the actual tests and proof
producers; passing hashes alone are not a substitute for understanding the
observable boundary. Consider dead stack bytes and >64-bit listener values.

Audit the unchanged Done-when against the evidence:

- Fresh ordered drive: `taps-rust-host2-v1.json` and its comparison log, including
  events, result, full memory, stretches and complete ordered tap hash; exactly
  880,504 native calls across exactly seven addresses.
- Differential: `differential-host2-v1.json`, 28,224/28,224 body/frame cases.
  Retain and explain the earlier failing wide-listener receipt.
- F40: final host2-v4 candidate, compare log/status, `assembly-host2-v4.json`
  and `validation-host2-v4.json`. Verify the 27+13 raw-line selection, preserved
  failures, no replacement of a completed match, full 40 IDs and exact current
  source/extension hashes. Audit `recover_host2_v1.py` and the ledger change too.
- Kit lifecycle: all four fresh checks, including suspended save/load, extra
  time and shootout replay. Public Rust/interpreter/wheel checks and final CI.
- Mutant: `mutant-host2-v1.json`; the synthetic full-frame machine differential
  catches the corrupted guest-return IP as `0791:0111`.
- Paired timing: all three `cpu-*-v1.json`, source/extension hashes, before/after
  load and the recovery supervisor log. CPython 146.111, PyPy 48.634, Rust 107.394
  CPU seconds; equality against both baselines. No claim that Rust beats PyPy.
- Next-subtree proposal: measured profile evidence and its stated limits; no
  additional subtree or unrequested semantics change belongs in T02.

Run appropriate public checks if useful. Any expensive private-image rerun must
respect shared host load and use fresh output names; preserve failed receipts.
Do not weaken a Done-when, patch the oracle, edit this implementation, merge the
PR, publish a review, or begin T03 as part of this review.

Return every finding with severity, concrete file/line evidence, reproduction
or failing case, and impact. Separate demonstrated defects from questions or
coverage limits. Report the reviewed SHA and checks actually run. If there are
no findings, say so and state the meaningful remaining coverage limits.
