# T17 sealed subtree inventory and proof plan

M1 source inventory is at accepted oracle 2cbeb36f. inventory-v1.json records
all five registered bodies, their actual ret/pop contracts, 13 outbound literal
sites and registered literal inbound sites; direct registry entry remains valid.
The root's 12 sites and zone's one site close over five new bodies plus accepted
3216 /278A->3A06 /2BE5. No dynamic guest target exists in the selected bodies.
No variant is newly native: any non-None variant uses the source Python body.
Existing default native boundaries retain their accepted semantics and proofs.

## Source ownership and state

Positioning ownership: choose_marking_target, near_post_zone; rec/player/country/
pitch, argptr/r8/r16/w8/w16, guest/near/same/far/local_far/push_word/pop_dx.
Mem.enter/Frame/arg/ss_lin primitives preserve their observable calls and order.
Every frame access separately reads actual SS, wraps its word address once,
and reads a contiguous word (no wrapping between bytes). Positioning record
subfields are linear additions after mem.addr wrapped the initial base.

47C5 enters 12 bytes at 47C5 before reading near arg0, captures parent BP, then
reads parent+8 segment before parent+6 offset, each through a fresh SS read.
It captures the resulting linear p across all suspensions. First 2996 SENT AX
selects country_id via signed AL; country(mem) reads pointer offset then segment
and captures c. Separate pointer rereads populate locals -12/-10 (47E2/47E5).
Local -1=0 at47E8; second 2996 SENT AL writes -8 at47EF and selects captured
side/base/mark_off. r8(p+6)-base is word-wrapped before doubling; ds16 wraps
mark_off once. Mark is captured and written at -7 (4836), distinct from later
local/record rereads.

If mark==0: -3=2 at483F; slots2..11 reread c[(slot-1)*2] into captured
player_id, call3216 at485D, then if available reread DS0668[side], compute
opponent/point and call4438 at4888. SENT AL true replaces mark and writes -7
at489A; every iteration writes -3=slot+1 at489D. No early break on match.
If mark!=0: -3=2 at48AB; slots2..11 reread player_id from captured c; mismatch
or unavailable at48E2 writes -3 at49D3 and continues. Success captures opp_slot,
writes parent -4 (48FB) then opponent position parent -2 (4914). Call2C54
at4930 reads actual DS at request construction. Keeper SENT AL true returns
actual live AX&FF00. Else -5=1 at4937; skill ours494D SENT is pushed at494D,
then theirs496A SENT is compared to a real stack pop_dx, including live SS/SP.
If theirs>ours repeat4980/499D and write wrapped difference//16+1 at49A7.
Read live frame -5 for random49B2, push its captured SENT at49B2 across direction
49C0, then real pop_dx. Parent -1 is reread and adjusted by signed direction AL
and signed popped draw AL (49C7); write local -1=1 at49CB and return live
AX&FF00|1. Exhausted nonzero mark clears captured mark_off at4A1B. Final return
reads live AX first, then live local -1. Parent -2/-1 overlap intentionally.
No extra register stores or artificial loop cap. Guest helper masks captured
SENT; final returns and stack pops use actual registers. Call args remain in
source push order and retain ret_to/far from inventory.

4438 argptr reads arg1,arg0 for p then arg1,arg0 again for seg/off; read arg2
point before enter4. Write captured p+9 word to -3 at4445. If live p+12 !=9,
read p+D player index, players pointer offset then segment, player+6 position,
read frame -2 before DS07BE[position], write -2 at4470. Signed X distance <4
short-circuits direction4493; then signed Y/direction SENT AL distance <9.
Write close -1 at44B5; return live AX high then frame -1. Seg/off/point/p
remain captured while local -2 is reread after guest suspension.

Geometry ownership: ball_holder_is_side0/c2996; in_own_half/c2c54/
direction_in_dx/c2be5/c2974, rec8/cbw/cwd/imul. 2996 Regs enters2, reads
DS830B<12, replaces AL, queues local -1, leaves/stores. 2C54 reads two args
through runtime.args's one SS base, enters2, direction_in_dx sets ES/DI and
inline-invokes geometry.c2be5 with return2C63. That helper differs from
registered entrypoints.direction (flags/accesses): use its source version.
It enters2, computes half/left flag with partial AX, pushes saved AX, invokes
c2974 at2C13, restores captured DX, increments cached SP, XOR/CBW/index lookup,
queues local -1/leaves. No invented flag updates. c2c54 sign-extends direction
into DX, rereads wrapped rec+1, signed multiply (AX low/DX high), tests AX sign,
queues local -1/leaves/stores. All Regs pending/dead-stack coalescing, first-use
reads, cached SS, dirty insertion/store order and untouched flags preserved.
Variant own-half-zero remains source. No logical guest frames for inline calls.

Entrypoints ownership: random_n/random_core/rng_core and runtime.args/Regs/
invoke/add_flags. Capture full word n before Regs enter2. Read DS:A978 contiguous
farptr offset then segment. Set DI/ES, inline invoke214B return06C4 with pushes
(seg,off,n). rng_core enters2, captures SP, queues DS/seg/off pushes, reads
explicit captured seed pointer, computes new word, writes069F immediately.
Only then read actual EFLAGS.DF; draw/high use captured new and full n, including
0/32768/65535. Set BX7ABD/SI/DI +/-2/ES/AX/DX; add_flags(high,1) with CF from
high!=0. Restore cached SP, queue draw local -2/leave; outer local -2/leave/store.
Callbacks may alter seed/pointer/registers/stack but not captured new/n.
Full state, dead frames, writes-before-store and flag preservation required.

## Fixed proof minima and positive coverage (before canonical runs)

Each body: eight actual source-entry RAM captures, each in four tap/listener
modes and three schedules (normal, entry/suspension pause-replay, direct done):
96 real comparisons. Add exactly 500 deterministic authored inputs in four
modes: 2000 comparisons. Total minimum2096/body, 10480 over five. Additional
edge/mutation cases may be sealed before canonical freeze; never silently reduce.
Callers pause at every distinct callee entry/return site, with pre/post state
and explicit completion callback comparison. Leaves have entry pause/direct done.
Compare full memory/all registers/ordered IO/listener/site observations, frame/
call state, result/error class+message, and resumption. No expected-failure credit
for normal cases. Required branch/site counters must be positive.

Root branches: marked/unmarked, all ten loop slots, unavailable/available,
within/outside, overwriting last selection, missing/stale mark clearing, mismatch,
unavailable selected, keeper early return, no skill difference and repeated skill
difference, zero and signed/wrapped draw/direction; all 12 return sites and every
write listed above. Zone: state9/non9, X pass/fail, Y pass/fail, both directions,
signed byte edges, linear record crossings, repeated arg/frame SS reads and
mutations across direction suspension. Holder: slots0/11/12/255, AH preserved.
Half: negative/zero/positive products, half sign/left compare, both sides, signed
byte edges/wrapped subfields/stack/aliases. Random: n0/1/2/5/32767/32768/65535,
seeds0/1/FFFF and wrap/high=0/nonzero, DF clear/set, pending stack alias seed,
seed/pointer/flags mutations at069F, full output/dirty order/untouched registers.

Individually reached errors: every new body entry, every caller's callee entry
and return site, each immediate write site, pending-stack flush, and relevant
SS/AX/EFLAGS register-tap refusal. For each failure selector run160 deterministic
inputs with observers enabled; require at least one reached failure and full
Python/native equality for every input, including those not reaching the selector.
Unexpected failure is an error, never success. Seal concrete selectors before
canonical freeze after preflight demonstrates reachability.

Controls: scoped body/dead-stack corruption for each new body; guest-return
corruption for both callers (each site individually reached). Leaves also corrupt
full-output/flag/stack results rather than rely on return AL alone. Mutant IDs26+
are reserved for T17; do not change prior23-body control IDs. Require positive
control detection on reached paths; no credit for unreached mutation selectors.

Actual integrated root: eight captured roots plus500 authored inputs, four
observer modes; actual new/existing callees, never ABI doubles. Supplementary
controlled ABI callers exercise hostile captured SENT versus live AX, stack and
record/frame alias cases separately. Instrument owned Python body/helper code
by actual subtree lifetime from root start to completion (including suspended
frames); any owned default Python execution fails. Instrumentation must prove
it catches intentional Python fallback and exclude unrelated shared-helper calls
outside active lifetime and nondefault variants. Remove instrumentation for timing.

Preserve all prior23-body proofs/controls; one frozen combined bundle runs public
CPython/PyPy/Rust/GC, exact ordered drive/lifecycle/ALL75/F40/profile, all three
quiet rotated four-arm timings and final closed ledger/actual-host shutdown.
Baseline and candidate/PyPy ratios are from the same rounds. No arbitrary5% floor.

## Upstream resume audit

Main cc58bd6 clean, CI41365271364 green. Archaeology main2a411f5 unchanged;
accepted oracle2cbeb36f unchanged. Goal2 advanced to f09d4a64: #497 explicitly
selects GOAL2_ENGINE_PYTHON or PyPy3.11 and raises when unavailable; no silent
CPython fallback. #511/#512/#513 adjust CI reachability/scheduling/launch tests.
These do not change T17 semantics or gates. Later integration must respect
explicit worker selection/missing-runtime reporting and verify Rust extension
ABI under the selected interpreter. T16 ledger324source+169evidence verified
before copying baseline. No build/measurement during M1 snapshot.
