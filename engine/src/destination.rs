//! T18 destination-tree inline queries, accepted archaeology 2cbeb36f.
use crate::host::{args, Host, Reg};
use crate::mem::lin;
use crate::regs::{invoke, sub_flags, Regs, PF, SF, ZF};
fn ds8<H: Host>(h: &mut H, off: u16) -> Result<u8,H::Err> { h.u8(lin(h.ds(),off)) }
fn ds16<H: Host>(h: &mut H, off: u16) -> Result<u16,H::Err> { h.u16(lin(h.ds(),off)) }
fn cbw<H: Host>(h:&mut H,r:&mut Regs)->Result<(),H::Err>{let al=r.al(h)?;r.set_i(Reg::Ax,al as i8 as i64);Ok(())}
fn cwd<H: Host>(h:&mut H,r:&mut Regs)->Result<(),H::Err>{let ax=r.get(h,Reg::Ax)?;r.set(Reg::Dx,if ax&0x8000!=0{65535}else{0});Ok(())}
fn imul<H: Host>(h:&mut H,r:&mut Regs)->Result<(),H::Err>{let ax=r.get(h,Reg::Ax)?;let dx=r.get(h,Reg::Dx)?;let p=ax as i16 as i32*dx as i16 as i32;r.set(Reg::Ax,p as u32&65535);r.set(Reg::Dx,(p>>16) as u32&65535);Ok(())}
fn negate<H: Host>(h:&mut H,r:&mut Regs)->Result<(),H::Err>{let ax=r.get(h,Reg::Ax)?;if ax&0x8000!=0{r.set(Reg::Ax,ax.wrapping_neg() as u32);}Ok(())}
pub(crate) fn direction<H: Host>(h:&mut H,r:&mut Regs,seg:u16,off:u16,ret:u16)->Result<(),H::Err>{
 r.set(Reg::Es,seg as u32);r.set(Reg::Di,off as u32);
 invoke(h,r,Some(0x791),ret,&[seg as u32,off as u32],|h,r|crate::marking::c2be5(h,r,seg,off))?;
 cbw(h,r)?;let ax=r.get(h,Reg::Ax)?;r.set(Reg::Dx,ax as u32);Ok(())
}
fn finish_bool<H:Host>(h:&mut H,r:&mut Regs,value:bool)->Result<(),H::Err>{r.set_al(h,u8::from(value))?;let al=r.al(h)?;r.local8(h,-1,al)?;r.leave(h)?;r.store(h,false)}
pub fn draw_table<H:Host>(h:&mut H)->Result<(),H::Err>{
 let mut r=Regs::new(false);r.enter(h,2)?;let di=ds16(h,0x8437)?;r.set(Reg::Di,di as u32);let v=ds8(h,0x8337u16.wrapping_add(di))?;r.set(Reg::Ax,v as u32);r.local16(h,-2,v as u32)?;
 let next=if di==255{1}else{di.wrapping_add(1)};h.write(lin(h.ds(),0x8437),&next.to_le_bytes(),lin(h.seg(0x791),if di==255{0x2635}else{0x263d}))?;
 r.leave(h)?;r.store(h,false)
}
pub fn mirror<H:Host>(h:&mut H)->Result<(),H::Err>{
 let a=args(h,3)?;let (off,seg,word)=(a[0],a[1],a[2]);let sp=h.entry().0;let mut r=Regs::new(false);r.enter(h,2)?;
 direction(h,&mut r,seg,off,0x2c95)?;r.set_al(h,(word>>8) as u8)?;cbw(h,&mut r)?;imul(h,&mut r)?;let y=r.al(h)?;
 let at=h.ss_lin(sp+9)?;h.write(at,&[y],lin(h.seg(0x791),0x2c9e))?;
 direction(h,&mut r,seg,off,0x2caa)?;r.set_al(h,word as u8)?;cbw(h,&mut r)?;imul(h,&mut r)?;let x=r.al(h)?;
 let at=h.ss_lin(sp+8)?;h.write(at,&[x],lin(h.seg(0x791),0x2cb3))?;
 let ax=((y as u16)<<8)|x as u16;r.set(Reg::Ax,ax as u32);r.local16(h,-2,ax as u32)?;r.leave(h)?;r.store(h,false)
}
pub fn ahead<H:Host>(h:&mut H,reversed:bool)->Result<(),H::Err>{
 let a=args(h,3)?;let (off,seg,n)=(a[0],a[1],a[2]);let mut r=Regs::new(false);r.enter(h,2)?;
 direction(h,&mut r,seg,off,if reversed{0x2d7c}else{0x2d1f})?;r.set(Reg::Es,seg as u32);r.set(Reg::Di,off as u32);
 let y=h.u8(lin(seg,off.wrapping_add(1)))?;r.set_al(h,y)?;cbw(h,&mut r)?;imul(h,&mut r)?;cwd(h,&mut r)?;
 let mut lo=r.get(h,Reg::Ax)?;let mut hi=r.get(h,Reg::Dx)?;
 if !reversed{
  r.set(Reg::Cx,lo as u32);r.set(Reg::Bx,hi as u32);r.set(Reg::Ax,n as u32);r.set(Reg::Dx,0);
  let total=(n as u32).wrapping_add(lo as u32).wrapping_add((hi as u32)<<16);lo=total as u16;hi=(total>>16) as u16;r.set(Reg::Ax,lo as u32);r.set(Reg::Dx,hi as u32);
 }
 r.push(h,hi as u32)?;r.push(h,lo as u32)?;
 direction(h,&mut r,seg,off,if reversed{0x2d95}else{0x2d45})?;let ball=ds8(h,0x82f7)?;r.set_al(h,ball)?;cbw(h,&mut r)?;imul(h,&mut r)?;cwd(h,&mut r)?;
 if reversed{
  let ax=r.get(h,Reg::Ax)?;let dx=r.get(h,Reg::Dx)?;r.set(Reg::Cx,ax as u32);r.set(Reg::Bx,dx as u32);r.set(Reg::Ax,n as u32);r.set(Reg::Dx,0);
  let total=(n as u32).wrapping_add(ax as u32).wrapping_add((dx as u32)<<16);r.set(Reg::Ax,total&65535);r.set(Reg::Dx,total>>16);
 }
 r.set(Reg::Cx,lo as u32);r.set(Reg::Bx,hi as u32);let sp=r.get(h,Reg::Sp)?;r.set(Reg::Sp,sp.wrapping_add(4) as u32);
 let ax=r.get(h,Reg::Ax)?;let dx=r.get(h,Reg::Dx)?;
 let value=if reversed{(dx as i16)<(hi as i16)||(dx==hi&&ax<lo)}else{(dx as i16)>(hi as i16)||(dx==hi&&ax>lo)};
 finish_bool(h,&mut r,value)
}
pub fn goal_area<H:Host>(h:&mut H)->Result<(),H::Err>{
 let a=args(h,3)?;let (off,seg,word)=(a[0],a[1],a[2]);let mut r=Regs::new(false);r.enter(h,2)?;direction(h,&mut r,seg,off,0x2e45)?;
 r.set_al(h,(word>>8) as u8)?;cbw(h,&mut r)?;imul(h,&mut r)?;
 let ax=r.get(h,Reg::Ax)?;
 if ax&0x8000==0{r.set_al(h,0)?;}else{
  r.set_al(h,(word>>8) as u8)?;cbw(h,&mut r)?;negate(h,&mut r)?;let ax=r.get(h,Reg::Ax)?;
  if (ax as i16)<33{r.set_al(h,0)?;}else{r.set_al(h,word as u8)?;cbw(h,&mut r)?;negate(h,&mut r)?;let ax=r.get(h,Reg::Ax)?;r.set_al(h,u8::from((ax as i16)<=2))?;}
 }
 let al=r.al(h)?;r.local8(h,-1,al)?;r.leave(h)?;r.store(h,false)
}
// runtime.rng_0688/pilot.rand have different scratch/flag semantics from
// entrypoints.rng_core. Keep their pointer reread and queued frames inline.
fn rng_value<H:Host>(h:&mut H,n:u16)->Result<u16,H::Err>{
 let ptr=lin(h.ds(),0xa978);let off=h.u16(ptr)?;let seg=h.u16(ptr+2)?;let at=lin(seg,off);let new=h.u16(at)?.wrapping_mul(0x7abd).wrapping_add(0x1b0f);
 h.write(at,&new.to_le_bytes(),lin(h.seg(0x214b),0x069f))?;Ok((((new as u32*n as u32)>>16)+1) as u16)
}
fn draw_is_one<H:Host>(h:&mut H,r:&mut Regs,n:u16)->Result<(),H::Err>{
 r.enter(h,2)?;let ptr=lin(h.ds(),0xa978);let off=h.u16(ptr)?;let seg=h.u16(ptr+2)?;let sp=r.get(h,Reg::Sp)?;
 for word in [seg,off,n,h.seg(0x214b),0x06e3]{r.push(h,word as u32)?;}
 r.enter(h,2)?;let inner=r.get(h,Reg::Sp)?;for word in [h.ds(),seg,off]{r.push(h,word as u32)?;}
 let draw=rng_value(h,n)?;r.set(Reg::Sp,inner as u32);r.local16(h,-2,draw as u32)?;r.set(Reg::Ax,draw as u32);r.set(Reg::Dx,draw as u32);r.leave(h)?;
 r.set(Reg::Sp,sp as u32);let ax=r.get(h,Reg::Ax)?;r.set_al(h,u8::from(ax==1))?;let al=r.al(h)?;r.local8(h,-1,al)?;r.leave(h)
}
pub fn energy_gate<H:Host>(h:&mut H)->Result<(),H::Err>{
 let a=args(h,2)?;let(off,seg)=(a[0],a[1]);let mut r=Regs::new(false);r.enter(h,2)?;crate::geometry::player_byte(h,&mut r,seg,off,0xe)?;cbw(h,&mut r)?;
 let energy=r.get(h,Reg::Ax)?;r.set(Reg::Dx,energy as u32);r.set(Reg::Ax,33);let n=33u16.wrapping_sub(energy);r.set(Reg::Ax,n as u32);
 invoke(h,&mut r,Some(0x791),0x2ba5,&[n as u32],|h,r|draw_is_one(h,r,n))?;
 let al=r.al(h)?;r.local8(h,-1,al)?;r.leave(h)?;r.store(h,false)
}
pub fn long_extreme<H:Host>(h:&mut H,maximum:bool)->Result<(),H::Err>{
 let a=args(h,4)?;let(blo,bhi,alo,ahi)=(a[0],a[1],a[2],a[3]);let mut r=Regs::new(false);r.enter(h,4)?;
 let pick=if ahi as i16>bhi as i16{maximum}else if (ahi as i16)<(bhi as i16){!maximum}else if maximum{alo>blo}else{alo<=blo};
 let(lo,hi)=if pick{(alo,ahi)}else{(blo,bhi)};r.local16(h,-4,lo as u32)?;r.local16(h,-2,hi as u32)?;r.set(Reg::Ax,lo as u32);r.set(Reg::Dx,hi as u32);r.set(Reg::Es,hi as u32);r.leave(h)?;
 if maximum{r.arith(if ahi==bhi{sub_flags(alo as u32,blo as u32,16)}else{sub_flags(ahi as u32,bhi as u32,16)});}
 r.store(h,false)
}
pub fn clamp_byte<H:Host>(h:&mut H)->Result<(),H::Err>{
 let a=args(h,4)?;let(hi,lo,off,seg)=(a[0],a[1],a[2],a[3]);let mut r=Regs::new(false);r.enter(h,0)?;r.set(Reg::Es,seg as u32);r.set(Reg::Di,off as u32);let at=lin(seg,off);
 let mut al=h.u8(at)?;if (al as i8)<(lo as u8 as i8){al=lo as u8;h.write(at,&[al],lin(h.seg(0x214b),0x2045))?;}
 al=h.u8(at)?;if (al as i8)>(hi as u8 as i8){al=hi as u8;h.write(at,&[al],lin(h.seg(0x214b),0x2059))?;}
 r.set_al(h,al)?;r.leave(h)?;r.store(h,false)
}
pub fn membership<H:Host>(h:&mut H)->Result<(),H::Err>{
 let a=args(h,3)?;let(off,seg,element)=(a[0],a[1],a[2]&255);let mut r=Regs::new(false);r.set(Reg::Di,off as u32);r.set(Reg::Es,seg as u32);r.set(Reg::Bx,(element>>3) as u32);
 let cx=r.get(h,Reg::Cx)?;r.set(Reg::Cx,((cx&0xff00)|(element&7)) as u32);let mask=1u8<<(element&7);r.set_al(h,mask)?;
 let value=h.u8(lin(seg,off.wrapping_add(element>>3)))?&mask;let mut flags=0;if value.count_ones()%2==0{flags|=PF;}if value==0{flags|=ZF;}if value&128!=0{flags|=SF;}r.arith(flags);r.store(h,false)
}
