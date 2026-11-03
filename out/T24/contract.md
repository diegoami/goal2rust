# T24 Source keyboard and frame contract

All four entries retf;only0993 pops2. None is long=True. Poll0723 has no frame.
_ret_site reads the entry SP,then live SS at(sp+2)&FFFF and the return CS word;
only then observes the memory view's machine load. Format relative CS masked16
as four uppercase hex digits. Then read SS AGAIN at sp&FFFF and the return IP;
never merge/capture the two SS reads. The current kit memory view and callbacks
belong to the port,not a fresh view. Fixed loaded-image identity remains valid.

0723 calls mem.keypressed(site),whose kit primitive coerces provider truth.
After it returns,read LIVE AX,keep AH,set AL to int(has). Do not cache AH before
callback or manufacture a BIOS enter/leave. Provider/no-kit/truth errors propagate
before AX is written. Poll has no additional stop check beyond the source API.

08DD reads DS:79AE first. Nonzero:Regs.enter14h queued frame,immediately clear
79AE at08EA before reading live DS:A976. Set cached AL preserving source AH,
write AL toA977 at097C,leave/store,no kit read. Zero:compute_ret_site then
call the original mem.read_key(site) semantic primitive,including its key writes
and _check_stop(None/events allowed;other stops refused). Ignore its returned
value;returnNone/preserve registers left by the callback. No invented frame.

0993:Regs.enter0 queued pushBP. Immediately setDS:79AE=1 at0996,THEN ss8 flushes
that queued prologue. Read current BP+6 through cached/live source rules and
live SS,only the argument low byte. Cache AL preserving AH,writeA976 at099E,
leave/store. Do not flush the prologue before the flag write or invent A977.

0983:Regs.enter0,store(stack=True)/flush before real far guest08DD at098A.
Resume with fresh Regs(resumed=True),ignore SENT. ClearA976 at098A first,then
leave using the live BP/SS and source frame word,store,returnNone. Preserve the
real request/return,pending words,argument absence and pause/replay. Mutations
at the return can distinguish live actual AX/BP/SS from captured send values.

Controls185..188 sorted0723/08DD/0983/0993;AX189..192 respective roots;
EFLAGS193..196 respective roots;return197 only at214B:098A. Register/output
controls apply after source completion. All nine owned inventory functions are
tracked;generic Mem key/read/stop primitives remain the explicit semantic API.
