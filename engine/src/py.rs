//! The PyO3 side: the port's guest memory as a zero-copy view of PortMachine._memory (`GuestMemory`), and the
//! `Host` a translated routine runs on, built from the `_PortMemory` the Python dispatcher hands a port
//! (`fn(mem, variant)`, port/guest.py PortFrame.start). Untapped (no io_tap), registers and memory are read and
//! written in place, as port/engine.py's T117 fast paths do; with an io_tap, every register read and set goes
//! through the machine's own `reg`/`set_reg`, so the tap sees what it sees for the Python routine. A write whose
//! address lies in the kit's listener span goes through `PortMachine.write_as`, so every listener (and listen_tap)
//! is called as for the Python routine; any other write lands directly, as write_as's own fast path does.
//! [confirmed: goal2-archaeology d3cf46a3, port/engine.py _PortMemory, _set_plain, PortMachine.write_as/_bounds]
use pyo3::exceptions::PyRuntimeError;
use pyo3::intern;
use pyo3::prelude::*;
use pyo3::types::{PyByteArray, PyBytes, PyDict, PyList, PySet, PyTuple};

use crate::host::{Host, Reg};
use crate::mem::{self, MEM_SIZE};

pub(crate) fn port_error(py: Python<'_>, what: String) -> PyErr {
    match py.import("original_match.port.mem").and_then(|m| m.getattr("PortError")) {
        Ok(cls) => match cls.call1((what.clone(),)) {
            Ok(e) => PyErr::from_value(e),
            Err(e) => e,
        },
        Err(_) => PyRuntimeError::new_err(what),
    }
}

fn bounds_error(py: Python<'_>, linear: u32, n: u32) -> PyErr {
    port_error(py, format!("plain-memory read/write outside mapped range: {}+{}", linear, n))
}

/// The machine's register dict key and width of a name (port/engine.py _alias_of).
fn base_of(r: Reg) -> (&'static str, u64) {
    match r {
        Reg::Ax => ("eax", 0xFFFF),
        Reg::Bx => ("ebx", 0xFFFF),
        Reg::Cx => ("ecx", 0xFFFF),
        Reg::Dx => ("edx", 0xFFFF),
        Reg::Si => ("esi", 0xFFFF),
        Reg::Di => ("edi", 0xFFFF),
        Reg::Sp => ("esp", 0xFFFF),
        Reg::Bp => ("ebp", 0xFFFF),
        Reg::Es => ("es", 0xFFFF),
        Reg::Ss => ("ss", 0xFFFF),
        Reg::Eflags => ("eflags", 0xFFFF_FFFF),
    }
}

pub struct PyHost<'py> {
    py: Python<'py>,
    m: Bound<'py, PyAny>,
    memory: Bound<'py, PyByteArray>,
    regs: Bound<'py, PyDict>,
    tapped: bool,
    ds: u16,
    load: u16,
    entry: (u32, bool),
}

impl<'py> PyHost<'py> {
    pub fn new(mem: &Bound<'py, PyAny>) -> PyResult<Self> {
        let py = mem.py();
        let m = mem.getattr(intern!(py, "m"))?;
        let memory = m.getattr(intern!(py, "_memory"))?.cast_into::<PyByteArray>()?;
        if memory.len() < MEM_SIZE as usize {
            return Err(port_error(py, format!("the port's memory holds {} bytes", memory.len())));
        }
        let regs = m.getattr(intern!(py, "_registers"))?.cast_into::<PyDict>()?;
        let tapped = !m.getattr(intern!(py, "io_tap"))?.is_none();
        let ds: u16 = mem.getattr(intern!(py, "DS"))?.extract()?;
        let load: u16 = m.getattr(intern!(py, "load"))?.extract()?;
        let entries = mem.getattr(intern!(py, "_entries"))?.cast_into::<PyList>()?;
        let n = entries.len();
        if n == 0 {
            return Err(port_error(py, "a Rust port outside a port frame".into()));
        }
        let last = entries.get_item(n - 1)?.cast_into::<PyTuple>()?;
        let sp: u32 = last.get_item(0)?.extract()?;
        let far: bool = last.get_item(1)?.is_truthy()?;
        Ok(PyHost { py, m, memory, regs, tapped, ds, load, entry: (sp, far) })
    }

    /// After Python code ran (a listener, a tap): whether an io_tap listens now.
    fn refresh(&mut self) -> PyResult<()> {
        self.tapped = !self.m.getattr(intern!(self.py, "io_tap"))?.is_none();
        Ok(())
    }

    fn plain_reg(&self, r: Reg) -> PyResult<u32> {
        let (base, mask) = base_of(r);
        let v: u64 = match self.regs.get_item(base)? {
            Some(v) => v.extract()?,
            None => return Err(pyo3::exceptions::PyKeyError::new_err(base)),
        };
        Ok((v & mask) as u32)
    }
}

impl<'py> Host for PyHost<'py> {
    type Err = PyErr;

    fn reg(&mut self, r: Reg) -> PyResult<u32> {
        if !self.tapped {
            return self.plain_reg(r);
        }
        let v: u64 = self.m.call_method1(intern!(self.py, "reg"), (r.name(),))?.extract()?;
        self.refresh()?;
        Ok(v as u32)
    }

    fn set_reg(&mut self, r: Reg, value: u32) -> PyResult<()> {
        if self.tapped {
            self.m.call_method1(intern!(self.py, "set_reg"), (r.name(), value))?;
            return self.refresh();
        }
        // _set_plain: none of these names clears its base first (only ip and flags do).
        let (base, mask) = base_of(r);
        let old: u64 = match self.regs.get_item(base)? {
            Some(v) => v.extract()?,
            None => 0,
        };
        let mut new = ((old & !mask) | (value as u64 & mask)) & 0xFFFF_FFFF;
        if r == Reg::Eflags {
            new |= 2;
        }
        self.regs.set_item(base, new)
    }

    #[inline]
    fn u8(&mut self, linear: u32) -> PyResult<u8> {
        // SAFETY: no Python code runs while the slice lives.
        let s = unsafe { self.memory.as_bytes() };
        mem::u8_at(s, linear).ok_or_else(|| bounds_error(self.py, linear, 1))
    }

    #[inline]
    fn u16(&mut self, linear: u32) -> PyResult<u16> {
        let s = unsafe { self.memory.as_bytes() };
        mem::u16_at(s, linear).ok_or_else(|| bounds_error(self.py, linear, 2))
    }

    fn write(&mut self, linear: u32, data: &[u8], at: u32) -> PyResult<()> {
        let size = data.len() as u32;
        if !mem::in_bounds(linear, size) {
            return Err(bounds_error(self.py, linear, size));
        }
        let span = self.m.getattr(intern!(self.py, "_writes_span"))?.cast_into::<PyTuple>()?;
        let lo: i64 = span.get_item(0)?.extract()?;
        let hi: i64 = span.get_item(1)?.extract()?;
        let l = linear as i64;
        if !(lo <= l && l <= hi) {
            // write_as's own path when no listener's range holds the address
            let s = unsafe { self.memory.as_bytes_mut() };
            mem::put(s, linear, data);
            return Ok(());
        }
        let py = self.py;
        let value = py
            .get_type::<pyo3::types::PyInt>()
            .call_method1(intern!(py, "from_bytes"), (PyBytes::new(py, data), intern!(py, "little")))?;
        self.m.call_method1(intern!(py, "write_as"), (linear, size, value, at))?;
        self.refresh()
    }

    fn ss_lin(&mut self, off: u32) -> PyResult<u32> {
        let ss = if self.tapped { self.reg(Reg::Ss)? } else { self.plain_reg(Reg::Ss)? };
        Ok((ss & 0xFFFF) * 16 + (off & 0xFFFF))
    }

    fn ds(&self) -> u16 {
        self.ds
    }

    fn seg(&self, paragraph: u16) -> u16 {
        self.load.wrapping_add(paragraph)
    }

    fn entry(&self) -> (u32, bool) {
        self.entry
    }

    fn store_order(&mut self, inserted: &[Reg]) -> PyResult<Vec<Reg>> {
        if !self.tapped {
            return Ok(inserted.to_vec()); // untapped, set_reg of distinct registers commute
        }
        // Regs._dirty is a set of names filled in this order: its iteration order is Python's, reproduced by
        // building the same set (same hashes under the same PYTHONHASHSEED, same insertion sequence).
        let set = PySet::empty(self.py)?;
        for r in inserted {
            set.add(r.name())?;
        }
        let mut out = Vec::with_capacity(inserted.len());
        for item in set.iter() {
            let name: String = item.extract()?;
            out.push(*inserted.iter().find(|r| r.name() == name).unwrap());
        }
        Ok(out)
    }

    fn port_error(&self, what: String) -> PyErr {
        port_error(self.py, what)
    }
}

/// PortMachine._memory as a zero-copy view: typed reads and writes with explicit width, sign and wrap. Writes
/// here reach no listener (they are for tests and tools; a routine writes through its Host).
#[pyclass(module = "goal2rust_engine", unsendable)]
pub struct GuestMemory {
    buf: Py<PyByteArray>,
}

#[pymethods]
impl GuestMemory {
    #[new]
    fn new(buf: Bound<'_, PyByteArray>) -> Self {
        GuestMemory { buf: buf.unbind() }
    }

    fn __len__(&self, py: Python<'_>) -> usize {
        self.buf.bind(py).len()
    }

    fn u8(&self, py: Python<'_>, linear: u32) -> PyResult<u8> {
        let b = self.buf.bind(py);
        mem::u8_at(unsafe { b.as_bytes() }, linear).ok_or_else(|| bounds_error(py, linear, 1))
    }

    fn u16(&self, py: Python<'_>, linear: u32) -> PyResult<u16> {
        let b = self.buf.bind(py);
        mem::u16_at(unsafe { b.as_bytes() }, linear).ok_or_else(|| bounds_error(py, linear, 2))
    }

    fn i16(&self, py: Python<'_>, linear: u32) -> PyResult<i16> {
        let b = self.buf.bind(py);
        mem::i16_at(unsafe { b.as_bytes() }, linear).ok_or_else(|| bounds_error(py, linear, 2))
    }

    /// The word at seg:(off + k), the offset wrapping at 16 bits as the listing's `[di + k]`.
    fn rec16(&self, py: Python<'_>, seg: u16, off: u16, k: u16) -> PyResult<u16> {
        self.u16(py, mem::lin(seg, mem::off_add(off, k)))
    }

    /// Writes the low 8 bits of `value` (any int: explicit wrap).
    fn w8(&self, py: Python<'_>, linear: u32, value: i64) -> PyResult<()> {
        let b = self.buf.bind(py);
        if mem::put(unsafe { b.as_bytes_mut() }, linear, &[(value & 0xFF) as u8]) {
            Ok(())
        } else {
            Err(bounds_error(py, linear, 1))
        }
    }

    /// Writes the low 16 bits of `value`, little-endian.
    fn w16(&self, py: Python<'_>, linear: u32, value: i64) -> PyResult<()> {
        let b = self.buf.bind(py);
        if mem::put_u16(unsafe { b.as_bytes_mut() }, linear, (value & 0xFFFF) as u16) {
            Ok(())
        } else {
            Err(bounds_error(py, linear, 2))
        }
    }

    /// The address of the first byte (to show the view is the bytearray's own storage, not a copy).
    fn address(&self, py: Python<'_>) -> usize {
        self.buf.bind(py).data() as usize
    }
}

/// The crossing alone: the host built from `mem` as a routine builds it, nothing read or written (T01's
/// measure of the per-call Python/Rust cost).
#[pyfunction]
fn crossing(mem: &Bound<'_, PyAny>, _variant: &Bound<'_, PyAny>) -> PyResult<()> {
    let _h = PyHost::new(mem)?;
    Ok(())
}

/// No argument use at all: the bare call cost.
#[pyfunction]
fn noop(_mem: &Bound<'_, PyAny>, _variant: &Bound<'_, PyAny>) {}

macro_rules! routine {
    ($pyname:ident, $f:path) => {
        #[pyfunction]
        fn $pyname(mem: &Bound<'_, PyAny>, _variant: &Bound<'_, PyAny>) -> PyResult<()> {
            let mut h = PyHost::new(mem)?;
            $f(&mut h)
        }
    };
}

include!("routines.inc.rs");

#[pymodule]
fn goal2rust_engine(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<crate::machine::MachineCore>()?;
    m.add_class::<GuestMemory>()?;
    m.add_function(wrap_pyfunction!(crossing, m)?)?;
    m.add_function(wrap_pyfunction!(noop, m)?)?;
    register_routines(m)?;
    Ok(())
}
