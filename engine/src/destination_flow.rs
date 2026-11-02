//! T18 immediate positioning generators and resumed-Reg advanced-holder query.
use crate::host::{Host,Reg};
use crate::mem::lin;
use crate::regs::Regs;
#[derive(Clone,Copy,PartialEq,Eq)]
pub enum Phase { RootStart,RootKeeper,RootStateDirection,RootSpecialOwn,RootMembership,RootDrawAbsent,RootDrawPresent,RootDrawOther,RootNormalOwn,RootGroup,RootT7,RootMaximum,RootAhead,RootOwnDirection,RootT6,RootT5,RootMinimum,RootClamp,RootMark,
 GroupStart,GroupTactic,GroupOwn,PostStart,PostDraw,PostMirror,
 MarkStart,MarkOwn,MarkGate,MarkAhead,MarkPostDone,MarkPostOther,MarkKeeper,MarkArea,MarkTacticArea,MarkAdvanced,MarkTarget,MarkDraw,MarkTactic,MarkDirection,
 AdvancedStart,AdvancedOwn,AdvancedHolder }
#[derive(Clone,Copy,Default)]
pub struct Saved {p:u32,seg:u16,off:u16,bp:u16,record:u32,pos:u8,own:bool,group:u16,t6:u16,write:u16}
pub struct Request {pub next:Phase,pub saved:Saved,pub target:&'static str,pub ret_to:&'static str,pub args:Vec<u16>,pub far:bool}
pub enum Action { Call(Request),Done(Option<u16>) }
fn ds8<H:Host>(h:&mut H,k:u32)->Result<u8,H::Err>{h.u8(lin(h.ds(),k as u16))}
fn ds16<H:Host>(h:&mut H,k:u32)->Result<u16,H::Err>{h.u16(lin(h.ds(),k as u16))}
fn arg<H:Host>(h:&mut H,i:u32)->Result<u16,H::Err>{let(sp,far)=h.entry();let at=h.ss_lin(sp+if far{4}else{2}+2*i)?;h.u16(at)}
fn argptr<H:Host>(h:&mut H,s:&mut Saved)->Result<(),H::Err>{let seg=arg(h,1)?;let off=arg(h,0)?;s.p=lin(seg,off);s.seg=arg(h,1)?;s.off=arg(h,0)?;Ok(())}
fn enter<H:Host>(h:&mut H,size:u16,site:u16)->Result<u16,H::Err>{let sp=(h.reg(Reg::Sp)? as u16).wrapping_sub(2);let at=h.ss_lin(sp as u32)?;let bp=h.reg(Reg::Bp)?;h.write(at,&(bp as u16).to_le_bytes(),lin(h.seg(0x791),site))?;h.set_reg(Reg::Sp,sp as u32)?;h.set_reg(Reg::Bp,sp as u32)?;h.set_reg(Reg::Sp,sp.wrapping_sub(size) as u32)?;Ok(sp)}
fn player<H:Host>(h:&mut H,id:u16)->Result<u32,H::Err>{let off=ds16(h,0xa91b)?;let seg=ds16(h,0xa91d)?;Ok(lin(seg,off.wrapping_add(id.wrapping_mul(20))))}
fn local8<H:Host>(h:&mut H,bp:u16,k:i16)->Result<u8,H::Err>{let at=h.ss_lin(bp.wrapping_add(k as u16) as u32)?;h.u8(at)}
fn local16<H:Host>(h:&mut H,bp:u16,k:i16)->Result<u16,H::Err>{let at=h.ss_lin(bp.wrapping_add(k as u16) as u32)?;h.u16(at)}
fn fw16<H:Host>(h:&mut H,bp:u16,k:i16,value:u16,site:u16)->Result<(),H::Err>{let at=h.ss_lin(bp.wrapping_add(k as u16) as u32)?;h.write(at,&value.to_le_bytes(),lin(h.seg(0x791),site))}
fn w8<H:Host>(h:&mut H,p:u32,k:u32,value:u8,site:u16)->Result<(),H::Err>{h.write(p+k,&[value],lin(h.seg(0x791),site))}
fn w16<H:Host>(h:&mut H,p:u32,k:u32,value:u16,site:u16)->Result<(),H::Err>{h.write(p+k,&value.to_le_bytes(),lin(h.seg(0x791),site))}
fn ax<H:Host>(h:&mut H,value:u16)->Result<(),H::Err>{h.set_reg(Reg::Ax,value as u32)}
fn push<H:Host>(h:&mut H,value:u16,site:u16)->Result<(),H::Err>{let sp=(h.reg(Reg::Sp)? as u16).wrapping_sub(2);let at=h.ss_lin(sp as u32)?;h.write(at,&value.to_le_bytes(),lin(h.seg(0x791),site))?;h.set_reg(Reg::Sp,sp as u32)}
fn pop<H:Host>(h:&mut H)->Result<u16,H::Err>{let sp=h.reg(Reg::Sp)?;let at=h.ss_lin(sp)?;let value=h.u16(at)?;h.set_reg(Reg::Sp,(sp+2)&65535)?;ax(h,value)?;Ok(value)}
fn drop<H:Host>(h:&mut H,n:u32)->Result<(),H::Err>{let sp=h.reg(Reg::Sp)?;h.set_reg(Reg::Sp,(sp+2*n)&65535)}
fn call(s:Saved,next:Phase,target:&'static str,ret_to:&'static str,args:Vec<u16>,far:bool)->Action{Action::Call(Request{next,saved:s,target,ret_to,args,far})}
fn same(s:Saved,next:Phase,target:&'static str,ret:&'static str,extra:Option<u16>)->Action{let args=if let Some(v)=extra{vec![v,s.seg,s.off]}else{vec![s.seg,s.off]};call(s,next,target,ret,args,true)}
fn done()->Action{Action::Done(None)}
fn mark(s:Saved)->Action{same(s,Phase::RootMark,"0791:4A28","0791:4D39",None)}
fn group_done<H:Host>(h:&mut H,s:Saved,flag:bool)->Result<Action,H::Err>{let group=ds8(h,0x7ba+if s.pos>4{2}else{0}+u32::from(flag))? as u16;fw16(h,s.bp,-2,group,0x4348)?;Ok(Action::Done(Some(group)))}
fn after_post<H:Host>(h:&mut H,s:Saved)->Result<Action,H::Err>{
 if (h.u8(s.p+0xc)? as i8)<2{let half=(h.u8(s.p+9)? as i8 as i16)/2;let old=h.u8(s.p+0xb)?;w8(h,s.p,0xb,old.wrapping_sub(half as u8),0x43e1)?;}
 let a=h.u8(s.p+10)? as i8;let b=h.u8(s.p+12)? as i8;w8(h,s.p,8,a.wrapping_add(b) as u8,0x43fc)?;
 let a=h.u8(s.p+9)? as i8;let b=h.u8(s.p+11)? as i8;w8(h,s.p,7,a.wrapping_add(b) as u8,0x4417)?;
 let word=h.u16(s.p+7)?;Ok(same(s,Phase::PostMirror,"0791:2C86","0791:442B",Some(word)))
}
fn special(s:Saved,yes:bool)->Action{same(s,if yes{Phase::RootSpecialOwn}else{Phase::RootNormalOwn},"0791:2B51",if yes{"0791:4BCC"}else{"0791:4C59"},None)}
fn copy_target<H:Host>(h:&mut H,s:Saved)->Result<Action,H::Err>{let point=local16(h,s.bp,-2)?;w16(h,s.p,7,point,0x4b3a)?;Ok(done())}
fn keeper_target<H:Host>(h:&mut H,s:Saved,yes:bool)->Result<Action,H::Err>{if yes{let point=ds16(h,0x82f6)?;w16(h,s.p,7,point,0x4ad7)?;}Ok(done())}
fn cbw<H:Host>(h:&mut H,r:&mut Regs)->Result<(),H::Err>{let al=r.al(h)?;r.set_i(Reg::Ax,al as i8 as i64);Ok(())}
fn abs_ax<H:Host>(h:&mut H,r:&mut Regs)->Result<(),H::Err>{let v=r.get(h,Reg::Ax)?;if v&0x8000!=0{r.set(Reg::Ax,v.wrapping_neg() as u32);}Ok(())}
fn advanced_end<H:Host>(h:&mut H,r:&mut Regs,value:bool)->Result<Action,H::Err>{
 r.set_al(h,u8::from(value))?;let al=r.al(h)?;r.local8(h,-1,al)?;r.flush(h)?;let bp=r.get(h,Reg::Bp)?;let at=h.ss_lin(bp.wrapping_sub(1) as u32)?;let al=h.u8(at)?;r.set_al(h,al)?;r.leave(h)?;r.store(h,false)?;Ok(done())
}
pub fn first(p:Phase)->bool{matches!(p,Phase::RootStart|Phase::GroupStart|Phase::PostStart|Phase::MarkStart|Phase::AdvancedStart)}
pub fn step<H:Host>(h:&mut H,phase:Phase,saved:Option<Saved>,sent:u16)->Result<Action,H::Err>{
 let mut s=saved.unwrap_or_default();
 match phase{
 Phase::RootStart|Phase::GroupStart|Phase::PostStart|Phase::MarkStart=>{
  argptr(h,&mut s)?;
  match phase{
   Phase::RootStart=>{enter(h,0,0x4b64)?;let slot=h.u8(s.p+6)?;let again=h.u8(s.p+6)?;ax(h,again as u16)?;Ok(call(s,Phase::RootKeeper,"0791:045D","0791:4B74",vec![slot as u16],false))}
   Phase::GroupStart=>{
    s.bp=enter(h,6,0x42cb)?;let id=h.u16(s.p+0xd)?;s.record=player(h,id)?;let off=ds16(h,0xa91b)?.wrapping_add(id.wrapping_mul(20));fw16(h,s.bp,-6,off,0x42e3)?;let seg=ds16(h,0xa91d)?;fw16(h,s.bp,-4,seg,0x42e6)?;s.pos=h.u8(s.record+6)?;
    if s.pos==0{fw16(h,s.bp,-2,4,0x42f3)?;return Ok(Action::Done(Some(4)));}
    if s.pos<=11{ax(h,1)?;Ok(same(s,Phase::GroupTactic,"0791:26D7","0791:4311",Some(1)))}else{group_done(h,s,true)}
   }
   Phase::PostStart=>{enter(h,0,0x4354)?;let id=h.u16(s.p+0xd)?;let record=player(h,id)?;s.pos=h.u8(record+6)?;
    if s.pos==0{w8(h,s.p,0xb,0,0x4374)?;return after_post(h,s);}
    let special=s.pos==13&&h.u8(s.p+0x12)?!=9;let n=if special{15}else{5};s.write=if special{0x43ad}else if s.pos==13{0x4398}else{0x43c2};ax(h,n)?;
    Ok(call(s,Phase::PostDraw,"214B:06B1",if special{"0791:43A7"}else if s.pos==13{"0791:4392"}else{"0791:43BC"},vec![n],true))
   }
   Phase::MarkStart=>{s.bp=enter(h,8,0x4a28)?;let id=h.u16(s.p+0xd)?;s.record=player(h,id)?;let off=ds16(h,0xa91b)?.wrapping_add(id.wrapping_mul(20));fw16(h,s.bp,-8,off,0x4a40)?;let seg=ds16(h,0xa91d)?;fw16(h,s.bp,-6,seg,0x4a43)?;Ok(same(s,Phase::MarkOwn,"0791:2B51","0791:4A4F",None))}
   _=>unreachable!()
  }
 }
 Phase::GroupTactic=>{if sent&255==0{group_done(h,s,false)}else{Ok(same(s,Phase::GroupOwn,"0791:2B51","0791:431E",None))}}
 Phase::GroupOwn=>group_done(h,s,sent&255!=0),
 Phase::PostDraw=>{w8(h,s.p,0xb,sent.wrapping_sub(if s.write==0x43ad{8}else{3}) as u8,s.write)?;after_post(h,s)}
 Phase::PostMirror=>{w16(h,s.p,7,sent,0x442e)?;Ok(done())}
 Phase::RootKeeper=>{if sent&255!=0{let word=h.u16(s.p+9)?;return Ok(same(s,Phase::RootOwnDirection,"0791:2C86","0791:4B88",Some(word)));}
  let state=h.u8(s.p+0x12)?;if state==11{Ok(same(s,Phase::RootStateDirection,"0791:2BE5","0791:4BB2",None))}else{Ok(special(s,state==9))}
 }
 // RootOwnDirection is also the keeper-mirror return; discriminate by saved write.
 Phase::RootStateDirection=>{let y=ds8(h,0x82f7)? as i8 as i32;let dir=sent as u8 as i8 as i32;Ok(special(s,(y*dir) as i16>20))}
 Phase::RootSpecialOwn=>{
  if sent&255==0{return Ok(call(s,Phase::RootDrawOther,"0791:261A","0791:4C33",vec![],false));}
  let id=h.u16(s.p+0xd)?;let r=player(h,id)?;let pos=h.u8(r+6)?;let value=(id.wrapping_mul(20)&0xff00)|pos as u16;ax(h,value)?;
  Ok(call(s,Phase::RootMembership,"23E4:08DF","0791:4BF1",vec![value,h.seg(0x791),0x4b44],true))
 }
 Phase::RootMembership=>{let absent=h.reg(Reg::Eflags)?&0x40!=0;Ok(call(s,if absent{Phase::RootDrawAbsent}else{Phase::RootDrawPresent},"0791:261A",if absent{"0791:4C14"}else{"0791:4BF6"},vec![],false))}
 Phase::RootDrawAbsent|Phase::RootDrawPresent|Phase::RootDrawOther=>{
  let y=h.u8(s.p+10)? as i8 as i32;let (v,site)=match phase{Phase::RootDrawAbsent=>(0x26-y-sent as i32,0x4c2a),Phase::RootDrawPresent=>(y.abs()+sent as i32,0x4c0b),_=>(-0x26-y+sent as i32,0x4c49)};w8(h,s.p,12,v as u8,site)?;Ok(mark(s))
 }
 Phase::RootNormalOwn=>{s.own=sent&255!=0;if s.own{push(h,0,0x4c62)?;push(h,20,0x4c63)?;}Ok(same(s,Phase::RootGroup,"0791:42CB",if s.own{"0791:4C6D"}else{"0791:4CCA"},None))}
 Phase::RootGroup=>{push(h,sent,if s.own{0x4c6d}else{0x4cca})?;let n=if s.own{7}else{6};ax(h,n)?;Ok(same(s,if s.own{Phase::RootT7}else{Phase::RootT6},"0791:26D7",if s.own{"0791:4C7B"}else{"0791:4CD8"},Some(n)))}
 Phase::RootT7=>{let group=pop(h)?;let limit=ds8(h,(0x7dbi32+((sent as u8 as i8 as i32*4+group as i32)&65535)) as u32)?;drop(h,2)?;ax(h,limit as u16)?;h.set_reg(Reg::Dx,0)?;Ok(call(s,Phase::RootMaximum,"214B:0D56","0791:4C94",vec![0,20,0,limit as u16],true))}
 Phase::RootMaximum=>{w8(h,s.p,12,sent as u8,0x4c97)?;ax(h,40)?;Ok(same(s,Phase::RootAhead,"0791:2D6D","0791:4CA8",Some(40)))}
 Phase::RootAhead=>{if sent&255!=0{s.write=0x4cbb;Ok(same(s,Phase::RootOwnDirection,"0791:2BE5","0791:4CB5",None))}else{Ok(mark(s))}}
 Phase::RootOwnDirection=>{if s.write==0x4cbb{w8(h,s.p,12,(0i16-(sent as u8 as i8 as i16)) as u8,0x4cbb)?;Ok(mark(s))}else{w16(h,s.p,7,sent,0x4b8b)?;Ok(done())}}
 Phase::RootT6=>{s.t6=sent;push(h,(sent as u8 as i8 as i16*4) as u16,0x4cdd)?;ax(h,5)?;Ok(same(s,Phase::RootT5,"0791:26D7","0791:4CEB",Some(5)))}
 Phase::RootT5=>{pop(h)?;let group=pop(h)?;let k=(sent as u8 as i8 as i32*8+s.t6 as u8 as i8 as i32*4+group as i32)&65535;let limit=ds8(h,0x7cb+k as u32)?;w8(h,s.p,12,limit,0x4cff)?;
  push(h,s.seg,0x4d0a)?;push(h,s.off.wrapping_add(12),0x4d0b)?;push(h,0,0x4d0e)?;let limit=(ds8(h,0x82f7)? as i8 as i32).abs() as u32*2;ax(h,limit as u16)?;h.set_reg(Reg::Dx,limit>>16)?;
  Ok(call(s,Phase::RootMinimum,"214B:0D1C","0791:4D2A",vec![0,42,(limit>>16) as u16,limit as u16],true))
 }
 Phase::RootMinimum=>{drop(h,3)?;ax(h,sent)?;Ok(call(s,Phase::RootClamp,"214B:2031","0791:4D30",vec![s.seg,s.off.wrapping_add(12),0,sent],true))}
 Phase::RootClamp=>Ok(mark(s)),Phase::RootMark|Phase::MarkPostDone=>Ok(done()),
 Phase::MarkOwn=>{if sent&255!=0{Ok(same(s,Phase::MarkGate,"0791:2B7B","0791:4A5C",None))}else{Ok(same(s,Phase::MarkPostOther,"0791:4354","0791:4A90",None))}}
 Phase::MarkGate=>{if sent&255!=0{Ok(same(s,Phase::MarkPostDone,"0791:4354","0791:4A84",None))}else if h.u8(s.record+6)?==1{Ok(same(s,Phase::MarkAhead,"0791:2D10","0791:4A77",Some(10)))}else{Ok(done())}}
 Phase::MarkAhead=>{if sent&255==0{Ok(same(s,Phase::MarkPostDone,"0791:4354","0791:4A84",None))}else{Ok(done())}}
 Phase::MarkPostOther=>{let slot=h.u8(s.p+6)?;Ok(call(s,Phase::MarkKeeper,"0791:045D","0791:4A9D",vec![slot as u16],false))}
 Phase::MarkKeeper=>{if sent&255!=0{if ds8(h,0x8325)?!=0{let point=ds16(h,0x82f6)?;Ok(same(s,Phase::MarkArea,"0791:2E36","0791:4AB5",Some(point)))}else{Ok(done())}}else{Ok(call(s,Phase::MarkTarget,"0791:47C5","0791:4AE1",vec![s.bp],false))}}
 Phase::MarkArea=>{if sent&255!=0{keeper_target(h,s,true)}else{Ok(same(s,Phase::MarkTacticArea,"0791:26D7","0791:4AC6",Some(1)))}}
 Phase::MarkTacticArea=>{if sent&255!=0{Ok(call(s,Phase::MarkAdvanced,"0791:40BC","0791:4ACD",vec![],false))}else{keeper_target(h,s,false)}}
 Phase::MarkAdvanced=>keeper_target(h,s,sent&255!=0),
 Phase::MarkTarget=>{if sent&255==0{return Ok(done());}if ds8(h,0x8325)?==0{let slot=ds8(h,0x830b)?;if slot as u16==local16(h,s.bp,-4)?{return Ok(done());}}
  Ok(call(s,Phase::MarkDraw,"214B:06B1","0791:4AFF",vec![6],true))
 }
 Phase::MarkDraw=>{let energy=h.u8(s.record+14)? as i8 as i32;if energy<=sent as i16 as i32{Ok(done())}else{Ok(same(s,Phase::MarkTactic,"0791:26D7","0791:4B1A",Some(5)))}}
 Phase::MarkTactic=>{if sent&255!=0{copy_target(h,s)}else{Ok(same(s,Phase::MarkDirection,"0791:2BE5","0791:4B27",None))}}
 Phase::MarkDirection=>{let y=local8(h,s.bp,-1)? as i8 as i32;if y*(sent as u8 as i8 as i32)>=0{Ok(done())}else{copy_target(h,s)}}
 Phase::AdvancedStart=>{
  let mut r=Regs::new(false);r.enter(h,6)?;let slot=ds8(h,0x830b)?;r.set_al(h,slot)?;r.set_ah(h,0)?;r.set(Reg::Dx,22);let ax=r.get(h,Reg::Ax)? as u32;let dx=r.get(h,Reg::Dx)? as u32;let p=ax*dx;r.set(Reg::Ax,p&65535);r.set(Reg::Dx,p>>16);let ax=r.get(h,Reg::Ax)?;r.set(Reg::Di,ax.wrapping_add(0x80e8) as u32);
  let off=r.get(h,Reg::Di)?;r.local16(h,-5,off as u32)?;r.local16(h,-3,h.ds() as u32)?;s.off=r.get(h,Reg::Di)?;s.seg=h.ds();r.set(Reg::Es,s.seg as u32);r.set(Reg::Di,s.off as u32);r.store(h,true)?;
  Ok(same(s,Phase::AdvancedOwn,"0791:2C54","0791:40E1",None))
 }
 Phase::AdvancedOwn=>{let mut r=Regs::new(true);let al=r.al(h)?;if al!=0{return advanced_end(h,&mut r,false);}r.store(h,true)?;Ok(call(s,Phase::AdvancedHolder,"0791:2996","0791:40E8",vec![],false))}
 Phase::AdvancedHolder=>{
  let mut r=Regs::new(true);let al=r.al(h)?;r.set_al(h,u8::from(al==0))?;cbw(h,&mut r)?;let ax=r.get(h,Reg::Ax)?;r.set(Reg::Di,ax as u32);let di=r.get(h,Reg::Di)?;r.set(Reg::Di,di.wrapping_shl(1) as u32);let di=r.get(h,Reg::Di)?;r.set(Reg::Si,di as u32);let di=r.get(h,Reg::Di)?;let si=r.get(h,Reg::Si)?;r.set(Reg::Di,di.wrapping_shl(1).wrapping_add(si) as u32);
  let di=r.get(h,Reg::Di)?;let b=ds8(h,0x82e3u32+di as u32)?;r.set_al(h,b)?;cbw(h,&mut r)?;abs_ax(h,&mut r)?;let ax=r.get(h,Reg::Ax)?;r.set(Reg::Dx,ax as u32);
  r.set(Reg::Es,s.seg as u32);r.set(Reg::Di,s.off as u32);let y=h.u8(lin(s.seg,s.off.wrapping_add(1)))?;r.set_al(h,y)?;cbw(h,&mut r)?;abs_ax(h,&mut r)?;
  let ax=r.get(h,Reg::Ax)?;let dx=r.get(h,Reg::Dx)?;let mut result=false;
  if ax as i16>dx as i16{r.set(Reg::Es,s.seg as u32);r.set(Reg::Di,s.off as u32);let y=h.u8(lin(s.seg,s.off.wrapping_add(1)))?;r.set_al(h,y)?;cbw(h,&mut r)?;abs_ax(h,&mut r)?;let ax=r.get(h,Reg::Ax)?;
   if (ax as i16)<35{r.set(Reg::Es,s.seg as u32);r.set(Reg::Di,s.off as u32);let x=h.u8(lin(s.seg,s.off))?;r.set_al(h,x)?;cbw(h,&mut r)?;abs_ax(h,&mut r)?;result=(r.get(h,Reg::Ax)? as i16)<4;}
  }advanced_end(h,&mut r,result)
 }
 }
}
