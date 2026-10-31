# T05 nearest-to-ball tree contract

Oracle e0270981883f02ce46a31391e7070079977bbfef, unchanged from T04.
Live heads rechecked: goal2rust 0eacd69d (main CI green), archaeology b11171f7,
goal2 4ef98298. Dependencies have not advanced since T04's upstream audit.
Preserve all completed T04 receipts/binaries. Profile selection is in T05.md.

## Root and guest closure

`ball.find_nearest_to_ball`, 0791:2FB1, near `ret`, no arguments, procedure
return None. Literal calls only: 0791:2956 at return 3013; 0791:2BE5 at 3090
and 30A3 (all far, two words pushed segment then offset, callee pops four).
2956 itself calls 1771:3216, already native. No dynamic guest target.
Inline helpers: local8/local16 flush pending writes then read wrapped SS:BP+off;
load_local_pitch assigns DI before ES, each through local16; cbw, unsigned
mul and signed imul alter AX/DX only, not flags. Every read/set order matters.

Enter 14-byte frame; local byte -1 starts side 0. Per side clear DS:8311+side
at 2FC6 and DS:830F+side at 2FD1, best distances -5/-7 =100, relative slot
-3 starts2. Loop slots2..11 inclusive, then side1; loop values are read back
from memory (callbacks may change them), never retained as hidden Rust counters.

Compute pitch pointer DS:(80E8 + 22*(DS:668[side]+relative_slot)), arithmetic
masked at each register assignment. Locals -D/-B hold offset/DS segment;
all stack writes remain pending/coalesced exactly as Regs does. Store stack
registers before each guest call. At each return create fresh resumed Regs;
no cached state may survive a call. The complete loop remains a resumable Rust
continuation, using the existing guest issue/return machinery.

At 3013, AL !=0 skips the player. Otherwise compare byte slot+6 against
DS:830B, then record+12 against0D. For eligible players compute unsigned
Manhattan sum from signed-byte ball/player coordinates (CBW, wrapped 16-bit
subtraction/negation). A strictly smaller distance replaces nearest slot at
DS:8311+side (307D); ties retain the prior winner. Read locals in source order.

First direction call returns3090: CBW AX, copy to DX; CBW ball Y, signed IMUL
by DX, push low AX live across the second direction call. Store stack and
call2BE5, returning30A3. CBW AX/DX, CBW player Y and signed IMUL; read pop DX
through ss_lin(SP), then SP+=2. Signed AX<DX admits a strictly closer goal-side
candidate, writing DS:830F+side at30CA. Keep every AH/DX intermediate effect,
the pushed live word, dead bytes and exact flush/listener order. Finish loop,
leave/store; common finish restores entry SP/BP and performs near ret.

## Observability and tests

Continuation phases: initial loop; after availability3013; after first direction
3090; after second direction30A3. Fields retained across yields are only phase;
all original live values reside in guest memory/stack. Callee variants and root
nondefault variants remain bridge paths. Keep sites, snapshots, taps, errors,
suspension/replay, done callbacks and repeated returns at the same addresses.

Authored states cover signed byte extrema, zero/nonzero energy/flags, slot/status
exclusion, zero/large/negative coordinate distances, strict ties, unsigned mul
wrapping, signed IMUL, both sides/direction signs, live stack word across calls,
SP wrap and nonzero dead bytes. Observe full state at each call/return boundary
and final completion. Real captures stay in RAM; receipts hold hashes/counts.
Body control starts side1 (skips side0); caller-return control corrupts only this
root's saved return IP, allowing native 2956/3216 to finish correctly first.
No hidden inlining or raised guards. Full sealed drive/F40/lifecycle, paired
CPU, exact hashes and a post-writer ledger precede acceptance.
