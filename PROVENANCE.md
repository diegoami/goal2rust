# Provenance

The current oracle is goal2-archaeology at
`2cbeb36fdd3feb369324aaa88e6e4d2aa3b3d99c` (accepted PR640, state/2,
including checkpoint-table retention and extractor-manifest fixes). CI and
`.cache/goal2-archaeology` use this exact commit. T07 refreshes compatibility
and artifact-bound proof for the unchanged twelve native bodies.

Previous e0270981 source remains in ignored `.cache/goal2-archaeology-T06`;
d3cf46a3 remains in `.cache/goal2-archaeology-T02`. Historical inputs, receipts,
translation-origin pins and measured binary archives stay unchanged. T07's input
and source audit is in `out/T07/input-audit-v1.json`. All translated routines,
helpers, machine and guest dispatcher sources are byte-identical across this
oracle update; changes are in the sealed image/checkpoint/table boundary and
associated checks/docs. No original bytes or extracted tables are committed.

Each translated routine is listed with its Python source and translation-origin
commit. T03's source audit records that the machine/frames/runtime and the
geometry/entrypoint bodies are byte-identical between the two oracle commits.

| Routine (address) | Python port | goal2-archaeology commit | Rust |
| --- | --- | --- | --- |
| 0791:2BE5 attack direction (retf 4) | `port/entrypoints.py` `direction` (with `side_core`) | d3cf46a3 | `engine/src/geometry.rs` `direction` |
| 0791:2B51 slot on the ball's side (retf 4) | `port/geometry.py` `slot_is_on_ball_side` (with `c2996`, `c2974`) | d3cf46a3 | `geometry.rs` `slot_is_on_ball_side` |
| 0791:26D7 player's effective tactic (retf 6) | `port/geometry.py` `player_effective_tactic` (with `player_byte`, `c2974`, `runtime.set_test`) | d3cf46a3 | `geometry.rs` `player_effective_tactic` |
| 0791:045D keeper slot (ret 2) | `port/entrypoints.py` `keeper` (with `finish_bool`, `pilot.is_keeper_slot`) | d3cf46a3 | `geometry.rs` `keeper` |
| 0791:2C29 slot is the idle ball slot (retf 4) | `port/geometry.py` `slot_is_idle_ball_slot` | d3cf46a3 | `geometry.rs` `slot_is_idle_ball_slot` |
| 0791:2CEC player at the ball (retf 4) | `port/geometry.py` `player_at_ball` | d3cf46a3 | `geometry.rs` `player_at_ball` |
| 0791:2974 side of a slot (retf 4) | `port/entrypoints.py` `side` (with `side_core`, `pilot.pitch_slot_side`) | d3cf46a3 | `geometry.rs` `side` |

The machinery each routine runs on is translated from the same commit: `Regs`, `invoke`, `sub_flags`
(`port/runtime.py`) in `engine/src/regs.rs`; `args` (`port/runtime.py`) in `engine/src/host.rs`; `_PortMemory`'s
reads, writes, registers and `ss_lin`, `_set_plain` and `PortMachine.write_as`'s fast path (`port/engine.py`) in
`engine/src/py.rs`. The hook that loads them is `out/T01/rust-hook-v1.patch` on a clone of d3cf46a3 (not in
goal2-archaeology).

## T02 machine

The same exact oracle commit is `d3cf46a3e87f0ba04916867b5b231c4646a0c2bd`.
`engine/src/machine.rs` translates `port/engine.py`'s `PortMachine` register/memory IO,
`write_as`, `pc`, `_dispatch`, and `run`; `port/guest.py`'s `PortFrame` constructor,
`start`, `_in_frame`, `_step`, `_issue`, `returned`, `resume`, and `_finish`; and
`machine.py`'s `return_from`, `stack_word`, `fire`, and listener delivery.

`MachineCore` owns one memory buffer and a Rust register bank. `_PortMemory` borrows
that buffer and accesses the same bank through `RegisterFile`; there is no bridge
state synchronization. Native bodies call the existing seven `geometry.rs`
functions through `NativeHost`, directly from Rust. No further routines are ported.
Python generator objects hold only unported bodies' continuations; their frame
metadata, guest-call pushes, dispatch, suspension, and returns are Rust's.

`engine/python/goal2rust/machine.py` adapts the unchanged kit's construction and
registration APIs. It inherits `Machine`'s address helpers, kit registration
helpers, far-call setup, and snapshot/restore (which use the Rust IO/register
methods). The kit's event/decision logic and replay-based save format remain the
pinned Python implementation. `goal2rust.Match` exposes its per-event API over
this machine; `install()` selects it process-locally for the oracle harnesses,
including `Match.load` replay. Nothing in the pinned clone is patched.

## T04 native availability subtree

Translation-origin pin: `e0270981883f02ce46a31391e7070079977bbfef`, the
unchanged T03 accepted oracle. Full inventory: `out/T04/contract.md`.

| Routine | Python source | Rust |
| --- | --- | --- |
| 0791:2956, retf 4 | `port/geometry.py` `player_unavailable_on_pitch` | `geometry.rs` `unavailable_start` / `unavailable_resume`; `machine.rs` `NativeContinuation` |
| 1771:3216, retf 2 | `port/attributes.py` `player_unavailable`, `mul`, `put`, `ret` | `machine.rs` `availability_body` |

The caller's native continuation uses the existing issue/return/suspend path,
including its observable guest Call metadata and separate callee frame. The
callee reproduces the upstream inline bit tests and retained stack bytes; it
has no yielded guest call. Nondefault variants use their original Python
bodies. This adds two bodies to T02's seven; it does not replace unported
Python generators. T03 receipts remain historical seven-body evidence.

## T05 nearest-to-ball tree

Translation-origin pin: `e0270981883f02ce46a31391e7070079977bbfef`.
`port/ball.py` `find_nearest_to_ball` at **0791:2FB1** (near ret, no args)
and its `local8`, `local16`, `load_local_pitch`, geometry `cbw`/`mul`/`imul`
semantics are reproduced in `engine/src/ball.rs`. `machine.rs` carries its
four native continuation phases through the existing guest dispatcher.
Its guest closure 2956 -> 3216 and 2BE5 stays separately observable and uses
previously translated bodies. Full contract: `out/T05/contract.md`.

## T06 effective-skill tree

Translation-origin pin: `e0270981883f02ce46a31391e7070079977bbfef`.
`geometry.skill_of_pitch_record` **0791:278A** (retf6) and
`attributes.derived_skill` **1771:3A06** (retf4) are reproduced in
`engine/src/skill.rs`, including the respective Regs and immediate Mem.Frame
semantics and the already-inline keeper membership operation. `machine.rs`
retains the caller's off/seg/element/base scalars and passes the dispatcher's
captured AX to its Rust continuation. One observable guest callee, no dynamic
target; nondefault variants retain Python bodies. Contract: out/T06/contract.md.

## T08 common bridge optimization

Semantics remain pinned to accepted `2cbeb36fdd3feb369324aaa88e6e4d2aa3b3d99c`.
`machine.rs` optimizes static register/name lookup and common exact-integer
write_as, retaining the original fallback/listener machinery. The adapter's
PortMemory binds exact-integer fixed-image reads to Rust, with the original
memory-view methods as fallback. Contract and callback/numeric boundaries:
`out/T08/contract.md`. No guest routine or state/table format is added.
The exact T07 source/adapter/extension baseline is preserved and hash-bound for
simultaneous before/after rounds; T07 historical evidence remains unchanged.

## T09 speaker/noise-state tree

Translation pin: `2cbeb36fdd3feb369324aaa88e6e4d2aa3b3d99c` (state/2).
`port/display.py` speaker_noise_state **0791:94E8** (ret), speaker_seed_step
**0791:94C9** (ret2), speaker_off_memory **214B:1E8D** (retf) and
`port/entrypoints.py` explicit_seed_draw **214B:0688** (retf6) are reproduced by
`engine/src/speaker.rs` and its `machine.rs` continuations. The source's existing
omitted-hardware stubs **214B:1EBC** (retf2) and **0791:0425** (ret2) remain
observable delegated calls. No hardware functionality is claimed. The RNG seed,
DF/flags, dead frame writes, secondary state and value-return timing remain
source ordered; nondefault variants retain Python bodies. Full contract:
`out/T09/contract.md`. Baseline T08 sources/binaries and the rejected descriptor
prototype are preserved, with hashes in `out/T09/`.

## T10 match key-poll caller

Translation pin: `2cbeb36fdd3feb369324aaa88e6e4d2aa3b3d99c` (state/2).
`port/menus.py` `match_key_poll` **0791:9372** (near ret/no arguments) is reproduced
in `engine/src/keys.rs` with native continuations in `machine.rs`. Its complete
six-slot delay-table loop and all key/quick-mode branches retain the15 literal
guest-call sites and12 distinct external ports. Those existing keyboard/menu/
library/display/speaker callees remain separately observable delegated routines,
not newly translated bodies. Fresh actual-AX reads, pending stack bytes, captured
short-lived arguments and live pointer reloads follow the source. Nondefault
variants use Python. Contract: out/T10/contract.md; preserved actual T09 baseline
source/adapter/extension: out/T10/baseline-snapshot-v1.json.

## T11 ball draw-state caller

Translation pin:`2cbeb36fdd3feb369324aaa88e6e4d2aa3b3d99c`(state/2).
`port/display.py` `draw_ball_state` **0791:8F10**(retf4) and its inline `grid_cell`
helper are reproduced in `engine/src/ball_draw.rs` and `machine.rs` continuations.
Record segment/offset remain captured across membership/travel calls; grid tables,
coordinates and post-return ZF/AX remain live. Signed-byte coordinates use unsigned
word MUL exactly as the Python helper, including highDX and unchanged flags.
Registered23E4:08DF and0791:835F, plus nested23E4:0279, remain delegated source
bodies with observable ABI/frames. No hardware or transitive-callee claim. Default
variant only; others stay Python. Full contract:out/T11/contract.md, preserved
actual T10 source/adapter/extension:out/T11/baseline-snapshot-v1.json.

## T12 watched sweep caller

Translation pin:`2cbeb36fdd3feb369324aaa88e6e4d2aa3b3d99c`(state/2).
`port/frame.py` watched_match_engine **0791:9564**(near ret/no args), immediate
Mem.Frame/helpers and its17 SITES rows are reproduced in engine/src/sweep.rs and
machine.rs continuations. Captured frameBP/DS/CS/slot/k/rec, liveSS/local stop/
register/flag/data reads, dead push and all immediate stack/possession/wait writes
retain source order.14 registered external callees remain observable/delegated;
no transitive callee/hardware claim. Default variant only; others stay Python.
Contract out/T12/contract.md; actual T11 source/adapter/extension baseline bound
in out/T12/baseline-snapshot-v1.json, no original data committed.

## T13 play-state caller

Pin:`2cbeb36fdd3feb369324aaa88e6e4d2aa3b3d99c`(state/2). contests.play_state_update
**0791:57AC**(retf4), inline live own/player_record helpers and finite probe/table
loops become engine/src/play.rs with machine.rs continuations.15 return sites/
14 registered external callees remain delegated, including actual default keeper/
side helpers; no transitive/hardware claim. CurrentBP/argument/table/AX reloads,
Regs pending stack and destination None/True/False preserve source semantics;
nondefault variants Python. Scope out/T13/contract.md, exact T12 source/adapter/
extension baseline bound in out/T13/baseline-snapshot-v1.json.

## T14 player-update caller

Pin:`2cbeb36fdd3feb369324aaa88e6e4d2aa3b3d99c`(state/2). motion.update_player
**0791:8AE9**(retf4), immediate frame/record and finite HANDLERS dispatch are
translated in engine/src/player_update.rs and machine.rs continuations. Captured
frameBP/record offset+segment/unwrapped linear record+code/AXreply/kept versus
live contents/conditional reads retain source lifetime/order. Return0 fatigue
versusNone normal remains distinct, same callbacks/flags/stack/ABI.16 registered
callees remain delegated, no hardware/transitive claim; variants Python. Contract
out/T14/contract.md, actual T13 baseline bound out/T14/baseline-snapshot-v1.json.

## T15 player sprite caller

`engine/src/player_sprite.rs` translates `motion.move_player_sprite` 0791:8537
and inline `record`, `cell`, `cell_mul`, `lo`, `regs` at the same accepted
`2cbeb36fdd3feb369324aaa88e6e4d2aa3b3d99c` pin. Five guest callees remain delegated;
variants stay Python. See docs/tasks/T15.md and out/T15/contract.md.

## T16 player run step

`engine/src/run_step.rs` translates `pilot.player_run_step` 0791:8889 and its
inline `rand`, `coin`, `in_set`, `pitch_slot_side`, `attack_direction`,
`is_keeper_slot`, `on_target`, `on_pitch`, `can_move` at accepted
`2cbeb36fdd3feb369324aaa88e6e4d2aa3b3d99c`. No guest calls are introduced;
variants stay Python. See docs/tasks/T16.md and out/T16/contract.md.
