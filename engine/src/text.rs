//! T25 source text cells and their four Pascal-string callers.
use crate::host::{Host,Reg};
use crate::mem::lin;
use crate::regs::Regs;
pub const BODIES:[&str;6]=["214B:00FF","214B:0123","214B:01A3","214B:0205","214B:026D","214B:02C8"];
pub const RETURNS:[&str;8]=["214B:01BE","214B:01FF","214B:0220","214B:0267","214B:0288","214B:02C2","214B:02E3","214B:0323"];
pub fn index(address:&str)->Option<u32>{BODIES.iter().position(|a|*a==address).map(|i|i as u32)}
fn ssword<H:Host>(h:&mut H,r:&mut Regs,k:u16)->Result<u16,H::Err>{
 let bp=r.get(h,Reg::Bp)?;r.flush(h)?;let a=h.ss_lin(bp.wrapping_add(k) as u32)?;h.u16(a)
}
fn farg<H:Host>(h:&mut H,r:&mut Regs,k:u16)->Result<(u16,u16),H::Err>{
 let seg=ssword(h,r,k.wrapping_add(2))?;let off=ssword(h,r,k)?;
 r.set(Reg::Es,seg as u32);r.set(Reg::Di,off as u32);Ok((seg,off))
}
fn end<H:Host>(h:&mut H,r:&mut Regs)->Result<(),H::Err>{r.leave(h)?;r.store(h,false)}
pub fn cells<H:Host>(h:&mut H,reverse:bool)->Result<(),H::Err>{
 let mut r=Regs::new(false);r.enter(h,0)?;let ds=h.ds();r.push(h,ds as u32)?;
 let k=if reverse{4}else{6};let si=ssword(h,&mut r,k+4)?;r.set(Reg::Si,si as u32);
 let source_seg=ssword(h,&mut r,k+6)?;
 if reverse{r.std();}else{r.cld();}
 let count=ssword(h,&mut r,k)?;r.set(Reg::Cx,count as u32);
 if count!=0{
  let di=ssword(h,&mut r,k+8)?;r.set(Reg::Di,di as u32);
  let es=ssword(h,&mut r,k+10)?;r.set(Reg::Es,es as u32);
  let ax=ssword(h,&mut r,k+2)?;r.set(Reg::Ax,ax as u32);r.set(Reg::Ax,ax.swap_bytes() as u32);
  while r.get(h,Reg::Cx)?!=0{
   let si=r.get(h,Reg::Si)?;let value=h.u8(lin(source_seg,si))?;r.set_al(h,value)?;
   r.set(Reg::Si,(if reverse{si.wrapping_sub(1)}else{si.wrapping_add(1)}) as u32);
   let ax=r.get(h,Reg::Ax)?;let es=r.get(h,Reg::Es)?;let di=r.get(h,Reg::Di)?;
   h.write(lin(es,di),&ax.to_le_bytes(),lin(h.seg(0x214b),if reverse{0x13d}else{0x119}))?;
   r.set(Reg::Di,(if reverse{di.wrapping_sub(2)}else{di.wrapping_add(2)}) as u32);
   let cx=r.get(h,Reg::Cx)?;r.set(Reg::Cx,cx.wrapping_sub(1) as u32);
  }
 }
 end(h,&mut r)
}
#[derive(Clone,Copy,PartialEq,Eq)]
pub enum Phase{Start,Copied,Written}
#[derive(Clone,Copy)]
pub struct Saved{pub kind:u8,temporary:u16}
impl Saved{pub fn new(kind:u8)->Self{Self{kind,temporary:0}}}
pub struct Request{pub next:Phase,pub saved:Saved,pub target:&'static str,pub ret_to:&'static str,pub args:Vec<u16>,pub far:bool}
pub enum Action{Call(Request),Done}
pub fn step<H:Host>(h:&mut H,phase:Phase,mut s:Saved)->Result<Action,H::Err>{
 let mut r=Regs::new(phase!=Phase::Start);
 let copied=RETURNS[s.kind as usize*2];let written=RETURNS[s.kind as usize*2+1];let backwards=s.kind<2;let set_attr=s.kind%2==1;
 match phase{
  Phase::Start=>{
   r.enter(h,0x100)?;let (seg,off)=farg(h,&mut r,0xe)?;
   let bp=r.get(h,Reg::Bp)?;r.set(Reg::Di,bp.wrapping_sub(0x100) as u32);s.temporary=r.get(h,Reg::Di)?;
   r.set(Reg::Ax,255);let ss=r.ss(h)?;let max=r.get(h,Reg::Ax)?;
   r.store(h,true)?;
   Ok(Action::Call(Request{next:Phase::Copied,saved:s,target:"23E4:0644",ret_to:copied,args:vec![seg,off,ss,s.temporary,max],far:true}))
  }
  Phase::Copied=>{
   if set_attr{
    let value=ssword(h,&mut r,0x12)? as u8;r.set_al(h,value)?;let value=r.al(h)?;
    h.write(lin(h.ds(),0xaab2),&[value],lin(h.seg(0x214b),if s.kind==1{0x223}else{0x2e6}))?;
   }
   let value=ssword(h,&mut r,0xa)? as u8;r.set_al(h,value)?;r.set_ah(h,0)?;
   let ax=r.get(h,Reg::Ax)?;r.set(Reg::Ax,ax.wrapping_shl(1) as u32);let ax=r.get(h,Reg::Ax)?;r.set(Reg::Cx,ax as u32);
   let value=ssword(h,&mut r,0xc)? as u8;r.set_al(h,value)?;r.set_ah(h,0)?;r.set(Reg::Dx,0xa0);
   let src=r.get(h,Reg::Dx)?;let product=r.get(h,Reg::Ax)? as u32*src as u32;r.set(Reg::Ax,product);r.set(Reg::Dx,product>>16);
   farg(h,&mut r,6)?;let es=r.get(h,Reg::Es)?;let di=r.get(h,Reg::Di)?;let ptr=lin(es,di);
   let off=h.u16(ptr)?;let seg=h.u16(ptr+2)?;r.set(Reg::Di,off as u32);r.set(Reg::Es,seg as u32);
   let di=r.get(h,Reg::Di)?;let ax=r.get(h,Reg::Ax)?;let cx=r.get(h,Reg::Cx)?;r.set(Reg::Di,di.wrapping_add(ax).wrapping_add(cx).wrapping_sub(0xa2) as u32);
   let dest_seg=r.get(h,Reg::Es)?;let dest_off=r.get(h,Reg::Di)?;r.flush(h)?;
   let at=h.ss_lin(s.temporary as u32)?;let length=h.u8(at)?;
   if backwards{
    r.set_al(h,length)?;r.set_ah(h,0)?;let ax=r.get(h,Reg::Ax)?;r.set(Reg::Di,ax as u32);
    let bp=r.get(h,Reg::Bp)?;let di=r.get(h,Reg::Di)?;r.set(Reg::Di,bp.wrapping_add(di).wrapping_sub(0x100) as u32);
   }else{let bp=r.get(h,Reg::Bp)?;r.set(Reg::Di,bp.wrapping_sub(0xff) as u32);}
   let source_seg=r.ss(h)?;let source_off=r.get(h,Reg::Di)?;
   let colour=h.u8(lin(h.ds(),0xaab2))?;r.set_al(h,colour)?;r.set_ah(h,0)?;let colour=r.get(h,Reg::Ax)?;
   r.set_al(h,length)?;r.set_ah(h,0)?;let n=r.get(h,Reg::Ax)?;r.store(h,true)?;
   Ok(Action::Call(Request{next:Phase::Written,saved:s,target:if backwards{"214B:0123"}else{"214B:00FF"},ret_to:written,args:vec![dest_seg,dest_off,source_seg,source_off,colour,n],far:!backwards}))
  }
  Phase::Written=>{end(h,&mut r)?;Ok(Action::Done)}
 }
}
