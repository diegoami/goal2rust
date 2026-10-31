# T06 effective skill contract

Oracle e0270981883f02ce46a31391e7070079977bbfef, unchanged from T05.
Live main0c3a698f and CI green, archaeology b11171f7 unchanged. Goal2 now
696edb07: T150-T152 sealed-engine adoption plan, plus a goal2-only table-policy
exception; no accepted oracle routine changed. Do not import that exception here.

## Caller 0791:278A, retf6

args3 uses one SS read and three contiguous word reads. Enter10-byte Regs
frame. Read record+13 player index; unsigned MUL20, preserving AX/DX. Read
player far pointer as two u16 reads; wrap offset addition. Locals -10/-8 retain
pointer. Signed form byte >=32 gives base0, else CBW(form)+1; local-4=base.
For element>=12 add32, else add signed energy, mask16. Store local-4 again,
ES/DI=original record and stack registers. One yielded far call3A06 with pushes
(player index,element), returning0791:27EB, callee pops4.

Unlike T05, Python locals off/seg/element/base survive the call independently
of guest memory. Retain these scalars in explicit Rust continuation fields;
do not re-read arguments or local-4 after callbacks. Resume's skill value is
AX sent by the dispatcher, not a later register read. Pass that existing sent
value through native-step logic; callbacks can change AX after its capture.

Fresh resumed Regs. local-6=skill; ES/DI=original record. Nonzero record+19
halves skill (except nondefault skill-no-halving, which stays Python), with
CX2, DX remainder, AX quotient and another local-6 write. CX4/BX skill/4,
DX remainder; AX=retained base, unsigned MUL skill. Discard high DX, divide
low AX by256 with CX256, add BX, local-4=newbase.

DI=element; DS:769+element controls extra. If false and element1, read DS:8327
and emulate upstream's inline membership operation: five pending pushes
(AX,CS791,276A,CS791,2841), then restore SP; read bit of the supplied 32-byte
set CS791:276A. Retain BX, CL, AL and ES/DI effects. This is already inline
upstream, not a yielded guest call; no hidden new guest entry. Extra adds
record+17 (AH cleared). Manager share applies only slot+6<12 and DS:80FC!=0:
add base/16 with CX16/DX remainder. Every addition masks16. AX/base and
local-2 retain final result; leave/store, procedure returnNone.

## Leaf 1771:3A06, retf4

Two mem.arg calls, hence two separate SS reads. Mem.enter10 performs immediate
saved-BP write at3A06 and actual SP/BP/SP sets, not Regs deferred writes.
Read DS:A91B far pointer (two u16 reads), multiply player index20 and wrap
record offset. Frame pointer words written separately at3A1A/3A1D; scale=byte4+1
written at3A2C. DS:6D25[12*byte7+element] selects DS:6DCD[12*byte5+value].
Frame local-4 written at3A66; low16 product(scale*tablebyte)/32 written at3A76.
Set DX remainder and return quotient; common finish restores frame and AX/retf4.
Frame writes retain distinct instruction sites and SS reads; no coalescing.
Nondefault skill-divisor-31 stays on Python bridge.

## Observability and controls

Full state/taps at entry, callee and return; direct leaf bodies and full frames;
SP wrapping, nonzero dead bytes, signed form/energy boundaries, element11/12
andFFFF, pointer/table wrap, scale1/256, halving, bit-set/member branches,
manager slot11/12, and overflow. Callbacks mutate caller arguments/local-4
while waiting and mutate AX after dispatch captures its sent value. Retained
scalars and sent AX must remain faithful. Preserve error/stop/replay/done behavior.
Body control5 corrupts leaf's final dead local word; root-return control6 changes
only saved27EB IP. No weakened guards or hidden inlining. Full task gates in T06.md.
