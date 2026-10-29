# T02: machine validation and measurement

All three unchanged Done-when lines in `docs/tasks/T02.md` are met. The Rust
machine runs the kit's event/answer/save/load interface, with T01's seven bodies
native and all other bodies bridged to the pinned, unmodified Python oracle
`d3cf46a3e87f0ba04916867b5b231c4646a0c2bd`. No further subtree was translated.
The final PR head's CI and owner-run milestone review are tracked in PR #5 and
checkpoint issue #1. No experiment process remains active.

## Equality and positive control

| Required gate | Result and evidence |
| --- | --- |
| Straight drive, including ordered taps | `taps-rust-host2-v1.json`, `compare-rust-host2-v1.log`: 831 events, result, full memory, 553 stretches and the complete ordered tap hash equal the oracle. Exactly 880,504 native calls across exactly seven addresses; all other bodies bridged. |
| Bridge-only milestone | `taps-bridge-v1.json`, `compare-bridge-v1.log`: all bodies bridged, same ordered drive equal on the previous artifact. Production sources stayed unchanged during the IT13 rebuild/proofs. |
| Seven-routine per-call/body/full-frame differential | `differential-host2-v1.json`: 28,224/28,224 equal, 500 random and four captured inputs per routine, four tap/listener modes, body and frame execution. |
| F40 | `family-F40-rust-host2-v4.jsonl`, `compare-F40-rust-host2-v4.log` and its status receipt: unchanged `compare.py --family F40 --no-screen`, **40 expected identical, 40 pass, 0 fail**, exit 0. |
| Kit engine and lifecycle | `check-rust-host2-v1.json`: engine, interactive save/load, goals and knockout replay all pass, including extra time and shootout-order replay. |
| Machine mutant | `mutant-host2-v1.json`: incrementing a pushed guest-call return IP is caught by the synthetic full-frame machine differential, with `PortError: no registered port/return at 0791:0111`. |
| Public checks and packaging | 11 Rust tests; six synthetic tests on CPython and PyPy; installed-wheel checks. See `cargo-tests-host2-v1.log`, `tests-host2-v1.log`, `tests-pypy-host2-v1.log`, `wheel-tests-cpython312-host2-v1.log`. |
| Artifact binding | `validation-host2-v4.json` binds the family, proof, lifecycle, differential, mutant, tests and recovery evidence to the exact current source and CPython extension hashes of the fresh native tap proof. |

The failed stronger listener differential (`differential-v1.json`) remains as
evidence of the earlier >64-bit stack-write truncation. Full memory alone did
not expose that observable error. The corrected host retains arbitrary-width
listener values and the stronger full-stack differential.

## Paired CPU receipts

`paired_v1.sh` launched all three runs together on IT13 after validation ended
and three observations had both one-minute and five-minute load below 4.
One-minute load was 0.48 before and 1.55 after; the three workers were the timing
workload. Every receipt contains source and installed-extension hashes, and
both oracle and Rust-source hashes remained unchanged. The CPython extension
also matches the fresh ordered-tap proof. Toolchain/build identity is in
`host2-environment-v1.json`.

| Backend | Drive CPU seconds | Drive wall seconds |
| --- | ---: | ---: |
| Plain CPython 3.12 port | 146.111 | 146.128 |
| Plain PyPy 3.11 port | 48.634 | 48.637 |
| Rust machine, seven native bodies | 107.394 | 107.403 |

Receipts: `cpu-python-v1.json`, `cpu-pypy-python-v1.json`, `cpu-rust-v1.json`.
Both comparisons pass for events, result, full memory and 553 stretches. Rust
records the same seven native call counts as the ordered proof; neither Python
baseline installs Rust. The longest Rust stretch is 21.709 CPU seconds, inside
the producer's unchanged 60-second guard.

This Rust machine is **1.361 times faster than plain CPython**, and uses
**2.208 times the CPU of plain PyPy** (0.453 times PyPy's speed). It has not beaten
the fastest Python baseline. These are one paired drive on one machine, with
the unported Python bridge still present. They do not establish a distribution
or an incremental speed-up over T01's hook on another host.

## Preserved interruptions and F40 assembly

Shared load repeatedly returned after brief quiet windows. IT13's first attempt
retains its two timeouts in `family-F40-rust-host2-v1.jsonl`. The full v2 attempt
retains 27 successes and `edit-8e05`'s unchanged-limit timeout. Its first recovery
retains two further timeouts in `family-F40-rust-host2-v2-rerun-v1.jsonl`.
`host2-interruptions-v1.jsonl` records the verified process groups and stops.

The owner chose waiting on IT13. The quiet gate was strengthened to include the
five-minute load average; no match limit, comparison field, ID or native-artifact
assertion changed. The successful rerun contains exactly the 13 failed/missing
IDs under the original limits. The final candidate selects the 27 original
successful lines and 13 successful rerun lines byte-for-byte. No completed match
was replaced after examining its comparison result.

`assembly-host2-v4.json` records each selected source file, line number and
SHA-256, input-file hashes and the candidate hash. `recover_host2_v1.py` rejects
duplicate completions, partial lines, failed reruns and changed native artifacts.
The final full-family comparison is the acceptance gate; no partial run is
reported as 40/40. All old host evidence is retained. Original game bytes remain
only in the ignored private cache.

## Next step

The profile-based order in `next-subtrees.md` and `profile-subtrees-v2.json`
remains the proposal: close geometry/availability (`0791:2956` to `1771:3216`),
then effective skill/attributes, ball selection/possession, contests/duels, and
positioning/movement with their display dependencies. Closing native caller and
callee trees should reduce Python bridge crossings; the amount is a hypothesis
to measure, not a promised speed-up. Keep per-call full-frame/listener equality,
ordered drive, F40, lifecycle checks and the PyPy timing baseline as gates.

No T03 work has begun. The main session supplies `review-prompt.md`; the owner
runs the milestone review on their chosen model under `CLAUDE.md` rule 4. Merge
must wait for that review and successful CI pinned to the final head.
