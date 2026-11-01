# T11 ball draw-state caller contract

Accepted2cbeb36f/state-v2, baselineT10/main57a7688. Native caller0791:8F10(retf4),
inline display.grid_cell only. Registered membership23E4:08DF(retf6), travel
0791:835F(retf4) and nested long multiply23E4:0279(retf) remain actual source
bodies/ordinary frames. All registered/ABI-checked before authoring tests; no test
production stubs or unknown-guest handling. Source variant/nondefault stays Python.

## Entry, capture and grid arithmetic

Regs.enter0. farg atBP+6 evaluates segment SS:(BP+8) then offset SS:(BP+6), each
ss16 flushes pending stack before actualSS read; assign ES thenDI, return cached
segment/offset. Keep these two captured scalars across both guest calls even if
callbacks alter arguments, actualES/DI or memory. Every grid calculation reloads
current record bytes and DS far pointers, never caches live tables across calls.

Read previous-position word record+2; if notDS:640, reload record andprevious word,
comparecurrent word+0. If different, grid(oldcoords2,3,DS:7C16), loadAL fromcell+90E,
retain fullAX argument, DI8EF0, far23E4:08DF(arg,seg0791,DI)/return8F66.
Fresh resumed Regs; member tests actualEFLAGS.ZF, ignoring dispatcher's SENTAX.
WhenZFclear: grid(old,DS:7C1E), BX=cellword+90E, grid(old,DS:7C16), writeBXword
atcell+90E/site8FAF. Then shared tail; otherwise tail directly.

Grid helper: ES/DI=record, AL=column byte, CBW, AX<<1 masked16, CXAX. Resetrecord,
AL=row byte, CBW, DXA0, unsigned MUL16 (readDX argument beforeAX), AXlow/DXhigh,
no arithmetic-flag update. Read DS:pointer offsetthen segment, assign DIthenES,
DI=(DI+AX+CX)&FFFF. This is signed-byte coordinates with unsigned word multiply;
negative rows leave nonzero highDX. Do not replace it with signed IMUL or dropDX.

## Tail, travel, glyph and current occupancy

Resetrecord, AX=current word+0, writeAX torecord+2/site8FBD. Then readrecord+D.
Ifnonzero, far0791:835F(capturedseg,capturedoff)/return8FD4; fresh resumed Regs,
high=(actualAX>2), not cachedSENT. Withouttravel highFalse using currentRegs.
AL=int(high), CBW, DIAX, AL=DS:(DI+880), resetrecord, writeAL byte+4/site8FE9.
Readcurrent word+0 afterthat write/listeners, compareDS:640. Ifdifferent:
grid(current0,1,DS:7C1E), BX=cellword90E; grid(current,DS:7C16), AX=cellword90E;
ifequal AX/BX, resetrecord, BX=recordword+4, grid(current,DS:7C16), writeBXword
atcell+90E/site906E. leave/store None, common retf4. Preserve all dead stack bytes,
register read/store order, flags, full-width writes and listener-before-commit.

## Observation and controls

Public/proof matrices use REAL delegated callee bodies(including nested multiply),
assert positive success and explicit both-target/both-return/four-write-site
coverage. Eight actual RAM captures plus500 authored cases, signed coordinate
extremes, sentinel skips, grid/record aliases and wrapping, pointer changes at
previous-position write, record changes atglyph write, argument and savedBP
changes atreturns, actual ZF/AX changes, direct done, pauses, errors and variants.
Body12 flips completed caller's dead savedBP word, so every completed case differs.
Return13 corrupts only8F66/8FD4 calls: cases with guest calls differ, no-call cases
must remain equal. Preserve every attempted source/build/report and invalid binding;
freeze all .py/Rust/test/binaries during each producer epoch. Full old17-body
regression/ordered/lifecycle/ALL75/F40/profile/artifact proof then three quiet
rotated four-arm timing rounds, every result retained/reported, no5% floor.
