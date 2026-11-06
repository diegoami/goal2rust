# T28 Source contract

Pinned contests.py is semantic truth;no algebraic reordering of callback reads.
533B takes a near ret2 parent BP argument. Regs.enter(2) pushes original BP,
sets frame BP/SP and defers stack writes. nested() flushes before each ss16,
reads parent at BP+4,then captures that DI in a Python local. It evaluates
parent+8(ES) BEFORE parent+6(DI),each with live machine SS after flush. Record
byte reads wrap DI+k through mem.addr. The first slot read is compared to live
DS:830C;nonreceiver queues local flag0 and skips the guest entirely.

Receiver queues flag1,then traverses the parent AGAIN,reads slot AGAIN,clears AH
and yields the ordinary near keeper call045D with current AX. guest() stores
stack/dirty regs after flushing flag. Preserve pending-flush effects and real
return5367. After the guest use fresh resumed Regs. A nonzero returned AL
short-circuits the DS:8300 read;otherwise an unsigned word<10 selects ball DS:82F6.
Default target selection is ball for keeper/countdown<10,DS:8313 otherwise.
The nondefault receiver-to-target changes the early selection and stays Python.

The chosen target word is read BEFORE re-traversing the live parent and writing
record+7 at537C/538C. The target AX stays cached through those reads/callbacks.
ss8(localBP-1) flushes pending writes then reads live SS;only AL is assigned.
leave() restores cached BP and SP;store() retains source dirty-register order and
flags behavior. Preserve AH,DX/ES/DI,leftover memory,stack words and return values.
Generic memory,Frame,Regs and Call operations remain established primitives;
all six explicitly owned helper/body code objects must disappear from default
native lifetimes,with positive source/outside/nondefault witnesses.
