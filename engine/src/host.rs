//! What a translated routine may ask of the machine it runs in: the same primitives the Python port uses
//! through `_PortMemory` (port/engine.py) and `Regs` (port/runtime.py), and nothing else, so that every
//! register read and set, every write (with its listeners) and every tap happens as the Python routine makes it.
//! [confirmed: goal2-archaeology d3cf46a3, port/engine.py _PortMemory, PortMachine.write_as]

/// The registers a routine names. `name()` is the lower-case name the port passes to `mem.reg` / `mem.set_reg`
/// (and an io_tap is told).
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum Reg {
    Ax = 0,
    Bx = 1,
    Cx = 2,
    Dx = 3,
    Si = 4,
    Di = 5,
    Es = 6,
    Sp = 7,
    Bp = 8,
    Ss = 9,
    Eflags = 10,
}

pub const REGS_NAMES: [&str; 11] = ["ax", "bx", "cx", "dx", "si", "di", "es", "sp", "bp", "ss", "eflags"];

impl Reg {
    pub fn name(self) -> &'static str {
        REGS_NAMES[self as usize]
    }
    /// Regs._NAMES order: the nine 16-bit registers a `Regs` holds.
    pub const SIXTEEN: [Reg; 9] = [Reg::Ax, Reg::Bx, Reg::Cx, Reg::Dx, Reg::Si, Reg::Di, Reg::Es, Reg::Sp, Reg::Bp];
}

/// The machine side of a routine. Errors are the host's own (a Python exception for the PyO3 host).
pub trait Host {
    type Err;
    /// `mem.reg(name)` (tapped by the host when an io_tap listens).
    fn reg(&mut self, r: Reg) -> Result<u32, Self::Err>;
    /// `mem.set_reg(name, value)`.
    fn set_reg(&mut self, r: Reg, value: u32) -> Result<(), Self::Err>;
    /// The port's own read of a byte (never tapped), bounds checked as PortMachine._bounds.
    fn u8(&mut self, linear: u32) -> Result<u8, Self::Err>;
    /// The port's own read of a word.
    fn u16(&mut self, linear: u32) -> Result<u16, Self::Err>;
    /// `Machine.write_as(linear, len(data), value, at)`: every listener whose range holds `linear` sees it first.
    fn write(&mut self, linear: u32, data: &[u8], at: u32) -> Result<(), Self::Err>;
    /// `mem.ss_lin(off)`: SS * 16 + (off & 0xFFFF), SS read through `reg` when an io_tap listens.
    fn ss_lin(&mut self, off: u32) -> Result<u32, Self::Err>;
    /// mem.DS.
    fn ds(&self) -> u16;
    /// mem.seg(paragraph): (load + paragraph) & 0xFFFF.
    fn seg(&self, paragraph: u16) -> u16;
    /// mem._entries[-1]: SP at the entry of the port running, and whether it was a far call.
    fn entry(&self) -> (u32, bool);
    /// The order in which `Regs.store` visits its dirty set: the host reproduces Python's set iteration
    /// (it only matters when an io_tap records the `set_reg` calls). `inserted` is the first-insertion order.
    fn store_order(&mut self, inserted: &[Reg]) -> Result<Vec<Reg>, Self::Err>;
    /// The error raised for a routine's own refusal (PortError).
    fn port_error(&self, what: String) -> Self::Err;
}

/// `args(mem, n)` (port/runtime.py): the first n argument words, one read from SS:(entry SP + 4 or 2).
pub fn args<H: Host>(h: &mut H, n: u32) -> Result<Vec<u16>, H::Err> {
    let (sp, far) = h.entry();
    let base = h.ss_lin(sp + if far { 4 } else { 2 })?;
    let mut out = Vec::with_capacity(n as usize);
    for i in 0..n {
        out.push(h.u16(base + 2 * i)?);
    }
    Ok(out)
}
