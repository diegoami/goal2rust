# T12 watched sweep contract

Accepted2cbeb36f/state-v2, actual T11 baseline31d741a. Native0791:9564(near ret,
no args), one complete caller. frame.SITES has17 literal rows/14 registered
callees with checked ABI; all stay observable delegated boundaries. Nondefault
possession-swapped and other variants stay Python. No hardware/transitive claim.

## Immediate frame and captured locals

Match Mem.enter8 exactly: readSP, subtract2/mask, readSS forwrite address, readBP,
immediate saved-BP write at9564, then setSP/BP/SP-8. Capture fr.bp after enter,
DS/seg0791 and Python-local slot=1, immediate local[-2]=1/site956A. No Regs cache
or deferred stack coalescing. Each fr.read/write uses capturedBP but currentSS.
slot/k/rec are captured scalars; callbacks can mutate actualBP/local record words
without replacing them. In contrast, outer stop reads actual fr[-2] each pass.

For each slot: live DS:8302 gates play logic. Ifactive, setAX(slot), immediate
push belowSP at9581 (setSP beforeSS read/write). DS:8303!=0 ->AL=DS:8327,
DI9544, SITES9592 membership. Its actualZF selects flag (not capturedSENT).
Set_product(flag,22) writes AX/DX with no flag update, popSP+2, setAXslot,
read gateDS:(flag22+slot+899), setAXgate; gate<=DS:8300 enables ball/holder work.
IfballY!=0 call direction95C6, actualAL becomesDL; signedY selects direction-table
entry, compare andincrement DS:80F6+2*same at95EE; preserve default variant.
Move-ball95F8, nearest95FB, holder-side95FE; actualAL yields side, setAL again
with freshAX read preservingAH, held=DS:(668+side)+1, product*22, rec+80E8.
Write capturedrec/local[-8]9620 andDS/local[-6]9623, setAL8327/DI9544,
membership962F. IfactualZF clear, at-ball963C; ifAL0 andrec.x==ball.x,
direction9659 actualAL controls holder update9666; unequal x updates directly.
Then play-check9669. ActualAL0 writes local[-4]=1/site9670, k=1; each of22
inner players reads live8302, optionally product/call9692, then capturedk increments
andlocal[-4] at9677. No reread oflocal[-4] or capturedrec as Python locals.

## Always-run player and termination

Read DS:(883+slot), setAX, read it AGAIN (set_reg observers may change data),
set_product(*22), capturedrec+80E8, local[-8]/[-6] at96AF/96B2. Availability96BB;
actualAL0 ->update96C8. Live player-table ==live holder830B ->nearest96D8.
Speaker96DB, setDI82F6, draw96E4, keypoll96E7. Live QUICK9A3E nonzero returnsNone
immediately. Otherwise readactual fr[-2]; !=22 increments capturedslot, writes
local[-2]/9571 andloops. At22 readwait832A; nonzero writeswait-2 masked16 at9703
(including1->FFFF), returnNone. Common runner alone restores SP/BP/near-return;
there is no extra Regs epilogue. Preserve every intermediate read/write/flag/ABI.

## Proof

Controlled test-only external ABI bodies allow every branch/17 return/14 target/
12 write sites and both22-iteration loops to complete. Actual admitted drive/
lifecycle/family uses real callees. FrameBP/record/slot/play-state/actualAX/ZF
mutations, dead extra push, static locals, sentinel waits/underflow, SP wraps,
near/far args and full waiting metadata, pause/replay/direct done/errors/variants.
Positive success and explicit site/loop coverage are mandatory. Initial fixture
missed9703 because all full sweeps hadwait0; retained initial harness/log, revised
wait1 underflow gives coverage before source freeze. No runtime fix required.
Body16 flips completed caller's dead saved-BP word; return17 corrupts caller
return addresses. Every completed caller has guest calls, both controls caught.
Full old18-body proof/control/observer/ordered/lifecycle/ALL75/F40/profile/artifact
closure, then3 quiet rotated four-arm measurements, retain/report all, no5% floor.
