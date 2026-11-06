//! T29 complete near-player-zone path, pinned positioning.py at 2cbeb36f.
use crate::host::{Host,Reg};
use crate::mem::lin;
#[derive(Clone,Copy,Default)]
pub struct Saved {pub bp:u16,pub p:u32,pub seg:u16,pub off:u16,pub point:u16}
pub enum Action {Direction(Saved),Done(u16)}
fn arg<H:Host>(h:&mut H,index:u32)->Result<u16,H::Err>{
 let (sp,far)=h.entry();let at=h.ss_lin(sp+if far{4}else{2}+index*2)?;h.u16(at)
}
fn enter<H:Host>(h:&mut H)->Result<u16,H::Err>{
 let sp=(h.reg(Reg::Sp)? as u16).wrapping_sub(2);
 let at=h.ss_lin(sp as u32)?;let bp=h.reg(Reg::Bp)?;
 h.write(at,&(bp as u16).to_le_bytes(),lin(h.seg(0x791),0x44c1))?;
 h.set_reg(Reg::Sp,sp as u32)?;h.set_reg(Reg::Bp,sp as u32)?;
 h.set_reg(Reg::Sp,sp.wrapping_sub(2) as u32)?;Ok(sp)
}
fn finish<H:Host>(h:&mut H,s:Saved,close:bool)->Result<Action,H::Err>{
 let at=h.ss_lin(s.bp.wrapping_sub(1) as u32)?;
 h.write(at,&[u8::from(close)],lin(h.seg(0x791),0x4526))?;
 // The high byte is captured before the independently live SS read of the local.
 let high=h.reg(Reg::Ax)? as u16&0xff00;
 let at=h.ss_lin(s.bp.wrapping_sub(1) as u32)?;let low=h.u8(at)?;
 Ok(Action::Done(high|low as u16))
}
pub fn step<H:Host>(h:&mut H,saved:Option<Saved>,sent:u16)->Result<Action,H::Err>{
 if let Some(s)=saved {
  let y=h.u8(s.p+1)? as i8 as i32;
  let direction=sent as u8 as i8 as i32;
  let point=(s.point>>8) as u8 as i8 as i32;
  return finish(h,s,(point-y*direction).abs()<6);
 }
 // argptr first computes p, then reads both argument words again for seg/off.
 let pseg=arg(h,1)?;let poff=arg(h,0)?;
 let p=lin(pseg,poff);let seg=arg(h,1)?;let off=arg(h,0)?;
 let point=arg(h,2)?;let bp=enter(h)?;let s=Saved{p,seg,off,point,bp};
 if h.u8(p+0x12)?==13{return finish(h,s,false);}
 let slot=h.u8(p+6)?;let holder=h.u8(lin(h.ds(),0x830b))?;
 if slot==holder{return finish(h,s,false);}
 let x=h.u8(p)? as i8 as i32;let point=point as u8 as i8 as i32;
 if (point-x).abs()>=4{return finish(h,s,false);}
 Ok(Action::Direction(s))
}
