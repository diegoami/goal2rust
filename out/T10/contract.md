# T10 match-key-poll state and ABI contract

Accepted2cbeb36f/state-v2; actual T09 baseline main76748f7. Translate one complete
menus.match_key_poll0791:9372 caller (near ret, no arguments). Existing keyboard,
menu, library, display, quick-mode and speaker callees remain observable delegated
ports. No transitive callee/hardware claim. Variant speed-right-increments and
all other nondefault variants stay Python. No oracle semantic fix.

## Start and loop

Regs.enter2, local16(-2,1). Six slots1..6, later slots append local16(-2,slot).
Each slot reloads game DI/ES fromDS:A923/A925, loads byteES:(DI+3F) intoAL, AH0,
DX=AX, AX=(6-DX)&FFFF, AL=int(unsignedAX>=slot), CBW, DI=AX. DX's low byte becomes
DS:(DI+882); AX=(slot+795)<<1. Reload destination DI/ES fromDS:7C26/7C28,
DI=(DI+AX)&FFFF and immediate w8(DI-2,DL) at0791:93B3. Pending saved BP/local writes
remain unflushed until the ordinary pre-call store. Live memory/pointer/aliasing
changes from every listener affect subsequent loop reads; cached routine registers
retain their source lifetime. No arithmetic flag updates from the Python operations.
Then far214B:0723 returning93C2. Source guest helper stores stack=True and returns
fresh Regs; it ignores captured SENTAX, so all phases read actual machine state.

## Key and quick-mode paths

After93C2, AL!=0 calls far214B:1E8D/93CE then far214B:08DD/93D3. LoadAL=DS:A976,
far23E4:19B2(fullAX)/93DC; fresh AL selects the key branch:

-20 ->near0791:1A04/93E3.
-AE/AF ->reload game/speed; AE andspeed<5 reload pointer andwrite speed+1 at93F9;
  AF andspeed>0 reload pointer/write speed-1 at9413. Source nondefault increment
  variant is never routed into this native caller.
-AC/B1 ->DI66A; AL0 lo=fullAX, AL4 hi=fullAX; AL=int(DS:A976==B1), CBW, DI=AX;
  AL=DS:(DI+7920), CBW; far214B:1D6F(DS,66A,lo,hi,AX)/9448 then near0691/944B.
-0D/1B ->AL1, nearED8A(fullAX)/945B.
-9F andDS:9A3E==0 ->load source ES/DI fromA96A/A96C; destination fromA972/A974,
  AX4000; far23E4:025D(source ES/DI,dest ES/DI,AX)/947D, far16D6:0945/9482,
  then fresh sourceA972/A974 anddestA96A/A96C, AX4000, samecopy/9497. Do not retain
  pointer values across these calls; return callbacks can change both pointers.
-A7 ->far214B:1E5A/94A2.
-R ->near92FC(actualBP)/94AC. Other keys have no handler call.

No key plusDS:7C38!=0 ->near92FC(actualBP)/94B9. After every branch, fresh live
DS:9A3E!=0 calls far214B:1E8D/94C5. End.leave/store returnsNone, preserving dead
stack locals, saved-BP observer effects and common frame finish.15 call sites,
12 distinct callee boundaries, no dynamic target or hidden inline callee.

## Proof and controls

Public authored cases compare full memory/registers/errors/ordered taps/listeners,
all fifteen exact return sites and ABI argument packets with controlled external
callee bodies. These boundary doubles test the caller and claim no real-callee
translation proof. Full sealed drive/lifecycle/ALL75/F40 use actual callees and
services. Eight actual RAM entry captures and500 authored inputs per new proof
arm; six immediate loop writes, aliasing/wrapping/speed changes, return actualAX,
saved-BP and copy-pointer mutations, direct done, variants and errors.10 flips the
completed caller's dead saved-BP word after its epilogue.11 corrupts caller guest
return addresses. Normal caller states agree; each control must be caught.

Full existing16-body proof/controls refreshed for the new artifact. Preserve
T09 baseline and all failures, seal source/binary/input/evidence and empty groups.
Three quiet four-arm rotated timing rounds with every result reported; no5% floor.

## External boundary clarification

Registry audit finds10 registered callees and2 unregistered external guest targets,
0791:1A04 and16D6:0945. Test-only near-ret/far-ret ABI entries allow the complete
caller continuation to be compared. They implement no claimed callee behavior and
are never registered in production. Public tests separately remove the doubles and
compare the original refusal at both unknown targets. Do not infer new Match hooks
or admitted keyboard paths from the authored caller test matrix. Existing accepted
full-match policies and actual callee/service behavior remain unchanged.
