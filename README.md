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

The complete offside-line/display tree is native: [T22 results](out/T22/assessment.md).
The profile confirms 56 native bodies and 83.56% native guest entries on the reference
fixture. Timings are mixed: two rounds improve, one uses 1.24% more CPU; the median
uses 1.01% less than saved T21. A repeatable gain is not established. Same-campaign
T21/PyPy and T22/PyPy median CPU ratios are 0.691683 and 0.694602.
This is a partial engine port and one-fixture result. Routine counts and guest-entry
frequency are not overall port or test coverage. No next task is included.
