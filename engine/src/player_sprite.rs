//! motion.move_player_sprite 0791:8537, accepted 2cbeb36f; immediate Mem semantics.
use crate::host::{Host,Reg};
use crate::mem::{lin,cbw};
#[derive(Clone,Copy)]
pub struct Saved{pub off:u16,pub seg:u16,pub rec:u32,pub ax:u16}
#[derive(Clone,Copy,PartialEq,Eq)]
pub enum Phase{Start,Holder,Keeper,Intercept,Direction,Draw}
pub struct Request{pub next:Phase,pub saved:Saved,pub target:&'static str,pub ret_to:&'static str,pub args:Vec<u16>,pub far:bool}
pub enum Action{Call(Request),Done}
fn ds8<H:Host>(h:&mut H,o:u16)->Result<u8,H::Err>{h.u8(lin(h.ds(),o))}
fn ds16<H:Host>(h:&mut H,o:u16)->Result<u16,H::Err>{h.u16(lin(h.ds(),o))}
fn write<H:Host>(h:&mut H,a:u32,b:&[u8],site:u16)->Result<(),H::Err>{h.write(a,b,lin(h.seg(0x0791),site))}
fn wds<H:Host>(h:&mut H,value:u8,site:u16)->Result<(),H::Err>{write(h,lin(h.ds(),0x82f7),&[value],site)}
fn ax<H:Host>(h:&mut H,x:u16)->Result<(),H::Err>{h.set_reg(Reg::Ax,x as u32)}
fn product(row:u8)->(u16,u16){let p=cbw(row) as u32*160;(p as u16,(p>>16) as u16)}
fn cell<H:Host>(h:&mut H,p:u16,row:u8,col:u8)->Result<u32,H::Err>{
 let off=ds16(h,p)?;let seg=ds16(h,p+2)?;
 let di=off.wrapping_add(product(row).0).wrapping_add(cbw(col).wrapping_shl(1));
 Ok(lin(seg,di.wrapping_add(0x90e)))
}
fn call(s:Saved,next:Phase,target:&'static str,ret:&'static str,args:Vec<u16>,far:bool)->Action{Action::Call(Request{next,saved:s,target,ret_to:ret,args,far})}
fn done<H:Host>(h:&mut H,mutant:bool)->Result<Action,H::Err>{
 if mutant{let a=h.ss_lin((h.entry().0 as u16).wrapping_sub(2) as u32)?;let old=h.u16(a)?;h.write(a,&(old^1).to_le_bytes(),lin(h.seg(0x214b),0))?;}
 Ok(Action::Done)
}
fn draw<H:Host>(h:&mut H,s:Saved)->Result<Action,H::Err>{
 ax(h,s.ax)?;h.set_reg(Reg::Di,0x82f6)?;
 // Source mem.reg("ds") is observable; Host DS is the fixed view property.
 // The machine bridge supplies this call's DS argument separately.
 Ok(call(s,Phase::Draw,"0791:8F10","0791:8699",vec![h.ds(),0x82f6],true))
}
fn clamps<H:Host>(h:&mut H,s:Saved)->Result<Action,H::Err>{
 if ds8(h,0x82f7)?==0x26{wds(h,0x24,0x867f)?;}
 if ds8(h,0x82f7)?==0xda{wds(h,0xdc,0x868b)?;}
 draw(h,s)
}
fn movement<H:Host>(h:&mut H,mut s:Saved)->Result<Action,H::Err>{
 let state=h.u8(s.rec+0xf)?;s.ax=(s.ax&0xff00)|state as u16;
 match state{
  1|2|5=>{ax(h,s.ax)?;return Ok(call(s,Phase::Direction,"0791:2BE5","0791:8660",vec![s.seg,s.off],true));}
  3=>{let b=ds8(h,0x82f7)?;wds(h,b.wrapping_sub(1),0x866a)?;}
  4=>{let b=ds8(h,0x82f7)?;wds(h,b.wrapping_add(1),0x8674)?;}
  _=>{}
 }clamps(h,s)
}
pub fn step<H:Host>(h:&mut H,phase:Phase,saved:Option<Saved>,sent:u16,mutant:bool)->Result<Action,H::Err>{
 if phase==Phase::Start{
  let bp=(h.reg(Reg::Sp)? as u16).wrapping_sub(2);let a=h.ss_lin(bp as u32)?;let old=h.reg(Reg::Bp)? as u16;
  write(h,a,&old.to_le_bytes(),0x8537)?;h.set_reg(Reg::Sp,bp as u32)?;h.set_reg(Reg::Bp,bp as u32)?;h.set_reg(Reg::Sp,bp as u32)?;
  let a=h.ss_lin(bp.wrapping_add(6) as u32)?;let off=h.u16(a)?;let seg=h.u16(a+2)?;let rec=lin(seg,off);
  let sentinel=ds16(h,0x640)?;let old=h.u16(rec+2)?;
  if old!=sentinel&&old!=h.u16(rec)?{
   let row=h.u8(rec+2)?;let col=h.u8(rec+3)?;let a=cell(h,0x7c1e,row,col)?;let bx=h.u16(a)?;
   let a=cell(h,0x7c16,row,col)?;write(h,a,&bx.to_le_bytes(),0x859d)?;
   h.set_reg(Reg::Dx,product(row).1 as u32)?;
  }
  let pos=h.u16(rec)?;write(h,rec+2,&pos.to_le_bytes(),0x85ab)?;let mut value=pos;
  if pos!=sentinel{
   let held=if h.u8(rec+4)?==1{let held=ds8(h,0x830b)?;held==h.u8(rec+6)?}else{false};
   let bx=(held as u16).wrapping_add(h.u16(rec+4)?);let row=h.u8(rec)?;let col=h.u8(rec+1)?;
   let a=cell(h,0x7c16,row,col)?;write(h,a,&bx.to_le_bytes(),0x8602)?;
   let (lo,hi)=product(row);value=lo;h.set_reg(Reg::Dx,hi as u32)?;
  }
  ax(h,value)?;let s=Saved{off,seg,rec,ax:value};return Ok(call(s,Phase::Holder,"0791:2C29","0791:8610",vec![seg,off],true));
 }
 let mut s=saved.unwrap();
 match phase{
  Phase::Holder=>{
   s.ax=sent;if sent&255==0{return done(h,mutant);}
   let pos=h.u16(s.rec)?;write(h,lin(h.ds(),0x82f6),&pos.to_le_bytes(),0x861d)?;
   s.ax=h.u8(s.rec+6)? as u16;ax(h,s.ax)?;Ok(call(s,Phase::Keeper,"0791:045D","0791:862D",vec![s.ax],false))
  }
  Phase::Keeper=>{
   s.ax=sent;if sent&255!=0{let pos=h.u16(s.rec)?;return Ok(call(s,Phase::Intercept,"0791:2EB8","0791:8640",vec![pos,s.seg,s.off],true));}
   movement(h,s)
  }
  Phase::Intercept=>{s.ax=sent;if sent&255!=0{draw(h,s)}else{movement(h,s)}}
  Phase::Direction=>{s.ax=sent;let b=ds8(h,0x82f7)?;wds(h,b.wrapping_add(sent as u8),0x8660)?;clamps(h,s)}
  Phase::Draw=>done(h,mutant),
  Phase::Start=>unreachable!(),
 }
}
