//! T24 owned keyboard data/frame operations. Kit services remain explicit callbacks.
use crate::host::{Host,Reg};
use crate::mem::lin;
use crate::regs::Regs;
fn ds8<H:Host>(h:&mut H,off:u16)->Result<u8,H::Err>{h.u8(lin(h.ds(),off))}
fn write<H:Host>(h:&mut H,off:u16,v:u8,pc:u16)->Result<(),H::Err>{h.write(lin(h.ds(),off),&[v],lin(h.seg(0x214b),pc))}
pub fn return_cs<H:Host>(h:&mut H)->Result<u16,H::Err>{let a=h.ss_lin(h.entry().0.wrapping_add(2))?;h.u16(a)}
pub fn return_ip<H:Host>(h:&mut H)->Result<u16,H::Err>{let a=h.ss_lin(h.entry().0)?;h.u16(a)}
pub fn poll_done<H:Host>(h:&mut H,has:bool)->Result<(),H::Err>{let ax=h.reg(Reg::Ax)?;h.set_reg(Reg::Ax,(ax&0xff00)|u32::from(has))}
pub fn read_pushed<H:Host>(h:&mut H)->Result<bool,H::Err>{
 if ds8(h,0x79ae)?==0{return Ok(false);}
 let mut r=Regs::new(false);r.enter(h,0x14)?;
 write(h,0x79ae,0,0x8ea)?;let key=ds8(h,0xa976)?;r.set_al(h,key)?;
 let key=r.al(h)?;write(h,0xa977,key,0x97c)?;r.leave(h)?;r.store(h,false)?;Ok(true)
}
pub fn push<H:Host>(h:&mut H)->Result<(),H::Err>{
 let mut r=Regs::new(false);r.enter(h,0)?;write(h,0x79ae,1,0x996)?;
 let bp=r.get(h,Reg::Bp)?;r.flush(h)?;let a=h.ss_lin(bp.wrapping_add(6) as u32)?;let key=h.u8(a)?;
 r.set_al(h,key)?;let key=r.al(h)?;write(h,0xa976,key,0x99e)?;r.leave(h)?;r.store(h,false)
}
pub fn wait<H:Host>(h:&mut H,first:bool)->Result<(),H::Err>{
 let mut r=Regs::new(!first);
 if first{r.enter(h,0)?;r.store(h,true)}
 else{write(h,0xa976,0,0x98a)?;r.leave(h)?;r.store(h,false)}
}
