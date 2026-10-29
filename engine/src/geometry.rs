//! Translated routines of the port's geometry queries and pilot helper entry points.
//!
//! Each function is the Python routine of goal2-archaeology d3cf46a3 (module and address named on it), statement by
//! statement, on the same `Regs` model, so that the registers it reads and sets, the stack words it writes (and the
//! runs they are flushed in), and its memory writes are the Python routine's, in its order. The structure is the
//! listing's (static/goal-exe/code/seg_0791_04.asm / _05.asm offsets as the Python cites them); the semantics are the
//! Python port's, proved against the original by T78d. [confirmed: goal2-archaeology d3cf46a3,
//! runtime/original_match/port/geometry.py, entrypoints.py, runtime.py set_test]
use std::sync::atomic::{AtomicU32, Ordering};

use crate::host::{args, Host, Reg};
use crate::mem::{cbw, lin, off_add, M16};
use crate::regs::{invoke, sub_flags, Regs, PF, SF, ZF};

pub const CS: u16 = 0x791;
pub const BALL_SLOT: u16 = 0x830B;
pub const PLAYERS_PTR: u16 = 0xA91B;
pub const COUNTRIES_PTR: u16 = 0xA917;
pub const DIRECTIONS: u16 = 0x7920;

/// T01's falsifiers: a deliberate difference in one translated routine, to show the equality checks catch it.
/// 0 none; 1: 2B51 leaves its dead frame byte [bp-1] unwritten; 2: 2974 counts slot 0xC as side 0.
pub static MUTANT: AtomicU32 = AtomicU32::new(0);

#[inline]
fn mutant() -> u32 {
    MUTANT.load(Ordering::Relaxed)
}

#[inline]
fn ds8<H: Host>(h: &mut H, off: u16) -> Result<u8, H::Err> {
    let ds = h.ds();
    h.u8(lin(ds, off))
}

#[inline]
fn ds16<H: Host>(h: &mut H, off: u16) -> Result<u16, H::Err> {
    let ds = h.ds();
    h.u16(lin(ds, off))
}

#[inline]
fn rec8<H: Host>(h: &mut H, seg: u16, off: u16, k: u16) -> Result<u8, H::Err> {
    h.u8(lin(seg, off_add(off, k)))
}

#[inline]
fn rec16<H: Host>(h: &mut H, seg: u16, off: u16, k: u16) -> Result<u16, H::Err> {
    h.u16(lin(seg, off_add(off, k)))
}

/// entrypoints.test_flags: TEST byte's PF ZF SF.
fn test_flags(value: u32) -> u32 {
    let mut f = 0;
    if (value & 255).count_ones() % 2 == 0 {
        f |= PF;
    }
    if value == 0 {
        f |= ZF;
    }
    if value & 128 != 0 {
        f |= SF;
    }
    f
}

/// geometry.mul: `mul src` (word): DX:AX := AX * src.
fn mul<H: Host>(h: &mut H, r: &mut Regs, src: u32) -> Result<(), H::Err> {
    let p = r.get(h, Reg::Ax)? as u32 * (src & M16);
    r.set(Reg::Ax, p & M16);
    r.set(Reg::Dx, p >> 16);
    Ok(())
}

/// geometry.cbw.
fn cbw_r<H: Host>(h: &mut H, r: &mut Regs) -> Result<(), H::Err> {
    let al = r.al(h)?;
    r.set(Reg::Ax, cbw(al) as u32);
    Ok(())
}

/// geometry.c2996 (2996): 1 when the ball slot DS:830B is below 0xC.
fn c2996<H: Host>(h: &mut H, r: &mut Regs) -> Result<(), H::Err> {
    r.enter(h, 2)?;
    let v = if ds8(h, BALL_SLOT)? < 0xC { 1 } else { 0 };
    r.set_al(h, v)?;
    let al = r.al(h)?;
    r.local8(h, -1, al)?;
    r.leave(h)
}

/// geometry.c2974 (2974 pitch_slot_side(rec)): 1 when the record's slot (+6) is below 0xC.
fn c2974<H: Host>(h: &mut H, r: &mut Regs, seg: u16, off: u16) -> Result<(), H::Err> {
    r.enter(h, 2)?;
    r.set(Reg::Es, seg as u32);
    r.set(Reg::Di, off as u32);
    let limit = if mutant() == 2 { 0xD } else { 0xC };
    let v = if rec8(h, seg, off, 6)? < limit { 1 } else { 0 };
    r.set_al(h, v)?;
    let al = r.al(h)?;
    r.local8(h, -1, al)?;
    r.leave(h)
}

/// geometry.slot_is_on_ball_side, 0791:2B51 (retf 4): 2996 = 2974(rec).
pub fn slot_is_on_ball_side<H: Host>(h: &mut H) -> Result<(), H::Err> {
    let a = args(h, 2)?;
    let (off, seg) = (a[0], a[1]);
    let mut r = Regs::new(false);
    r.enter(h, 2)?; // 2B51-2B56
    invoke(h, &mut r, None, 0x2B5A, &[], |h, r| c2996(h, r))?; // 2B57
    let side = r.get(h, Reg::Ax)?;
    r.push(h, side as u32)?; // 2B5A push ax
    r.set(Reg::Es, seg as u32); // 2B5B
    r.set(Reg::Di, off as u32);
    invoke(h, &mut r, Some(CS), 0x2B64, &[seg as u32, off as u32], |h, r| c2974(h, r, seg, off))?; // 2B5E-2B61
    r.set(Reg::Dx, side as u32); // 2B64 pop dx
    let sp = r.get(h, Reg::Sp)?;
    r.set(Reg::Sp, sp.wrapping_add(2) as u32);
    let al = r.al(h)?;
    let dx = r.get(h, Reg::Dx)?;
    r.set_al(h, if al == (dx & 0xFF) as u8 { 1 } else { 0 })?; // 2B65-2B6D
    if mutant() != 1 {
        let al = r.al(h)?;
        r.local8(h, -1, al)?; // 2B6F
    }
    r.leave(h)?;
    r.store(h, false)
}

/// entrypoints.side_core: 2974 with its flags (the slot compared with 0xC).
fn side_core<H: Host>(h: &mut H, r: &mut Regs, off: u16, seg: u16) -> Result<(), H::Err> {
    r.enter(h, 2)?;
    r.set(Reg::Di, off as u32);
    r.set(Reg::Es, seg as u32);
    let slot = h.u8(lin(seg, off_add(off, 6)))?;
    r.arith(sub_flags(slot as u32, 12, 8));
    // pilot.pitch_slot_side(mem, seg * 16 + off): the linear rec + 6, not wrapped in its segment
    let limit = if mutant() == 2 { 0xD } else { 0xC };
    let v = if h.u8(lin(seg, off) + 6)? < limit { 1 } else { 0 };
    r.set_al(h, v)?;
    let al = r.al(h)?;
    r.local8(h, -1, al)?;
    r.leave(h)
}

/// entrypoints.side, 0791:2974 (retf 4).
pub fn side<H: Host>(h: &mut H) -> Result<(), H::Err> {
    let a = args(h, 2)?;
    let (off, seg) = (a[0], a[1]);
    let mut r = Regs::new(false);
    side_core(h, &mut r, off, seg)?;
    r.store(h, false)
}

/// entrypoints.direction, 0791:2BE5 (retf 4): attack direction of the record.
pub fn direction<H: Host>(h: &mut H) -> Result<(), H::Err> {
    let a = args(h, 2)?;
    let (off, seg) = (a[0], a[1]);
    let mut r = Regs::new(false);
    r.enter(h, 2)?;
    let half = ds8(h, 0x8319)? as i8 as i32; // s8
    let left = ds16(h, 0x831B)? as i32;
    r.set_i(Reg::Cx, half as i64);
    r.set_i(Reg::Bx, if half < 0 { -1 } else { 0 });
    r.set(Reg::Dx, 0);
    r.set(Reg::Ax, left as u32);
    r.set_al(h, (half < 0 || left > half) as u8)?;
    let saved = r.get(h, Reg::Ax)?;
    r.push(h, saved as u32)?;
    r.set(Reg::Di, off as u32);
    r.set(Reg::Es, seg as u32);
    invoke(h, &mut r, Some(0x0791), 0x2C13, &[seg as u32, off as u32], |h, r| side_core(h, r, off, seg))?;
    r.set(Reg::Dx, saved as u32);
    let sp = r.get(h, Reg::Sp)?;
    r.set(Reg::Sp, sp.wrapping_add(2) as u32);
    let al = r.al(h)?;
    let dx = r.get(h, Reg::Dx)?;
    let value = (al ^ (dx & 255) as u8) as u32;
    r.arith(test_flags(value));
    r.set(Reg::Ax, cbw(value as u8) as u32); // s8(value), masked
    let ax = r.get(h, Reg::Ax)?;
    r.set(Reg::Di, ax as u32);
    let di = r.get(h, Reg::Di)?;
    let v = ds8(h, di.wrapping_add(DIRECTIONS))?;
    r.set_al(h, v)?;
    let al = r.al(h)?;
    r.local8(h, -1, al)?;
    r.leave(h)?;
    r.store(h, false)
}

/// entrypoints.keeper, 0791:045D (ret 2): the word is slot 1 or 0xC.
pub fn keeper<H: Host>(h: &mut H) -> Result<(), H::Err> {
    let slot = args(h, 1)?[0];
    let mut r = Regs::new(false);
    r.enter(h, 2)?;
    r.arith(sub_flags(slot as u32, if slot == 1 { 1 } else { 12 }, 16));
    // finish_bool
    r.set_al(h, (slot == 1 || slot == 0xC) as u8)?;
    let al = r.al(h)?;
    r.local8(h, -1, al)?;
    r.leave(h)?;
    r.store(h, false)
}

/// geometry.player_byte: the player record's byte `field` of a pitch record.
fn player_byte<H: Host>(h: &mut H, r: &mut Regs, seg: u16, off: u16, field: u16) -> Result<(), H::Err> {
    r.set(Reg::Es, seg as u32);
    r.set(Reg::Di, off as u32);
    let idx = rec16(h, seg, off, 0xD)?;
    r.set(Reg::Ax, idx as u32);
    r.set(Reg::Dx, 0x14);
    mul(h, r, 0x14)?;
    let ds = h.ds();
    let p = lin(ds, PLAYERS_PTR);
    let poff = h.u16(p)?;
    let pseg = h.u16(p + 2)?;
    let ax = r.get(h, Reg::Ax)?;
    r.set(Reg::Es, pseg as u32);
    r.set(Reg::Di, poff.wrapping_add(ax) as u32);
    let di = r.get(h, Reg::Di)?;
    let b = rec8(h, pseg, di, field)?;
    r.set_al(h, b)?;
    r.set_ah(h, 0)
}

/// runtime.set_test (214B:0C57 from its push bp): bit k - 1 of the word value.
fn set_test<H: Host>(h: &mut H, r: &mut Regs, value: u32, k: u32) -> Result<(), H::Err> {
    r.enter(h, 2)?;
    let dx = k.wrapping_sub(1) & M16;
    r.set(Reg::Dx, dx);
    r.set(Reg::Cx, dx);
    let shift = (dx & 0xFF) & 0x1F;
    r.set(Reg::Ax, (value >> shift) & 1);
    let al = r.al(h)?;
    r.local8(h, -1, al)?;
    r.leave(h)
}

/// geometry.player_effective_tactic, 0791:26D7 (retf 6).
pub fn player_effective_tactic<H: Host>(h: &mut H) -> Result<(), H::Err> {
    let a = args(h, 3)?;
    let (off, seg, k) = (a[0], a[1], a[2] as u32);
    let mut r = Regs::new(false);
    r.enter(h, 2)?; // 26D7-26DC
    let sp_frame = r.get(h, Reg::Sp)?;
    if k < 5 {
        player_byte(h, &mut r, seg, off, 0xF)?; // 26E3-26FF
        let own = r.get(h, Reg::Ax)? as u32;
        let k4 = (k + 4) & M16;
        invoke(h, &mut r, Some(CS), 0x2708, &[k4, own], |h, r| set_test(h, r, own, k4))?;
        if r.al(h)? != 0 {
            player_byte(h, &mut r, seg, off, 0xF)?;
            let own = r.get(h, Reg::Ax)? as u32;
            invoke(h, &mut r, Some(CS), 0x272D, &[k, own], |h, r| set_test(h, r, own, k))?;
            let al = r.al(h)?;
            r.local8(h, -1, al)?;
            r.leave(h)?;
            return r.store(h, false);
        }
    }
    r.push(h, k)?; // 2732
    r.set(Reg::Es, seg as u32);
    r.set(Reg::Di, off as u32);
    invoke(h, &mut r, Some(CS), 0x273E, &[seg as u32, off as u32], |h, r| c2974(h, r, seg, off))?;
    cbw_r(h, &mut r)?; // 273E
    let ax = r.get(h, Reg::Ax)? as u32;
    r.set(Reg::Di, (ax << 1) & M16);
    let di = r.get(h, Reg::Di)?;
    let w = ds16(h, 0x9B34u16.wrapping_add(di))?;
    r.set(Reg::Ax, w as u32);
    r.set(Reg::Dx, 0xBF);
    mul(h, &mut r, 0xBF)?;
    let ds = h.ds();
    let p = lin(ds, COUNTRIES_PTR);
    let coff = h.u16(p)?;
    let cseg = h.u16(p + 2)?;
    let ax = r.get(h, Reg::Ax)?;
    r.set(Reg::Es, cseg as u32);
    r.set(Reg::Di, coff.wrapping_add(ax) as u32);
    let di = r.get(h, Reg::Di)?;
    let b = rec8(h, cseg, di, 0x2D)?;
    r.set_al(h, b)?;
    r.set_ah(h, 0)?;
    let value = r.get(h, Reg::Ax)? as u32;
    r.push(h, value)?; // 2758
    let cs = h.seg(CS);
    r.push(h, cs as u32)?; // 2759
    r.push(h, 0x275E)?;
    set_test(h, &mut r, value, k)?;
    r.set(Reg::Sp, sp_frame as u32);
    let al = r.al(h)?;
    r.local8(h, -1, al)?; // 275E
    r.leave(h)?;
    r.store(h, false)
}

/// geometry.slot_is_idle_ball_slot, 0791:2C29 (retf 4): the record's slot is the ball slot and DS:8302 is 0.
pub fn slot_is_idle_ball_slot<H: Host>(h: &mut H) -> Result<(), H::Err> {
    let a = args(h, 2)?;
    let (off, seg) = (a[0], a[1]);
    let mut r = Regs::new(false);
    r.enter(h, 2)?; // 2C29-2C2E
    let b = ds8(h, BALL_SLOT)?;
    r.set_al(h, b)?; // 2C2F
    r.set(Reg::Es, seg as u32); // 2C32
    r.set(Reg::Di, off as u32);
    let al = r.al(h)?;
    // `R.al == rec8(...) and mem.ds8(0x8302) == 0`: the second read only when the first holds
    let v = al == rec8(h, seg, off, 6)? && ds8(h, 0x8302)? == 0;
    r.set_al(h, v as u8)?; // 2C35-2C46
    let al = r.al(h)?;
    r.local8(h, -1, al)?; // 2C48
    r.leave(h)?;
    r.store(h, false)
}

/// geometry.player_at_ball, 0791:2CEC (retf 4): the record's position word equals the ball word DS:82F6.
pub fn player_at_ball<H: Host>(h: &mut H) -> Result<(), H::Err> {
    let a = args(h, 2)?;
    let (off, seg) = (a[0], a[1]);
    let mut r = Regs::new(false);
    r.enter(h, 2)?; // 2CEC-2CF1
    r.set(Reg::Es, seg as u32); // 2CF2
    r.set(Reg::Di, off as u32);
    let w = rec16(h, seg, off, 0)?;
    r.set(Reg::Ax, w as u32); // 2CF5
    let ax = r.get(h, Reg::Ax)?;
    let v = ax == ds16(h, 0x82F6)?;
    r.set_al(h, v as u8)?; // 2CF8-2D02
    let al = r.al(h)?;
    r.local8(h, -1, al)?; // 2D04
    r.leave(h)?;
    r.store(h, false)
}
