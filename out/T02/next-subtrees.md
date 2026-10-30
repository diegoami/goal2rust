# T02 M4: proposed subtree order

Owner update, 2026-10-30: [the roadmap](../../docs/roadmap.md) inserts T03's
accepted sealed-engine compatibility before T04's first native tree. The
post-T02 diagnostic profile and preflight live in `out/roadmap/`; confirm the
candidate at the new oracle pin. The original proposal below is historical.

Planning only; T02 ports no additional routine. Oracle: archaeology
`d3cf46a3e87f0ba04916867b5b231c4646a0c2bd`. Evidence is T01's measured
`out/T01/profile-d3cf46a3-v1.prof` / `.txt`, summarised with literal guest-call
edges by `subtree_plan_v1.py` into `profile-subtrees-v2.json`.

The Rust machine now provides dispatch, return frames, register/memory state,
listeners and sites. Its Python bridge is a proof boundary. The next unit of
translation should close a hot call tree so that internal guest calls can stay
in Rust, while preserving stack bytes, register effects, callback order, and
suspension at kit stops.

## Proposed sequence

1. **Geometry and its attribute dependencies.** First close
   `0791:2956` → `1771:3216` (player availability). The drive dispatched these
   184,872 and 233,587 times respectively. T01 left 2956 Python because it yields
   a guest call; T02's Rust frame machinery removes that constraint. Then close
   `0791:278A` → `1771:3A06` (effective skill / player attribute), 23,342 dispatches
   each, plus remaining geometry helpers used by the next root. Reuse the seven
   existing native queries. This is the smallest next proof of a native caller
   and callee, including their return bytes, rather than another isolated leaf.
2. **Ball selection and possession.** Close `0791:2FB1` (`find_nearest_to_ball`)
   over 2956 and the already-native 2BE5. Its Python body/resumptions account for
   2.94 s self time in the profile. It is called/resumed 298,641 times; that is
   **not** its guest-entry count. Continue with the receiver, pass, clearance and
   possession roots that use the geometry/skill tree, taking runtime/RNG helpers
   as dependencies, rather than translating every function in `ball.py` at once.
3. **Contests and duels.** The drive dispatches `0791:5049`, `56D9` and `57AC`
   36,198 times each, `533B` 35,723 times, `5565` 35,193 times, and `6188` 57,791
   times. Close their literal and dynamic callees bottom up, sharing the same
   geometry, skill and RNG helpers. Keep event-producing sites and listener
   writes visible; these roots are where an apparently harmless ordering change
   can alter a match.
4. **Positioning, then movement and their display dependencies.** The hot
   positioning roots are `0791:42CB` (65,877 entries), `4A28` (37,118), and `474D`
   (34,783). Movement follows: `8537` (75,943), `8AE9` and `8889` (75,781 each).
   `8537` also calls `8F10` (draw-ball state, 79,194 entries overall). Preserve
   those display-memory effects even in a no-screen receipt. Translate the
   required display/service bodies or retain explicit bridge calls until their
   own subtree is proved.

Menus, sound/display services, frame loops and the rest follow a fresh profile
once these trees have moved. Their high call counts are not evidence that their
individual bodies dominate: `214B:0723` is 78,132 dispatches, `0791:9372` 76,928,
`0791:94E8` 76,847 and `214B:1E8D` 63,498, but much of their cost remains calling
machinery. The next timing comparison must still use the plain PyPy port as its
fastest Python baseline.

## Proof and measurement for the next task

- Capture real inputs for the new subtree as well as random/edge states. Compare
  full memory, every register, return values/errors and ordered callbacks at each
  completed call, including dead stack bytes. Include near/far calls, caller-pop
  returns, recursion/repeated return addresses, wraparound and suspended frames.
- Replay the ordered E034-03 drive with `PYTHONHASHSEED=0`, F40 with
  `compare.py --no-screen`, and the kit's save/load checks. The admitted 75-match
  family remains the go/no-go's gate before an engine milestone review.
- Use a caller/return mutant as well as a body mutant. Keep failing receipts.
  T02's wide-flush bug was invisible to full memory alone but visible to a
  full-stack listener's arbitrary-width integer.
- Keep paired receipts from the same quiet machine, including CPython and PyPy
  baselines and source/extension hashes. Count bridge crossings after closing
  each tree, then re-profile before choosing the next one.

Profile limits: the stored dispatch table includes only its top 40 addresses;
`dispatch_calls: null` means the entry count was not recorded there. Python
profile counts include generator resumes and inline helper calls. Self times
add across unique Python code; cumulative times overlap. The generated literal
call graph omits dynamic targets and inline helpers, so each proposed subtree
needs a full caller/callee inventory before implementation. This ordering is a
recommendation for the next task, not a change to the current contract.
