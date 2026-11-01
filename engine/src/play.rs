//! contests.play_state_update57AC and live own/player-record helpers, oracle2cbeb36f.
use crate::host::{Host,Reg};
use crate::mem::{lin,cbw};
use crate::regs::Regs;
#[derive(Clone,Copy,PartialEq,Eq)]
pub enum Phase {Start,Probe(u8),Keeper,EarlyEnd,OnBall,Side,Chase,Nearest(bool),Point,Destination,Moved,End}
pub struct Request{pub next:Phase,pub target:&'static str,pub ret_to:&'static str,pub args:Vec<u16>,pub far:bool}
fn ds8<H:Host>(h:&mut H,off:u16)->Result<u8,H::Err>{h.u8(lin(h.ds(),off))}
fn ds16<H:Host>(h:&mut H,off:u16)->Result<u16,H::Err>{h.u16(lin(h.ds(),off))}
fn ss16<H:Host>(h:&mut H,r:&mut Regs,off:u16)->Result<u16,H::Err>{r.flush(h)?;let at=h.ss_lin(off as u32)?;h.u16(at)}
fn own<H:Host>(h:&mut H,r:&mut Regs)->Result<(u16,u16),H::Err>{
 let bp=r.get(h,Reg::Bp)?;let seg=ss16(h,r,bp.wrapping_add(8))?;
 let bp=r.get(h,Reg::Bp)?;let off=ss16(h,r,bp.wrapping_add(6))?;
 r.set(Reg::Es,seg as u32);r.set(Reg::Di,off as u32);Ok((seg,off))
}
fn rb<H:Host>(h:&mut H,r:&mut Regs,k:u16)->Result<u8,H::Err>{let seg=r.get(h,Reg::Es)?;let off=r.get(h,Reg::Di)?.wrapping_add(k);h.u8(lin(seg,off))}
fn rw<H:Host>(h:&mut H,r:&mut Regs,k:u16)->Result<u16,H::Err>{let seg=r.get(h,Reg::Es)?;let off=r.get(h,Reg::Di)?.wrapping_add(k);h.u16(lin(seg,off))}
fn player<H:Host>(h:&mut H,r:&mut Regs)->Result<(),H::Err>{
 let a=rw(h,r,13)?;r.set(Reg::Ax,a as u32);r.set(Reg::Dx,20);
 let dx=r.get(h,Reg::Dx)?;let ax=r.get(h,Reg::Ax)?;let p=ax as u32*dx as u32;r.set(Reg::Ax,p);r.set(Reg::Dx,p>>16);
 let di=ds16(h,0xa91b)?;let es=ds16(h,0xa91d)?;r.set(Reg::Di,di as u32);r.set(Reg::Es,es as u32);
 let di=r.get(h,Reg::Di)?;let ax=r.get(h,Reg::Ax)?;r.set(Reg::Di,di.wrapping_add(ax) as u32);Ok(())
}
fn request<H:Host>(h:&mut H,r:&mut Regs,next:Phase,target:&'static str,ret_to:&'static str,args:Vec<u16>,far:bool)->Result<Option<Request>,H::Err>{r.store(h,true)?;Ok(Some(Request{next,target,ret_to,args,far}))}
fn end<H:Host>(h:&mut H,r:&mut Regs,mutant:bool)->Result<Option<Request>,H::Err>{
 r.leave(h)?;r.store(h,false)?;
 if mutant{let at=h.ss_lin((h.entry().0 as u16).wrapping_sub(2) as u32)?;let old=h.u16(at)?;h.write(at,&(old^1).to_le_bytes(),lin(h.seg(0x214b),0))?;}Ok(None)
}
fn move_to<H:Host>(h:&mut H,r:&mut Regs)->Result<Option<Request>,H::Err>{let(seg,off)=own(h,r)?;request(h,r,Phase::Moved,"0791:474D","0791:58CB",vec![seg,off],true)}
fn destination<H:Host>(h:&mut H,r:&mut Regs)->Result<Option<Request>,H::Err>{let(seg,off)=own(h,r)?;request(h,r,Phase::Destination,"0791:4A28","0791:58C2",vec![seg,off],true)}
fn ball<H:Host>(h:&mut H,r:&mut Regs,site:u16)->Result<Option<Request>,H::Err>{
 let ax=ds16(h,0x82f6)?;r.set(Reg::Ax,ax as u32);let(seg,off)=own(h,r)?;let ax=r.get(h,Reg::Ax)?;h.write(lin(seg,off.wrapping_add(7)),&ax.to_le_bytes(),lin(h.seg(0x791),site))?;move_to(h,r)
}
fn chase<H:Host>(h:&mut H,r:&mut Regs)->Result<Option<Request>,H::Err>{let bp=r.get(h,Reg::Bp)?;request(h,r,Phase::Chase,"0791:5729","0791:585F",vec![bp],false)}
fn candidate<H:Host>(h:&mut H,r:&mut Regs)->Result<Option<Request>,H::Err>{
 if ds8(h,0x8302)?==0{let(seg,off)=own(h,r)?;return request(h,r,Phase::Side,"0791:2B51","0791:5857",vec![seg,off],true);}chase(h,r)
}
fn choose<H:Host>(h:&mut H,r:&mut Regs)->Result<Option<Request>,H::Err>{
 if ds8(h,0x8327)?==5&&ds16(h,0x8300)?>0{return ball(h,r,0x5809);}
 if ds8(h,0x8325)?!=0{
  if ds8(h,0x830c)?!=0{let(seg,off)=own(h,r)?;return request(h,r,Phase::OnBall,"0791:2BB1","0791:582A",vec![seg,off],true);}
  return candidate(h,r);
 }destination(h,r)
}
fn nearest<H:Host>(h:&mut H,r:&mut Regs,second:bool)->Result<Option<Request>,H::Err>{
 let(seg,off)=own(h,r)?;request(h,r,Phase::Nearest(second),"0791:2974",if second{"0791:5885"}else{"0791:586C"},vec![seg,off],true)
}
pub fn step<H:Host>(h:&mut H,phase:Phase,mutant:bool)->Result<Option<Request>,H::Err>{
 let mut r=Regs::new(phase!=Phase::Start);
 match phase{
  Phase::Start=>{r.enter(h,2)?;let bp=r.get(h,Reg::Bp)?;request(h,&mut r,Phase::Probe(0),"0791:56D9","0791:57B6",vec![bp],false)}
  Phase::Probe(i)=>{
   if r.al(h)?!=0{return end(h,&mut r,mutant);}
   if i<3{let(target,ret)=[("0791:5049","0791:57BE"),("0791:533B","0791:57C6"),("0791:5565","0791:57CE")][i as usize];let bp=r.get(h,Reg::Bp)?;return request(h,&mut r,Phase::Probe(i+1),target,ret,vec![bp],false);}
   let b=ds8(h,0x830b)?;r.set_al(h,b)?;r.set_ah(h,0)?;let ax=r.get(h,Reg::Ax)?;request(h,&mut r,Phase::Keeper,"0791:045D","0791:57DE",vec![ax],false)
  }
  Phase::Keeper=>{
   if r.al(h)?!=0&&ds8(h,0x8302)?==0{let(seg,off)=own(h,&mut r)?;return request(h,&mut r,Phase::EarlyEnd,"0791:4B64","0791:57F2",vec![seg,off],true);}choose(h,&mut r)
  }
  Phase::EarlyEnd|Phase::End=>end(h,&mut r,mutant),
  Phase::OnBall=>{
   if r.al(h)?!=2{own(h,&mut r)?;player(h,&mut r)?;if rb(h,&mut r,6)?!=1{return destination(h,&mut r);}}candidate(h,&mut r)
  }
  Phase::Side=>{if r.al(h)?==0{chase(h,&mut r)}else{destination(h,&mut r)}}
  Phase::Chase=>{if r.al(h)?!=0{ball(h,&mut r,0x58b3)}else{nearest(h,&mut r,false)}}
  Phase::Nearest(second)=>{
   let al=r.al(h)?;r.set(Reg::Ax,cbw(al) as u32);let ax=r.get(h,Reg::Ax)?;r.set(Reg::Di,ax as u32);
   let di=r.get(h,Reg::Di)?;let b=ds8(h,di.wrapping_add(if second{0x830f}else{0x8311}))?;r.set_al(h,b)?;
   own(h,&mut r)?;let al=r.al(h)?;if al==rb(h,&mut r,6)?{return ball(h,&mut r,0x58b3);}
   if !second{return nearest(h,&mut r,true);}
   if ds8(h,0x830c)?==0{let point=ds16(h,0x82f6)?;let(seg,off)=own(h,&mut r)?;return request(h,&mut r,Phase::Point,"0791:44C1","0791:58A9",vec![point,seg,off],true);}destination(h,&mut r)
  }
  Phase::Point=>{if r.al(h)?!=0{ball(h,&mut r,0x58b3)}else{destination(h,&mut r)}}
  Phase::Destination=>move_to(h,&mut r),
  Phase::Moved=>{
   if ds8(h,0x8302)?!=0{let(seg,off)=own(h,&mut r)?;return request(h,&mut r,Phase::End,"0791:6188","0791:58DB",vec![seg,off],true);}end(h,&mut r,mutant)
  }
 }
}
