# T25 Source text-cell contract

00FF is retf12;0123 is near ret12. Both delegate inline to _text_cells.
Regs.enter0,push current DS,then source offset/segment through separate ss16
flush/live-SS reads. k=6 for forward,k=4 for backward. Direction flag is cached,
count read next. Zero count does not read destination or attribute words.
Nonzero count captures destination,ES and byte-swapped attribute AX. Each byte
is read live at captured source segment/current SI,SI advances before each word
write at0119/013D,then DI moves by+2/-2 and CX decrements. Every assignment
wraps16. Preserve overlap propagation,word writes crossing offsetFFFF,source
read versus write-listener order,cached AX high byte and pending DS push.
_end leaves/stores in the source order;DF update is late and preserves live
other flag bits. No eager snapshot of source bytes or invented popDS.

Four string callers use Regs.enter100h,capture source farg(+E),temporary BP-100h
andAX=FFh,then guest0644 with its actual source/destination/max argument order.
After resume use fresh Regs;retain original temporary captured before guest.
0205/02C8 capture low-byte attribute through live SS and writeDS:AAB2 at0223/
02E6 BEFORE position reads. Read column then row,mask each byte;calculateCX=2col,
unsigned MUL row*A0h in AX/DX with source flag behavior. farg(+6),then read far
destination words at linearptr andptr+2(no wrapped second word),addAX+CX-A2h.
Flush before reading length through live SS. Capture destination tuple,source
SS and sourceDI,then read current global colour,then call actual0123(near) or
00FF(far). Do not replace current SS with cached Regs.ss or use SENT values.

01A3:0644/01BE,0123/01FF. 0205:0644/0220,0123/0267.
026D:0644/0288,00FF/02C2. 02C8:0644/02E3,00FF/0323.
Final resumed _end preserves live frame/register mutations and returns None.
Variants omit their whole source export and remain Python. Generic Regs/memory
and already-native0644 form explicit boundaries;all function helpers discovered
by inventory must enter the first scoped-code probe.
