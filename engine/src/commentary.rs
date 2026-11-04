//! T26: the complete offside/commentary tree at accepted oracle 2cbeb36f.
use crate::host::{args, Host, Reg};
use crate::mem::lin;
use crate::regs::Regs;

pub const BODIES: [&str; 10] = ["0791:1829", "0791:1C78", "0791:1D4A", "0791:1E53", "0791:1EB5", "0791:26A0", "0791:2B0F", "0791:56D9", "214B:0018", "214B:1C86"];
pub const RETURNS: [&str; 25] = ["0791:5700", "0791:570E", "0791:571B", "0791:2B22", "0791:1EBF", "0791:1ED0", "0791:1F21", "0791:1873", "0791:18A5", "0791:18AF", "0791:18BD", "0791:18DD", "0791:192E", "0791:18E7", "0791:1938", "0791:1900", "0791:1951", "0791:190E", "0791:195F", "0791:1988", "0791:19B2", "0791:19DE", "0791:1D5F", "0791:1D88", "0791:1E36"];
pub fn index(address: &str) -> Option<u32> { BODIES.iter().position(|a| *a == address).map(|i| i as u32) }

#[derive(Clone, Copy, PartialEq, Eq)]
pub enum Phase { Start, OffDirection, OffMessage, OffComment, PlainDone, WriteCompare, WriteRing, WriteNext,
    EmitRating, EmitWritten, EmitDraw, RenderCopied, PrefixStored, PrefixConcat, PrefixCopied,
    MarkerCheck, MarkerStored, MarkerConcat, MarkerName, MarkerCopied, Pad, Filled, Draw, Drawn }
#[derive(Clone, Copy, Default)]
pub struct Saved { pub kind: u32, bp: u16, ds: u16, n: u16, i: u16, record: u16, line: u16, expression: u16, marker: u8, draw: u8 }
impl Saved { pub fn new(kind: u32) -> Self { Self { kind, ..Self::default() } } }
pub struct Request { pub next: Phase, pub saved: Saved, pub target: &'static str, pub ret_to: &'static str, pub args: Vec<u16>, pub far: bool }
pub enum Action { Call(Request), Done(Option<u16>) }
fn call(s: Saved, next: Phase, target: &'static str, ret_to: &'static str, words: Vec<u16>, far: bool) -> Action {
    Action::Call(Request { next, saved: s, target, ret_to, args: words, far })
}
fn d8<H: Host>(h: &mut H, off: u16) -> Result<u8, H::Err> { h.u8(lin(h.ds(), off)) }
fn d16<H: Host>(h: &mut H, off: u16) -> Result<u16, H::Err> { h.u16(lin(h.ds(), off)) }
fn write<H: Host>(h: &mut H, at: u32, v: &[u8], pc: u16) -> Result<(), H::Err> { h.write(at, v, lin(h.seg(0x791), pc)) }
fn f8<H: Host>(h: &mut H, bp: u16, k: i32) -> Result<u8, H::Err> { let a = h.ss_lin(bp.wrapping_add(k as u16) as u32)?; h.u8(a) }
fn f16<H: Host>(h: &mut H, bp: u16, k: i32) -> Result<u16, H::Err> { let a = h.ss_lin(bp.wrapping_add(k as u16) as u32)?; h.u16(a) }
fn fw8<H: Host>(h: &mut H, bp: u16, k: i32, v: u8, pc: u16) -> Result<(), H::Err> { let a = h.ss_lin(bp.wrapping_add(k as u16) as u32)?; write(h, a, &[v], pc) }
fn fw16<H: Host>(h: &mut H, bp: u16, k: i32, v: u16, pc: u16) -> Result<(), H::Err> { let a = h.ss_lin(bp.wrapping_add(k as u16) as u32)?; write(h, a, &v.to_le_bytes(), pc) }
fn arg<H: Host>(h: &mut H, i: u32) -> Result<u16, H::Err> { let (sp, far) = h.entry(); let a = h.ss_lin(sp + if far { 4 } else { 2 } + 2*i)?; h.u16(a) }
fn enter<H: Host>(h: &mut H, size: u16, pc: u16) -> Result<u16, H::Err> {
    let sp = (h.reg(Reg::Sp)? as u16).wrapping_sub(2);
    let a = h.ss_lin(sp as u32)?; let bp = h.reg(Reg::Bp)? as u16;
    write(h, a, &bp.to_le_bytes(), pc)?; h.set_reg(Reg::Sp, sp as u32)?;
    h.set_reg(Reg::Bp, sp as u32)?; h.set_reg(Reg::Sp, sp.wrapping_sub(size) as u32)?; Ok(sp)
}
fn set_ax<H: Host>(h: &mut H, v: u16) -> Result<u16, H::Err> { h.set_reg(Reg::Ax, v as u32)?; Ok(v) }
fn set_al<H: Host>(h: &mut H, v: u8) -> Result<u16, H::Err> { let high = h.reg(Reg::Ax)? as u16 & 0xff00; set_ax(h, high | v as u16) }
fn far_record<H: Host>(h: &mut H, pointer: u16, index: u16, size: u16) -> Result<(u16,u16), H::Err> {
    let a = lin(h.ds(), pointer); let off = h.u16(a)?; let seg = h.u16(a+2)?;
    Ok((seg, off.wrapping_add(index.wrapping_mul(size))))
}
fn word<H: Host>(h: &mut H, seg: u16, off: u16, index: u16) -> Result<u16, H::Err> {
    h.u16(lin(seg, off.wrapping_add(index.wrapping_shl(1)).wrapping_sub(2)))
}
fn ss16<H: Host>(h: &mut H, r: &mut Regs, off: u16) -> Result<u16, H::Err> { r.flush(h)?; let a = h.ss_lin(off as u32)?; h.u16(a) }
fn raw8<H: Host>(h: &mut H, off: u16) -> Result<u8, H::Err> { let a = h.ss_lin(off as u32)?; h.u8(a) }
fn end<H: Host>(h: &mut H, r: &mut Regs, returns_ax: bool) -> Result<Action, H::Err> {
    let value = if returns_ax { Some(r.get(h, Reg::Ax)?) } else { None };
    r.leave(h)?; r.store(h, false)?; Ok(Action::Done(value))
}
fn mul<H: Host>(h: &mut H, r: &mut Regs) -> Result<(), H::Err> {
    let ax = r.get(h, Reg::Ax)?; let dx = r.get(h, Reg::Dx)?; let p = ax as u32 * dx as u32;
    r.set(Reg::Ax, p); r.set(Reg::Dx, p >> 16); Ok(())
}
fn cbw<H: Host>(h: &mut H, r: &mut Regs) -> Result<(), H::Err> { let al = r.al(h)?; r.set_i(Reg::Ax, al as i8 as i64); Ok(()) }
fn guest<H: Host>(h: &mut H, r: &mut Regs, s: Saved, next: Phase, target: &'static str, ret: &'static str, words: Vec<u16>, far: bool) -> Result<Action,H::Err> {
    r.store(h, true)?; Ok(call(s, next, target, ret, words, far))
}

fn is_new<H: Host>(h: &mut H) -> Result<u16,H::Err> {
    let parent = arg(h, 0)?; let bp = enter(h, 14, 0x1c78)?; let ds = h.ds();
    let ring = d16(h, 0x80ee)?.wrapping_mul(6).wrapping_add(0x7c38);
    fw16(h, bp, -9, ring, 0x1c8e)?; fw16(h, bp, -7, ds, 0x1c91)?;
    let side = f8(h, parent, 10)? as i8 as i32;
    let prod = d16(h, (0x9b34 + 2*side) as u16)? as u32 * 0xbf;
    let index = d16(h, (0x9b34 + 2*side) as u16)?;
    let (seg, off) = far_record(h, 0xa917, index, 0xbf)?;
    fw16(h, bp, -13, off, 0x1caf)?; fw16(h, bp, -11, seg, 0x1cb2)?;
    let first = f16(h, parent, 8)?;
    let v3 = if first == 0 { fw16(h, bp, -3, 0, 0x1cc1)?; 0 } else { let v = word(h, seg, off, first)?; fw16(h, bp, -3, v, 0x1cd8)?; v };
    let second = f16(h, parent, 6)?;
    let v5 = if second == 0 { fw16(h, bp, -5, 0, 0x1ce7)?; 0 } else { let v = word(h, seg, off, second)?; fw16(h, bp, -5, v, 0x1cfe)?; v };
    let code = f8(h, parent, 4)?; let top = lin(ds, ring); let mut ax = (v5 & 0xff00) | code as u16; let mut differ = 1;
    if code == h.u8(top)? { ax = v3; if v3 == h.u16(top+1)? { ax = v5; if v5 == h.u16(top+3)? {
        ax = (ax & 0xff00) | h.u8(top+5)? as u16; differ = u8::from(ax as u8 != f8(h, parent, 10)?);
    } } }
    ax = (ax & 0xff00) | differ as u16; fw8(h, bp, -1, differ, 0x1d3e)?;
    h.set_reg(Reg::Dx, prod >> 16)?; Ok(ax)
}
fn performance_delta<H: Host>(h: &mut H) -> Result<(),H::Err> {
    let parent = arg(h, 0)?; let bp = enter(h, 8, 0x1e53)?; let ds = h.ds();
    let side = f8(h, parent, 10)? as i8 as i32;
    let base = d8(h, (0x668 + side) as u16)?; let slot = (base as u16).wrapping_add(f16(h, parent, 8)?);
    let rec = slot.wrapping_mul(22).wrapping_add(0x80e8);
    fw16(h, bp, -4, rec, 0x1e7b)?; fw16(h, bp, -2, ds, 0x1e7e)?;
    let prod = h.u16(lin(ds, rec.wrapping_add(13)))? as u32 * 20;
    let id = h.u16(lin(ds, rec.wrapping_add(13)))?; let (seg, off) = far_record(h, 0xa91b, id, 20)?;
    fw16(h, bp, -8, off, 0x1e93)?; fw16(h, bp, -6, seg, 0x1e96)?;
    let code = f8(h, parent, 4)? as i8 as i32; let delta = d8(h, (0x720 + code) as u16)? as i8 as i16;
    let target = lin(seg, off.wrapping_add(18)); let old = h.u16(target)?;
    write(h, target, &old.wrapping_add(delta as u16).to_le_bytes(), 0x1eab)?;
    set_ax(h, delta as u16)?; h.set_reg(Reg::Dx, prod >> 16)
}
fn fill<H: Host>(h: &mut H) -> Result<(),H::Err> {
    let a = args(h, 4)?; let (value, count, off, seg) = (a[0], a[1], a[2], a[3]);
    let mut r = Regs::new(false); r.enter(h, 0)?; r.push(h, count as u32)?; r.cld();
    r.set(Reg::Es, seg as u32); r.set(Reg::Ax, value as u32); let low = r.al(h)?; r.set_ah(h, low)?;
    let word = r.get(h, Reg::Ax)?;
    for k in 0..count/2 { h.write(lin(seg, off.wrapping_add(2*k)), &word.to_le_bytes(), lin(h.seg(0x214b), 0x2d))?; }
    let mut di = off.wrapping_add(2*(count/2));
    if count & 1 != 0 { h.write(lin(seg, di), &[word as u8], lin(h.seg(0x214b), 0x34))?; di = di.wrapping_add(1); }
    r.set(Reg::Di, di as u32); r.set(Reg::Cx, 0); let sp = r.get(h, Reg::Sp)?; r.set(Reg::Sp, sp.wrapping_add(2) as u32);
    r.leave(h)?; r.store(h, false)
}
fn wrap<H: Host>(h: &mut H) -> Result<(),H::Err> {
    let a = args(h, 5)?; let (delta, hi, lo, off, seg) = (a[0], a[1], a[2], a[3], a[4]);
    let mut r = Regs::new(false); r.enter(h, 0)?; r.flush(h)?;
    let v = h.u16(lin(seg, off))?; let d = delta as i16 as i32 as u32; let total = (v as u32).wrapping_add(d);
    let upper = (total >> 16) as u16 as i16;
    let positive = (delta as i16) > 0;
    let wraps = if positive { upper > 0 || (upper == 0 && hi < total as u16) } else { upper < 0 || (upper == 0 && lo > total as u16) };
    let (new, ax, dx, pc) = if wraps {
        let result = if positive { (v as u32).wrapping_add(d).wrapping_sub(hi as u32).wrapping_add(lo as u32).wrapping_sub(1) }
                     else { (v as u32).wrapping_add(d).wrapping_add(hi as u32).wrapping_sub(lo as u32).wrapping_add(1) };
        let sp = r.get(h, Reg::Sp)?; r.push(h, 0)?; r.push(h, if positive { hi } else { lo } as u32)?; r.set(Reg::Sp, sp as u32);
        (result as u16, result as u16, (result >> 16) as u16, if positive { 0x1cf8 } else { 0x1d66 })
    } else { (v.wrapping_add(delta), delta, 0, if positive { 0x1cbc } else { 0x1d2a }) };
    r.set(Reg::Es, seg as u32); r.set(Reg::Di, off as u32);
    h.write(lin(seg, off), &new.to_le_bytes(), lin(h.seg(0x214b), pc))?;
    r.set(Reg::Ax, ax as u32); r.set(Reg::Dx, dx as u32); r.leave(h)?; r.store(h, false)
}

fn emit_end<H: Host>(h: &mut H, s: Saved) -> Result<Action,H::Err> {
    let a = lin(s.ds, 0x7c16); let off = h.u16(a)?; let seg = h.u16(a+2)?;
    set_ax(h, off)?; h.set_reg(Reg::Dx, seg as u32)?;
    let a = lin(h.ds(), 0x7c26); write(h, a, &off.to_le_bytes(), 0x1f2f)?;
    let a = lin(h.ds(), 0x7c28); write(h, a, &seg.to_le_bytes(), 0x1f32)?; Ok(Action::Done(None))
}
fn emit_loop<H: Host>(h: &mut H, mut s: Saved, after: bool) -> Result<Action,H::Err> {
    let mut check = after;
    loop {
        if check {
            if s.i == f16(h, s.bp, -4)? { return emit_end(h, s); }
            s.i = s.i.wrapping_sub(1); fw16(h, s.bp, -2, s.i, 0x1eef)?;
        }
        if (s.i as i16) > 0 {
            let row = 4u16.wrapping_sub(s.n.wrapping_sub(s.i)); set_ax(h, 33)?; h.set_reg(Reg::Dx, 0)?;
            return Ok(call(s, Phase::EmitDraw, "0791:1829", "0791:1F21", vec![s.i, row, 33], false));
        }
        check = true;
    }
}
fn write_ring<H: Host>(h: &mut H, s: Saved) -> Result<Action,H::Err> {
    let side = f8(h, s.bp, 10)? as i8 as i32; let at = (0x80f2 + 2*side) as u16;
    let old = d16(h, at)?; write(h, lin(h.ds(), at), &old.wrapping_add(1).to_le_bytes(), 0x1d6e)?;
    set_ax(h, 1)?; h.set_reg(Reg::Di, 0x80ee)?;
    Ok(call(s, Phase::WriteRing, "214B:1C86", "0791:1D88", vec![s.ds, 0x80ee, 1, 200, 1], true))
}

pub fn step<H: Host>(h: &mut H, phase: Phase, mut s: Saved) -> Result<Action,H::Err> {
    if s.kind == 0 { return render(h, phase, s); }
    let mut r = Regs::new(phase != Phase::Start);
    match phase {
        Phase::Start => match s.kind {
            1 => Ok(Action::Done(Some(is_new(h)?))),
            2 => { s.bp = enter(h, 12, 0x1d4a)?; s.ds = h.ds(); fw8(h, s.bp, -1, 0, 0x1d50)?;
                if d16(h, 0x80ee)? != 0 { Ok(call(s, Phase::WriteCompare, "0791:1C78", "0791:1D5F", vec![s.bp], false)) } else { write_ring(h, s) } }
            3 => { performance_delta(h)?; Ok(Action::Done(None)) }
            4 => { s.bp = enter(h, 4, 0x1eb5)?; s.ds = h.ds(); Ok(call(s, Phase::EmitRating, "0791:1E53", "0791:1EBF", vec![s.bp], false)) }
            5 => { r.enter(h, 0)?; let flag = args(h, 1)?[0] as u8; let v = if flag != 0 { 0xeafu16 } else { 0xeae };
                write(h, lin(h.ds(), 0x8308), &v.to_le_bytes(), if flag != 0 { 0x26a9 } else { 0x26b1 })?;
                write(h, lin(h.ds(), 0x8328), &[1], 0x26b7)?; end(h, &mut r, false) }
            6 => { let code = args(h, 1)?[0]; r.enter(h, 0)?; r.set_al(h, 1)?; let first = r.get(h, Reg::Ax)?;
                r.set(Reg::Ax, 0); r.set_al(h, code as u8)?; let last = r.get(h, Reg::Ax)?;
                guest(h, &mut r, s, Phase::PlainDone, "0791:1EB5", "0791:2B22", vec![first, 0, 0, last], false) }
            7 => { r.enter(h, 2)?; r.local8(h, -1, 0)?;
                let slot = d8(h, 0x830e)?;
                if slot == 0 { let bp = r.get(h, Reg::Bp)?; r.flush(h)?; let value = raw8(h, bp.wrapping_sub(1))?; r.set_al(h, value)?; return end(h, &mut r, true); }
                r.set_al(h, slot)?; r.set_ah(h, 0)?; r.set(Reg::Dx, 22); mul(h, &mut r)?;
                let ax = r.get(h, Reg::Ax)?; r.set(Reg::Di, ax.wrapping_add(0x80e8) as u32); let di = r.get(h, Reg::Di)?;
                guest(h, &mut r, s, Phase::OffDirection, "0791:2BE5", "0791:5700", vec![h.ds(), di], true) }
            8 => { fill(h)?; Ok(Action::Done(None)) }
            9 => { wrap(h)?; Ok(Action::Done(None)) }
            _ => unreachable!(),
        },
        Phase::OffDirection => { let al = r.al(h)?; r.set_al(h, u8::from(al & 128 != 0))?; let ax = r.get(h, Reg::Ax)?;
            guest(h, &mut r, s, Phase::OffMessage, "0791:26A0", "0791:570E", vec![ax], false) }
        Phase::OffMessage => { if d8(h, 0x8329)? == 0 { r.set_al(h, 0x42)?; let ax = r.get(h, Reg::Ax)?;
                guest(h, &mut r, s, Phase::OffComment, "0791:2B0F", "0791:571B", vec![ax], false) }
            else { off_end(h, &mut r) } }
        Phase::OffComment => off_end(h, &mut r),
        Phase::PlainDone => Ok(Action::Done(None)),
        Phase::WriteCompare => { if h.reg(Reg::Ax)? & 255 != 0 { write_ring(h, s) } else { Ok(Action::Done(Some(set_al(h, 0)?))) } }
        Phase::WriteRing => {
            let ring = d16(h, 0x80ee)?.wrapping_mul(6).wrapping_add(0x7c38); fw16(h, s.bp, -7, ring, 0x1d98)?; fw16(h, s.bp, -5, s.ds, 0x1d9b)?;
            let side = f8(h, s.bp, 10)? as i8 as i32; let index = d16(h, (0x9b34 + 2*side) as u16)?;
            let (seg, off) = far_record(h, 0xa917, index, 0xbf)?; let prod = index as u32*0xbf;
            set_ax(h, prod as u16)?; h.set_reg(Reg::Dx, prod >> 16)?;
            fw16(h, s.bp, -11, off, 0x1db5)?; fw16(h, s.bp, -9, seg, 0x1db8)?;
            let top = lin(s.ds, ring); let code = f8(h, s.bp, 4)?; write(h, top, &[code], 0x1dc1)?;
            let first = f16(h, s.bp, 8)?; let second = f16(h, s.bp, 6)?;
            let v = if first != 0 { word(h, seg, off, first)? } else { 0 }; write(h, top+1, &v.to_le_bytes(), if first != 0 { 0x1ddb } else { 0x1de6 })?;
            let v = if second != 0 { word(h, seg, off, second)? } else { 0 }; write(h, top+3, &v.to_le_bytes(), if second != 0 { 0x1e01 } else { 0x1e0c })?;
            let side = f8(h, s.bp, 10)?; write(h, top+5, &[side], 0x1e16)?;
            let count = d16(h, 0x80ee)?; fw16(h, s.bp, -3, count, 0x1e1d)?; set_ax(h, 1)?;
            h.set_reg(Reg::Di, s.bp.wrapping_sub(3) as u32)?; let ss = h.reg(Reg::Ss)? as u16;
            Ok(call(s, Phase::WriteNext, "214B:1C86", "0791:1E36", vec![ss, s.bp.wrapping_sub(3), 1, 200, 1], true))
        }
        Phase::WriteNext => { let index = f16(h, s.bp, -3)?; let off = index.wrapping_mul(6).wrapping_add(0x7c38);
            write(h, lin(s.ds, off), &[255], 0x1e41)?; fw8(h, s.bp, -1, 1, 0x1e46)?; Ok(Action::Done(Some(set_al(h, 1)?))) }
        Phase::EmitRating => { let side = f8(h, s.bp, 10)?; let first = set_al(h, side)?; let last = (first & 0xff00) | f8(h, s.bp, 4)? as u16;
            set_ax(h, last)?; let p1 = f16(h, s.bp, 8)?; let p2 = f16(h, s.bp, 6)?;
            Ok(call(s, Phase::EmitWritten, "0791:1D4A", "0791:1ED0", vec![first, p1, p2, last], false)) }
        Phase::EmitWritten => { if h.reg(Reg::Ax)? & 255 == 0 { return Ok(Action::Done(None)); }
            s.n = d16(h, 0x80ee)?; let low = s.n.wrapping_sub(2); fw16(h, s.bp, -4, low, 0x1edf)?;
            if (s.n as i16) < (low as i16) { return emit_end(h, s); }
            s.i = s.n; fw16(h, s.bp, -2, s.i, 0x1eea)?; emit_loop(h, s, false) }
        Phase::EmitDraw => emit_loop(h, s, true),
        _ => unreachable!(),
    }
}
fn off_end<H: Host>(h: &mut H, r: &mut Regs) -> Result<Action,H::Err> {
    write(h, lin(h.ds(), 0x8329), &[1], 0x571b)?; let bp = r.get(h, Reg::Bp)?; r.flush(h)?;
    let value = raw8(h, bp.wrapping_sub(1))?; r.set_al(h, value)?; end(h, r, true)
}

fn name_pointer<H: Host>(h: &mut H, r: &mut Regs, record: u16, field: u16) -> Result<(),H::Err> {
    let value = d16(h, record.wrapping_add(field))?; r.set(Reg::Ax, value as u32); r.set(Reg::Dx, 11); mul(h, r)?;
    let off = d16(h, 0x9b6c)?; let ax = r.get(h, Reg::Ax)?; r.set(Reg::Di, off.wrapping_add(ax) as u32);
    let seg = d16(h, 0x9b6e)?; r.set(Reg::Es, seg as u32); Ok(())
}
fn render<H: Host>(h: &mut H, mut phase: Phase, mut s: Saved) -> Result<Action,H::Err> {
    let mut r = Regs::new(phase != Phase::Start);
    loop { match phase {
        Phase::Start => {
            r.enter(h, 0x128)?; let bp = r.get(h, Reg::Bp)?; let index = ss16(h, &mut r, bp.wrapping_add(8))?;
            r.set(Reg::Di, index.wrapping_mul(6).wrapping_add(0x7c38) as u32); s.record = r.get(h, Reg::Di)?;
            let di = r.get(h, Reg::Di)?; r.local16(h, -0x28, di as u32)?; r.local16(h, -0x26, h.ds() as u32)?; r.set(Reg::Es, h.ds() as u32);
            if d8(h, s.record)? == 255 { return end(h, &mut r, false); }
            let code = d8(h, s.record)?; r.set_al(h, code)?; cbw(h, &mut r)?; r.set(Reg::Dx, 21); mul(h, &mut r)?;
            let ax = r.get(h, Reg::Ax)?; r.set(Reg::Di, ax.wrapping_add(0xbe) as u32); let source = (h.ds(), r.get(h, Reg::Di)?);
            let bp = r.get(h, Reg::Bp)?; s.line = bp.wrapping_sub(0x24); s.expression = bp.wrapping_sub(0x128);
            r.set(Reg::Di, s.line as u32); r.set(Reg::Ax, 35); let ss = r.ss(h)?; let max = r.get(h, Reg::Ax)?;
            return guest(h, &mut r, s, Phase::RenderCopied, "23E4:0644", "0791:1873", vec![source.0, source.1, ss, s.line, max], true);
        }
        Phase::RenderCopied => {
            if raw8(h, s.line)? == 0 { phase = Phase::Pad; continue; }
            if raw8(h, s.line.wrapping_add(1))? != 1 { s.marker = 0; phase = Phase::MarkerCheck; continue; }
            r.local8(h, -0x23, 32)?; r.set(Reg::Di, s.expression as u32); let ss = r.ss(h)?; r.push(h, ss as u32)?; let di = r.get(h, Reg::Di)?; r.push(h, di as u32)?;
            name_pointer(h, &mut r, s.record, 1)?; let seg = r.get(h, Reg::Es)?; let off = r.get(h, Reg::Di)?;
            return guest(h, &mut r, s, Phase::PrefixStored, "23E4:062A", "0791:18A5", vec![seg, off], true);
        }
        Phase::PrefixStored => { r.set(Reg::Di, s.line as u32); let ss = r.ss(h)?; let di = r.get(h, Reg::Di)?;
            return guest(h, &mut r, s, Phase::PrefixConcat, "23E4:06B7", "0791:18AF", vec![ss, di], true); }
        Phase::PrefixConcat | Phase::MarkerName => {
            r.set(Reg::Di, s.line as u32); r.set(Reg::Ax, 35); let sp = r.get(h, Reg::Sp)?; r.set(Reg::Sp, sp.wrapping_add(4) as u32);
            let ss = r.ss(h)?; let max = r.get(h, Reg::Ax)?;
            let next = if phase == Phase::PrefixConcat { Phase::PrefixCopied } else { Phase::MarkerCopied };
            let ret = if phase == Phase::PrefixConcat { "0791:18BD" } else if s.marker == 0 { "0791:190E" } else { "0791:195F" };
            return guest(h, &mut r, s, next, "23E4:0644", ret, vec![ss, s.expression, ss, s.line, max], true);
        }
        Phase::PrefixCopied => { s.marker = 0; phase = Phase::MarkerCheck; }
        Phase::MarkerCopied => { s.marker += 1; phase = Phase::MarkerCheck; }
        Phase::MarkerCheck => {
            if s.marker >= 2 { phase = Phase::Pad; continue; }
            let length = raw8(h, s.line)?; r.set_al(h, length)?; r.set_ah(h, 0)?; let ax = r.get(h, Reg::Ax)?; r.set(Reg::Di, ax as u32); let di = r.get(h, Reg::Di)?;
            if raw8(h, s.line.wrapping_add(di))? != s.marker+1 { s.marker += 1; continue; }
            let length = raw8(h, s.line)?; r.local8(h, -0x24, length.wrapping_sub(1))?;
            r.set(Reg::Di, s.expression as u32); let ss = r.ss(h)?; r.push(h, ss as u32)?; let di = r.get(h, Reg::Di)?; r.push(h, di as u32)?;
            r.set(Reg::Di, s.line as u32); let ss = r.ss(h)?; let di = r.get(h, Reg::Di)?;
            return guest(h, &mut r, s, Phase::MarkerStored, "23E4:062A", if s.marker == 0 { "0791:18DD" } else { "0791:192E" }, vec![ss, di], true);
        }
        Phase::MarkerStored => { r.set(Reg::Di, 0x1827); let di = r.get(h, Reg::Di)?;
            return guest(h, &mut r, s, Phase::MarkerConcat, "23E4:06B7", if s.marker == 0 { "0791:18E7" } else { "0791:1938" }, vec![h.seg(0x791), di], true); }
        Phase::MarkerConcat => { name_pointer(h, &mut r, s.record, if s.marker == 0 { 1 } else { 3 })?;
            let seg = r.get(h, Reg::Es)?; let off = r.get(h, Reg::Di)?;
            return guest(h, &mut r, s, Phase::MarkerName, "23E4:06B7", if s.marker == 0 { "0791:1900" } else { "0791:1951" }, vec![seg, off], true); }
        Phase::Pad => {
            let length = raw8(h, s.line)?;
            if length < 30 {
                r.set_al(h, length)?; r.set_ah(h, 0)?; let ax = r.get(h, Reg::Ax)?; r.set(Reg::Ax, ax.wrapping_add(1) as u32);
                let bp = r.get(h, Reg::Bp)?; let ax = r.get(h, Reg::Ax)?; r.set(Reg::Di, bp.wrapping_add(ax).wrapping_sub(0x24) as u32);
                let ss = r.ss(h)?; let off = r.get(h, Reg::Di)?;
                r.set_al(h, length)?; r.set_ah(h, 0)?; let ax = r.get(h, Reg::Ax)?; r.set(Reg::Dx, ax as u32); let dx = r.get(h, Reg::Dx)?;
                r.set(Reg::Ax, 30u16.wrapping_sub(dx) as u32); let count = r.get(h, Reg::Ax)?; r.set(Reg::Ax, 32); let value = r.get(h, Reg::Ax)?;
                return guest(h, &mut r, s, Phase::Filled, "214B:0018", "0791:1988", vec![ss, off, count, value], true);
            }
            phase = Phase::Filled;
        }
        Phase::Filled => { r.local8(h, -0x24, 30)?; s.draw = 0; phase = Phase::Draw; }
        Phase::Drawn => { s.draw += 1; phase = Phase::Draw; }
        Phase::Draw => {
            if s.draw >= 2 { return end(h, &mut r, false); }
            if s.draw == 1 { let bp = r.get(h, Reg::Bp)?; if ss16(h, &mut r, bp.wrapping_add(6))? > 4 { return end(h, &mut r, false); } }
            let side = d8(h, s.record.wrapping_add(5))?; r.set_al(h, side)?; cbw(h, &mut r)?; let ax = r.get(h, Reg::Ax)?; r.set(Reg::Di, ax as u32);
            let di = r.get(h, Reg::Di)?; let v = d8(h, 0x832eu16.wrapping_add(di))?; r.set_al(h, v)?; let colour = r.get(h, Reg::Ax)?;
            r.set(Reg::Di, s.line as u32); let ss = r.ss(h)?; let off = r.get(h, Reg::Di)?;
            let bp = r.get(h, Reg::Bp)?; let v = ss16(h, &mut r, bp.wrapping_add(6))? as u8; r.set_al(h, v)?; let row = r.get(h, Reg::Ax)?;
            let bp = r.get(h, Reg::Bp)?; let v = ss16(h, &mut r, bp.wrapping_add(4))? as u8; r.set_al(h, v)?; let col = r.get(h, Reg::Ax)?;
            r.set(Reg::Di, if s.draw == 0 { 0xa96a } else { 0xa972 }); let di = r.get(h, Reg::Di)?;
            return guest(h, &mut r, s, Phase::Drawn, "214B:02C8", if s.draw == 0 { "0791:19B2" } else { "0791:19DE" }, vec![colour, ss, off, row, col, h.ds(), di], true);
        }
        _ => unreachable!(),
    } }
}
