//! T23 complete Pascal assignment/append trees and their shared forward copy.
use crate::host::{Host,Reg};
use crate::mem::lin;
use crate::regs::Regs;
fn write<H:Host>(h:&mut H,a:u32,v:u8,pc:u16)->Result<(),H::Err>{h.write(a,&[v],lin(h.seg(0x23e4),pc))}
fn copy<H:Host>(h:&mut H,ss:u16,so:u32,ds:u16,doff:u32,n:u16,pc:u16)->Result<(u16,u16),H::Err>{
 if n==0{return Ok((so as u16,doff as u16));}
 let sl=lin(ss,so as u16);let dl=lin(ds,doff as u16);let count=n as u32;
 if n>8 && so+count<=0x10000 && doff+count<=0x10000 && (sl+count<=dl || dl+count<=sl) {
  let data=h.read_snapshot(sl,n as usize)?;
  for (k,value) in data.into_iter().enumerate(){write(h,dl+k as u32,value,pc)?;}
 }else{
  for k in 0..count{let value=h.u8(lin(ss,(so+k) as u16))?;write(h,lin(ds,(doff+k) as u16),value,pc)?;}
 }
 Ok(((so+count) as u16,(doff+count) as u16))
}
pub fn run<H:Host>(h:&mut H,kind:u32)->Result<(),H::Err>{
 // args(mem,n) captures one contiguous block, including an unwrapped final word.
 let (sp,far)=h.entry();let a=h.ss_lin(sp+if far{4}else{2})?;let count=if kind==1{5}else{4};let bytes=h.read_snapshot(a,count*2)?;
 let words:Vec<u16>=bytes.chunks_exact(2).map(|b|u16::from_le_bytes([b[0],b[1]])).collect();
 let (so,ss,doff,ds)=if kind==1{(words[3],words[4],words[1],words[2])}else{(words[0],words[1],words[2],words[3])};
 let mut r=Regs::new(false);r.set(Reg::Bx,sp);r.set(Reg::Dx,h.ds() as u32);
 r.cld();
 let (si,di)=if kind==2 {
  let cl=h.u8(lin(ds,doff))? as u16;let mut al=h.u8(lin(ss,so))? as u16;let total=cl+al;
  write(h,lin(ds,doff),total as u8,0x6ca)?;
  if total>255{write(h,lin(ds,doff),255,0x6cf)?;al=(!cl)&255;}
  r.set_al(h,al as u8)?;copy(h,ss,so as u32+1,ds,doff as u32+cl as u32+1,al,0x6dc)?
 }else{
  let mut length=h.u8(lin(ss,so))?;
  if kind==1 && length>words[0] as u8{length=words[0] as u8;}
  r.set_al(h,length)?;write(h,lin(ds,doff),length,if kind==1{0x65c}else{0x638})?;
  copy(h,ss,so as u32+1,ds,doff as u32+1,length as u16,if kind==1{0x661}else{0x63d})?
 };
 r.set(Reg::Si,si as u32);r.set(Reg::Di,di as u32);r.set(Reg::Cx,0);r.set(Reg::Es,ds as u32);r.store(h,false)
}
