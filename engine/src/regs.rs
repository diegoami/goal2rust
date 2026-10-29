//! `Regs` of port/runtime.py, faithfully: registers read from the machine when first used (SP of a fresh frame
//! from the entry), 16-bit masked at every assignment, a dirty set written back by `store`, and the stack words
//! the listing's code writes collected and flushed in runs. [confirmed: goal2-archaeology d3cf46a3,
//! runtime/original_match/port/runtime.py Regs, invoke, _register_property]
use crate::host::{Host, Reg};
use crate::mem::M16;

/// The instruction a stack write names (runtime.py STACK_AT = "214B:0000").
pub const STACK_AT_PARAGRAPH: u16 = 0x214B;

pub const CF: u32 = 0x0001;
pub const PF: u32 = 0x0004;
pub const AF: u32 = 0x0010;
pub const ZF: u32 = 0x0040;
pub const SF: u32 = 0x0080;
pub const OF: u32 = 0x0800;
pub const ARITH: u32 = CF | PF | AF | ZF | SF | OF;

struct Pending {
    addr: u32,
    len: u8,
    data: [u8; 2],
}

pub struct Regs {
    v: [Option<u16>; 9],
    inserted: Vec<Reg>,
    flags_on: u32,
    flags_off: u32,
    ss: Option<u16>,
    pending: Vec<Pending>,
    bps: Vec<u16>,
    fresh: bool,
}

impl Regs {
    /// `Regs(mem, resumed)`.
    pub fn new(resumed: bool) -> Self {
        Regs {
            v: [None; 9],
            inserted: Vec::with_capacity(9),
            flags_on: 0,
            flags_off: 0,
            ss: None,
            pending: Vec::with_capacity(16),
            bps: Vec::with_capacity(4),
            fresh: !resumed,
        }
    }

    #[inline]
    pub fn get<H: Host>(&mut self, h: &mut H, r: Reg) -> Result<u16, H::Err> {
        let i = r as usize;
        if let Some(v) = self.v[i] {
            return Ok(v);
        }
        let v = if r == Reg::Sp && self.fresh {
            h.entry().0 as u16 // _entries[-1][0], unmasked in Python but always a 16-bit SP
        } else {
            (h.reg(r)? & M16) as u16
        };
        self.v[i] = Some(v);
        Ok(v)
    }

    #[inline]
    pub fn set(&mut self, r: Reg, value: u32) {
        self.v[r as usize] = Some((value & M16) as u16);
        if !self.inserted.contains(&r) {
            self.inserted.push(r);
        }
    }

    /// A signed value assigned to a register (`R.ax = -R.ax`, `R.bx = -1`): masked to 16 bits.
    #[inline]
    pub fn set_i(&mut self, r: Reg, value: i64) {
        self.set(r, (value & 0xFFFF) as u32);
    }

    pub fn al<H: Host>(&mut self, h: &mut H) -> Result<u8, H::Err> {
        Ok((self.get(h, Reg::Ax)? & 0xFF) as u8)
    }

    /// `R.al = v`: AX read (first use reads the machine), its low byte replaced.
    pub fn set_al<H: Host>(&mut self, h: &mut H, v: u8) -> Result<(), H::Err> {
        let ax = self.get(h, Reg::Ax)?;
        self.set(Reg::Ax, ((ax & 0xFF00) | v as u16) as u32);
        Ok(())
    }

    pub fn set_ah<H: Host>(&mut self, h: &mut H, v: u8) -> Result<(), H::Err> {
        let ax = self.get(h, Reg::Ax)?;
        self.set(Reg::Ax, ((ax & 0xFF) | ((v as u16) << 8)) as u32);
        Ok(())
    }

    pub fn ss<H: Host>(&mut self, h: &mut H) -> Result<u16, H::Err> {
        if let Some(v) = self.ss {
            return Ok(v);
        }
        let v = h.reg(Reg::Ss)? as u16;
        self.ss = Some(v);
        Ok(v)
    }

    // -- the stack -------------------------------------------------------------------------------------------
    pub fn push<H: Host>(&mut self, h: &mut H, value: u32) -> Result<(), H::Err> {
        let sp = self.get(h, Reg::Sp)?.wrapping_sub(2);
        let ss = self.ss(h)?;
        let v = (value & M16) as u16;
        self.pending.push(Pending { addr: ss as u32 * 16 + sp as u32, len: 2, data: v.to_le_bytes() });
        self.set(Reg::Sp, sp as u32);
        Ok(())
    }

    /// push bp; mov bp, sp; sub sp, size.
    pub fn enter<H: Host>(&mut self, h: &mut H, size: u16) -> Result<(), H::Err> {
        let bp = self.get(h, Reg::Bp)?;
        self.bps.push(bp);
        self.push(h, bp as u32)?;
        let sp = self.get(h, Reg::Sp)?;
        self.set(Reg::Bp, sp as u32);
        let sp = self.get(h, Reg::Sp)?;
        self.set(Reg::Sp, sp.wrapping_sub(size) as u32);
        Ok(())
    }

    /// mov sp, bp; pop bp.
    pub fn leave<H: Host>(&mut self, h: &mut H) -> Result<(), H::Err> {
        let bp = self.get(h, Reg::Bp)?;
        self.set(Reg::Sp, bp as u32);
        if let Some(saved) = self.bps.pop() {
            self.set(Reg::Bp, saved as u32);
        } else {
            self.flush(h)?;
            let sp = self.get(h, Reg::Sp)?;
            let at = h.ss_lin(sp as u32)?;
            let bp = h.u16(at)?;
            self.set(Reg::Bp, bp as u32);
        }
        let sp = self.get(h, Reg::Sp)?;
        self.set(Reg::Sp, sp.wrapping_add(2) as u32);
        Ok(())
    }

    pub fn local8<H: Host>(&mut self, h: &mut H, off: i32, value: u8) -> Result<(), H::Err> {
        let ss = self.ss(h)?;
        let bp = self.get(h, Reg::Bp)?;
        let a = ss as u32 * 16 + ((bp as i32 + off) as u32 & M16);
        self.pending.push(Pending { addr: a, len: 1, data: [value, 0] });
        Ok(())
    }

    pub fn local16<H: Host>(&mut self, h: &mut H, off: i32, value: u32) -> Result<(), H::Err> {
        let ss = self.ss(h)?;
        let bp = self.get(h, Reg::Bp)?;
        let a = ss as u32 * 16 + ((bp as i32 + off) as u32 & M16);
        self.pending.push(Pending { addr: a, len: 2, data: ((value & M16) as u16).to_le_bytes() });
        Ok(())
    }

    /// The stack words collected so far, written in order (later writes win), one write per run of bytes.
    pub fn flush<H: Host>(&mut self, h: &mut H) -> Result<(), H::Err> {
        if self.pending.is_empty() {
            return Ok(());
        }
        let at = h.seg(STACK_AT_PARAGRAPH) as u32 * 16;
        if self.pending.len() == 1 {
            let p = self.pending.pop().unwrap();
            return h.write(p.addr, &p.data[..p.len as usize], at);
        }
        let lo = self.pending.iter().map(|p| p.addr).min().unwrap();
        let hi = self.pending.iter().map(|p| p.addr + p.len as u32).max().unwrap();
        let n = (hi - lo) as usize;
        let mut buf = vec![0u8; n];
        let mut seen = vec![false; n];
        for p in &self.pending {
            let s = (p.addr - lo) as usize;
            for k in 0..p.len as usize {
                buf[s + k] = p.data[k];
                seen[s + k] = true;
            }
        }
        self.pending.clear();
        let mut i = 0;
        while i < n {
            if seen[i] {
                let mut j = i;
                while j < n && seen[j] {
                    j += 1;
                }
                h.write(lo + i as u32, &buf[i..j], at)?;
                i = j;
            } else {
                i += 1;
            }
        }
        Ok(())
    }

    // -- flags ---------------------------------------------------------------------------------------------------
    /// The six arithmetic flags as the listing's last flag-setting instruction leaves them.
    pub fn arith(&mut self, bits: u32) {
        self.flags_on = (self.flags_on & !ARITH) | bits;
        self.flags_off |= ARITH & !bits;
    }

    /// After a call of the original's code: its registers are what the callee left.
    pub fn reload(&mut self) {
        self.v = [None; 9];
        self.inserted.clear();
    }

    /// The stack words and the registers set, written to the machine (SP and BP only with `stack`).
    pub fn store<H: Host>(&mut self, h: &mut H, stack: bool) -> Result<(), H::Err> {
        self.flush(h)?;
        if !self.inserted.is_empty() {
            let order = h.store_order(&self.inserted)?;
            for r in order {
                if stack || (r != Reg::Sp && r != Reg::Bp) {
                    let v = self.v[r as usize].unwrap();
                    h.set_reg(r, v as u32)?;
                }
            }
            self.inserted.clear();
        }
        if self.flags_on != 0 || self.flags_off != 0 {
            let f = h.reg(Reg::Eflags)?;
            h.set_reg(Reg::Eflags, (f & !self.flags_off) | self.flags_on)?;
            self.flags_on = 0;
            self.flags_off = 0;
        }
        Ok(())
    }
}

/// `invoke(mem, R, cs_paragraph, ret_ip, core, ..., pushes=...)`: the pushed words, the segment (far) and the
/// return address are written, the callee writes its frame, and SP comes back to where it was (Pascal).
pub fn invoke<H: Host, F>(h: &mut H, r: &mut Regs, cs_paragraph: Option<u16>, ret_ip: u16, pushes: &[u32], core: F)
    -> Result<(), H::Err>
where
    F: FnOnce(&mut H, &mut Regs) -> Result<(), H::Err>,
{
    let sp0 = r.get(h, Reg::Sp)?;
    for &w in pushes {
        r.push(h, w)?;
    }
    if let Some(p) = cs_paragraph {
        let s = h.seg(p);
        r.push(h, s as u32)?;
    }
    r.push(h, ret_ip as u32)?;
    core(h, r)?;
    r.set(Reg::Sp, sp0 as u32);
    Ok(())
}

/// CF PF AF ZF SF OF of `cmp a, b` on bits-wide operands (runtime.py sub_flags).
pub fn sub_flags(a: u32, b: u32, bits: u32) -> u32 {
    let mask: u32 = ((1u64 << bits) - 1) as u32;
    let a = a & mask;
    let b = b & mask;
    let r = a.wrapping_sub(b) & mask;
    let sign = 1u32 << (bits - 1);
    let mut f = 0;
    if a < b {
        f |= CF;
    }
    if (r & 0xFF).count_ones() % 2 == 0 {
        f |= PF;
    }
    if (a ^ b ^ r) & 0x10 != 0 {
        f |= AF;
    }
    if r == 0 {
        f |= ZF;
    }
    if r & sign != 0 {
        f |= SF;
    }
    if (a ^ b) & (a ^ r) & sign != 0 {
        f |= OF;
    }
    f
}
