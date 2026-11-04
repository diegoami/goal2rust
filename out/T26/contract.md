# T26 Source contract to preserve

The pinned Python bodies and their actual helper/function code objects are the
semantics. This inventory summary does not replace inspection of those sources.

56D9 enters2,stores local false before the offside test,derives the offside
record,guests2BE5 at5700,normalizes the sign bit through AL and calls26A0 at570E.
It emits code42 through2B0F at571B only when8329 is clear,then sets8329 and
reloads the live local byte before leaving/storing. Preserve nested live SS,
slot arithmetic,return AH and every guest's actual near/far form.

26A0 uses its argument's low byte to write8308(EAF/EAE),then8328=1,with its
Regs prologue/leave/store ordering and registers otherwise untouched. 2B0F
captures its code argument before enter,forms1/0/0/code words with the source
AX high-byte behavior,stores stack state and yields the actual near1EB5 call.
No invented explicit source epilogue after that yield.

1EB5 uses the live PortFrame API,not a Regs snapshot. It applies1E53 first,
then writes1D4A;on a new line it redraws at most the three source-selected
records through1829,retaining signed comparisons,live locals,AX/DX setters and
the source's captured n/i values. Read the actual far pointer only after those
guests,then write7C26/7C28 in order. Resolve go's target/far/return/arity from
frame.SITES;ignore sent generator values as the source does.

1E53 captures the parent frame before its own enter,reads live parent/DS/table
values in source order,retains unsigned multiplication high words and signed
byte deltas,updates the actual player's rating word,then AX/DX. 1C78 compares
newest ring fields with live parent arguments and captured country pointer;
preserve its local writes/short-circuit order,two repeated country-index reads,
nested word helper,AX high bytes and final DX. 1D4A preserves duplicate gating,
bar increment before ring wrap,the real1C86 guests,live frame/player reads,
captured segment/offset in its nested word helper,field-write order,next-index
sentinel and final AL. Variants stay on their full Python exports.

1829 captures the record and stack temporaries,then expands marker1/2 through
actual T23 Pascal-string guests. Preserve temporary pushes across guests,
explicit SP repair,cached versus live line lengths/record pointers and source
mul/cbw semantics. Its two marker tuples produce eight distinct returns and
the two display pointers produce19B2/19DE;the second draw is skipped for rows
above4. Argument reads and colour/row/column formation follow source order;
use actual T25 text rendering and real64K wrap/callback/alias behavior.

0018 captures args before enter,pushes count,queues CLD,forms the repeated-byte
word and writes each word/odd byte at the actual sites. Destination offset
wraps per word;each word itself remains contiguous. Preserve captured word and
base across callbacks,final DI/CX,stack adjustment and late flag store.

1C86 captures args before Regs,flushes before reading its word,uses source32-bit
signed-delta/unsigned comparisons and single-wrap formulas,including zero/large
and malformed bounds. Preserve temporary pushes/SP restoration,ES/DI timing,
write before AX/DX assignment,leave/store and the actual long far return.
All generic memory/Regs/frame operations remain explicit established primitives;
no owned function may execute in Python during default native lifetimes.
