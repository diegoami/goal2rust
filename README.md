# goal2rust

A Rust translation of the match engine of *goal (version 2)* (1993), for speed, checked routine by
routine against [goal2-archaeology](https://github.com/diegoami/goal2-archaeology)'s accepted Python
port and, through it, the original. Rules: [CLAUDE.md](CLAUDE.md). No byte of the original game is here.

Build, state/tables API and backend-worker isolation: [engine/README.md](engine/README.md).
The translation sequence is in [docs/roadmap.md](docs/roadmap.md); current sealed-engine
state-v2 compatibility evidence is in [out/T07](out/T07/README.md), with the
historical baseline in [out/T03](out/T03/README.md). The first native
caller/callee tree is documented in [out/T04](out/T04/README.md). The native
nearest-to-ball tree is in [out/T05](out/T05/README.md), and effective skill
in [out/T06](out/T06/README.md). Common-bridge performance evidence and
baseline/confirmation rules are in [out/T08](out/T08/README.md). Read the latest
[checkpoint](https://github.com/diegoami/goal2rust/issues/1) before restarting work.

Accepted main includes the native keyboard-service chunk: [T24 results](out/T24/assessment.md).
Its profile confirms 63 native bodies and 86.62% native guest entries on the reference
fixture. Selected quiet timings are mixed: one round improves, two regress;
the median uses 1.00% more CPU than saved T23. No speed improvement is established.
Same-campaign T23/PyPy and T24/PyPy median CPU ratios are 0.623213 and 0.629438.
The first campaign was rejected for external load; every sample remains.
This is a partial engine port and one-fixture result. Routine counts and guest-entry
frequency are not overall port or test coverage. The connected six-routine
[T25 text-cell chunk](docs/tasks/T25.md) is in progress; its full-match and timing
gates remain required. Read the checkpoint for current shutdown/resume status.
