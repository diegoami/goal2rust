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

The native text-cell chunk passes fidelity and timing gates: [T25 results](out/T25/assessment.md).
Its profile confirms 69 native bodies and 86.96% native guest entries on the reference
fixture. All three quiet timing rounds improve over saved T24; the paired median
uses 1.66% less CPU. Same-campaign T24/PyPy and T25/PyPy median CPU ratios are
0.684160 and 0.667383; T25 uses 33.26% less CPU than PyPy on this fixture.
Every raw sample remains. This is a partial engine port and one-fixture result.
Routine counts and guest-entry frequency are not overall port or test coverage.
Read the checkpoint for exact-head CI, merge and current continuation status.

T25 is merged;[T26](docs/tasks/T26.md) continues with the ten-body offside/
commentary closure. Its baseline,source inventory and80 genuine entry captures
are preserved. The native candidate passes development/98-test interpreter
checks and is frozen for canonical validation. No T26 speed result yet.
