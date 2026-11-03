# T21 register arithmetic and suspension contract

Accepted oracle2cbeb36fdd3feb369324aaa88e6e4d2aa3b3d99c. Inventory fixes the
two-body closure and single far return0791:8396; no default Python boundary.

835F is immediate-memory code, retf4, not long=True. Enter2 first. record(mem,f)
computes ONE live-SS linear address at captured BP+6, then reads offset and segment
at that linear address/+2; the second word is not separately segment-wrapped.
Capture the linear record. Read signed-word abs at record+6 and+8 in order;
0x8000 negates to0x8000. Wrap their sum to16 bits, write CX, then BX as sign-
extension of the captured sum. Only then read LIVE record+0xA and write AX,DX=0.
Keep CX/BX writes separate from the later scale read; callbacks may change data
or actual input registers. Call0279 with no stack arguments, far return8396.
On resumption return captured SENT low AX, preserving LIVE DX/other state. Do not
reload AX instead or return a long value. Do not invent the dead local-word write
mentioned by the listing but absent from the accepted Python body.

0279 is plain Regs, retf, not long=True. Read AX,DX,BX,CX in that order and capture
all four before writes/flush. SI/DI copy original AX/DX. Form unsigned AX*CX,
push low then high words, restore cached SP+4 without emitting SP at final store;
keep the dead words. Compute low16 AX*BX and DX*CX cross terms, add low product
high +BX_out wrapped16, then add CX_out wrapped16. Store AX,DX,BX,CX,SI,DI in
source insertion order. Final six arithmetic flags are add_flags(partial,CX_out)
from the LAST 16-bit addition, not the whole product or earlier carry. Preserve
all non-arithmetic flags, read live flags only at source store point. No host
floating point, algebraic rewrite that loses scratch/flags, frame prologue/leave
or returned long object. Final guest machinery retains DX because value is None.

Controls preserve earlier IDs: sorted body controls155/156; multiply output
controls157 AX-high-bit,158 DX-high-bit,159 full-EFLAGS bit; return control160
only at8396. Both captured/live callback behavior and full scratch/flag banks
must distinguish these controls. Unreached return paths remain equal. All prior51
controls and T19's scoped own-write error selectors remain mandatory. Exact
case/row/distinct-selector/arithmetic edge counts are sealed before producers.
