//! T20 closed chase gate and inline goal-strip queries, oracle2cbeb36f.
use crate::host::{args,Host,Reg};
use crate::mem::lin;
use crate::regs::{invoke,Regs};
#[derive(Clone,Copy,PartialEq,Eq)]
pub enum Phase {Start,Keeper,Side,OwnStrip,OpposingStrip,Tactic}
pub struct Request {pub next:Phase,pub target:&'static str,pub ret_to:&'static str,pub args:Vec<u16>,pub far:bool}
pub enum Action {Call(Request),Done(u16)}
fn ds16<H:Host>(h:&mut H,k:u16)->Result<u16,H::Err>{h.u16(lin(h.ds(),k))}
fn ss16<H:Host>(h:&mut H,r:&mut Regs,k:u16)->Result<u16,H::Err>{r.flush(h)?;let at=h.ss_lin(k as u32)?;h.u16(at)}
fn nested<H:Host>(h:&mut H,r:&mut Regs)->Result<(u16,u16),H::Err>{let bp=r.get(h,Reg::Bp)?;let di=ss16(h,r,bp.wrapping_add(4))?;r.set(Reg::Di,di as u32);let di=r.get(h,Reg::Di)?;let seg=ss16(h,r,di.wrapping_add(8))?;let off=ss16(h,r,di.wrapping_add(6))?;r.set(Reg::Es,seg as u32);r.set(Reg::Di,off as u32);let seg=r.get(h,Reg::Es)?;let off=r.get(h,Reg::Di)?;Ok((seg,off))}
fn rb<H:Host>(h:&mut H,r:&mut Regs,k:u16)->Result<u8,H::Err>{let seg=r.get(h,Reg::Es)?;let off=r.get(h,Reg::Di)?;h.u8(lin(seg,off.wrapping_add(k)))}
fn rw<H:Host>(h:&mut H,r:&mut Regs,k:u16)->Result<u16,H::Err>{let seg=r.get(h,Reg::Es)?;let off=r.get(h,Reg::Di)?;h.u16(lin(seg,off.wrapping_add(k)))}
fn request<H:Host>(h:&mut H,r:&mut Regs,next:Phase,target:&'static str,ret_to:&'static str,args:Vec<u16>,far:bool)->Result<Action,H::Err>{r.store(h,true)?;Ok(Action::Call(Request{next,target,ret_to,args,far}))}
fn finish<H:Host>(h:&mut H,r:&mut Regs,yes:bool)->Result<Action,H::Err>{r.set_al(h,u8::from(yes))?;let al=r.al(h)?;r.local8(h,-1,al)?;r.leave(h)?;r.store(h,false)?;let ax=r.get(h,Reg::Ax)?;Ok(Action::Done(ax))}
pub fn step<H:Host>(h:&mut H,phase:Phase)->Result<Action,H::Err>{let mut r=Regs::new(phase!=Phase::Start);match phase{
 Phase::Start=>{r.enter(h,2)?;nested(h,&mut r)?;let slot=rb(h,&mut r,6)?;r.set_al(h,slot)?;r.set_ah(h,0)?;let ax=r.get(h,Reg::Ax)?;request(h,&mut r,Phase::Keeper,"0791:045D","0791:5740",vec![ax],false)}
 Phase::Keeper=>{if r.al(h)?!=0{return finish(h,&mut r,false);}let(seg,off)=nested(h,&mut r)?;request(h,&mut r,Phase::Side,"0791:2B51","0791:5751",vec![seg,off],true)}
 Phase::Side=>{if r.al(h)?!=0{return finish(h,&mut r,false);}let point=ds16(h,0x82f6)?;let(seg,off)=nested(h,&mut r)?;request(h,&mut r,Phase::OwnStrip,"0791:2EB8","0791:5766",vec![point,seg,off],true)}
 Phase::OwnStrip=>{if r.al(h)?==0{return finish(h,&mut r,false);}nested(h,&mut r)?;let point=rw(h,&mut r,0)?;let(seg,off)=nested(h,&mut r)?;request(h,&mut r,Phase::OpposingStrip,"0791:2EF0","0791:5781",vec![point,seg,off],true)}
 Phase::OpposingStrip=>{if r.al(h)?!=0{return finish(h,&mut r,true);}r.set(Reg::Ax,6);let(seg,off)=nested(h,&mut r)?;request(h,&mut r,Phase::Tactic,"0791:26D7","0791:5796",vec![6,seg,off],true)}
 Phase::Tactic=>{let yes=r.al(h)?==0;finish(h,&mut r,yes)}
}}
fn cbw<H:Host>(h:&mut H,r:&mut Regs)->Result<(),H::Err>{let al=r.al(h)?;r.set_i(Reg::Ax,al as i8 as i64);Ok(())}
fn abs<H:Host>(h:&mut H,r:&mut Regs)->Result<(),H::Err>{let ax=r.get(h,Reg::Ax)?;if ax&0x8000!=0{r.set(Reg::Ax,ax.wrapping_neg() as u32);}Ok(())}
fn strip_core<H:Host>(h:&mut H,r:&mut Regs,word:u16)->Result<(),H::Err>{r.enter(h,2)?;r.set_al(h,(word>>8) as u8)?;cbw(h,r)?;abs(h,r)?;let ax=r.get(h,Reg::Ax)?;if (ax as i16)<25{r.set_al(h,0)?;}else{r.set_al(h,word as u8)?;cbw(h,r)?;abs(h,r)?;let ax=r.get(h,Reg::Ax)?;r.set_al(h,u8::from((ax as i16)<=5))?;}let al=r.al(h)?;r.local8(h,-1,al)?;r.leave(h)}
pub fn goal_strip<H:Host>(h:&mut H,opposing:bool)->Result<(),H::Err>{let a=args(h,3)?;let(off,seg,word)=(a[0],a[1],a[2]);let mut r=Regs::new(false);r.enter(h,2)?;crate::destination::direction(h,&mut r,seg,off,if opposing{0x2eff}else{0x2ec7})?;r.set_al(h,(word>>8) as u8)?;cbw(h,&mut r)?;let ax=r.get(h,Reg::Ax)?;let dx=r.get(h,Reg::Dx)?;let product=ax as i16 as i32*dx as i16 as i32;r.set(Reg::Ax,product as u32&65535);r.set(Reg::Dx,(product>>16) as u32&65535);let ax=r.get(h,Reg::Ax)?;let passes=if opposing{(ax as i16)>0}else{ax&0x8000!=0};if passes{invoke(h,&mut r,None,if opposing{0x2f12}else{0x2eda},&[word as u32],|h,r|strip_core(h,r,word))?;let al=r.al(h)?;r.set_al(h,u8::from(al!=0))?;}else{r.set_al(h,0)?;}let al=r.al(h)?;r.local8(h,-1,al)?;r.leave(h)?;r.store(h,false)}
