# T23 exact source contract

Accepted oracle2cbeb36f. Roots062A/0644/06B7 are plain Regs, no enter/leave or
new guest calls. All retf, not long=True; return value None.062A/06B7 read four
input words but pop4;0644 reads five and pops10. Do not infer pop from nargs.
Capture all argument bytes before any data write. Capture entry SP for BX, fixed
mem.DS for DX. CLD caches a DF-clear mask; preserve all other live EFLAGS at the
late flags store after register stores, including callback mutations.

062A and0644 read source length at linear sseg*16+soff before writing it to
linear dseg*16+doff.0644 clips by max LOW BYTE only, including max256->0.
Set AL through cached/live AX in source order, preserving AH.062A length PC0638,
copy PC063D;0644 length PC065C,copy PC0661. No flag arithmetic or added frame.

06B7 captures destination length then source length. Capture their sum and write
its wrapped low byte at06CA. If the captured sum exceeds255, write255 at06CF
and use captured complement of original destination length as copy count. Both
writes stay observable, even if callbacks mutate either string/header/registers.
Then set AL, preserving live/cached AH at THAT source point(after length writes).
Copy to doff+captured destination length+1 at06DC. Saturation is unsigned.

_copy_forward: n<=0 returns masked offsets without reads/writes. For n>8,
UNMASKED soff+n and doff+n must be<=65536 and masked-linear source/destination
ranges disjoint before read-ahead applies. Only then capture one source byte block
before the first per-byte write. A callback may change future source bytes but
that captured block remains unchanged. Otherwise each source byte is read live
immediately before its write, using separately wrapped offsets, reproducing
forward-overlap propagation. Keep every one-byte write, PC, error boundary and
listener ordering. Do not replace this branch with memmove, a universally eager
snapshot or a globally bytewise loop. Keep unmasked soff+1/doff+1 additions at
helper entry(65536 is meaningful to the no-wrap predicate).

After copying, capture SI/DI returned masked offsets, then CX=0,ES=dseg and
Regs.store insertion/set ordering. Store DF against live flags last. Callbacks
may mutate actual AX, flags, source/destination/header bytes, SS or argument
slots; preserve captured scalars and each later live read exactly.

Controls170..172 for sorted062A/0644/06B7 bodies. For each root i=0..2,
output controls173+4i AX,174+4i SI,175+4i DI,176+4i EFLAGS/DF. Zero guest-return
controls are applicable. Every output control needs its own comparison key and
positive detection. Seal case/error/branch/variant counts before canonical runs.
