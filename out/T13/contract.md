# T13 play-state caller contract

Accepted2cbeb36f/state-v2, actual T12 baseline1c20841. contests.play_state_update
0791:57AC(retf4), one complete caller;14 registered external callees remain
observable/delegated,15 returns. No arbitrary dynamic dispatch: probe target/ret
are the finite4-tuple, nearest table/return is the finite2-tuple. No callee or
hardware claim. Native only default, nearest-not-chasing/other variants Python.

## Probes and keeper

Regs.enter2; near56D9/57B6,5049/57BE,533B/57C6,5565/57CE, each args(actualBP)
evaluated BEFORE guest helper store(stackTrue). After every call fresh Regs,
ignore capturedSENT; actualAL!=0 ->leave/store None immediately. After4 zeros,
AL=DS:830B/AH0, near045D(fullAX)/57DE. ActualAL!=0 andlive8302==0 ->own, far4B64/
57F2 thenend. Source own always reloads live far arguments via current freshBP:
ss16(BP+8) then ss16(BP+6), each flushes pending stack/reads actualSS, assign ES
thenDI. Do NOT capture original entry pointers or originalBP across guest calls.

## Tri-state destination and candidates

Initial choiceNone. IfDS:8327==5 andDS:8300>0: AX=ballword82F6, own, immediate
wordwriteES:(DI+7)/5809, choiceFalse ->skip marking-destination call, go move.
Elseif8325 nonzero: candidateTrue. If830C nonzero, own/far2BB1/582A. ActualAL!=2
thenown/player_record: AX=recordword+D, DX14, unsignedMUL16(no flag update),
DI/ES fromDS:A91B/A91D, DI+=AX; candidate=(playerbyte+6==1). False ->choiceNone.
CandidateTrue and8302==0 ->own/far2B51/5857, candidate=(actualAL==0).
IfcandidateTrue ->near5729(actualBP)/585F. ActualAL!=0 ->choiceTrue.
Otherwise first table8311: own/far2974/586C, fresh CBW(actualAL), DIAX,
AL=DS:(DI+table)&FFFF, ownagain, compareAL withrecordbyte6. Match ->choiceTrue.
Else repeat table830F/5885. Ifneither matches andlive830C==0, readpoint82F6 BEFORE
own, far44C1(point,seg,off)/58A9; actualAL!=0 ->choiceTrue, elseNone.

True: AX=liveballword, own, wordwrite+7/58B3, skip marking call. None: own/far4A28/
58C2, preserving its returned destination. False: special5809 already wrote it;
this is NOT None. Thenall paths own/far474D/58CB; iflive8302 nonzero, own/far6188/
58DB; leave/store None. Preserve highAH in table/AL paths, signed CBW index,
all real-pointer reloads/captured argument evaluation ordering, stack and flags.

## Proof and controls

Controlled registered ABI bodies cover every caller branch/target/return/write;
full admitted drive/lifecycle/family use actual bodies. Positive success mandatory,
eight real RAM captures/500 authored cases/four tap-listener modes, all5 early
exits/three destination choices, static links/liveBP/argument/table/ball/play/actual
AX changes, wrap/dead stack/near-far/full waiting metadata, pause/direct done/
errors/variants. Body18 flips completed dead savedBP; return19 corrupts caller
return addresses. Every completed caller makes at least one probe call, so both
controls differ in all positive cases. Preserve all artifacts/receipts, freeze
all .py/Rust/tests/binaries before bound runs. Full previous19-body/new proof,
ordered/sealed lifecycle/ALL75/F40/profile/artifact closure and3 quiet rotated
four-arm measured outcomes, no5% minimum, exact-head CI before squash.
