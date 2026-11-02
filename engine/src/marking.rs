//! T17: complete marking-target closure, accepted archaeology 2cbeb36f.
//! Captured generator locals survive real guest suspensions; inline helpers do
//! not acquire guest frames. Frame accesses read live SS separately each time.
use crate::host::{args, Host, Reg};
use crate::mem::lin;
use crate::regs::{invoke, Regs, CF, PF, AF, ZF, SF, OF};

#[derive(Clone,Copy,PartialEq,Eq)]
pub enum Phase { Start, SideCountry, SideMark, ScanAvailable, ScanZone, SelectedAvailable,
    Keeper, Ours, Theirs, OursAgain, TheirsAgain, Draw, Direction, ZoneStart, ZoneDirection }
#[derive(Clone,Copy,Default)]
pub struct Saved { bp:u16, parent:u16, seg:u16, off:u16, p:u32, country:u32,
    side:u8, mark_off:u32, mark:u16, slot:u16, player:u16, opp_slot:u16, point:u16 }
pub struct Request {pub next:Phase,pub saved:Saved,pub target:&'static str,pub ret_to:&'static str,pub args:Vec<u16>,pub far:bool}
pub enum Action { Call(Request), Done(u16) }
fn ds8<H:Host>(h:&mut H,off:u32)->Result<u8,H::Err>{h.u8(lin(h.ds(),off as u16))}
fn ds16<H:Host>(h:&mut H,off:u32)->Result<u16,H::Err>{h.u16(lin(h.ds(),off as u16))}
fn frame8<H:Host>(h:&mut H,bp:u16,k:i32)->Result<u8,H::Err>{let at=h.ss_lin(bp.wrapping_add(k as u16) as u32)?;h.u8(at)}
fn frame16<H:Host>(h:&mut H,bp:u16,k:i32)->Result<u16,H::Err>{let at=h.ss_lin(bp.wrapping_add(k as u16) as u32)?;h.u16(at)}
fn fw8<H:Host>(h:&mut H,bp:u16,k:i32,v:u8,site:u16)->Result<(),H::Err>{let at=h.ss_lin(bp.wrapping_add(k as u16) as u32)?;h.write(at,&[v],lin(h.seg(0x791),site))}
fn fw16<H:Host>(h:&mut H,bp:u16,k:i32,v:u16,site:u16)->Result<(),H::Err>{let at=h.ss_lin(bp.wrapping_add(k as u16) as u32)?;h.write(at,&v.to_le_bytes(),lin(h.seg(0x791),site))}
fn enter<H:Host>(h:&mut H,size:u16,site:u16)->Result<u16,H::Err>{
    let sp=(h.reg(Reg::Sp)? as u16).wrapping_sub(2);
    let at=h.ss_lin(sp as u32)?;let bp=h.reg(Reg::Bp)?;
    h.write(at,&(bp as u16).to_le_bytes(),lin(h.seg(0x791),site))?;
    h.set_reg(Reg::Sp,sp as u32)?;h.set_reg(Reg::Bp,sp as u32)?;
    h.set_reg(Reg::Sp,sp.wrapping_sub(size) as u32)?;Ok(sp)
}
fn arg<H:Host>(h:&mut H,i:u32)->Result<u16,H::Err>{let (sp,far)=h.entry();let at=h.ss_lin(sp+if far{4}else{2}+2*i)?;h.u16(at)}
fn record<H:Host>(h:&mut H,ptr:u32,stride:u32,idx:u16)->Result<u32,H::Err>{let off=ds16(h,ptr)?;let seg=ds16(h,ptr+2)?;Ok(lin(seg,off.wrapping_add((stride*idx as u32) as u16)))}
fn call(s:Saved,next:Phase,target:&'static str,ret_to:&'static str,args:Vec<u16>,far:bool)->Action{Action::Call(Request{next,saved:s,target,ret_to,args,far})}
fn push<H:Host>(h:&mut H,v:u16,site:u16)->Result<(),H::Err>{let sp=(h.reg(Reg::Sp)? as u16).wrapping_sub(2);let at=h.ss_lin(sp as u32)?;h.write(at,&v.to_le_bytes(),lin(h.seg(0x791),site))?;h.set_reg(Reg::Sp,sp as u32)}
fn pop_dx<H:Host>(h:&mut H)->Result<u16,H::Err>{let sp=h.reg(Reg::Sp)?;let at=h.ss_lin(sp)?;let v=h.u16(at)?;h.set_reg(Reg::Sp,(sp+2)&65535)?;h.set_reg(Reg::Dx,v as u32)?;Ok(v)}
fn end<H:Host>(h:&mut H,value:u16,mutant:bool)->Result<Action,H::Err>{if mutant{corrupt(h)?;}Ok(Action::Done(value))}
fn live_high<H:Host>(h:&mut H)->Result<u16,H::Err>{Ok(h.reg(Reg::Ax)? as u16&0xff00)}
fn final_local<H:Host>(h:&mut H,s:Saved,mutant:bool)->Result<Action,H::Err>{let high=live_high(h)?;let al=frame8(h,s.bp,-1)?;end(h,high|al as u16,mutant)}
fn scan<H:Host>(h:&mut H,mut s:Saved,mutant:bool)->Result<Action,H::Err>{
    if s.slot<12 {s.player=h.u16(s.country+(s.slot as u32-1)*2)?;return Ok(call(s,Phase::ScanAvailable,"1771:3216","0791:485D",vec![s.player],true));}
    if s.mark!=0 {fw16(h,s.bp,-3,2,0x48ab)?;s.slot=2;return selected(h,s,mutant);}
    final_local(h,s,mutant)
}
fn next_scan<H:Host>(h:&mut H,mut s:Saved,mutant:bool)->Result<Action,H::Err>{fw16(h,s.bp,-3,s.slot+1,0x489d)?;s.slot+=1;scan(h,s,mutant)}
fn selected<H:Host>(h:&mut H,mut s:Saved,mutant:bool)->Result<Action,H::Err>{
    while s.slot<12 {
        s.player=h.u16(s.country+(s.slot as u32-1)*2)?;
        if s.player==s.mark{return Ok(call(s,Phase::SelectedAvailable,"1771:3216","0791:48E2",vec![s.player],true));}
        fw16(h,s.bp,-3,s.slot+1,0x49d3)?;s.slot+=1;
    }
    h.write(lin(h.ds(),s.mark_off as u16),&0u16.to_le_bytes(),lin(h.seg(0x791),0x4a1b))?;
    final_local(h,s,mutant)
}
fn theirs<H:Host>(h:&mut H,s:Saved,again:bool)->Result<Action,H::Err>{
    let ds=h.ds();Ok(call(s,if again{Phase::TheirsAgain}else{Phase::Theirs},"0791:278A",if again{"0791:499D"}else{"0791:496A"},vec![8,ds,0x80e8u16.wrapping_add(0x16u16.wrapping_mul(s.opp_slot))],true))
}
fn draw<H:Host>(h:&mut H,s:Saved)->Result<Action,H::Err>{let n=frame16(h,s.bp,-5)?;Ok(call(s,Phase::Draw,"214B:06B1","0791:49B2",vec![n],true))}
pub fn step<H:Host>(h:&mut H,phase:Phase,saved:Option<Saved>,sent:u16,mutant:bool)->Result<Action,H::Err>{
    let mut s=saved.unwrap_or_default();
    match phase {
        Phase::Start=>{
            s.bp=enter(h,12,0x47c5)?;s.parent=arg(h,0)?;
            s.seg=frame16(h,s.parent,8)?;s.off=frame16(h,s.parent,6)?;s.p=lin(s.seg,s.off);
            Ok(call(s,Phase::SideCountry,"0791:2996","0791:47CE",vec![],false))
        }
        Phase::SideCountry=>{
            let id=ds16(h,(0x9b34i32+2*(sent as u8 as i8 as i32)) as u32)?;
            s.country=record(h,0xa917,0xbf,id)?;
            let off=ds16(h,0xa917)?.wrapping_add((0xbfu32*id as u32) as u16);fw16(h,s.bp,-12,off,0x47e2)?;
            let seg=ds16(h,0xa919)?;fw16(h,s.bp,-10,seg,0x47e5)?;fw8(h,s.bp,-1,0,0x47e8)?;
            Ok(call(s,Phase::SideMark,"0791:2996","0791:47EF",vec![],false))
        }
        Phase::SideMark=>{
            s.side=sent as u8;fw8(h,s.bp,-8,s.side,0x47ef)?;
            let base=ds8(h,0x668+u32::from(s.side==0))?;
            let slot=h.u8(s.p+6)?;s.mark_off=0x9a3e+u32::from(s.side==0)*0x28+2*(slot as u16).wrapping_sub(base as u16) as u32;
            s.mark=ds16(h,s.mark_off)?;fw16(h,s.bp,-7,s.mark,0x4836)?;
            s.slot=2;
            if s.mark==0{fw16(h,s.bp,-3,2,0x483f)?;scan(h,s,mutant)}else{fw16(h,s.bp,-3,2,0x48ab)?;selected(h,s,mutant)}
        }
        Phase::ScanAvailable=>{
            if sent&255!=0{return next_scan(h,s,mutant);}
            let base=ds8(h,0x668+s.side as u32)?;let opp=lin(h.ds(),0x80e8u16.wrapping_add(0x16*(base as u16+s.slot)));
            let point=h.u16(opp)?;Ok(call(s,Phase::ScanZone,"0791:4438","0791:4888",vec![point,s.seg,s.off],true))
        }
        Phase::ScanZone=>{if sent&255!=0{s.mark=s.player;fw16(h,s.bp,-7,s.mark,0x489a)?;}next_scan(h,s,mutant)}
        Phase::SelectedAvailable=>{
            if sent&255!=0{fw16(h,s.bp,-3,s.slot+1,0x49d3)?;s.slot+=1;return selected(h,s,mutant);}
            s.opp_slot=ds8(h,0x668+s.side as u32)? as u16+s.slot;
            fw16(h,s.parent,-4,s.opp_slot,0x48fb)?;
            let opp=lin(h.ds(),0x80e8u16.wrapping_add(0x16*s.opp_slot));let point=h.u16(opp)?;
            fw16(h,s.parent,-2,point,0x4914)?;
            Ok(call(s,Phase::Keeper,"0791:2C54","0791:4930",vec![h.ds(),0x80e8u16.wrapping_add(0x16*s.opp_slot)],true))
        }
        Phase::Keeper=>{
            if sent&255!=0{let high=live_high(h)?;return end(h,high,mutant);}
            fw16(h,s.bp,-5,1,0x4937)?;Ok(call(s,Phase::Ours,"0791:278A","0791:494D",vec![5,s.seg,s.off],true))
        }
        Phase::Ours=>{push(h,sent,0x494d)?;theirs(h,s,false)}
        Phase::Theirs=>{let ours=pop_dx(h)?;if sent>ours{Ok(call(s,Phase::OursAgain,"0791:278A","0791:4980",vec![5,s.seg,s.off],true))}else{draw(h,s)}}
        Phase::OursAgain=>{push(h,sent,0x4980)?;theirs(h,s,true)}
        Phase::TheirsAgain=>{let ours=pop_dx(h)?;fw16(h,s.bp,-5,sent.wrapping_sub(ours)/16+1,0x49a7)?;draw(h,s)}
        Phase::Draw=>{push(h,sent,0x49b2)?;Ok(call(s,Phase::Direction,"0791:2BE5","0791:49C0",vec![s.seg,s.off],true))}
        Phase::Direction=>{
            let draw=pop_dx(h)?;let old=frame8(h,s.parent,-1)?;
            fw8(h,s.parent,-1,(old as i32-(sent as u8 as i8 as i32)*(draw as u8 as i8 as i32)) as u8,0x49c7)?;
            fw8(h,s.bp,-1,1,0x49cb)?;let high=live_high(h)?;end(h,high|1,mutant)
        }
        Phase::ZoneStart=>{
            // argptr performs four independent reads, not runtime.args's one base.
            let seg=arg(h,1)?;let off=arg(h,0)?;s.p=lin(seg,off);s.seg=arg(h,1)?;s.off=arg(h,0)?;
            s.point=arg(h,2)?;s.bp=enter(h,4,0x4438)?;
            let word=h.u16(s.p+9)?;fw16(h,s.bp,-3,word,0x4445)?;
            if h.u8(s.p+0x12)?!=9{
                let id=h.u16(s.p+0xd)?;let p=record(h,0xa91b,0x14,id)?;let position=h.u8(p+6)?;
                let old=frame8(h,s.bp,-2)?;let add=ds8(h,0x7be+position as u32)?;fw8(h,s.bp,-2,old.wrapping_add(add),0x4470)?;
            }
            let x=frame8(h,s.bp,-3)?;let close=((s.point as u8 as i8 as i32)-(x as i8 as i32)).abs()<4;
            if close{return Ok(call(s,Phase::ZoneDirection,"0791:2BE5","0791:4493",vec![s.seg,s.off],true));}
            fw8(h,s.bp,-1,0,0x44b5)?;final_local(h,s,mutant)
        }
        Phase::ZoneDirection=>{
            let y=frame8(h,s.bp,-2)?;
            let close=(((s.point>>8) as u8 as i8 as i32)-(y as i8 as i32)*(sent as u8 as i8 as i32)).abs()<9;
            fw8(h,s.bp,-1,u8::from(close),0x44b5)?;final_local(h,s,mutant)
        }
    }
}

pub fn corrupt<H:Host>(h:&mut H)->Result<(),H::Err>{let at=h.ss_lin((h.entry().0 as u16).wrapping_sub(2) as u32)?;let old=h.u16(at)?;h.write(at,&(old^1).to_le_bytes(),lin(h.seg(0x214b),0))}

// Geometry's inline direction intentionally has no arithmetic flag writes.
fn cbw<H:Host>(h:&mut H,r:&mut Regs)->Result<(),H::Err>{let al=r.al(h)?;r.set_i(Reg::Ax,al as i8 as i64);Ok(())}
fn c2974<H:Host>(h:&mut H,r:&mut Regs,seg:u16,off:u16)->Result<(),H::Err>{
    r.enter(h,2)?;r.set(Reg::Es,seg as u32);r.set(Reg::Di,off as u32);
    let v=u8::from(h.u8(lin(seg,off.wrapping_add(6)))?<12);r.set_al(h,v)?;
    let al=r.al(h)?;r.local8(h,-1,al)?;r.leave(h)
}
pub(crate) fn c2be5<H:Host>(h:&mut H,r:&mut Regs,seg:u16,off:u16)->Result<(),H::Err>{
    r.enter(h,2)?;let half=ds8(h,0x8319)?;r.set_al(h,half)?;cbw(h,r)?;
    let ax=r.get(h,Reg::Ax)?;let dx=if ax&0x8000!=0{65535}else{0};r.set(Reg::Dx,dx);r.set(Reg::Cx,ax as u32);r.set(Reg::Bx,dx);
    let left=ds16(h,0x831b)?;r.set(Reg::Ax,left as u32);r.set(Reg::Dx,0);
    let bx=r.get(h,Reg::Bx)?;let cx=r.get(h,Reg::Cx)?;
    let flag=u8::from((0i16)>(bx as i16)||(bx==0&&left>cx));r.set_al(h,flag)?;
    let pushed=r.get(h,Reg::Ax)?;r.push(h,pushed as u32)?;
    r.set(Reg::Es,seg as u32);r.set(Reg::Di,off as u32);
    invoke(h,r,Some(0x791),0x2c13,&[seg as u32,off as u32],|h,r|c2974(h,r,seg,off))?;
    r.set(Reg::Dx,pushed as u32);let sp=r.get(h,Reg::Sp)?;r.set(Reg::Sp,sp.wrapping_add(2) as u32);
    let al=r.al(h)?;let dx=r.get(h,Reg::Dx)?;r.set_al(h,al^(dx as u8))?;cbw(h,r)?;
    let ax=r.get(h,Reg::Ax)?;r.set(Reg::Di,ax as u32);let v=ds8(h,0x7920+ax as u32)?;r.set_al(h,v)?;
    let al=r.al(h)?;r.local8(h,-1,al)?;r.leave(h)
}
pub fn in_own_half<H:Host>(h:&mut H,mutant:bool)->Result<(),H::Err>{
    let a=args(h,2)?;let (off,seg)=(a[0],a[1]);let mut r=Regs::new(false);r.enter(h,2)?;
    r.set(Reg::Es,seg as u32);r.set(Reg::Di,off as u32);
    invoke(h,&mut r,Some(0x791),0x2c63,&[seg as u32,off as u32],|h,r|c2be5(h,r,seg,off))?;
    cbw(h,&mut r)?;let ax=r.get(h,Reg::Ax)?;r.set(Reg::Dx,ax as u32);
    r.set(Reg::Es,seg as u32);r.set(Reg::Di,off as u32);let y=h.u8(lin(seg,off.wrapping_add(1)))?;r.set_al(h,y)?;cbw(h,&mut r)?;
    let ax=r.get(h,Reg::Ax)?;let dx=r.get(h,Reg::Dx)?;let p=ax as i16 as i32*dx as i16 as i32;r.set(Reg::Ax,p as u32&65535);r.set(Reg::Dx,((p>>16) as u32)&65535);
    let ax=r.get(h,Reg::Ax)?;r.set_al(h,u8::from(ax&0x8000!=0))?;let al=r.al(h)?;r.local8(h,-1,al)?;r.leave(h)?;r.store(h,false)?;
    if mutant{corrupt(h)?;}Ok(())
}
fn add_flags(a:u16)->u32{let b=1;let result=a.wrapping_add(b);let mut f=0;
    if a==65535{f|=CF;}if (result as u8).count_ones()%2==0{f|=PF;}if (a^b^result)&16!=0{f|=AF;}
    if result==0{f|=ZF;}if result&0x8000!=0{f|=SF;}if (!(a^b)&(a^result)&0x8000)!=0{f|=OF;}f}
fn rng_core<H:Host>(h:&mut H,r:&mut Regs,off:u16,seg:u16,n:u16)->Result<(),H::Err>{
    r.enter(h,2)?;let sp=r.get(h,Reg::Sp)?;r.push(h,h.ds() as u32)?;r.push(h,seg as u32)?;r.push(h,off as u32)?;
    let at=lin(seg,off);let new=h.u16(at)?.wrapping_mul(0x7abd).wrapping_add(0x1b0f);
    h.write(at,&new.to_le_bytes(),lin(h.seg(0x214b),0x069f))?;
    let high=((new as u32*n as u32)>>16) as u16;let draw=high.wrapping_add(1);
    let step=if h.reg(Reg::Eflags)?&0x400!=0{65534}else{2};
    r.set(Reg::Bx,0x7abd);r.set(Reg::Si,off.wrapping_add(step) as u32);r.set(Reg::Di,off.wrapping_add(step) as u32);r.set(Reg::Es,seg as u32);
    r.set(Reg::Ax,draw as u32);r.set(Reg::Dx,draw as u32);r.arith((add_flags(high)&!CF)|if high!=0{CF}else{0});r.set(Reg::Sp,sp as u32);
    r.local16(h,-2,draw as u32)?;r.leave(h)
}
pub fn random_n<H:Host>(h:&mut H,mutant:bool)->Result<(),H::Err>{
    let n=args(h,1)?[0];let mut r=Regs::new(false);r.enter(h,2)?;
    let ptr=lin(h.ds(),0xa978);let off=h.u16(ptr)?;let seg=h.u16(ptr+2)?;
    r.set(Reg::Di,off as u32);r.set(Reg::Es,seg as u32);
    invoke(h,&mut r,Some(0x214b),0x06c4,&[seg as u32,off as u32,n as u32],|h,r|rng_core(h,r,off,seg,n))?;
    let ax=r.get(h,Reg::Ax)?;r.local16(h,-2,ax as u32)?;r.leave(h)?;r.store(h,false)?;
    if mutant{corrupt(h)?;}Ok(())
}
