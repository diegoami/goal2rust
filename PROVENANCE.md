# Provenance

The current oracle is goal2-archaeology at
`e0270981883f02ce46a31391e7070079977bbfef` (accepted T80d handover, including
T80c's sealed family and T79's larger fidelity corpus). CI and the ignored
`.cache/goal2-archaeology` clone use this exact commit. T03 validates the same
Rust implementation against the state-and-tables API. The T02 oracle remains
available in `.cache/goal2-archaeology-T02` at `d3cf46a3`; historical T01/T02
receipts and the translation-origin pins below remain unchanged.

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
