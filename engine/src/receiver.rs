//! T28 pass-receiver destination, pinned contests.py at oracle 2cbeb36f.
use crate::host::{Host, Reg};
use crate::mem::lin;
use crate::regs::Regs;

pub enum Action { Keeper(u16), Done(u16) }
fn ss16<H: Host>(h: &mut H, r: &mut Regs, off: u16) -> Result<u16,H::Err> {
    r.flush(h)?;
    let at=h.ss_lin(off as u32)?;
    h.u16(at)
}
fn nested<H: Host>(h: &mut H, r: &mut Regs) -> Result<(),H::Err> {
    let bp=r.get(h,Reg::Bp)?;
    let parent=ss16(h,r,bp.wrapping_add(4))?;
    r.set(Reg::Di,parent as u32);
    // Python captures DI before evaluating ES then DI with independent live SS.
    let di=r.get(h,Reg::Di)?;
    let seg=ss16(h,r,di.wrapping_add(8))?;
    let off=ss16(h,r,di.wrapping_add(6))?;
    r.set(Reg::Es,seg as u32);
    r.set(Reg::Di,off as u32);
    Ok(())
}
fn slot<H: Host>(h: &mut H,r: &mut Regs) -> Result<u8,H::Err> {
    let seg=r.get(h,Reg::Es)?;
    let off=r.get(h,Reg::Di)?;
    h.u8(lin(seg,off.wrapping_add(6)))
}
fn finish<H: Host>(h: &mut H,r: &mut Regs) -> Result<Action,H::Err> {
    let bp=r.get(h,Reg::Bp)?;
    r.flush(h)?;
    let at=h.ss_lin(bp.wrapping_sub(1) as u32)?;
    let value=h.u8(at)?;
    r.set_al(h,value)?;
    r.leave(h)?;
    r.store(h,false)?;
    Ok(Action::Done(r.get(h,Reg::Ax)?))
}
pub fn step<H: Host>(h: &mut H,resumed: bool) -> Result<Action,H::Err> {
    let mut r=Regs::new(resumed);
    if !resumed {
        r.enter(h,2)?;
        nested(h,&mut r)?;
        let value=slot(h,&mut r)?;
        r.set_al(h,value)?;
        let al=r.al(h)?;
        let receiver=h.u8(lin(h.ds(),0x830c))?;
        if al!=receiver {
            r.local8(h,-1,0)?;
            return finish(h,&mut r);
        }
        r.local8(h,-1,1)?;
        nested(h,&mut r)?;
        let value=slot(h,&mut r)?;
        r.set_al(h,value)?;
        r.set_ah(h,0)?;
        let ax=r.get(h,Reg::Ax)?;
        r.store(h,true)?;
        return Ok(Action::Keeper(ax));
    }
    // Source short-circuits the live countdown read for a nonzero keeper AL.
    let early=if r.al(h)?!=0 {true} else {h.u16(lin(h.ds(),0x8300))?<10};
    let value=h.u16(lin(h.ds(),if early {0x82f6}else{0x8313}))?;
    r.set(Reg::Ax,value as u32);
    nested(h,&mut r)?;
    let seg=r.get(h,Reg::Es)?;
    let off=r.get(h,Reg::Di)?;
    let ax=r.get(h,Reg::Ax)?;
    let site=if early {0x537c}else{0x538c};
    h.write(lin(seg,off.wrapping_add(7)),&ax.to_le_bytes(),lin(h.seg(0x791),site))?;
    finish(h,&mut r)
}
