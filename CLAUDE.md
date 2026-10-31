# goal2rust

[designed: owner, 2026-10-29] A Rust translation of the match engine of *goal (version 2)* (New
Era Software, 1993), for speed: goal2-archaeology's plain Python port runs a match about 14 times
slower than the original under Unicorn (T78d, `experiments/E036-match-port/out/T78/play-speed-v1.json`).
This repository translates; it decides nothing about what the original does.

[designed: owner, 2026-10-29] Scope: the engine first, then the game, into Rust, in parallel with
goal2 (which keeps its Python engine and its milestones meanwhile). The T01 spike's first finding
shapes the order: leaf routines under the Python dispatcher gain only about 1.1 to 1.2 times on a
match, because the port's per-call Python machinery dominates, so the dispatcher, the frames and
the guest calls move to Rust early (T01's go/no-go, `docs/go-no-go.md` on its branch).

[owner, 2026-11-01] Incremental Python-to-Rust translations do not each need a
5% whole-match CPU gain. Preserve fidelity and report complete measured outcomes;
use the task's explicit performance criteria. T09 is owner-approved with all
three rounds faster and a 4.28% median CPU gain. T08's historical optimization
gate is unchanged. See [incremental acceptance](docs/porting-acceptance.md).

## Sources and the oracle

[designed: owner, 2026-10-30] Follow `docs/roadmap.md`: adopt archaeology's
accepted state-and-tables boundary before the next native subtree, retain PyPy
as the performance baseline, and add the larger explicit fidelity corpus at the
engine milestone. Refresh proof receipts when changing the oracle or artifact;
T01/T02's historical evidence stays bound to its original source.

- **Semantics**: [goal2-archaeology](https://github.com/diegoami/goal2-archaeology)'s accepted Python
  port (`runtime/original_match/port/`, accepted for the 75-match admitted family by T78d) and the
  findings it cites. Where a decompiled routine and the port disagree, the port (proved against the
  original) is right until shown otherwise there.
- **Structure**: its decompiled code (`named/seg_*.c`, the listings), for control flow, 16-bit
  fields and layouts. It is evidence to check, not truth.
- **Oracle**: every translated routine is run against the Python port on the same inputs, and the
  port against the original, with goal2-archaeology's own harness: E034-03's drive receipts (events,
  result, full memory, the ordered tap sequence with `PYTHONHASHSEED=0`), `family.py` and
  `compare.py`, `original_match.check`.
- Every translated routine is pinned in `PROVENANCE.md` to the goal2-archaeology commit and the
  Python routine (module and address) it reproduces. A defect found in the port goes back to
  goal2-archaeology as an issue; it is never fixed only here.

## Architecture

- A Rust crate (`engine/`) with PyO3 bindings built by maturin. The guest state stays the port's:
  one memory image (a zero-copy buffer over the port's `bytearray`) and the port's registers, with
  typed accessors (`u16`/`i16`, explicit wrapping). Faithful first; refactor only behind passing tests.
- A translated routine replaces its Python port at the same address, as one more port module the
  Python dispatcher can load, so the rest of the match keeps running in Python and every check
  above applies unchanged. Whole subsystems move once their routines are equal.
- Speed is measured with the same paired receipts as T117: before and after on one machine, at once.

## Working rules

1. No model is fixed; the main session implements itself or spawns helpers on its own judgment.
2. Work on a branch in the checkout at hand, one task at a time per checkout. Never `git stash`,
   never force-push, never rewrite `main`.
3. One task, one PR, squash-merged once its Done-when lines and CI pass, pinned to the checked head.
4. Only milestones mandate a review. No session starts a review: the main session writes the prompt
   and the owner runs it on a model of their choice. Relay findings in full.
   Review prompts must name the PR and explicitly instruct the owner-invoked reviewer to post the
   complete report as a PR comment: reviewed SHA, every finding and severity, checks run/skipped,
   and coverage limits. Return the comment URL. If posting fails or is unavailable, say so and return
   the full paste-ready report; do not leave the destination implicit or claim it was posted.
5. The Done-when is not negotiable by the implementer: it stops and reports, never weakens an
   assertion or skips a test. The main session amends a Done-when on `main` with the reason.
6. A question is not a request to edit files. Design decisions go to the owner; nothing else waits.
7. Lessons and decisions of the owner go into this file or `docs/` in a commit. Status lives in
   GitHub labels and issues.
8. Every task is resumable and cut into milestones: outputs pushed at each, a checkpoint comment;
   long runs append-only with a resume command.
9. Nothing of the original game in git: no GOAL2 byte, savestate or image (they stay in the owner's
   private Drive folder, as for goal2). Records hold digests and counts.
10. Tests fail before and pass after; equality with the Python port is shown on the receipts, never
    assumed from a unit test alone.
