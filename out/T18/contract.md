# T18 source and proof contract

Accepted oracle2cbeb36f. inventory-v1.json binds registry-selected functions,
ABIs/pop/long behavior, full helper symbols, inline invokes and41 expanded guest
sites. Native boundaries include the accepted T17 subtree; no default remaining
Python guest target is excluded. Finite conditional returns in4354 (4392/43BC)
and4B64 (4C6D/4CCA) are separate sites. Direct registry entry remains valid for
every body. Positioning/geometry/runtime variants all use source Python.

## Captured/live state and helpers

Positioning common helpers: argptr repeats arg1,arg0 then arg1,arg0, each through
independent entry SS reads. mem.addr wraps the initial base; r8/r16/w8/w16 then
add subfields linearly. mem.enter is immediate, with SP/SS/BP access/write order;
Frame accesses reread live SS independently. guest consumes captured SENT AX;
explicit mem.reg accesses read live registers. push_word writes the real word
before setting SP; pop_ax/pop_dx read actual SS:SP and set SP then the register.
drop_words adjusts actual SP before Call rewrites the pre-pushed argument words.

42CB enters6, captures index/player address and pos, then separately rereads
players offset/segment for local -6/-4. Position remains captured across tactic/
side calls. Group table is read live after them, local -2 is written, and captured
group returned; do not reread the local on return or the player pos after a call.
Pos0, <=4/>4, <=11/>11, tactic false/true and both side flags must be reached.

4354 enters0. Captured pos selects pos0/pos13-state!=9/pos13-state9/other draws,
with ret43A7/4392/43BC and writes43AD/4398/43C2. Rng args15/5 also set actual AX.
Read live depth after the draw; int(s8(y)/2) truncates toward zero. Each later
write observes fresh source reads in order (offsetB, then8, then7); mirror receives
the freshly read word and final7 write uses captured SENT. Return None.

4A28 enters8, captures player id and linear player record, then separately rereads
pointer words into -8/-6. Keep that record across all suspensions. On own side,
energy gate/position1/ahead10 decide post. Opposite side calls post first, then
live keeper/ball/play checks. Keeper area/tactic/advanced-strip branches preserve
captured area across calls. Marking47C5 receives this frame's BP; it writes parent
-4 slot and -2 position, including overlapping -1 Y. Later short circuit uses
live -4 and globals; signed energy versus s16 draw, tactic and direction gate the
live local -2 copy. Actual AX/DX are not guessed from captured SENT. Return None;
marking-no-copy stays Python. Every early return and final copy must be positive.

4B64 enters0 and captures p/seg/off. Keeper argument byte is read twice, once for
args then AX. State11 direction uses captured SENT but live ball Y. Membership
builds AX from captured player id high/position low, pushes exact args/AX, ignores
SENT and reads LIVE EFLAGS.ZF. All three draw-table branches set depth with source
signed bytes/word draw. Non-special side flag remains captured across group call
and picks4C6D/4CCA; group and tactic6-derived words stay live on real stack.
Own branch pre-pushes0/20, then group; pops actual AX, reads table, drops two words
before long max call. Other branch pushes group, then captured t6-derived word;
after t5 pops actual AX twice, but uses CAPTURED t6/t5 plus popped group for table.
It pre-pushes seg/off+C/zero across long min, drops3 before byte clamp. Preserve
full-word low results and returned DX/ES/flags even where caller uses AX only.
Both paths finish with actual4A28. No condition or read is prefetched across a
source write/call. Return None; membership/table/random/min/max/clamp branches,
pre-pushed word aliases and live ZF versus SENT all need positive cases.

40BC uses Regs: enter6, compute/capture holder offset/DS, queue locals -5/-3,
store(stack=True), actual2C54 at40E1. Resume with NEW Regs(resumed=True), reading
live AX. If AL0, store stack and call2996 at40E8; resume fresh cache again. Keep
captured off/seg across calls. Absolute-y/marker/35/x4 gates short circuit; repeated
record reads remain live. Queue bool -1, then ball.local8 FLUSHES and reads live
BP/SS; leave/store preserves callback-mutated locals and partial AX. Do not return
a cached bool or use captured frame BP in place of the resumed Regs reads.

Geometry helpers retain Regs cached reads/dirty order/queued coalesced writes,
wrapped rec fields, cbw/cwd/mul/imul and geometry.c2be5/c2974 (no invented flag
updates). Existing registered entrypoints.direction differs from that inline
helper and cannot replace it. 261A captures index, reads wrapped table byte,
queues local word, writes next index1 onFF else di+1, leaves/stores.

2C86 captures three args plus entry SP; immediate argument-byte writes2C9E/2CB3
use fresh actual SS and captured word bytes. The two inline directions reread
live globals/record each time. Do not flush queued Regs writes earlier, reread
modified argument bytes, or merge the two directions. Final AX/local word is y:x.

2D10/2D6D use two inline directions and exact16-bit signed products/CWD followed
by32-bit high-signed/low-unsigned comparisons with unsigned n. Captured saved
high/low words are queued as real pushes but restored from Python scalars,
not reread from the stack. SP +=4 is cached Regs. Ahead-inclusive remains Python.
2E36 sign/absolute-y>=33/absolute-x<=2 preserve partial AH, wrapped fields and
short-circuit reads, with no invented CMP flags.

2B7B player_byte wraps record field offsets, captures player far pointer and
signed energy; n=(33-energy)&FFFF. INLINE runtime.draw_is_one/rng_0688/pilot.rand
are distinct from registered entrypoints.random_n: queue exact fake far stack,
read seed pointer again in pilot.rand, step/write069F immediately, keep captured
new/n, update AX/DX and AL bool, preserve other registers and arithmetic/DF flags.
No use of T17's flag/DF-changing rng_core and no logical0688/06D0 guest frames.

Runtime min/max capture four full argument words and use signed high/unsigned
low comparison. Min ties choose a and flags unchanged; max ties choose b and
sets last CMP flags (low if highs equal, else raw high). Enter4, queue local
low/high, assign AX/DX/ES, leave/store, return None despite long=True. Clamp2031
enters0, captures args; lower-bound write2045 then REREAD actual target byte
before upper2059. Low/high comparisons use signed bytes; low/hi args stay
captured. Set AL late, preserving live initial AH at its first read; no invented
flags. Parameter/target/frame/AX mutation callbacks must be exercised.

Membership08DF has NO prologue/frame or guest call. Capture args, mask elementFF,
set DI/ES/BX, preserve CX high while setting CL, replace AL with bitmask preserving
AH, read wrapped target byte and set TEST arithmetic flags. Return None.

## Proof obligations sealed before runs

Minimum per body:8 actual source-entry captures,4 observer modes,3 schedules
(normal/entry or suspension pause/direct completion)=96 real comparisons;
500 deterministic authored random/edge inputs x4 modes=2000. Total31,440 across15.
Each of5 callers adds500 x4 controlled ABI cases (10,000), supplementing actual
integrated real-callee root/subtree proofs. Require full memory/all registers,
ordered IO/site/listeners, results/None distinctions, frames and error text/state.
No unexpected-error credit. Every semantic branch/site must have positive traces.

Scoped body controls49..63 (sorted new addresses);10 leaf full-output/flag
controls64..73;41 individual guest-return controls74..114 in inventory return-site
order. Every reached mutation differs; unreached paths stay equal. Keep all prior
28-body controls. Fix concrete reached error selectors/extra alias/branch counts
before canonical freeze; each error selector uses160 authored inputs with positive
reachability. Include direct completion, variants and suspension replay.

Own default Python body/helper code is forbidden during actual integrated root
lifetimes, including waiting frames. Prove detector positives using Python/default
fallback/variants, and exclusions for outside shared helpers. Instrumentation is
proof-only. Native counters are complementary evidence, not closure proof alone.

One frozen combined artifact runs complete prior28/new proofs, public CPython/
PyPy/Rust/GC, old observer matrices, ordered drive/lifecycle, strict ALL75/F40,
profile and three quiet paired four-arm timings. No dropped historical fidelity
gate, arbitrary5% translation floor, output-as-input matcher or ignored rejection.
All completed/rejected receipts remain immutable and every producer is closed in
the actual host namespace before final validation/CI/squash/mainCI/checkpoint.

## Upstreams at start

Main ead0e94 clean/green, accepted pin2cbeb36f unchanged; archaeology main2a411f5.
Goal2 mained582f99 adds#515 (goal2 tests choose PyPy children only) and planned
T154/#516 evaluating one UI/engine boundary after playableT153. That evaluation
considers a persistent PyPy pipe and Rust as a CPython module, including API,
GIL/threading and Windows ZIP needs. T18 does not change goal2 test routing or
implement integration/GIL release. Existing Rust run/callback/Python-body work
requires its interpreter/GIL; later adoption must evaluate those capabilities
explicitly. Our declared CPython/PyPy fidelity and four-arm timing gates remain.
