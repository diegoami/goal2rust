# T19 source and suspension contract

Accepted oracle 2cbeb36fdd3feb369324aaa88e6e4d2aa3b3d99c. Inventory-v1 resolves
the exact five-body closure and 23 finite guest sites against the T18 profile.
Source behavior is authoritative; no numerical/flag/order simplification.

474D is an immediate-memory generator, retf4. Capture argptr's independently
read linear p and seg/off before entering its two-byte frame. Capture attack
from the SENT low byte; conditionally read live player pointer/id/position and
ball-ahead result. Near calls 4532/4649 receive captured frame BP. On return,
read the live record byte and apply the SENT low byte with byte wrapping. On
defense, query slot side and conditionally negate the live signed record byte.
Do not substitute actual AX for the yielded SENT value or capture live memory.

4532/4649 are near ret2 procedures. Enter frame and write initial false byte
before reading parent argument. Capture parent frame's far pointer in source
order (segment then offset), retaining linear p/seg/off across suspensions.
Group/tactic calls remain real guest calls. Each push writes live stack memory
and updates SP; pop_ax reads current SS/SP, advances SP and writes AX, with
captured yielded values retained separately. Attack uses the popped group and
captured tactic, signed depth and unsigned limit. Defense captures t6 independently
of its dead pushed product; pop twice even though the first result is discarded.
Re-read live player pointers/id/position on the group-3 path. Capture the frame
BP but resolve SS fresh for every local access. Final return combines live AX
high byte with the local result byte, in that read order. Boolean normalization
occurs only at the source's bool writes; group-1/2 defense writes the yielded
low byte without bool conversion. Keep the depth-plus-one variant on Python.

2BB1 is a plain retf4 Regs body. Read args first, enter two-byte frame, retain
captured slot value. For slot>11 assign full wrapped AX=slot-11; otherwise assign
AL only, preserving AH. Store the local result and leave/store in exact order.
The slot-side-12 variant stays Python. No invented guest/helper frame.

214B:06FA is a plain retf Regs body. Reproduce random_core(2,True) with its inline
0688 RNG via invoke return070E, exact pushes/dead words/seed write at214B:069F,
live DF and source error ordering. Set AX=2 before invoke, compare full resulting
AX with1 using sub_flags, normalize AL only, local8(-1), leave/store. Retain DX,
all preserved registers and full flags. Reuse an existing RNG implementation only
with identical source-inline semantics; do not call the registered random_n guest.

Ownership includes all five bodies and reachable positioning/geometry/RNG inline
helpers, including helpers referenced as arguments. Existing native callees and
intentional variants/outside-scope shared helpers are tracked separately. Scoped
Python execution must be zero inside native default lifetimes; positive outside
and variant probes prevent vacuous closure. Guest-entry totals are not FFI counts.

Control IDs follow existing T18 controls without renumbering: sorted five bodies
115..119; sorted leaves 2BB1/06FA output controls120/121 (AX/full EFLAGS); the 23
inventory-ordered guest return sites122..144. Return controls only corrupt the
selected reached return, and unreached paths remain equal. Historical controls
remain mandatory. Exact proof/error counts are sealed before canonical runs.
