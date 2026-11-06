# T29 near-player-zone source contract

Pinned positioning.near_player_zone0791:44C1 is semantic truth. It returns far,
popping6bytes. argptr evaluates mem.arg(1),mem.arg(0) to compute cached physical
p, then evaluates arg(1),arg(0) AGAIN for cached seg/off. point=arg(2) is captured
before mem.enter(2) writes savedBP, updatesSP/BP/SP and creates Frame. Preserve
all five argument reads, their order, liveSS per read and callback mutations.

Short circuits: first cached p+0x12!=13, then p+6!=liveDS:830B; read the latter
only after p+6. For admitted player, read cached point low signed8 before cached
p+0 signed8; abs difference<4 (3 passes,4 fails). Only the true x branch calls
existing native2BE5(seg,off),far actualreturn4500. same/guest masks the yielded
SENT value, not fresh liveAX; signed8(direction&255) multiplies a newly read
signed8(p+1). Python evaluation is signed8(point>>8) MINUS (signed8(p+1) TIMES
signed8(direction&255)), absolute<6; retain this grouping and post-guest read.

Write local close at FrameBP-1 via liveSS,site0791:4526,even when earlyfalse.
Then evaluate liveAX&FF00 BEFORE f.u8(-1) with a fresh liveSS. Frame offsets wrap
16bits; cached physical p+k does NOT wrap as a segment offset. Do not change
AH/other registers except normal frame and guest behavior. Frame unwinding and
return pop remain common dispatcher duties; this body does not Regs.leave/store.

Owned functions:near_player_zone,argptr,r8,s8,same,guest. positioning.w8 has the
same spelling as f.w8 but is not called; its exclusion is explicit in inventory.
Frame/memory/Call are generic primitives. Nondefault variants and changed Entry
identities remain Python. Positive source/outside/nondefault witnesses for all
six owned code objects,zero owned default Python inside native lifetime.
