# T09 selection, ABI and state contract

Accepted2cbeb36f/state-v2, baseline15fadea13/T08 unchanged. Residual Python
register/frame costs motivated an isolated Rust property-descriptor prototype.
Measured cached get66.25ns ->59.21ns, set90.89ns ->105.32ns, byte-half201.15ns
->227.85ns: rejected before enabling any factory. Its source, binary and data
are preserved; current production has no descriptor/register-factory hook.

Select the optimized profile's speaker/noise-state tree:94E8 starts76,847,
94C9/0688 each32,727,1E8D63,498 =205,799 remaining Python entries. All literal
calls only, no dynamic target. Four data-state bodies plus the source's existing
omitted hardware boundaries1EBC(retf2)/0425(ret2), still delegated visible ABI
stubs. No hardware code, callback, guest entry or RNG call is removed.

## Phases and data

Noise94E8 near ret/no args: enter0. If DS:832A>0, AX50 then near94C9, return94F9;
else far off1E8D, return9532. Fresh resumed Regs. CWD AX, CX=AX/BX=DX, AX=level
DX0. Signed high-word comparison then unsigned low-word comparison determines
larger. Larger and game-pointer+3F>0 selects tone; AX=level+300 (mask16), near94C9
return9522. Fresh AX+=100 (mask16), far tone stub1EBC return952B. Tone=True is
encoded by continuation phase and survives later game-speed mutations. No tone
calls far off1E8D. Both branches reload game DI then ES, AL=speed/AH0, call near
delay stub0425 with AX, return9540, then leave/store. Procedure valueNone.

Seed94C9 near ret2: enter2, DI8336 (nondefault adjacent variant stays Python).
ss16 evaluates BP+4, flushes pending writes, reads N through SS; DS,DI,N are pushed
as source guest arguments to far0688, return94DC. Resumed local-2=actual AX;
leave/store; return cached AX AFTER store as source _end(value=True), not None.
Existing native-step completion now carries an optional value without changing
previous procedure continuations.

Explicit RNG0688 retf6: args N,offset,segment, one contiguous source read. Regs
enter2; retain SP, pending pushes DS/segment/offset. Read pointed seed, compute
(new=old*7ABD+1B0F)&FFFF, write at214B:069F BEFORE flushing stack. Listener changes
to seed/DF occur in source order. Draw=high16(new*N)+1 masked16; pure locals retain
new/N after callbacks. DF read from EFLAGS after seed write selects pointer step
-2/+2. BX7ABD,SI/DI=offset+step,ES=segment,AX then DX=draw. Arithmetic bits match
add_flags(high,1), with CF explicitly high!=0. Restore SP, local-2 draw, leave/store;
other EFLAGS bits preserved from the value read at store time. Procedure valueNone.

Off1E8D retf/no args: enter0, byte DS:A9FC compared against0 with8-bit flags.
Disabled0 sets AL0 preserving AH; disabled!=0 leaves AX unread/unchanged. Pending
saved BP and dirty registers/flags flush exactly as source _end. ValueNone.

All arguments, register read/store order, pending/dead stack bytes, 16-bit wraps,
secondary seed, signed high-word comparisons, mixed near/far cleanup, stubs,
site/listener/IO behavior, errors and suspension/replay remain visible. Seed-step
uses actual machine AX after call; the source ignores the dispatcher's sent AX.

## Controls and evidence

Body7 flips the completed routine's dead saved-BP word (after its normal epilogue,
before common finish). Root-return8 corrupts only94E8 return sites, letting94C9
return correctly; seed-return9 corrupts only94DC. Leaf-only cases stay equal for
return controls. Public cases cover all four routines/stubs/returns, N0/FFFF,
levels0/FFFF, speed0/255, disabled, overflow, DF, SP wrap, signed values, seed and
DF changes at seed write/stack flush, callback errors, done and variants. Direct
RNG/off bodies and complete frames are compared with full state at boundaries.
Eight real captures/body +500 synthetic inputs, then full existing12-body/control
proofs, exact ordered drive/lifecycle/ALL75/F40/profile and three rotated quiet
baseline/candidate/CPython/PyPy rounds precede merge; ratio<=0.95 median and every
candidate faster. No primitive-only performance claim or discarded sample.

## Owner acceptance amendment — 2026-11-01

The owner clarified the incremental porting objective and authorized merging T09.
The <=0.95 magnitude requirement above describes the original optimization gate;
it is superseded for this increment by docs/tasks/T09.md and
docs/porting-acceptance.md (recorded on main in 981335f). Every paired candidate
round must still improve, and all fidelity/artifact/CI requirements remain.
The measured median ratio 0.957204635 satisfies the amended contract. Preserve
the original failed assertion and receipts; owner-acceptance-v2.json records the
separate owner-approved acceptance of the same runtime artifact.
