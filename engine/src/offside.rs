//! T22 closed offside-line/display tree, accepted oracle 2cbeb36f.
use crate::host::{Host,Reg};
use crate::mem::{lin,cbw};
#[derive(Clone,Copy,PartialEq,Eq)]
pub enum Phase { Start,Direction,Sprite,Marker,MarkerStart,MarkerDraw }
#[derive(Clone,Copy)]
pub struct Saved { side:u16,line_off:u16,line:u32,first:u16 }
pub struct Request { pub next:Phase,pub saved:Saved,pub target:&'static str,pub ret_to:&'static str,pub args:Vec<u16>,pub live_ds:bool }
pub enum Action { Call(Request),Done }
fn ds8<H:Host>(h:&mut H,o:u16)->Result<u8,H::Err>{h.u8(lin(h.ds(),o))}
fn ds16<H:Host>(h:&mut H,o:u16)->Result<u16,H::Err>{h.u16(lin(h.ds(),o))}
fn write<H:Host>(h:&mut H,a:u32,b:&[u8],pc:u16)->Result<(),H::Err>{h.write(a,b,lin(h.seg(0x791),pc))}
fn enter<H:Host>(h:&mut H,n:u16,pc:u16)->Result<u16,H::Err>{
 let bp=(h.reg(Reg::Sp)? as u16).wrapping_sub(2);let a=h.ss_lin(bp as u32)?;let old=h.reg(Reg::Bp)? as u16;
 write(h,a,&old.to_le_bytes(),pc)?;h.set_reg(Reg::Sp,bp as u32)?;h.set_reg(Reg::Bp,bp as u32)?;h.set_reg(Reg::Sp,bp.wrapping_sub(n) as u32)?;Ok(bp)
}
fn frame8<H:Host>(h:&mut H,bp:u16,k:u16)->Result<u8,H::Err>{let a=h.ss_lin(bp.wrapping_add(k) as u32)?;h.u8(a)}
fn frame16<H:Host>(h:&mut H,bp:u16,k:u16)->Result<u16,H::Err>{let a=h.ss_lin(bp.wrapping_add(k) as u32)?;h.u16(a)}
fn record<H:Host>(h:&mut H,bp:u16)->Result<(u16,u16,u32),H::Err>{let a=h.ss_lin(bp.wrapping_add(6) as u32)?;let off=h.u16(a)?;let seg=h.u16(a+2)?;Ok((off,seg,lin(seg,off)))}
fn product(row:u8)->(u16,u16){let p=cbw(row) as u32*160;(p as u16,(p>>16) as u16)}
fn cell<H:Host>(h:&mut H,p:u16,row:u8,col:u8)->Result<u32,H::Err>{
 let off=ds16(h,p)?;let seg=ds16(h,p+2)?;let di=off.wrapping_add(product(row).0).wrapping_add(cbw(col).wrapping_shl(1));Ok(lin(seg,di.wrapping_add(0x90e)))
}
pub fn sprite<H:Host>(h:&mut H)->Result<u16,H::Err>{
 let bp=enter(h,0,0x8e24)?;let (_,_,rec)=record(h,bp)?;
 let old=h.u16(rec+2)?;let current=h.u16(rec)?;
 if old!=current {
  let row=h.u8(rec+2)?;let col=h.u8(rec+3)?;let a=cell(h,0x7c16,row,col)?;let value=h.u16(a)?;
  if value==h.u16(rec+4)? {
   let a=cell(h,0x7c1e,row,col)?;let bx=h.u16(a)?;let a=cell(h,0x7c16,row,col)?;write(h,a,&bx.to_le_bytes(),0x8eac)?;
  }
 }
 let value=h.u16(rec)?;write(h,rec+2,&value.to_le_bytes(),0x8eba)?;
 let bx=h.u16(rec+4)?;let row=h.u8(rec)?;let col=h.u8(rec+1)?;let a=cell(h,0x7c16,row,col)?;write(h,a,&bx.to_le_bytes(),0x8ee5)?;
 let (ax,dx)=product(row);h.set_reg(Reg::Dx,dx as u32)?;Ok(ax)
}
fn call(s:Saved,next:Phase,target:&'static str,ret_to:&'static str,args:Vec<u16>,live_ds:bool)->Action{Action::Call(Request{next,saved:s,target,ret_to,args,live_ds})}
fn begin_side<H:Host>(h:&mut H,side:u16)->Result<Action,H::Err>{
 let line_off=0x82e2+side*6;let line=lin(h.ds(),line_off);write(h,line+1,&[0],0x8d1f)?;
 let first=ds8(h,0x668+side)? as u16;let ax=(first+1)*0x16;let di=ax.wrapping_add(0x80e8);
 h.set_reg(Reg::Ax,ax as u32)?;h.set_reg(Reg::Dx,0)?;h.set_reg(Reg::Di,di as u32)?;
 Ok(call(Saved{side,line_off,line,first},Phase::Direction,"0791:2BE5","0791:8D42",vec![h.ds(),di],true))
}
fn next<H:Host>(h:&mut H,s:Saved)->Result<Action,H::Err>{if s.side==0{begin_side(h,1)}else{Ok(Action::Done)}}
pub fn first(p:Phase)->bool{matches!(p,Phase::Start|Phase::MarkerStart)}
pub fn step<H:Host>(h:&mut H,p:Phase,saved:Option<Saved>,sent:u16)->Result<Action,H::Err>{
 match p {
  Phase::Start=>{enter(h,12,0x8cf5)?;begin_side(h,0)}
  Phase::Direction=>{
   let s=saved.unwrap();let d=cbw(sent as u8) as i16 as i32;
   for k in s.first+2..=s.first+11 {
    let cx=h.u8(s.line+1)? as i8 as i32;let di=k.wrapping_mul(0x16);let y=ds8(h,di.wrapping_add(0x80e9))?;let ax=((y as i8 as i32)*d) as u16;
    if (ax as i16 as i32)<cx{write(h,s.line+1,&[ax as u8],0x8da9)?;}
   }
   let row=h.u8(s.line+1)?;let value=(row as i8 as i32)*d;let ax=value as u16;let dx=(value>>16) as u16;
   write(h,s.line+1,&[ax as u8],0x8dc3)?;h.set_reg(Reg::Ax,ax as u32)?;h.set_reg(Reg::Dx,dx as u32)?;h.set_reg(Reg::Di,s.line_off as u32)?;
   Ok(call(s,Phase::Sprite,"0791:8E24","0791:8DD0",vec![h.ds(),s.line_off],true))
  }
  Phase::Sprite=>{
   let s=saved.unwrap();let dl=u8::from((h.u8(s.line+1)? as i8)>0);let dx=h.reg(Reg::Dx)? as u16;
   let al=u8::from((ds8(h,0x82f7)? as i8)>0);let ax=(sent&0xff00)|al as u16;let dx=(dx&0xff00)|dl as u16;
   h.set_reg(Reg::Ax,ax as u32)?;h.set_reg(Reg::Dx,dx as u32)?;
   if al==dl && ds8(h,0x8328)?!=0 && h.u8(s.line+1)?!=0 {
    h.set_reg(Reg::Di,0x8304)?;let sprite=ds16(h,0x8308)?;let point=h.u16(s.line)?;
    Ok(call(s,Phase::Marker,"0791:90C5","0791:8E17",vec![sprite,point,h.ds(),0x8304],true))
   }else{next(h,s)}
  }
  Phase::Marker=>next(h,saved.unwrap()),
  Phase::MarkerStart=>{
   let bp=enter(h,0,0x90c5)?;let (off,seg,rec)=record(h,bp)?;let sprite=frame16(h,bp,12)?;write(h,rec+4,&sprite.to_le_bytes(),0x90ce)?;
   let index=if h.u16(rec+4)?==0x0eae{0}else{1};let dx=cbw(ds8(h,0x7920+index)?);let row=frame8(h,bp,11)?;let ax=cbw(row).wrapping_add(dx);write(h,rec+1,&[ax as u8],0x90f6)?;
   let col=frame8(h,bp,10)?;let ax=(ax&0xff00)|col as u16;write(h,rec,&[ax as u8],0x9100)?;
   h.set_reg(Reg::Ax,ax as u32)?;h.set_reg(Reg::Dx,dx as u32)?;
   if ds8(h,0x9a3e)?==0{Ok(call(Saved{side:0,line_off:0,line:0,first:0},Phase::MarkerDraw,"0791:8E24","0791:9113",vec![seg,off],false))}else{Ok(Action::Done)}
  }
  Phase::MarkerDraw=>Ok(Action::Done),
 }
}
