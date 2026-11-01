# T14 player-update caller contract

Accepted2cbeb36f/private state-v2, actual T13 baselinefd2d515. One complete
motion.update_player0791:8AE9(retf4),11 finite state HANDLERS+5 fixed calls,
16 registered boundaries/returns; all delegated/observable, no callee/hardware
claim. Default only, variants sourcePython.

## Immediate prologue and captured addresses

Mem.enter6 exact: readSP-2mask, readSS forwrite address, readBP, savedBP write8AE9,
setSP/BP/SP-6. Capture fr.bp. record() does ONE frame.lin(BP+6) currentSS read,
farptr offset atthatlinear andsegment atlinear+2, no second offset wrap/SS read.
Capture off/seg/LINEARrec=addr(seg,off). Every rec+k field is UNWRAPPED linear.
Readindexword rec+D, unsigned*14 ->localaxlow/dxhigh. DS:A91B farptrone base,
code=addr(pseg,poff+axlow) wraps baseoffset only; captureLINEARcode across calls.
Readstatebyte rec+12, setAX(lo(localax,state))/DX(high). Dispatch capturedstate
through11-row map (not a reread after set_reg callbacks), far(seg,off)11 returns.
Then near8889(captured fr.bp)/8BB7 evenifactualBP orrootargwords change.

## Counter, possession and captured replies

Afterrun reply IGNORED. localax=int(recbyteF<5) beforecounterwrite. Readcounter
rec+14, writecounter+localax masked at8BCC; do NOT setmachineAX yet. Read8302;
ifnonzero localax=recbyte6. Read8302 AGAIN, thenrecbyte6==DS:830D. Iftrue,
setmachineAX(localax), far2CEC(seg,off)/8BED. Source explicitly assigns localax
from yield's CAPTUREDSENT, unlike Regs guest helper. Ignore actualAX clobbers
AFTER dispatcher captures it (test io_tap atgetAX thenSP setter).
Ifcapturedax low!=0 andlive recstate!=0C, capturekept=DS:8303, writeDS830C from
live830D/8C04. localax=lo(capturedax,DS830B), then reread830B/830D/live8303;
ifB!=D andliveflag0, localax=lo(ax,19), setmachineAX, near2AD4(ax)/8C1D,
assign capturedSENT tolocalax. SetmachineAX(localax), far869F(seg,off)/8C26,
assign capturedSENT, writeoriginalkept back8303/8C29, localax=lo(sent,kept).
Everypath setmachineAX(localax) and far8537(seg,off)/8C35. Its reply IGNORED.
Skip-possession paths still distinguish localax0/1 versus recslot and captured
callee replies. Conditional/repeated reads and callback-before-commit stay ordered.

## Fatigue/value

AfterSprite read8325; ifnonzero readcounter> B4, then signedbyte(code+E)>1:
iftrue reread code+E, writebyte-1/8C54; alwayscounter0/8C5D, returninteger0.
Otherwise returnNone, no register read/assignment afterSprite; leave its AX/DX.
Onlycommon runner restores SP/BP/retf4, no extra Regs epilogue. Capturedrec/code/
frameBP/kept survivearg/globalptr/actualBP/flag mutations, their contents staylive.

## Proof and controls

Registered controlled callee ABI bodies cover all16 dispatch returns/targets,
unknown state/nohandler,6 write sites, counterwrap, possession/comment/take/skip,
signed-energy/no-decrement/decrement, value0/None. Positive success required;
8 real RAM captures/500 authored/four tap-listener modes, full memory/all regs/
ordered observers/errors/full waiting metadata/direct done/pause/variants.
Actual admitted full drive/lifecycle/family uses actual callees. Test continuous
farptr atSSboundary, unwrapped rec/code subfields crossing64K, captured pointers/
state/BP/kept versus live contents and AXreply clobbers after capture.
Body20 flips completed dead savedBP; return21 corrupts caller returns, both caught
allpositive cases. Freeze all .py/Rust/tests/binaries/inputs during run; preserve
allhistorical receipts. Full existing20-body/control/observer/ordered/lifecycle/
ALL75/F40/profile/artifact closure and3 quiet rotated four-arm outcomes; no5% floor.
