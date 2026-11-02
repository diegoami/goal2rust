# T20 instruction-state and suspension contract

Accepted oracle2cbeb36fdd3feb369324aaa88e6e4d2aa3b3d99c. Registry-resolved
inventory-v1 fixes three bodies, five guest returns and full inline ownership.

5729 is a near ret2 instruction-style Regs generator. Enter2; keep go false until
both keeper and side gates clear and own-strip passes. nested() flushes queued
writes, reads current BP's parent word through live SS, captures that parent DI,
then reads its segment and offset in source order. Rebuild these pointers on each
source nested() call; do not retain them across guests. Each guest stores registers
and pending stack before suspension, then resumes with fresh Regs. It ignores
SENT and reads live actual AX/AL. Preserve the distinct nested() call that reads
record point and the following nested() that obtains the far pointer: listeners
can change parent data between them. Goal go is true after opposing-strip,
unless a zero result requires tactic6 and its actual AL is nonzero. Final AL is
normalized, local8(-1) written, leave/store performed, full AX returned.

2EB8/2EF0 are plain retf6 Regs bodies. Read all three words before enter2. Capture
word/seg/off and retain source-inline direction_in_dx via c2be5 invoke (2EC7 or
2EFF), including source push words, return words, scratch registers and flags.
Sign-extend word high byte, signed multiply by DX and test the original full AX
(negative versus strictly positive). On success invoke c2e82 inline with near
return2EDA/2F12 and pushed original word; never turn this into a registered guest.
c2e82 enters2, checks signed abs(y)>=25 and abs(x)<=5, writes AL/local and leaves.
Normalize AL after invoke, outer local8/leave/store. Preserve all dead stack bytes,
flush ordering and unchanged flag behavior. Penalty-strip-4 stays Python.

Helpers referenced as values to invoke belong to ownership too. Existing native
callee boundaries and intentional variants/outside-scope shared helpers are
separate from zero-owned-Python checks. Counters alone do not establish closure.

Controls preserve every earlier ID: sorted three body controls145..147;
sorted leaf AX/full-EFLAGS controls148/149; inventory-ordered five guest-return
controls150..154. Reached return corruption must be detected; unreached paths
stay equal. All prior48 controls and T19's distinct post-return own-write failures
remain mandatory. Exact case/selector/branch/variant counts are sealed before
canonical runs, with no duplicate selector strings counted as distinct.
