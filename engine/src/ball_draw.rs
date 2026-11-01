//! display.draw_ball_state0791:8F10/grid_cell, accepted oracle2cbeb36f.
use crate::host::{Host, Reg};
use crate::mem::{cbw, lin};
use crate::regs::{Regs, ZF};

#[derive(Clone, Copy)]
pub struct Record { pub seg: u16, pub off: u16 }
#[derive(Clone, Copy)]
pub enum Phase { Start, Member(Record), Travel(Record) }
pub struct Request { pub next: Phase, pub target: &'static str, pub ret_to: &'static str, pub args: Vec<u16> }

fn ds16<H: Host>(h: &mut H, off: u16) -> Result<u16, H::Err> { h.u16(lin(h.ds(), off)) }
fn rb<H: Host>(h: &mut H, r: &mut Regs, off: u16) -> Result<u8, H::Err> {
    let seg = r.get(h, Reg::Es)?; let di = r.get(h, Reg::Di)?;
    h.u8(lin(seg, di.wrapping_add(off)))
}
fn rw<H: Host>(h: &mut H, r: &mut Regs, off: u16) -> Result<u16, H::Err> {
    let seg = r.get(h, Reg::Es)?; let di = r.get(h, Reg::Di)?;
    h.u16(lin(seg, di.wrapping_add(off)))
}
fn write<H: Host>(h: &mut H, r: &mut Regs, off: u16, bytes: &[u8], at: u16) -> Result<(), H::Err> {
    let seg = r.get(h, Reg::Es)?; let di = r.get(h, Reg::Di)?;
    h.write(lin(seg, di.wrapping_add(off)), bytes, lin(h.seg(0x0791), at))
}
fn record(r: &mut Regs, p: Record) { r.set(Reg::Es, p.seg as u32); r.set(Reg::Di, p.off as u32); }
fn ss16<H: Host>(h: &mut H, r: &mut Regs, off: u16) -> Result<u16, H::Err> {
    r.flush(h)?; let at = h.ss_lin(off as u32)?; h.u16(at)
}
fn grid<H: Host>(h: &mut H, r: &mut Regs, p: Record, row: u16, column: u16, pointer: u16) -> Result<(), H::Err> {
    record(r, p);
    let b = rb(h, r, column)?; r.set_al(h, b)?;
    let al = r.al(h)?; r.set(Reg::Ax, cbw(al) as u32);
    let ax = r.get(h, Reg::Ax)?.wrapping_shl(1); r.set(Reg::Ax, ax as u32);
    let ax = r.get(h, Reg::Ax)?; r.set(Reg::Cx, ax as u32);
    record(r, p);
    let b = rb(h, r, row)?; r.set_al(h, b)?;
    let al = r.al(h)?; r.set(Reg::Ax, cbw(al) as u32); r.set(Reg::Dx, 0xa0);
    // Source mul evaluates DX first, then AX, and does not update flags.
    let src = r.get(h, Reg::Dx)?; let ax = r.get(h, Reg::Ax)?;
    let product = ax as u32 * src as u32;
    r.set(Reg::Ax, product & 0xffff); r.set(Reg::Dx, product >> 16);
    let di = ds16(h, pointer)?; let es = ds16(h, pointer.wrapping_add(2))?;
    r.set(Reg::Di, di as u32); r.set(Reg::Es, es as u32);
    let di = r.get(h, Reg::Di)?; let ax = r.get(h, Reg::Ax)?; let cx = r.get(h, Reg::Cx)?;
    r.set(Reg::Di, di.wrapping_add(ax).wrapping_add(cx) as u32); Ok(())
}
fn request<H: Host>(h: &mut H, r: &mut Regs, next: Phase, target: &'static str, ret_to: &'static str, args: Vec<u16>) -> Result<Option<Request>, H::Err> {
    r.store(h, true)?; Ok(Some(Request { next, target, ret_to, args }))
}
fn finish<H: Host>(h: &mut H, r: &mut Regs, p: Record, high: bool, mutant: bool) -> Result<Option<Request>, H::Err> {
    r.set_al(h, u8::from(high))?;
    let al = r.al(h)?; r.set(Reg::Ax, cbw(al) as u32);
    let ax = r.get(h, Reg::Ax)?; r.set(Reg::Di, ax as u32);
    let di = r.get(h, Reg::Di)?; let glyph = h.u8(lin(h.ds(), di.wrapping_add(0x880)))?;
    r.set_al(h, glyph)?; record(r, p);
    let al = r.al(h)?; write(h, r, 4, &[al], 0x8fe9)?;
    let ax = rw(h, r, 0)?; r.set(Reg::Ax, ax as u32);
    let ax = r.get(h, Reg::Ax)?;
    if ax != ds16(h, 0x640)? {
        grid(h, r, p, 0, 1, 0x7c1e)?;
        let bx = rw(h, r, 0x90e)?; r.set(Reg::Bx, bx as u32);
        grid(h, r, p, 0, 1, 0x7c16)?;
        let ax = rw(h, r, 0x90e)?; r.set(Reg::Ax, ax as u32);
        let ax = r.get(h, Reg::Ax)?; let bx = r.get(h, Reg::Bx)?;
        if ax == bx {
            record(r, p); let bx = rw(h, r, 4)?; r.set(Reg::Bx, bx as u32);
            grid(h, r, p, 0, 1, 0x7c16)?;
            let bx = r.get(h, Reg::Bx)?; write(h, r, 0x90e, &bx.to_le_bytes(), 0x906e)?;
        }
    }
    r.leave(h)?; r.store(h, false)?;
    if mutant {
        let at = h.ss_lin((h.entry().0 as u16).wrapping_sub(2) as u32)?;
        let old = h.u16(at)?; h.write(at, &(old ^ 1).to_le_bytes(), lin(h.seg(0x214b), 0))?;
    }
    Ok(None)
}
fn tail<H: Host>(h: &mut H, r: &mut Regs, p: Record, mutant: bool) -> Result<Option<Request>, H::Err> {
    record(r, p); let ax = rw(h, r, 0)?; r.set(Reg::Ax, ax as u32);
    let ax = r.get(h, Reg::Ax)?; write(h, r, 2, &ax.to_le_bytes(), 0x8fbd)?;
    if rb(h, r, 0xd)? != 0 {
        return request(h, r, Phase::Travel(p), "0791:835F", "0791:8FD4", vec![p.seg, p.off]);
    }
    finish(h, r, p, false, mutant)
}
pub fn step<H: Host>(h: &mut H, phase: Phase, mutant: bool) -> Result<Option<Request>, H::Err> {
    let mut r = Regs::new(!matches!(phase, Phase::Start));
    match phase {
        Phase::Start => {
            r.enter(h, 0)?;
            let bp = r.get(h, Reg::Bp)?; let seg = ss16(h, &mut r, bp.wrapping_add(8))?;
            let bp = r.get(h, Reg::Bp)?; let off = ss16(h, &mut r, bp.wrapping_add(6))?;
            let p = Record { seg, off }; record(&mut r, p);
            let ax = rw(h, &mut r, 2)?; r.set(Reg::Ax, ax as u32);
            let ax = r.get(h, Reg::Ax)?;
            if ax != ds16(h, 0x640)? {
                record(&mut r, p); let ax = rw(h, &mut r, 2)?; r.set(Reg::Ax, ax as u32);
                let ax = r.get(h, Reg::Ax)?;
                if ax != rw(h, &mut r, 0)? {
                    grid(h, &mut r, p, 2, 3, 0x7c16)?;
                    let al = rb(h, &mut r, 0x90e)?; r.set_al(h, al)?;
                    let arg = r.get(h, Reg::Ax)?; r.set(Reg::Di, 0x8ef0);
                    let di = r.get(h, Reg::Di)?; let code = h.seg(0x0791);
                    return request(h, &mut r, Phase::Member(p), "23E4:08DF", "0791:8F66", vec![arg, code, di]);
                }
            }
            tail(h, &mut r, p, mutant)
        }
        Phase::Member(p) => {
            if h.reg(Reg::Eflags)? & ZF == 0 {
                grid(h, &mut r, p, 2, 3, 0x7c1e)?;
                let bx = rw(h, &mut r, 0x90e)?; r.set(Reg::Bx, bx as u32);
                grid(h, &mut r, p, 2, 3, 0x7c16)?;
                let bx = r.get(h, Reg::Bx)?; write(h, &mut r, 0x90e, &bx.to_le_bytes(), 0x8faf)?;
            }
            tail(h, &mut r, p, mutant)
        }
        Phase::Travel(p) => {
            let high = r.get(h, Reg::Ax)? > 2;
            finish(h, &mut r, p, high, mutant)
        }
    }
}
