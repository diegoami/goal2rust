//! 0791:2FB1, ball.find_nearest_to_ball at oracle e0270981.
//! Live values stay in the guest frame; each guest return starts fresh Regs.
use crate::host::{Host, Reg};
use crate::mem::lin;
use crate::regs::Regs;

#[derive(Clone, Copy, PartialEq, Eq)]
pub enum Phase { Start, Availability, DirectionOne, DirectionTwo }

pub struct Request {
    pub next: Phase,
    pub target: &'static str,
    pub ret_to: &'static str,
    pub args: (u16, u16),
}

fn local8<H: Host>(h: &mut H, r: &mut Regs, off: i16) -> Result<u8, H::Err> {
    r.flush(h)?;
    let bp = r.get(h, Reg::Bp)?;
    let at = h.ss_lin(bp.wrapping_add(off as u16) as u32)?;
    h.u8(at)
}
fn local16<H: Host>(h: &mut H, r: &mut Regs, off: i16) -> Result<u16, H::Err> {
    r.flush(h)?;
    let bp = r.get(h, Reg::Bp)?;
    let at = h.ss_lin(bp.wrapping_add(off as u16) as u32)?;
    h.u16(at)
}
fn load_pitch<H: Host>(h: &mut H, r: &mut Regs) -> Result<(), H::Err> {
    let di = local16(h, r, -13)?;
    r.set(Reg::Di, di as u32);
    let es = local16(h, r, -11)?;
    r.set(Reg::Es, es as u32);
    Ok(())
}
fn ds8<H: Host>(h: &mut H, off: u16) -> Result<u8, H::Err> {
    h.u8(lin(h.ds(), off))
}
fn wds8<H: Host>(h: &mut H, off: u16, value: u8, at: u16) -> Result<(), H::Err> {
    h.write(lin(h.ds(), off), &[value], lin(h.seg(0x0791), at))
}
fn rec8<H: Host>(h: &mut H, r: &mut Regs, off: u16) -> Result<u8, H::Err> {
    let es = r.get(h, Reg::Es)?;
    let di = r.get(h, Reg::Di)?;
    h.u8(lin(es, di.wrapping_add(off)))
}
fn request<H: Host>(h: &mut H, r: &mut Regs, next: Phase, target: &'static str, ret_to: &'static str) -> Result<Request, H::Err> {
    r.store(h, true)?;
    let es = r.get(h, Reg::Es)?;
    let di = r.get(h, Reg::Di)?;
    Ok(Request { next, target, ret_to, args: (es, di) })
}
fn start_side<H: Host>(h: &mut H, r: &mut Regs) -> Result<(), H::Err> {
    for (base, at) in [(0x8311u16, 0x2fc6), (0x830f, 0x2fd1)] {
        let side = local8(h, r, -1)?;
        r.set_al(h, side)?;
        let al = r.al(h)?;
        r.set(Reg::Ax, crate::mem::cbw(al) as u32);
        let ax = r.get(h, Reg::Ax)?;
        r.set(Reg::Di, ax as u32);
        let di = r.get(h, Reg::Di)?;
        wds8(h, base.wrapping_add(di), 0, at)?;
    }
    r.local16(h, -5, 100)?;
    r.local16(h, -7, 100)?;
    r.local16(h, -3, 2)
}
fn advance<H: Host>(h: &mut H, r: &mut Regs) -> Result<bool, H::Err> {
    if local16(h, r, -3)? == 11 {
        if local8(h, r, -1)? == 1 { return Ok(false); }
        let side = local8(h, r, -1)?.wrapping_add(1);
        r.local8(h, -1, side)?;
        start_side(h, r)?;
    } else {
        let slot = local16(h, r, -3)?.wrapping_add(1);
        r.local16(h, -3, slot as u32)?;
    }
    Ok(true)
}

pub fn step<H: Host>(h: &mut H, phase: Phase, mutant: bool) -> Result<Option<Request>, H::Err> {
    let mut r = Regs::new(phase != Phase::Start);
    // Evaluate RHS before borrowing the register bank for assignment.
    macro_rules! get { ($reg:ident) => { r.get(h, Reg::$reg)? }; }
    macro_rules! set { ($reg:ident, $v:expr) => {{ let v = $v; r.set(Reg::$reg, v as u32); }}; }
    macro_rules! al { () => { r.al(h)? }; }
    macro_rules! sal { ($v:expr) => {{ let v = $v; r.set_al(h, v)?; }}; }
    macro_rules! cbw { () => { set!(Ax, crate::mem::cbw(al!())) }; }
    macro_rules! imul { () => {{
        let src = get!(Dx) as i16 as i32;
        let product = (get!(Ax) as i16 as i32) * src;
        set!(Ax, product); set!(Dx, product >> 16);
    }}; }
    match phase {
        Phase::Start => {
            r.enter(h, 14)?;
            // T05 body control: deliberately skip the first side.
            r.local8(h, -1, u8::from(mutant))?;
            start_side(h, &mut r)?;
        }
        Phase::Availability => {
            if al!() == 0 {
                sal!(ds8(h, 0x830b)?);
                load_pitch(h, &mut r)?;
                if al!() != rec8(h, &mut r, 6)? {
                    load_pitch(h, &mut r)?;
                    if rec8(h, &mut r, 0x12)? != 13 {
                        sal!(ds8(h, 0x82f6)?); cbw!(); set!(Dx, get!(Ax));
                        load_pitch(h, &mut r)?;
                        sal!(rec8(h, &mut r, 0)?); cbw!();
                        set!(Ax, get!(Ax).wrapping_sub(get!(Dx)));
                        if (get!(Ax) as i16) < 0 { set!(Ax, get!(Ax).wrapping_neg()); }
                        set!(Cx, get!(Ax));
                        sal!(ds8(h, 0x82f7)?); cbw!(); set!(Dx, get!(Ax));
                        load_pitch(h, &mut r)?;
                        sal!(rec8(h, &mut r, 1)?); cbw!();
                        set!(Ax, get!(Ax).wrapping_sub(get!(Dx)));
                        if (get!(Ax) as i16) < 0 { set!(Ax, get!(Ax).wrapping_neg()); }
                        set!(Ax, get!(Ax).wrapping_add(get!(Cx)));
                        let ax = get!(Ax); r.local16(h, -9, ax as u32)?;
                        if get!(Ax) < local16(h, &mut r, -5)? {
                            load_pitch(h, &mut r)?;
                            set!(Dx, (get!(Dx) & 0xff00) | rec8(h, &mut r, 6)? as u16);
                            sal!(local8(h, &mut r, -1)?); cbw!(); set!(Di, get!(Ax));
                            let di = get!(Di); let dx = get!(Dx);
                            wds8(h, 0x8311u16.wrapping_add(di), dx as u8, 0x307d)?;
                            set!(Ax, local16(h, &mut r, -9)?);
                            let ax = get!(Ax); r.local16(h, -5, ax as u32)?;
                        }
                        load_pitch(h, &mut r)?;
                        return Ok(Some(request(h, &mut r, Phase::DirectionOne, "0791:2BE5", "0791:3090")?));
                    }
                }
            }
            if !advance(h, &mut r)? { r.leave(h)?; r.store(h, false)?; return Ok(None); }
        }
        Phase::DirectionOne => {
            cbw!(); set!(Dx, get!(Ax));
            sal!(ds8(h, 0x82f7)?); cbw!(); imul!();
            let ax = get!(Ax); r.push(h, ax as u32)?;
            load_pitch(h, &mut r)?;
            return Ok(Some(request(h, &mut r, Phase::DirectionTwo, "0791:2BE5", "0791:30A3")?));
        }
        Phase::DirectionTwo => {
            cbw!(); set!(Dx, get!(Ax));
            load_pitch(h, &mut r)?;
            sal!(rec8(h, &mut r, 1)?); cbw!(); imul!();
            let sp = get!(Sp); let at = h.ss_lin(sp as u32)?;
            set!(Dx, h.u16(at)?); set!(Sp, get!(Sp).wrapping_add(2));
            if (get!(Ax) as i16) < (get!(Dx) as i16) {
                set!(Ax, local16(h, &mut r, -9)?);
                if get!(Ax) < local16(h, &mut r, -7)? {
                    load_pitch(h, &mut r)?;
                    set!(Dx, (get!(Dx) & 0xff00) | rec8(h, &mut r, 6)? as u16);
                    sal!(local8(h, &mut r, -1)?); cbw!(); set!(Di, get!(Ax));
                    let di = get!(Di); let dx = get!(Dx);
                    wds8(h, 0x830fu16.wrapping_add(di), dx as u8, 0x30ca)?;
                    set!(Ax, local16(h, &mut r, -9)?);
                    let ax = get!(Ax); r.local16(h, -7, ax as u32)?;
                }
            }
            if !advance(h, &mut r)? { r.leave(h)?; r.store(h, false)?; return Ok(None); }
        }
    }
    // Next iteration: source keeps Regs until the next yielded availability call.
    sal!(local8(h, &mut r, -1)?); cbw!(); set!(Di, get!(Ax));
    let di = get!(Di); sal!(ds8(h, 0x668u16.wrapping_add(di))?);
    r.set_ah(h, 0)?;
    let ax = get!(Ax); set!(Ax, ax.wrapping_add(local16(h, &mut r, -3)?));
    set!(Dx, 22);
    let src = get!(Dx); let product = get!(Ax) as u32 * src as u32;
    set!(Ax, product); set!(Dx, product >> 16);
    set!(Di, get!(Ax).wrapping_add(0x80e8));
    let di = get!(Di); r.local16(h, -13, di as u32)?;
    let ds = h.ds(); r.local16(h, -11, ds as u32)?;
    load_pitch(h, &mut r)?;
    Ok(Some(request(h, &mut r, Phase::Availability, "0791:2956", "0791:3013")?))
}
