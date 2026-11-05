# T27 Source contract

Pinned Python is semantic truth. This inventory summary does not replace its
actual operations or authorize algebraic reordering of callback-bearing reads.

0BC4 builds its18-byte Regs frame through explicit push/BP/SP operations. Keep
its source pc/z/unsigned/signed control state,all masked assignments,live local
reads/counters and source writes at the listed sites. Clear four aggregate
words,scan all eleven slots,skip zero roster words,compute each strength and
conditionally add manager bonus,then accumulate tactic and position bands.
Membership/bit tests use their actual far calls. Regs `_read`/`_write` flush
before memory access;_call POPS each pre-pushed word via live SS,updates SP,
reverses those words for guest arguments,stores stack state and then re-pushes
them through the ordinary call protocol. After every guest,use fresh Regs and
read live EFLAGS.ZF exactly where the source does,including reads whose z is
later overwritten. Local arithmetic flags are not guest flag writes.

Record helpers capture pointer words and wrapped offset in Rec.__init__;
Rec.lin wraps each field offset,while u8 reads remain live. Each ptr_local write
uses the actual Frame/live SS. Preserve argument-read order relative to enter,
independent repeated field reads and live versus captured record/table values.

0AA7 enters before reading country,computes country*BFh/manager*3,then manager
byte//8+10h and its remainder,stores its locals and sets DX before returning AX.
3041 enters before argument read,captures player record,reads+5 then+2,tests
their unbounded byte sum==30,retains sum AH and sets DX to original+5. 3088 reads
player argument before enter,captures record,+7 and n%3 table row,then unsigned
row*14 and foot-table value with source pointer/word order and final DX/AH.

3179 reads argument before enter,captures record,guests3088 then3041,retains
returned foot byte and captured Rec across both,reads CS live,uses actual
right/left membership helpers/returns,then independently reads+6/+7 if still
needed. Preserve bit-set variant fallback,AX high byte and DX from the actual
callee. attributes.gcall consumes SENT&FFFF,then reads live DX;it is not setup.
guest's ignore-SENT Regs contract. The membership helper then reads live flags.

377E reads argument before enter,captures record,checks native availability,
then computes signed energy/confidence contribution with source truncation
toward zero,16-bit intermediate wrap,clamp0..256 and the exact local/AX values
handed to3179. Retain local v across the call,source halving/remainder and all
frame writes/set-register order. Ret does DX store before returning masked AX.

0C57 captures value/k before entering its shared Regs helper. Compute masked
k-1,source low-CL shift mask,DX/CX,AX bit and local byte,then leave/store without
inventing flag updates. Include zero/full-width k,large/zero shift and source
variant behavior. Generic memory/Regs/Frame operations remain primitives;all
owned function and Rec-method code objects must disappear from default native
lifetimes,with positive source/outside/nondefault witnesses.
