# T04 first native caller/callee tree

Oracle: e0270981883f02ce46a31391e7070079977bbfef (T03 accepted sealed
boundary). Live upstream main b11171f70ee8f4a24b2ed7e389efd5bc2cc6fb90
was inspected at resume: later changes fix extraction manifest, checkpoint
serialized tables, diagnostics and CI/review policy. Geometry, attributes,
runtime, guest and engine bodies have no intervening change. Retain the T03
pin for translation; later checkpoint-table adoption needs its own refreshed
compatibility evidence. Existing explicit tables-after-load remains required.

## Caller 0791:2956, geometry.player_unavailable_on_pitch, retf 4

Read two arguments via runtime.args (one ss_lin read, two contiguous u16
reads). Regs.enter(2) caches entry SP, pushes BP, reserves two bytes. Assign
ES/DI to the record segment/offset, flush/store with stack=True. Only then
read the player word at segment:((offset+13)&65535). One literal far guest
call to 1771:3216; one argument, return 0791:2968, callee pops it. No dynamic
callee. Resume with fresh Regs(resumed=True), not the old cached registers;
read AL, write local byte BP-1, leave (including stack read), flush/store.
No value returned. Preserve issue's separate argument/CS/IP writes and frame
waiting metadata. Pause at callee entry or return site leaves the caller
waiting; resumption runs the same dispatcher path. Match save reconstructs
continuations by replay rather than serializing Rust frames.

## Callee 1771:3216, attributes.player_unavailable, retf 2

Read current SP and BP, argument via ss_lin(SP+4), multiply player word by
20 (AX low, DX high). Read DS:A91B's four-byte pointer; wrap offset addition
and energy/flag offsets independently. Signed energy <1 takes early path;
AX retains multiply AH and sets AL=1, DX retains multiply high word. Positive
energy reads flags and tests bit 7, then 5, then 2, short circuiting. Return
AX=bit (AH=0), DX=last tested shift (7/5/2). Variant unavailable-bit-6 tests
bit 4 in place of bit 5; every nondefault variant stays on the Python bridge.

Read exactly 20 contiguous bytes beginning at ss_lin(SP-20), retaining all
unwritten bytes. Push-BP, offset, segment, result populate the same byte spans
as Python. Early path writes only base+12..base+19; positive path writes all
20, including only the final inline bit-test frame/argument/return bytes.
These are inline operations upstream; no yielded call or hidden dynamic
callee. One write at 1771:3285 invokes listeners before committing bytes.
Set DX before returning value; common finish sets SP/BP/AX and retf 2.
Do not overwrite ES/DI or flags: the optimized Python body does not.

## Observability and controls

Actual guest entries and native entries remain separately counted. Caller
continuation is explicit Rust state; unported generators remain Python objects.
The existing guest Call metadata may be shared without running a Python
routine or generator. Use the same issue/return machinery, sites, pending
errors, listeners, IO tap order, suspended frames and done callback semantics.

Synthetic differentials cover whole memory and all register banks, stack
wrap, signed boundaries, multiply overflow/AH, flag short circuits, wrapped
record/player offsets, listener errors, site errors, tap modes, callee/return
pauses and nondefault variant fallback. Public native-count assertions fail
on the baseline; Python-vs-bridge state equality already passes. The first
test-helper attempt incorrectly tried passing done through a registered runner
subclass (the Rust registry stores its metadata); preserve that failed log,
then test the actual registration API. Direct done callbacks need a separate
start-path test. Private capture/body/full-frame, ordered drives, family,
lifecycle and paired timing gates remain required as specified in roadmap.
