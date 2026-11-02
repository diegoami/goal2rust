//! T21 ball-travel caller and shared long multiply, oracle2cbeb36f.
use crate::host::{Host,Reg};
use crate::mem::lin;
use crate::regs::Regs;
fn abs_word(x:u16)->u16{if x&0x8000!=0{x.wrapping_neg()}else{x}}
pub fn start<H:Host>(h:&mut H)->Result<(),H::Err>{
 let sp=(h.reg(Reg::Sp)? as u16).wrapping_sub(2);let at=h.ss_lin(sp as u32)?;let bp=h.reg(Reg::Bp)?;
 h.write(at,&(bp as u16).to_le_bytes(),lin(h.seg(0x791),0x835f))?;
 h.set_reg(Reg::Sp,sp as u32)?;h.set_reg(Reg::Bp,sp as u32)?;h.set_reg(Reg::Sp,sp.wrapping_sub(2) as u32)?;
 let at=h.ss_lin(sp.wrapping_add(6) as u32)?;let off=h.u16(at)?;let seg=h.u16(at+2)?;let rec=lin(seg,off);
 let a=abs_word(h.u16(rec+6)?);let b=abs_word(h.u16(rec+8)?);let sum=a.wrapping_add(b);
 h.set_reg(Reg::Cx,sum as u32)?;h.set_reg(Reg::Bx,if sum&0x8000!=0{65535}else{0})?;
 let scale=h.u16(rec+10)?;h.set_reg(Reg::Ax,scale as u32)?;h.set_reg(Reg::Dx,0)
}
pub fn multiply<H:Host>(h:&mut H)->Result<(),H::Err>{
 let mut r=Regs::new(false);let ax=r.get(h,Reg::Ax)?;let dx=r.get(h,Reg::Dx)?;let bx=r.get(h,Reg::Bx)?;let cx=r.get(h,Reg::Cx)?;
 let low=ax as u32*cx as u32;r.push(h,low&65535)?;r.push(h,low>>16)?;let sp=r.get(h,Reg::Sp)?;r.set(Reg::Sp,sp.wrapping_add(4) as u32);
 let bx_out=(ax as u32*bx as u32) as u16;let cx_out=(dx as u32*cx as u32) as u16;let partial=((low>>16) as u16).wrapping_add(bx_out);let high=partial.wrapping_add(cx_out);
 r.set(Reg::Ax,low&65535);r.set(Reg::Dx,high as u32);r.set(Reg::Bx,bx_out as u32);r.set(Reg::Cx,cx_out as u32);r.set(Reg::Si,ax as u32);r.set(Reg::Di,dx as u32);
 r.arith(crate::speaker::add_flags(partial,cx_out));r.store(h,false)
}
