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
guest-call sites and 12 distinct external ports. Those existing keyboard/menu/
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
Registered23E4:08DF and 0791:835F, plus nested23E4:0279, remain delegated source
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

## T17 marking-target subtree

At the same accepted `2cbeb36fdd3feb369324aaa88e6e4d2aa3b3d99c` pin,
`engine/src/marking.rs` translates positioning.choose_marking_target **0791:47C5**,
positioning.near_post_zone **0791:4438**, geometry.in_own_half **0791:2C54** and
entrypoints.random_n **214B:06B1**. `geometry.rs` exposes the existing inline
c2996 as geometry.ball_holder_is_side0 **0791:2996**. Helpers remain inline;
13 real guest sites retain source arguments/ret_to/far and suspension behavior.
Default variants close over the new bodies and accepted native 3216/278A/3A06/
2BE5; nondefault variants stay Python. Source/helper/ABI/observer inventory and
proof requirements are in out/T17/contract.md and inventory-v1.json. Actual T16
baseline is preserved in .cache/T17-baseline, bound before builds in
out/T17/baseline-snapshot-v1.json. Full combined fidelity/performance validation is bound in
out/T17/validation-final-v2.json; scope, all outcomes and the preserved metadata
rejection/recovery are documented in out/T17/assessment.md.

## T18 player-destination subtree

At accepted oracle `2cbeb36fdd3feb369324aaa88e6e4d2aa3b3d99c`,
`engine/src/destination.rs` translates geometry.draw_table_byte **0791:261A**,
energy_gate_chance **0791:2B7B**, mirror_to_team_frame **0791:2C86**,
ball_ahead_of_by **0791:2D10**, ahead_of_ball_by **0791:2D6D**,
in_own_goal_area **0791:2E36**; runtime.min_longint **214B:0D1C**,
max_longint **214B:0D56**, clamp_byte **214B:2031**; and
entrypoints.membership **23E4:08DF**.

`engine/src/destination_flow.rs` translates ball.holder_in_advanced_central_strip
**0791:40BC**, positioning.position_group **0791:42CB**,
set_destination_from_post **0791:4354**, update_marking_destination **0791:4A28**
and update_player_destination **0791:4B64**. All 41 real guest return sites,
ABI/pop/long behavior and captured versus live callback state follow the source.
Source-inline Regs, geometry/direction and random operations remain inline;
nondefault variants remain Python. Existing native descendants bound the closure.

The complete source/helper inventory is `out/T18/inventory-v2.json` (v1 retained),
with semantics in `out/T18/contract.md`. The accepted T17 baseline was saved before
builds under `.cache/T18-baseline`, bound by `baseline-snapshot-v1.json`.
Accepted candidate archive: `artifact-archive-v2.json`; v1 is retained as a rejected
preflight archive. `freeze-v2.json` binds the unchanged production artifact and
versioned proof recovery. Private state/tables/captures remain outside git.

The final timing recovery retains all 409 previous bindings and adds versioned
proof tooling only: `freeze-v3.json` binds 417 inputs, with no production rebuild
or guard change. Full final evidence is `out/T18/validation-final-v3.json`; the
assessment reports both complete replacement timings and the rejected campaign.

## T19 depth-adjustment subtree

At accepted oracle `2cbeb36fdd3feb369324aaa88e6e4d2aa3b3d99c`,
`engine/src/depth.rs` translates positioning.adjust_depth_offset **0791:474D**,
depth_step_attack **0791:4532**, depth_step_defend **0791:4649**,
geometry.slot_in_side **0791:2BB1** and entrypoints.coin **214B:06FA**.
All 23 real guest return sites, near/far return ABI, source argument/read/write
order and captured versus live callback state remain explicit. The coin keeps
its RNG inline via the existing source-equivalent `marking::rng_core`; no
registered random_n call or guest frame is introduced. Nondefault variants remain
Python. Existing native descendants form the closed tree's boundaries.

Source/helper/site inventory and semantics: `out/T19/inventory-v1.json` and
`out/T19/contract.md`. The actual accepted T18 source/adapter/tests and both
interpreter binaries were saved before builds under `.cache/T19-baseline`,
bound by `out/T19/baseline-snapshot-v1.json`. Candidate archive-v1 was copied
only after both interpreter installations and passing preflight.
`out/T19/freeze-v1.json` binds 466 concrete proof/source/binary/private inputs.
Historical receipts and private state/tables/captures remain preserved.

Final T19 validation is `out/T19/validation-final-v2.json`. Post-writer supplemental
sources are explicitly bound, retaining all 466 original inputs and both binaries.
A selector-cardinality rejection retained the original 19,520 comparisons and
added 640 scoped own-write cases for 122 distinct selectors; no runtime rebuild
or timing rerun. All results, limits and rejected logs are in the assessment.

## T20 chase-gate subtree

At accepted oracle `2cbeb36fdd3feb369324aaa88e6e4d2aa3b3d99c`,
`engine/src/chase.rs` translates contests.chase_ball_gate **0791:5729** and
geometry.in_own_goal_strip **0791:2EB8** / in_opposing_goal_strip **0791:2EF0**.
The five real guest return sites preserve their near/far ABI and suspensions.
The gate resumes with fresh Regs and reads live AX, ignoring SENT. Repeated
parent-pointer reads remain separate from the captured point/parent DI.

Both leaf queries retain source-inline direction_in_dx/c2be5 and c2e82, including
argument/return words, queued stack writes, scratch state and flag behavior. The
existing source-equivalent `destination::direction` is exposed crate-locally;
no registered goal-strip helper call or guest frame is invented. Nondefault
variants remain Python. Contract/helper/site inventory: `out/T20/contract.md`
and `out/T20/inventory-v1.json`.

Actual accepted T19 source/adapter/tests and both interpreter binaries were saved
before builds in `.cache/T20-baseline`, bound by baseline-snapshot-v1.json.
Candidate artifact-archive-v1 was copied after both installs and public70 each
passed. Freeze-v1 binds 542 concrete source/binary/private/proof inputs; independent
fidelity suites use a bounded pool before guarded corpus/profile/timing stages.
Historical receipts and private state/tables/captures remain preserved.

Final T20 validation is `out/T20/validation-final-v1.json`; source/baseline/profile
audit is baseline-input-audit-v1.json. All 542 inputs and both binaries remained
fixed, including all inherited proof sources/metadata. Exact row/distinct-selector
counts both 99 were sealed before the campaign. Every outcome and the one-fixture
measurement limit are reported in the assessment.

## T21 ball-travel and long-multiply subtree

At accepted oracle `2cbeb36fdd3feb369324aaa88e6e4d2aa3b3d99c`,
`engine/src/travel.rs` translates motion.ball_travel **0791:835F** and
runtime.sys_long_mul **23E4:0279**. The single far guest return **0791:8396**
remains explicit; neither entry has long=True. The caller preserves its captured
low SENT return and live DX. Its single live-SS far-pointer read, wrapped abs/sum,
register writes and later live scale read keep source order.

The multiply captures AX/DX/BX/CX before flushing, retains its dead pushes and
scratch outputs, and uses the last 16-bit addition's six arithmetic flags. The
existing source-equivalent `speaker::add_flags` is exposed crate-locally. No new
frame prologue or returned long object is invented. Variants remain Python.
Inventory/helper/ABI/observer contract: out/T21/inventory-v1.json and contract.md.

Actual accepted T20 source/adapter/tests and both interpreter binaries were
preserved before builds under `.cache/T21-baseline`, bound by the 58-file
baseline-snapshot-v1.json. Both installs/public76 completed before archive-v1.
Freeze-v1 binds 598 source/binary/private/proof inputs. The earlier draw-state
instrumented wrappers now have explicit nondefault tags; all original tracing/
fault assertions remain, with an added actual-native integration test. Rejected
preflight logs and original harness are preserved. No original bytes in git.

Final T21 validation is out/T21/validation-final-v1.json; baseline-input-audit-v1
verifies accepted T20 snapshot/profile/native-presence identity. All 598 bound
inputs and both binaries remained fixed. Failed instrumentation preflight logs
are preserved; canonical campaign has no rejected stage. Arithmetic/flag/sign/
overflow witnesses and every raw timing outcome are in the assessment.

## T22 offside-line/display tree

At accepted oracle`2cbeb36fdd3feb369324aaa88e6e4d2aa3b3d99c`,
engine/src/offside.rs translates motion.track_offside_line0791:8CF5,
motion.move_sprite0791:8E24 and motion.place_marker0791:90C5. Four far guest
returns8D42/8DD0/8E17/9113 preserve observable boundaries; direction2BE5 remains
native. Inline cell/record/signed-byte/multiply helpers are translated with exact
read/write/register ordering and captured/live values; no invented local writes.
Variants remain Python. See out/T22/inventory-v1.json and contract.md.
Actual accepted T21 source/tests/adapter/both interpreter binaries were preserved
before builds in.cache/T22-baseline; all598 old inputs/214 evidence verified.
No original bytes enter git. Full fidelity/strict ALL75/F40/lifecycle and complete
three-round measurements pass their predeclared gates; performance is mixed,
with two faster samples and one1.24% regression(median1.01% less CPU).
No sample is discarded or repeatable gain claimed. validation-final-v1 binds661
primary inputs and230 evidence hashes. A post-writer all-inventory helper proof
adds shared s8/s16 instrumentation with6,288 scoped/64 variant pairs, separately
sealed by supplemental-source-inputs-v1 for both proof/audit drivers. Canonical
sources/artifacts/receipts remain fixed; all91 producer groups/controller stopped.
Live CI/merge status remains checkpoint#1.

## T23 Pascal string-write chunk

At accepted oracle`2cbeb36fdd3feb369324aaa88e6e4d2aa3b3d99c`,
engine/src/pascal.rs translates runtime.sys_str_store23E4:062A,
sys_str_store_max23E4:0644 andsys_str_concat23E4:06B7, including their complete
_copy_forward/str_concat helpers. All seven inventoried source body/helper
functions are included in the first scoped-closure probe. Zero guest calls;
retf4 for062A/06B7 despite four input words, retf10 for0644. Variants remain
Python. The source's disjoint/no-wrap/read-ahead snapshot is retained separately
from live per-byte overlap/wrap reads, including unmasked helper-entry offsets.
A pure untapped Host::read_snapshot primitive captures input blocks without
running Python callbacks while borrowed; existing host paths remain unchanged.
Regs::cld defers DF clearing to the late flags store and preserves other live
bits. Inventory and read/write/register/flag/callback contract are in out/T23.
Actual accepted T22 source/tests/adapter/CPython/PyPy artifacts were preserved
before builds in.cache/T23-baseline(71 files), after verifying661 primary/230
old evidence/two supplemental bindings. No original bytes enter git. Full combined-artifact fidelity/lifecycle/ALL75/F40 and selected complete
measurement gates pass. The first campaign is preserved/rejected for late load;
a separately sealed full repeat on the unchanged artifact passes stricter load
checks. Its paired median is0.62% less CPU,two faster rounds/one3.01% slower;
no repeatable gain claim. Final-v2 ledger binds731 primary inputs/263 evidence
hashes,two additive measurement/audit sources and five immutable supplemental
inputs. All107 producer groups/controller stopped. Live CI/merge status is
checkpoint#1;source contracts and original Done-when remain unchanged.

## T24 keyboard-service chunk

At accepted oracle`2cbeb36fdd3feb369324aaa88e6e4d2aa3b3d99c`,
engine/src/keyboard.rs and native dispatch translate menus.key_pressed214B:0723,
read_key08DD,wait_key_clear0983 and push_back_key0993. The wait caller retains
its sole actual far guest08DD/return098A. All nine owned body/helper functions are
scoped;generic Mem key/poll/read/stop primitives remain the kit service boundary.
No BIOS frame or new first-poll auto-answer policy is added. Source return-site
word/SS/load ordering,callback truth and live AH,pushed-key frames,pending flag/
prologue ordering,source-style fresh resumed Regs and stop/error behavior remain.
Nondefault variants stay Python. Native bodies use the existing per-port memory
view rather than creating one without its kit. Source load subtraction retains
unbounded integer/operator fallback behavior in return-site formatting.

Actual accepted T23 source/tests/adapter/both interpreter artifacts preserved
before builds in.cache/T24-baseline(73 files),after731 primary/263 evidence/two
source/five input hashes passed. Initial genuine-entry capture hit the unchanged
dispatch guard on a loaded host;failed log/source identity/harness preserved.
The idle v2 capture was superseded before collecting any entries;its empty
attempt/input/log receipt remains. Accepted capture-v3 obtains32 real entries
(eight per body) from eight genuine source-drive prefixes,with append-only
private shards/journal and the unchanged dispatch guard. Its historical
evidence.py source hash maps only to the exact archived pre-extension version
in.cache/T24-capture-v2-source/evidence.py. No fabricated entry state or original
bytes in git. Both interpreter builds/full88-test preflights preceded archive;
the canonical combined-artifact campaign binds852 fixed files and59 proof/audit
sources. All combined-artifact fidelity/lifecycle/strict ALL75/F40/prefix and
selected quiet-measurement gates pass. Loaded v1 and complete quiet replacement
v2 are both preserved;paired median is1.00% more CPU than saved T23,one faster
and two slower rounds. No speed improvement is claimed. Final validation binds
852 primary files/281 evidence hashes. The separate profile-reference audit is
sealed by supplemental-source-inputs-v1(one source/four receipts),proving the
older comparator against accepted history and the profile against fresh drives.
All111 canonical/timing groups,controller and three capture PIDs exited. Live
CI/merge/mainCI/merged audit and owner-requested pause remain in checkpoint#1.

## T25 text-cell rendering chunk

At accepted oracle2cbeb36fdd3feb369324aaa88e6e4d2aa3b3d99c,
engine/src/text.rs translates display.text_cells_forward214B:00FF,
text_cells_backward0123,string_at_attr01A3,string_at_set_attr0205,
string_forward_attr026D and string_forward_set_attr02C8. Inventory-v2 resolves
all14 owned body/helper functions and specializes _string_cells' eight real
guest returns;23E4:0644 is an existing native boundary. Preserve bytewise live
source/overlap/wrap,word-write ordering,captured versus live SS/pointers/AX,
attribute-write order,fresh resumed Regs and late DF stores. Source geometry.mul
writesAX/DX and does not change arithmetic flags. Variants remain Python.

Actual accepted T24 source/tests/adapter/both interpreter artifacts were
preserved before any build in.cache/T25-baseline(75 files),after852 primary/
281 evidence plus supplemental1source/4inputs verified. Forty-eight genuine
entry shards(eight per body)come from two pure-oracle prefixes,with49 capture
inputs sealed before execution. Private memory remains ignored. Initial
inventory line-attribution diagnostics and development probe epochs are
preserved;accepted inventory-v2 uses actual AST call locations. All completion,
final artifact binding,CI/merge and stop/resume status remain in checkpoint#1.

Fresh prior63/new6 proofs,all14-owned closure,ordered drive,lifecycle and
strict ALL75/F40/10/20/30/60 comparisons pass. Full profile confirms69 bodies,
2,699,104 native/404,581 Python entries. First complete quiet campaign passes
all runner/load checks;paired median1.66% less CPU than saved T24,all three
rounds improve. Same-campaign T24/PyPy0.684159861 and T25/PyPy0.667383160
remain alongside all raw samples. Original1083 bindings and additive6sources/
121inputs stay fixed;the original pre-proof failed wrapper remains preserved.
