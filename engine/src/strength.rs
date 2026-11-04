//! T27 complete quick-result strength tree,accepted oracle 2cbeb36f.
use crate::host::{args,Host,Reg};
use crate::mem::lin;
use crate::regs::Regs;
pub const BODIES:[&str;7]=["1771:0AA7","1771:0BC4","1771:3041","1771:3088","1771:3179","1771:377E","214B:0C57"];
pub const RETURNS:[&str;12]=["1771:0BE5","1771:0C5C","1771:0C90","1771:0CB1","1771:0CC7","1771:0CEE","1771:379F","1771:3808","1771:319A","1771:31A4","1771:31C0","1771:31DA"];
pub fn index(address:&str)->Option<u32>{BODIES.iter().position(|a|*a==address).map(|i|i as u32)}
#[derive(Clone,Copy,PartialEq,Eq)]
pub enum Phase{Start,Quick,FlagFoot,FlagTwo,FlagRight,FlagLeft,StrengthAvailable,StrengthPlace}
#[derive(Clone,Copy,Default)]
struct Record{seg:u16,off:u16}
#[derive(Clone,Copy,Default)]
pub struct Saved{pub kind:u32,qpc:u16,z:bool,unsigned:i64,signed:i64,v:i64,a:i64,b:i64,off:i64,seg:i64,divisor:i64,q:i64,
 bp:u16,id:u16,record:Record,ax:u16,dx:u16,foot:u8,cs:u16,value:u16}
impl Saved{pub fn new(kind:u32)->Self{Self{kind,qpc:0x0bc4,..Self::default()}}}
pub struct Request{pub next:Phase,pub saved:Saved,pub target:&'static str,pub ret_to:&'static str,pub args:Vec<u16>,pub far:bool}
pub enum Action{Call(Request),Done(Option<u16>)}
fn call(s:Saved,next:Phase,target:&'static str,ret:&'static str,args:Vec<u16>,far:bool)->Action{Action::Call(Request{next,saved:s,target,ret_to:ret,args,far})}
fn stamp<H:Host>(h:&H,pc:u16)->u32{lin(h.seg(0x1771),pc)}
fn arg<H:Host>(h:&mut H,i:u32)->Result<u16,H::Err>{let(sp,far)=h.entry();let a=h.ss_lin(sp+if far{4}else{2}+2*i)?;h.u16(a)}
fn enter<H:Host>(h:&mut H,size:u16,pc:u16)->Result<u16,H::Err>{let sp=(h.reg(Reg::Sp)? as u16).wrapping_sub(2);let a=h.ss_lin(sp as u32)?;let old=h.reg(Reg::Bp)? as u16;
 h.write(a,&old.to_le_bytes(),stamp(h,pc))?;h.set_reg(Reg::Sp,sp as u32)?;h.set_reg(Reg::Bp,sp as u32)?;h.set_reg(Reg::Sp,sp.wrapping_sub(size) as u32)?;Ok(sp)}
fn fw<H:Host>(h:&mut H,bp:u16,k:i32,value:u16,byte:bool,pc:u16)->Result<(),H::Err>{let a=h.ss_lin(bp.wrapping_add(k as u16) as u32)?;let bytes=value.to_le_bytes();h.write(a,&bytes[..if byte{1}else{2}],stamp(h,pc))}
fn record<H:Host>(h:&mut H,ptr:u16,ax:u16)->Result<Record,H::Err>{let a=lin(h.ds(),ptr);let off=h.u16(a)?;let seg=h.u16(a+2)?;Ok(Record{seg,off:off.wrapping_add(ax)})}
fn rec8<H:Host>(h:&mut H,rec:Record,k:u16)->Result<u8,H::Err>{h.u8(lin(rec.seg,rec.off.wrapping_add(k)))}
fn ptr_local<H:Host>(h:&mut H,s:Saved,k:i32,pc1:u16,pc2:u16)->Result<(),H::Err>{fw(h,s.bp,k,s.record.off,false,pc1)?;fw(h,s.bp,k+2,s.record.seg,false,pc2)}
fn done<H:Host>(h:&mut H,ax:u16,dx:u16)->Result<Action,H::Err>{h.set_reg(Reg::Dx,dx as u32)?;Ok(Action::Done(Some(ax)))}
fn gcall<H:Host>(h:&mut H,s:Saved,next:Phase,target:&'static str,ret:&'static str,args:Vec<u16>)->Result<Action,H::Err>{
 h.set_reg(Reg::Ax,s.ax as u32)?;h.set_reg(Reg::Dx,s.dx as u32)?;Ok(call(s,next,target,ret,args,true))}
fn idiv(a:i32,b:i32)->(u16,u16){let q=a/b;(q as u16,(a-q*b) as u16)}
fn read<H:Host>(h:&mut H,r:&mut Regs,seg:u16,off:i64,width:u8)->Result<u16,H::Err>{r.flush(h)?;let a=lin(seg,off as u16);if width==8{Ok(h.u8(a)? as u16)}else{h.u16(a)}}
fn write_regs<H:Host>(h:&mut H,r:&mut Regs,seg:u16,off:i64,width:u8,value:u16,pc:u16)->Result<(),H::Err>{r.flush(h)?;let a=lin(seg,off as u16);let bytes=value.to_le_bytes();h.write(a,&bytes[..if width==8{1}else{2}],stamp(h,pc))}
fn pop<H:Host>(h:&mut H,r:&mut Regs)->Result<u16,H::Err>{let ss=r.ss(h)?;let sp=r.get(h,Reg::Sp)?;let value=read(h,r,ss,sp as i64,16)?;let sp=r.get(h,Reg::Sp)?;r.set(Reg::Sp,sp.wrapping_add(2) as u32);Ok(value)}
include!("strength_quick.inc.rs");

fn flag_end<H:Host>(h:&mut H,s:Saved,flag:u16)->Result<Action,H::Err>{fw(h,s.bp,-1,flag,true,0x320a)?;done(h,(s.ax&0xff00)|flag,s.dx)}
fn mismatch<H:Host>(h:&mut H,s:Saved)->Result<Action,H::Err>{let p6=rec8(h,s.record,6)?;let p7=rec8(h,s.record,7)?;flag_end(h,s,u16::from((p6==0)!=(p7==0)))}
fn left<H:Host>(h:&mut H,mut s:Saved)->Result<Action,H::Err>{
 if s.foot!=0{return mismatch(h,s);}
 s.ax=(s.ax&0xff00)|rec8(h,s.record,6)? as u16;
 gcall(h,s,Phase::FlagLeft,"23E4:08DF","1771:31DA",vec![s.ax,s.cs,0x3159])
}
pub fn step<H:Host>(h:&mut H,phase:Phase,mut s:Saved,sent:u16)->Result<Action,H::Err>{
 if s.kind==1{return quick(h,phase!=Phase::Start,s);}
 if phase!=Phase::Start{s.ax=sent;s.dx=h.reg(Reg::Dx)? as u16;}
 match phase{
 Phase::Start=>match s.kind{
  0=>{s.bp=enter(h,6,0x0aa7)?;let id=arg(h,0)?;let p=id as u32*191;s.record=record(h,0xa917,p as u16)?;ptr_local(h,s,-6,0x0abb,0x0abe)?;
   let manager=rec8(h,s.record,0x2e)?;let manager_record=record(h,0xa91f,manager as u16*3)?;let value=rec8(h,manager_record,1)? as u16;
   fw(h,s.bp,-2,value/8+16,false,0x0ae4)?;done(h,value/8+16,value%8)}
  2=>{s.bp=enter(h,6,0x3041)?;let n=arg(h,0)?;let p=n as u32*20;s.record=record(h,0xa91b,p as u16)?;ptr_local(h,s,-5,0x3055,0x3058)?;
   let dx=rec8(h,s.record,5)? as u16;let total=rec8(h,s.record,2)? as u16+dx;let flag=u16::from(total==30);
   fw(h,s.bp,-1,flag,true,0x307c)?;done(h,(total&0xff00)|flag,dx)}
  3=>{s.id=arg(h,0)?;s.bp=enter(h,6,0x3088)?;let p=s.id as u32*20;s.record=record(h,0xa91b,p as u16)?;ptr_local(h,s,-5,0x309c,0x309f)?;
   let bx=rec8(h,s.record,7)? as u16;let row=h.u8(lin(h.ds(),0xe7c+s.id%3))?;let p=row as u32*14;let ax=p as u16;
   let value=h.u8(lin(h.ds(),0xe60u16.wrapping_add(ax.wrapping_add(bx))))? as u16;
   fw(h,s.bp,-1,value,true,0x30cd)?;done(h,(ax&0xff00)|value,(p>>16) as u16)}
  4=>{s.id=arg(h,0)?;s.bp=enter(h,6,0x3179)?;let p=s.id as u32*20;s.ax=p as u16;s.dx=(p>>16) as u16;s.record=record(h,0xa91b,s.ax)?;ptr_local(h,s,-6,0x318d,0x3190)?;
   gcall(h,s,Phase::FlagFoot,"1771:3088","1771:319A",vec![s.id])}
  5=>{s.id=arg(h,0)?;s.bp=enter(h,8,0x377e)?;let p=s.id as u32*20;s.ax=p as u16;s.dx=(p>>16) as u16;s.record=record(h,0xa91b,s.ax)?;ptr_local(h,s,-8,0x3792,0x3795)?;
   gcall(h,s,Phase::StrengthAvailable,"1771:3216","1771:379F",vec![s.id])}
  6=>{let a=args(h,2)?;let(value,k)=(a[0],a[1]);let mut r=Regs::new(false);r.enter(h,2)?;let dx=k.wrapping_sub(1);r.set(Reg::Dx,dx as u32);r.set(Reg::Cx,dx as u32);
   let bit=((value as u32)>>((dx as u8)&31))&1;r.set(Reg::Ax,bit);let al=r.al(h)?;r.local8(h,-1,al)?;r.leave(h)?;r.store(h,false)?;Ok(Action::Done(None))}
  _=>unreachable!()},
 Phase::FlagFoot=>{s.foot=s.ax as u8;fw(h,s.bp,-2,s.foot as u16,true,0x319a)?;gcall(h,s,Phase::FlagTwo,"1771:3041","1771:31A4",vec![s.id])}
 Phase::FlagTwo=>{s.cs=h.reg(Reg::Cs)? as u16;if s.ax&255==0 && s.foot!=0{s.ax=(s.ax&0xff00)|rec8(h,s.record,6)? as u16;
  gcall(h,s,Phase::FlagRight,"23E4:08DF","1771:31C0",vec![s.ax,s.cs,0x3139])}else{left(h,s)}}
 Phase::FlagRight=>{if h.reg(Reg::Eflags)?&64==0{flag_end(h,s,1)}else{left(h,s)}}
 Phase::FlagLeft=>{if h.reg(Reg::Eflags)?&64==0{flag_end(h,s,1)}else{mismatch(h,s)}}
 Phase::StrengthAvailable=>{
  if s.ax&255!=0{fw(h,s.bp,-2,0,false,0x37a5)?;return done(h,0,s.dx);}
  s.dx=(rec8(h,s.record,14)? as i8 as i16) as u16;
  let ability=rec8(h,s.record,4)?;let mut value=(ability as u16).wrapping_sub(62).wrapping_add(s.dx);s.ax=value;
  let confidence=rec8(h,s.record,12)? as i8 as i32;
  if confidence>=32{let(q,rem)=idiv(value as i16 as i32,16);s.dx=rem;value=value.wrapping_sub(q);s.ax=q;}
  else{s.ax=confidence as u16;value=value.wrapping_add(confidence as u16);}
  if (value as i16)<0{value=0;s.ax=0;}else if (value as i16)>256{value=256;}
  s.value=value;fw(h,s.bp,-4,value,false,0x3801)?;gcall(h,s,Phase::StrengthPlace,"1771:3179","1771:3808",vec![s.id])
 }
 Phase::StrengthPlace=>{if s.ax&255!=0{let(q,rem)=idiv(s.value as i16 as i32,2);s.dx=rem;s.value=q;s.ax=q;fw(h,s.bp,-4,q,false,0x3815)?;}else{s.ax=s.value;}
  fw(h,s.bp,-2,s.value,false,0x381b)?;done(h,s.value,s.dx)}
 Phase::Quick=>unreachable!(),
 }
}
