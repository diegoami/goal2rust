//! T19: closed depth-adjustment tree, accepted oracle 2cbeb36f.
use crate::host::{args,Host,Reg};
use crate::mem::lin;
use crate::regs::{invoke,Regs};
#[derive(Clone,Copy,PartialEq,Eq)]
pub enum Phase {Start,Own,Ahead,AttackDone,DefendDone,SlotDone,
 AttackStart,AttackGroup,AttackTactic,AttackGroupAgain,AttackAhead,AttackChoice,AttackCoin,
 DefendStart,DefendGroup,DefendT6,DefendT5,DefendGroupAgain,DefendAhead,DefendBallAhead,DefendSlot}
#[derive(Clone,Copy,Default)]
pub struct Saved {bp:u16,p:u32,seg:u16,off:u16,t6:u16,group:u16}
pub struct Request {pub next:Phase,pub saved:Saved,pub target:&'static str,pub ret_to:&'static str,pub args:Vec<u16>,pub far:bool}
pub enum Action {Call(Request),Done(Option<u16>)}
fn ds8<H:Host>(h:&mut H,k:u32)->Result<u8,H::Err>{h.u8(lin(h.ds(),k as u16))}
fn ds16<H:Host>(h:&mut H,k:u32)->Result<u16,H::Err>{h.u16(lin(h.ds(),k as u16))}
fn arg<H:Host>(h:&mut H,i:u32)->Result<u16,H::Err>{let(sp,far)=h.entry();let at=h.ss_lin(sp+if far{4}else{2}+2*i)?;h.u16(at)}
fn frame16<H:Host>(h:&mut H,bp:u16,k:u16)->Result<u16,H::Err>{let at=h.ss_lin(bp.wrapping_add(k) as u32)?;h.u16(at)}
fn enter<H:Host>(h:&mut H,site:u16)->Result<u16,H::Err>{let sp=(h.reg(Reg::Sp)? as u16).wrapping_sub(2);let at=h.ss_lin(sp as u32)?;let bp=h.reg(Reg::Bp)?;h.write(at,&(bp as u16).to_le_bytes(),lin(h.seg(0x791),site))?;h.set_reg(Reg::Sp,sp as u32)?;h.set_reg(Reg::Bp,sp as u32)?;h.set_reg(Reg::Sp,sp.wrapping_sub(2) as u32)?;Ok(sp)}
fn local<H:Host>(h:&mut H,s:Saved,value:u8,site:u16)->Result<(),H::Err>{let at=h.ss_lin(s.bp.wrapping_sub(1) as u32)?;h.write(at,&[value],lin(h.seg(0x791),site))}
fn ax<H:Host>(h:&mut H,value:u16)->Result<(),H::Err>{h.set_reg(Reg::Ax,value as u32)}
fn push<H:Host>(h:&mut H,value:u16,site:u16)->Result<(),H::Err>{let sp=(h.reg(Reg::Sp)? as u16).wrapping_sub(2);let at=h.ss_lin(sp as u32)?;h.write(at,&value.to_le_bytes(),lin(h.seg(0x791),site))?;h.set_reg(Reg::Sp,sp as u32)}
fn pop<H:Host>(h:&mut H)->Result<u16,H::Err>{let sp=h.reg(Reg::Sp)?;let at=h.ss_lin(sp)?;let value=h.u16(at)?;h.set_reg(Reg::Sp,(sp+2)&65535)?;ax(h,value)?;Ok(value)}
fn write<H:Host>(h:&mut H,s:Saved,k:u32,value:u8,site:u16)->Result<(),H::Err>{h.write(s.p+k,&[value],lin(h.seg(0x791),site))}
fn position<H:Host>(h:&mut H,s:Saved)->Result<u8,H::Err>{let id=h.u16(s.p+13)?;let off=ds16(h,0xa91b)?;let seg=ds16(h,0xa91d)?;h.u8(lin(seg,off.wrapping_add(id.wrapping_mul(20)))+6)}
fn call(s:Saved,next:Phase,target:&'static str,ret_to:&'static str,args:Vec<u16>,far:bool)->Action{Action::Call(Request{next,saved:s,target,ret_to,args,far})}
fn same(s:Saved,next:Phase,target:&'static str,ret:&'static str,value:Option<u16>)->Action{let args=if let Some(v)=value{vec![v,s.seg,s.off]}else{vec![s.seg,s.off]};call(s,next,target,ret,args,true)}
fn done()->Action{Action::Done(None)}
fn finish<H:Host>(h:&mut H,s:Saved)->Result<Action,H::Err>{let high=h.reg(Reg::Ax)? as u16&0xff00;let at=h.ss_lin(s.bp.wrapping_sub(1) as u32)?;Ok(Action::Done(Some(high|h.u8(at)? as u16)))}
fn answer<H:Host>(h:&mut H,s:Saved,value:u8,site:u16)->Result<Action,H::Err>{local(h,s,value,site)?;finish(h,s)}
fn root_branch(s:Saved,attack:bool)->Action{call(s,if attack{Phase::AttackDone}else{Phase::DefendDone},if attack{"0791:4532"}else{"0791:4649"},if attack{"0791:478D"}else{"0791:479A"},vec![s.bp],false)}
fn attack_answer<H:Host>(h:&mut H,s:Saved,value:u16)->Result<Action,H::Err>{answer(h,s,u8::from(value&255!=0),match s.group{1=>0x45ca,2=>0x4603,_=>0x463d})}
pub fn first(p:Phase)->bool{matches!(p,Phase::Start|Phase::AttackStart|Phase::DefendStart)}
pub fn step<H:Host>(h:&mut H,phase:Phase,saved:Option<Saved>,sent:u16)->Result<Action,H::Err>{
 let mut s=saved.unwrap_or_default();
 match phase{
 Phase::Start=>{let seg=arg(h,1)?;let off=arg(h,0)?;s.p=lin(seg,off);s.seg=arg(h,1)?;s.off=arg(h,0)?;s.bp=enter(h,0x474d)?;Ok(same(s,Phase::Own,"0791:2B51","0791:475C",None))}
 Phase::Own=>{if sent&255!=0{if position(h,s)?<=4{ax(h,0)?;Ok(same(s,Phase::Ahead,"0791:2D10","0791:4785",Some(0)))}else{Ok(root_branch(s,true))}}else{Ok(root_branch(s,false))}}
 Phase::Ahead=>Ok(root_branch(s,sent&255!=0)),
 Phase::AttackDone=>{let old=h.u8(s.p+12)?;write(h,s,12,old.wrapping_add(sent as u8),0x4790)?;Ok(done())}
 Phase::DefendDone=>{let old=h.u8(s.p+12)?;write(h,s,12,old.wrapping_sub(sent as u8),0x479d)?;Ok(same(s,Phase::SlotDone,"0791:2BB1","0791:47AA",None))}
 Phase::SlotDone=>{if sent&255==2{let old=h.u8(s.p+9)? as i8;write(h,s,11,old.wrapping_neg() as u8,0x47bb)?;}Ok(done())}
 Phase::AttackStart|Phase::DefendStart=>{let attack=phase==Phase::AttackStart;s.bp=enter(h,if attack{0x4532}else{0x4649})?;local(h,s,0,if attack{0x4538}else{0x464f})?;let parent=arg(h,0)?;s.seg=frame16(h,parent,8)?;s.off=frame16(h,parent,6)?;s.p=lin(s.seg,s.off);Ok(same(s,if attack{Phase::AttackGroup}else{Phase::DefendGroup},"0791:42CB",if attack{"0791:4549"}else{"0791:4660"},None))}
 Phase::AttackGroup=>{push(h,sent,0x4549)?;ax(h,7)?;Ok(same(s,Phase::AttackTactic,"0791:26D7","0791:455B",Some(7)))}
 Phase::AttackTactic=>{let group=pop(h)?;let k=(sent as u8 as i8 as i32*4+group as i32)&65535;let limit=ds8(h,0x7db+k as u32)?;if (h.u8(s.p+12)? as i8 as i32)<limit as i32{Ok(same(s,Phase::AttackGroupAgain,"0791:42CB","0791:458D",None))}else{finish(h,s)}}
 Phase::AttackGroupAgain=>{s.group=sent;if (1..=3).contains(&sent){let value=if sent==3{30}else{0};ax(h,value)?;Ok(same(s,Phase::AttackAhead,"0791:2D10",match sent{1=>"0791:45A2",2=>"0791:45E4",_=>"0791:461E"},Some(value)))}else{finish(h,s)}}
 Phase::AttackAhead=>{if sent&255!=0{attack_answer(h,s,sent)}else{let value=if s.group==3{7}else{1};ax(h,value)?;Ok(same(s,Phase::AttackChoice,"0791:26D7",match s.group{1=>"0791:45B7",2=>"0791:45F9",_=>"0791:4633"},Some(value)))}}
 Phase::AttackChoice=>{if s.group==1&&sent&255==0{Ok(call(s,Phase::AttackCoin,"214B:06FA","0791:45C0",vec![],true))}else{attack_answer(h,s,sent)}}
 Phase::AttackCoin=>attack_answer(h,s,sent),
 Phase::DefendGroup=>{push(h,sent,0x4660)?;ax(h,6)?;Ok(same(s,Phase::DefendT6,"0791:26D7","0791:4672",Some(6)))}
 Phase::DefendT6=>{s.t6=sent;push(h,(sent as u8 as i8 as i16*4) as u16,0x4677)?;ax(h,5)?;Ok(same(s,Phase::DefendT5,"0791:26D7","0791:4689",Some(5)))}
 Phase::DefendT5=>{pop(h)?;let group=pop(h)?;let k=(sent as u8 as i8 as i32*8+s.t6 as u8 as i8 as i32*4+group as i32)&65535;let limit=ds8(h,0x7cb+k as u32)?;if (h.u8(s.p+12)? as i8 as i32)>limit as i32{Ok(same(s,Phase::DefendGroupAgain,"0791:42CB","0791:46BE",None))}else{finish(h,s)}}
 Phase::DefendGroupAgain=>{s.group=sent;match sent{1|2=>{let value=if sent==1{15}else{0};ax(h,value)?;Ok(same(s,Phase::DefendAhead,"0791:2D6D",if sent==1{"0791:46D4"}else{"0791:46EE"},Some(value)))},3=>{ax(h,10)?;Ok(same(s,Phase::DefendBallAhead,"0791:2D10","0791:4709",Some(10)))},_=>finish(h,s)}}
 Phase::DefendAhead=>answer(h,s,sent as u8,if s.group==1{0x46d4}else{0x46ee}),
 Phase::DefendBallAhead=>{if sent&255!=0{Ok(same(s,Phase::DefendSlot,"0791:2BB1","0791:471A",None))}else{answer(h,s,1,0x4741)}}
 Phase::DefendSlot=>{let yes=if sent&255!=2{position(h,s)?==1}else{true};answer(h,s,u8::from(yes),0x4741)}
 }
}
pub fn slot<H:Host>(h:&mut H)->Result<(),H::Err>{let a=args(h,2)?;let(off,seg)=(a[0],a[1]);let mut r=Regs::new(false);r.enter(h,2)?;r.set(Reg::Es,seg as u32);r.set(Reg::Di,off as u32);let slot=h.u8(lin(seg,off.wrapping_add(6)))?;if slot>11{r.set(Reg::Ax,(slot as u16).wrapping_sub(11) as u32);}else{r.set_al(h,slot)?;}let al=r.al(h)?;r.local8(h,-1,al)?;r.leave(h)?;r.store(h,false)}
fn sub_flags(a:u16,b:u16)->u32{use crate::regs::{CF,PF,AF,ZF,SF,OF};let result=a.wrapping_sub(b);(if a<b{CF}else{0})|(if (result as u8).count_ones()%2==0{PF}else{0})|(if (a^b^result)&16!=0{AF}else{0})|(if result==0{ZF}else{0})|(if result&0x8000!=0{SF}else{0})|(if ((a^b)&(a^result)&0x8000)!=0{OF}else{0})}
pub fn coin<H:Host>(h:&mut H)->Result<(),H::Err>{let mut r=Regs::new(false);r.enter(h,2)?;let ptr=lin(h.ds(),0xa978);let off=h.u16(ptr)?;let seg=h.u16(ptr+2)?;r.set(Reg::Di,off as u32);r.set(Reg::Es,seg as u32);r.set(Reg::Ax,2);invoke(h,&mut r,Some(0x214b),0x070e,&[seg as u32,off as u32,2],|h,r|crate::marking::rng_core(h,r,off,seg,2))?;let ax=r.get(h,Reg::Ax)?;r.arith(sub_flags(ax,1));r.set_al(h,u8::from(ax==1))?;let al=r.al(h)?;r.local8(h,-1,al)?;r.leave(h)?;r.store(h,false)}
