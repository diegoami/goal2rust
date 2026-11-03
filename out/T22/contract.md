# T22 source evaluation and suspension contract

Accepted oracle2cbeb36f. All three use immediate-memory enter, not Regs buffers.
Never add local writes suggested only by listing comments. Frame BP is captured;
frame reads use live SS, linear record address is captured after one SS argument
address lookup and two consecutive word reads. Constants DS and segment mapping
retain source semantics. Return None preserves live registers as guest machinery
requires; a returned word uses the captured value.

8CF5 enters0xC. For each side0,1 capture line_off/linear line, first and direction
SENT low AX. first+2 through first+11 is a finite ten-record loop, using full
unwrapped Python k (first may be255); unsigned low multiply selects DI, mem.ds8
wraps offset. Each iteration rereads live line+1 before live row. Signed-byte
comparison chooses minimum, writes only when lower. Re-read live line+1 then
signed multiply by captured direction; write lowbyte at8DC3 before AX/DX/DI.
Suspend at far8D42(direction),8DD0(sprite), optionally8E17(marker). Preserve SENT
AX at8DD0 versus live DX; read signed line row thenDS:82F7, write AX/DX in order.
Short-circuit marker predicate in source order; marker arguments are evaluated
sprite DS:8308, captured line word, actual DS,8304. Captured line pointers remain
valid if callbacks change registers/pointer data.

8E24 enters0. Capture record. Compare record+2 thenrecord; conditional restore
reads old row then column, computes PICTURE cell, reads contents then live record
sprite. On match recompute BACKGROUND cell, read background, then recompute
PICTURE cell for write8EAC (callbacks can mutate table pointers). Each cell reads
pointer low thenhigh before signed row/column arithmetic. Signed byte row is
sign-extended before UNSIGNED16x160 multiply; signed column contributes doubled
wrapped byte. Cell address arithmetic is masked16 then added to pointer base.
Afterward read live record word thenwrite record+2 at8EBA; read glyph then row/
column, recompute current picture cell and write8EE5. Only then write DX from
captured row's unsigned multiplication, return captured low AX. No guest calls.

90C5 enters0, capture offset/segment/record. Read sprite from live-SS captured
frame+0xC beforewrite record+4 at90CE. Re-read record+4 tochoose direction index
(0 onlyfor0EAE), read liveDS direction byte. Read frame+0xB, signedbyte add with
captured direction and write row90F6. Read frame+0xA and combine capturedAX high,
write column at9100. Write capturedAX thenDX. Read liveDS:9A3E;
if zero call captured seg/off to8E24 far9113. Return None, including after callee.

Controls:161..163 sorted body addresses8CF5/8E24/90C5;164 sprite AX,165 sprite DX;
166..169 for8D42/8DD0/8E17/9113 respectively. Distinguish repeated writes by ordinal
selector and shared site phases; require each selector positively reached.
