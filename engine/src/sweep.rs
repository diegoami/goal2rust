//! frame.watched_match_engine9564, accepted2cbeb36f: immediate Mem.Frame, not Regs.
use crate::host::{Host,Reg};
use crate::mem::lin;
#[derive(Clone,Copy)]
pub struct Saved {pub bp:u16,pub ds:u16,pub cs:u16,pub slot:u32,pub k:u32,pub rec:u16}
#[derive(Clone,Copy,PartialEq,Eq)]
pub enum Phase {Start,Gate,Direction,Moved,Nearest,Side,HolderMember,HolderAt,HolderDirection,HolderUpdated,PlayCheck,Inner,Available,PlayerUpdated,Recomputed,SpeakerDone,DrawDone,KeyDone}
pub struct Request {pub next:Phase,pub saved:Saved,pub target:&'static str,pub ret_to:&'static str,pub args:Vec<u16>,pub far:bool}
fn ds8<H:Host>(h:&mut H,s:Saved,off:u32)->Result<u8,H::Err>{h.u8(lin(s.ds,off as u16))}
fn ds16<H:Host>(h:&mut H,s:Saved,off:u16)->Result<u16,H::Err>{h.u16(lin(s.ds,off))}
fn wds16<H:Host>(h:&mut H,s:Saved,off:u16,v:u16,site:u16)->Result<(),H::Err>{h.write(lin(s.ds,off),&v.to_le_bytes(),lin(s.cs,site))}
fn local<H:Host>(h:&mut H,s:Saved,off:i16,v:u16,site:u16)->Result<(),H::Err>{let at=h.ss_lin(s.bp.wrapping_add(off as u16) as u32)?;h.write(at,&v.to_le_bytes(),lin(s.cs,site))}
fn local_read<H:Host>(h:&mut H,s:Saved,off:i16)->Result<u16,H::Err>{let at=h.ss_lin(s.bp.wrapping_add(off as u16) as u32)?;h.u16(at)}
fn ax<H:Host>(h:&mut H,v:u32)->Result<u16,H::Err>{let v=v as u16;h.set_reg(Reg::Ax,v as u32)?;Ok(v)}
fn al<H:Host>(h:&mut H,v:u8)->Result<u16,H::Err>{let old=h.reg(Reg::Ax)? as u16;ax(h,((old&0xff00)|v as u16) as u32)}
fn product<H:Host>(h:&mut H,a:u32,b:u32)->Result<u32,H::Err>{let p=a*b;h.set_reg(Reg::Ax,p&0xffff)?;h.set_reg(Reg::Dx,(p>>16)&0xffff)?;Ok(p)}
fn call(s:Saved,site:u16,args:Vec<u16>)->Option<Request>{
 let (target,far,ret_to,next)=match site {
  0x9592=>("23E4:08DF",true,"0791:9597",Phase::Gate),
  0x95c6=>("0791:2BE5",true,"0791:95C9",Phase::Direction),
  0x95f8=>("0791:83A2",true,"0791:95FB",Phase::Moved),
  0x95fb=>("0791:2FB1",false,"0791:95FE",Phase::Nearest),
  0x95fe=>("0791:2996",false,"0791:9601",Phase::Side),
  0x962f=>("23E4:08DF",true,"0791:9634",Phase::HolderMember),
  0x963c=>("0791:2CEC",true,"0791:963F",Phase::HolderAt),
  0x9659=>("0791:2E36",true,"0791:965C",Phase::HolderDirection),
  0x9666=>("0791:8AE9",true,"0791:9669",Phase::HolderUpdated),
  0x9669=>("0791:59B3",false,"0791:966C",Phase::PlayCheck),
  0x9692=>("0791:6188",true,"0791:9695",Phase::Inner),
  0x96bb=>("0791:2956",true,"0791:96BE",Phase::Available),
  0x96c8=>("0791:8AE9",true,"0791:96CB",Phase::PlayerUpdated),
  0x96d8=>("0791:2FB1",false,"0791:96DB",Phase::Recomputed),
  0x96db=>("0791:94E8",false,"0791:96DE",Phase::SpeakerDone),
  0x96e4=>("0791:8F10",true,"0791:96E7",Phase::DrawDone),
  0x96e7=>("0791:9372",false,"0791:96EA",Phase::KeyDone),
  _=>unreachable!(),
 };Some(Request{next,saved:s,target,ret_to,args,far})
}
fn end<H:Host>(h:&mut H,mutant:bool)->Result<Option<Request>,H::Err>{
 if mutant{let at=h.ss_lin((h.entry().0 as u16).wrapping_sub(2) as u32)?;let old=h.u16(at)?;h.write(at,&(old^1).to_le_bytes(),lin(h.seg(0x214b),0))?;}
 Ok(None)
}
fn player<H:Host>(h:&mut H,mut s:Saved)->Result<Option<Request>,H::Err>{
 let first=ds8(h,s,0x883+s.slot)?;ax(h,first as u32)?;
 let next=ds8(h,s,0x883+s.slot)?;let p=product(h,next as u32,0x16)?;
 s.rec=(p as u16).wrapping_add(0x80e8);
 local(h,s,-8,s.rec,0x96af)?;local(h,s,-6,s.ds,0x96b2)?;
 Ok(call(s,0x96bb,vec![s.ds,s.rec]))
}
fn inner<H:Host>(h:&mut H,mut s:Saved)->Result<Option<Request>,H::Err>{
 loop{
  if ds8(h,s,0x8302)?!=0{let p=product(h,s.k,0x16)?;let rec=(p as u16).wrapping_add(0x80e8);return Ok(call(s,0x9692,vec![s.ds,rec]));}
  if s.k==0x16{return player(h,s);}s.k+=1;local(h,s,-4,s.k as u16,0x9677)?;
 }
}
fn moved<H:Host>(h:&mut H,s:Saved)->Result<Option<Request>,H::Err>{h.set_reg(Reg::Di,0x82f6)?;Ok(call(s,0x95f8,vec![s.ds,0x82f6]))}
fn gate<H:Host>(h:&mut H,s:Saved,flag:u32)->Result<Option<Request>,H::Err>{
 product(h,flag,0x16)?;
 let sp=(h.reg(Reg::Sp)? as u16).wrapping_add(2);h.set_reg(Reg::Sp,sp as u32)?;ax(h,s.slot)?;
 let value=ds8(h,s,flag*0x16+s.slot+0x899)?;ax(h,value as u32)?;
 if value as u16<=ds16(h,s,0x8300)?{
  if ds8(h,s,0x82f7)?!=0{h.set_reg(Reg::Di,0x80fe)?;return Ok(call(s,0x95c6,vec![s.ds,0x80fe]));}
  return moved(h,s);
 }player(h,s)
}
fn start_slot<H:Host>(h:&mut H,s:Saved)->Result<Option<Request>,H::Err>{
 if ds8(h,s,0x8302)?!=0{
  let value=ax(h,s.slot)?;let sp=(h.reg(Reg::Sp)? as u16).wrapping_sub(2);h.set_reg(Reg::Sp,sp as u32)?;
  let at=h.ss_lin(sp as u32)?;h.write(at,&value.to_le_bytes(),lin(s.cs,0x9581))?;
  if ds8(h,s,0x8303)?!=0{let value=ds8(h,s,0x8327)?;let a=al(h,value)?;h.set_reg(Reg::Di,0x9544)?;return Ok(call(s,0x9592,vec![a,s.cs,0x9544]));}
  return gate(h,s,0);
 }player(h,s)
}
fn after_player<H:Host>(h:&mut H,s:Saved)->Result<Option<Request>,H::Err>{
 let slot=ds8(h,s,0x883+s.slot)?;let holder=ds8(h,s,0x830b)?;
 if slot==holder{return Ok(call(s,0x96d8,vec![]));}Ok(call(s,0x96db,vec![]))
}
pub fn step<H:Host>(h:&mut H,phase:Phase,saved:Option<Saved>,mutant:bool)->Result<Option<Request>,H::Err>{
 if phase==Phase::Start{
  let sp=(h.reg(Reg::Sp)? as u16).wrapping_sub(2);let at=h.ss_lin(sp as u32)?;let bp=h.reg(Reg::Bp)? as u16;
  h.write(at,&bp.to_le_bytes(),lin(h.seg(0x0791),0x9564))?;
  h.set_reg(Reg::Sp,sp as u32)?;h.set_reg(Reg::Bp,sp as u32)?;h.set_reg(Reg::Sp,sp.wrapping_sub(8) as u32)?;
  let s=Saved{bp:sp,ds:h.ds(),cs:h.seg(0x0791),slot:1,k:0,rec:0};local(h,s,-2,1,0x956a)?;
  return start_slot(h,s);
 }
 let mut s=saved.unwrap();
 match phase{
  Phase::Gate=>{let flag=u32::from(h.reg(Reg::Eflags)?&0x40!=0);gate(h,s,flag)}
  Phase::Direction=>{
   let direction=(h.reg(Reg::Ax)?&255) as u8;let dx=h.reg(Reg::Dx)?;h.set_reg(Reg::Dx,(dx&0xff00)|direction as u32)?;
   let ahead=u32::from(ds8(h,s,0x82f7)? as i8>0);let same=u16::from(ds8(h,s,0x7920+ahead)?==direction);
   let counter=0x80f6+2*same;let old=ds16(h,s,counter)?;wds16(h,s,counter,old.wrapping_add(1),0x95ee)?;moved(h,s)
  }
  Phase::Moved=>Ok(call(s,0x95fb,vec![])),
  Phase::Nearest=>Ok(call(s,0x95fe,vec![])),
  Phase::Side=>{
   let side=u32::from(h.reg(Reg::Ax)?&255==0);al(h,side as u8)?;
   let held=(ds8(h,s,0x668+side)? as u16).wrapping_add(1);let p=product(h,held as u32,0x16)?;s.rec=(p as u16).wrapping_add(0x80e8);
   local(h,s,-8,s.rec,0x9620)?;local(h,s,-6,s.ds,0x9623)?;
   let b=ds8(h,s,0x8327)?;let a=al(h,b)?;h.set_reg(Reg::Di,0x9544)?;Ok(call(s,0x962f,vec![a,s.cs,0x9544]))
  }
  Phase::HolderMember=>{
   if h.reg(Reg::Eflags)?&0x40==0{return Ok(call(s,0x963c,vec![s.ds,s.rec]));}Ok(call(s,0x9669,vec![]))
  }
  Phase::HolderAt=>{
   if h.reg(Reg::Ax)?&255==0{
    let x=h.u8(lin(s.ds,s.rec))?;let ball=ds8(h,s,0x82f6)?;
    if x==ball{let point=ds16(h,s,0x82f6)?;return Ok(call(s,0x9659,vec![point,s.ds,s.rec]));}
    return Ok(call(s,0x9666,vec![s.ds,s.rec]));
   }Ok(call(s,0x9669,vec![]))
  }
  Phase::HolderDirection=>{if h.reg(Reg::Ax)?&255!=0{return Ok(call(s,0x9666,vec![s.ds,s.rec]));}Ok(call(s,0x9669,vec![]))}
  Phase::HolderUpdated=>Ok(call(s,0x9669,vec![])),
  Phase::PlayCheck=>{if h.reg(Reg::Ax)?&255==0{local(h,s,-4,1,0x9670)?;s.k=1;return inner(h,s);}player(h,s)}
  Phase::Inner=>{if s.k==0x16{return player(h,s);}s.k+=1;local(h,s,-4,s.k as u16,0x9677)?;inner(h,s)}
  Phase::Available=>{if h.reg(Reg::Ax)?&255==0{return Ok(call(s,0x96c8,vec![s.ds,s.rec]));}after_player(h,s)}
  Phase::PlayerUpdated=>after_player(h,s),
  Phase::Recomputed=>Ok(call(s,0x96db,vec![])),
  Phase::SpeakerDone=>{h.set_reg(Reg::Di,0x82f6)?;Ok(call(s,0x96e4,vec![s.ds,0x82f6]))}
  Phase::DrawDone=>Ok(call(s,0x96e7,vec![])),
  Phase::KeyDone=>{
   if ds8(h,s,0x9a3e)?!=0{return end(h,mutant);}
   if local_read(h,s,-2)?!=0x16{s.slot+=1;local(h,s,-2,s.slot as u16,0x9571)?;return start_slot(h,s);}
   let wait=ds16(h,s,0x832a)?;if wait!=0{wds16(h,s,0x832a,wait.wrapping_sub(2),0x9703)?;}end(h,mutant)
  }
  Phase::Start=>unreachable!(),
 }
}
