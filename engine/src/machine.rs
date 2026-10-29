//! PortMachine, PortFrame and guest calls, translated from archaeology d3cf46a3.
//! Python bodies and callbacks borrow the SAME memory/register state. No state
//! is copied into/out of the bridge, and no Python PortFrame or dispatcher runs.
use std::cell::RefCell;
use std::collections::HashMap;
use std::rc::Rc;
use std::time::Instant;

use pyo3::class::gc::{PyTraverseError, PyVisit};
use pyo3::exceptions::{PyKeyError, PyStopIteration, PyValueError};
use pyo3::prelude::*;
use pyo3::types::{PyByteArray, PyBytes, PyDict, PyList, PySet, PyTuple};

use crate::host::{Host, Reg};
use crate::mem::{self, MEM_SIZE};
use crate::py::port_error;

const NAMES: [&str; 16] = ["eax", "ebx", "ecx", "edx", "esi", "edi", "ebp", "esp", "eflags", "eip", "cs", "ds", "es", "ss", "fs", "gs"];
type Bank = Rc<RefCell<[u32; 16]>>;

fn alias(py: Python<'_>, name: &str) -> PyResult<(usize, u32, u32, bool)> {
    let n = name.to_lowercase();
    if let Some(i) = NAMES.iter().position(|s| *s == n) {
        return Ok((i, 0, if i < 10 { u32::MAX } else { 0xffff }, false));
    }
    let base = match n.as_str() {
        "ax" => 0, "bx" => 1, "cx" => 2, "dx" => 3, "si" => 4, "di" => 5,
        "bp" => 6, "sp" => 7, "flags" => 8, "ip" => 9,
        "al" | "ah" => 0, "bl" | "bh" => 1, "cl" | "ch" => 2, "dl" | "dh" => 3,
        _ => return Err(port_error(py, format!("unsupported plain register {n:?}").replace('"', "'"))),
    };
    let byte = matches!(n.as_str(), "al" | "ah" | "bl" | "bh" | "cl" | "ch" | "dl" | "dh");
    Ok((base, if byte && n.ends_with('h') { 8 } else { 0 }, if byte { 255 } else { 0xffff }, n == "ip" || n == "flags"))
}

#[pyclass(unsendable, module = "goal2rust_engine")]
pub struct RegisterFile { regs: Bank }

#[pymethods]
impl RegisterFile {
    fn __getitem__(&self, name: &str) -> PyResult<u32> {
        let i = NAMES.iter().position(|s| *s == name).ok_or_else(|| PyKeyError::new_err(name.to_string()))?;
        Ok(self.regs.borrow()[i])
    }
    fn __setitem__(&self, name: &str, value: u32) -> PyResult<()> {
        let i = NAMES.iter().position(|s| *s == name).ok_or_else(|| PyKeyError::new_err(name.to_string()))?;
        self.regs.borrow_mut()[i] = value;
        Ok(())
    }
    fn keys(&self) -> Vec<&'static str> { NAMES.to_vec() }
    fn clear(&self) { self.regs.borrow_mut().fill(0); }
    fn update(&self, values: &Bound<'_, PyDict>) -> PyResult<()> {
        for (k, v) in values.iter() { self.__setitem__(&k.extract::<String>()?, v.extract()?)?; }
        Ok(())
    }
}

struct Port {
    entry: Py<PyAny>, variant: Py<PyAny>, mem: Py<PyAny>, calls: Py<PyDict>,
}
impl Port {
    fn clone_ref(&self, py: Python<'_>) -> Self {
        Self { entry: self.entry.clone_ref(py), variant: self.variant.clone_ref(py), mem: self.mem.clone_ref(py), calls: self.calls.clone_ref(py) }
    }
    fn traverse(&self, visit: &PyVisit<'_>) -> Result<(), PyTraverseError> {
        visit.call(&self.entry)?; visit.call(&self.variant)?; visit.call(&self.mem)?; visit.call(&self.calls)
    }
}
struct Frame {
    port: Port, done: Py<PyAny>, ss: u32, sp: u32, bp: u32,
    gen: Option<Py<PyAny>>, waiting: Option<Py<PyAny>>,
    ret_lin: Option<u32>, expect_sp: Option<u32>, after_sp: Option<u32>,
}
impl Frame {
    fn describe<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let d = PyDict::new(py);
        d.set_item("entry", self.port.entry.bind(py))?;
        d.set_item("variant", self.port.variant.bind(py))?;
        d.set_item("ss", self.ss)?; d.set_item("sp", self.sp)?; d.set_item("bp", self.bp)?;
        d.set_item("ret_lin", self.ret_lin)?; d.set_item("expect_sp", self.expect_sp)?; d.set_item("after_sp", self.after_sp)?;
        d.set_item("waiting", self.waiting.as_ref().map(|v| v.bind(py)))?;
        py.import("goal2rust.machine")?.getattr("_FrameView")?.call((), Some(&d))
    }
}

#[pyclass(unsendable, module = "goal2rust_engine")]
pub struct MachineCore {
    memory: Py<PyByteArray>, regs: Bank, load: u16,
    ports: RefCell<HashMap<u32, Port>>, frames: RefCell<Vec<Frame>>,
    native: bool, mutant: u32,
    native_calls: RefCell<HashMap<String, u64>>,
    // Bridge type tests/StopIteration and NOOP identity resolved once, never per call.
    generator_type: Py<PyAny>, call_type: Py<PyAny>, noop: Py<PyAny>,
}

#[pymethods]
impl MachineCore {
    #[new]
    fn new(memory: &Bound<'_, PyAny>, load: u16, native: bool, mutant: u32) -> PyResult<Self> {
        let py = memory.py();
        let b = py.get_type::<PyBytes>().call1((memory,))?.cast_into::<PyBytes>()?;
        if b.as_bytes().len() < MEM_SIZE as usize { return Err(PyValueError::new_err(format!("the image holds {} bytes; {MEM_SIZE} are needed", b.as_bytes().len()))); }
        let mut regs = [0; 16]; regs[8] = 2;
        Ok(Self { memory: PyByteArray::new(py, &b.as_bytes()[..MEM_SIZE as usize]).unbind(),
            regs: Rc::new(RefCell::new(regs)), load, ports: RefCell::new(HashMap::new()), frames: RefCell::new(Vec::new()), native, mutant,
            native_calls: RefCell::new(HashMap::new()),
            generator_type: py.import("types")?.getattr("GeneratorType")?.unbind(),
            call_type: py.import("original_match.port.guest")?.getattr("Call")?.unbind(),
            noop: py.import("original_match.machine")?.getattr("NOOP")?.unbind() })
    }
    #[getter]
    fn memory(&self, py: Python<'_>) -> Py<PyByteArray> { self.memory.clone_ref(py) }
    #[getter]
    fn registers(&self) -> RegisterFile { RegisterFile { regs: self.regs.clone() } }
    #[getter]
    fn native_calls(&self) -> HashMap<String, u64> { self.native_calls.borrow().clone() }
    #[getter]
    fn frames<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyList>> {
        let out = PyList::empty(py);
        for f in self.frames.borrow().iter() { out.append(f.describe(py)?)?; }
        Ok(out)
    }
    fn bounds(&self, linear: &Bound<'_, PyAny>, n: &Bound<'_, PyAny>) -> PyResult<()> {
        let l = linear.extract::<u32>(); let count = n.extract::<u32>();
        if let (Ok(l), Ok(count)) = (l, count) { if mem::in_bounds(l, count) { return Ok(()); } }
        Err(port_error(linear.py(), format!("plain-memory read/write outside mapped range: {}+{}", linear.str()?, n.str()?)))
    }
    fn reg(&self, m: &Bound<'_, PyAny>, name: &str) -> PyResult<u32> {
        let (i, shift, mask, _) = alias(m.py(), name)?;
        let value = self.regs.borrow()[i] >> shift & mask;
        let tap = m.getattr("io_tap")?;
        if !tap.is_none() { tap.call1(("g", name.to_lowercase(), value))?; }
        Ok(value)
    }
    fn set_reg(&self, m: &Bound<'_, PyAny>, name: &str, value: &Bound<'_, PyAny>) -> PyResult<()> {
        let (i, shift, mask, clears) = alias(m.py(), name)?;
        let low: u32 = value.call_method1("__and__", (u32::MAX,))?.extract()?;
        { let mut regs = self.regs.borrow_mut();
          if clears { regs[i] = 0; }
          regs[i] = (regs[i] & !(mask << shift)) | ((low & mask) << shift);
          if i == 8 { regs[i] |= 2; }
        }
        let tap = m.getattr("io_tap")?;
        if !tap.is_none() { tap.call1(("s", name.to_lowercase(), value))?; }
        Ok(())
    }
    fn read<'py>(&self, m: &Bound<'py, PyAny>, linear: &Bound<'py, PyAny>, n: &Bound<'py, PyAny>) -> PyResult<Bound<'py, PyBytes>> {
        self.bounds(linear, n)?;
        let data = self.bytes(m.py(), linear.extract()?, n.extract()?)?;
        let tap = m.getattr("io_tap")?;
        if !tap.is_none() { tap.call1(("r", linear, &data))?; }
        Ok(data)
    }
    fn write(&self, m: &Bound<'_, PyAny>, linear: &Bound<'_, PyAny>, data: &Bound<'_, PyAny>) -> PyResult<()> {
        let py = m.py();
        let data = py.get_type::<PyBytes>().call1((data,))?.cast_into::<PyBytes>()?;
        self.bounds(linear, &data.as_bytes().len().into_pyobject(py)?.into_any())?;
        let tap = m.getattr("write_tap")?;
        if !tap.is_none() { tap.call1((linear, &data))?; }
        self.put(py, linear.extract()?, data.as_bytes())
    }
    fn write_as(&self, m: &Bound<'_, PyAny>, linear: &Bound<'_, PyAny>, size: &Bound<'_, PyAny>, value: &Bound<'_, PyAny>, at: &Bound<'_, PyAny>) -> PyResult<()> {
        self.bounds(linear, size)?;
        let py = m.py();
        let n: usize = size.extract()?;
        let int = py.get_type::<pyo3::types::PyInt>();
        let mask = int.call1((1,))?.call_method1("__lshift__", (n * 8,))?.call_method1("__sub__", (1,))?;
        let v = value.call_method1("__and__", (mask,))?;
        self.listeners(m, linear.extract()?, n, &v, at)?;
        let data = v.call_method1("to_bytes", (n, "little"))?.cast_into::<PyBytes>()?;
        self.put(py, linear.extract()?, data.as_bytes())
    }
    fn pc(&self, m: &Bound<'_, PyAny>) -> PyResult<u32> {
        // Machine.pc invokes its io tap even when the override supplies the PC.
        let override_pc = m.getattr("_pc_override")?;
        let pc = if !override_pc.is_none() { override_pc.extract()? }
        else if !m.getattr("io_tap")?.is_none() { self.reg(m, "cs")? * 16 + self.reg(m, "ip")? }
        else { let r = self.regs.borrow(); (r[10] & 0xffff) * 16 + (r[9] & 0xffff) };
        let tap = m.getattr("io_tap")?;
        if !tap.is_none() { tap.call1(("p", m.py().None(), pc))?; }
        Ok(pc)
    }
    #[pyo3(signature = (m, far, pop=0))]
    fn return_from(&self, m: &Bound<'_, PyAny>, far: bool, pop: u32) -> PyResult<()> {
        let sp = self.reg(m, "sp")?;
        let ip = self.stack_word(m, 0)?;
        if far {
            let cs = self.stack_word(m, 2)?;
            self.set(m, "sp", sp.wrapping_add(4).wrapping_add(pop) & 0xffff)?;
            self.set(m, "cs", cs)?;
        } else { self.set(m, "sp", sp.wrapping_add(2).wrapping_add(pop) & 0xffff)?; }
        self.set(m, "eip", ip)
    }
    fn port(&self, m: &Bound<'_, PyAny>, address: &str, entry: Bound<'_, PyAny>, variant: Bound<'_, PyAny>, mem: Bound<'_, PyAny>, calls: Bound<'_, PyDict>) -> PyResult<()> {
        let lin = self.lin(address)?;
        if self.ports.borrow().contains_key(&lin) { return Err(PyValueError::new_err(format!("two ports of {address}"))); }
        self.ports.borrow_mut().insert(lin, Port { entry: entry.unbind(), variant: variant.unbind(), mem: mem.unbind(), calls: calls.unbind() });
        self.placeholder(m, lin)
    }
    #[pyo3(signature = (m, entry, variant, mem, calls, done=None))]
    fn start(&self, m: &Bound<'_, PyAny>, entry: Bound<'_, PyAny>, variant: Bound<'_, PyAny>, mem: Bound<'_, PyAny>, calls: Bound<'_, PyDict>, done: Option<Py<PyAny>>) -> PyResult<()> {
        let p = Port { entry: entry.unbind(), variant: variant.unbind(), mem: mem.unbind(), calls: calls.unbind() };
        self.start_port(m, p, done.unwrap_or_else(|| m.py().None()))
    }
    fn dispatch(&self, m: &Bound<'_, PyAny>, linear: u32) -> PyResult<()> {
        let py = m.py();
        let replay = m.getattr("_resume_lin")?.extract::<Option<u32>>()? == Some(linear);
        m.setattr("_resume_lin", py.None())?;
        if self.handlers(m, linear, replay, false)? { return Ok(()); }
        let port = self.ports.borrow().get(&linear).map(|p| p.clone_ref(py));
        if let Some(port) = port { self.start_port(m, port, py.None())?; }
        else {
            let candidate = self.frames.borrow().last().map(|f| (f.ret_lin, f.ss, f.expect_sp));
            let returned = if let Some((Some(ret), ss, sp)) = candidate {
                ret == linear && self.reg(m, "ss")? == ss && Some(self.reg(m, "sp")?) == sp
            } else { false };
            if returned {
                let mut f = self.frames.borrow_mut().pop().unwrap();
                let ax = self.reg(m, "ax")?;
                self.set(m, "sp", f.after_sp.unwrap())?;
                f.waiting = None; f.ret_lin = None;
                self.step(m, f, &ax.into_pyobject(py)?.into_any())?;
            } else if self.pc(m)? == linear {
                let cs = self.reg(m, "cs")?; let ip = self.reg(m, "ip")?;
                return Err(port_error(py, format!("no registered port/return at {:04X}:{ip:04X}", (cs as u16).wrapping_sub(self.load))));
            }
        }
        if !m.getattr("stop_reason")?.is_none() { m.setattr("no_replay_at", self.pc(m)?)?; }
        Ok(())
    }
    #[pyo3(signature = (m, until, timeout_s=600.0, fresh=false))]
    fn run(&self, m: &Bound<'_, PyAny>, until: u32, timeout_s: f64, fresh: bool) -> PyResult<Py<PyAny>> {
        let py = m.py();
        if m.getattr("muted")?.is_truthy()? { return Err(port_error(py, "plain engine cannot execute a muted original proof".into())); }
        m.setattr("stop_reason", py.None())?;
        let start = self.pc(m)?;
        let no_replay: Option<u32> = m.getattr("no_replay_at")?.extract()?;
        m.setattr("_resume_lin", if fresh || no_replay == Some(start) { None } else { Some(start) })?;
        m.setattr("no_replay_at", py.None())?;
        let begin = Instant::now();
        m.setattr("running", true)?;
        let result = (|| {
            loop {
                let pc = self.pc(m)?;
                if pc == until { break; }
                if begin.elapsed().as_secs_f64() > timeout_s { return Err(port_error(py, "plain dispatch time limit exceeded".into())); }
                let linear = if m.getattr("io_tap")?.is_none() { pc } else { self.pc(m)? };
                self.dispatch(m, linear)?;
                self.raise_pending(m)?;
                if !m.getattr("stop_reason")?.is_none() { break; }
            }
            Ok(m.getattr("stop_reason")?.unbind())
        })();
        m.setattr("running", false)?;
        result
    }
    fn fire(&self, m: &Bound<'_, PyAny>, address: &str) -> PyResult<()> {
        let py = m.py();
        let lin = self.lin(address)?;
        let saved = m.getattr("_pc_override")?;
        m.setattr("_pc_override", lin)?;
        let handlers = m.getattr("_handlers")?.cast_into::<PyDict>()?;
        let hs: Vec<Py<PyAny>> = match handlers.get_item(lin)? {
            Some(v) => v.try_iter()?.map(|h| h.map(Bound::unbind)).collect::<PyResult<_>>()?,
            None => vec![],
        };
        let tap = if hs.iter().any(|h| !h.bind(py).is(self.noop.bind(py))) { m.getattr("site_tap")? } else { py.None().into_bound(py) };
        let kw = PyDict::new(py); kw.set_item("fired", true)?;
        if !tap.is_none() { tap.call_method("site_enter", (lin, false), Some(&kw))?; }
        let result: PyResult<()> = (|| {
            for h in hs { h.bind(py).call1((false,))?; self.raise_pending(m)?; }
            Ok(())
        })();
        m.setattr("_pc_override", saved)?;
        if !tap.is_none() { tap.call_method("site_leave", (lin, false), Some(&kw))?; }
        result
    }
    /// Run a native routine body for per-call differentials, inside mem._entries.
    fn routine(&self, m: &Bound<'_, PyAny>, mem: &Bound<'_, PyAny>, address: &str) -> PyResult<()> {
        let entries = mem.getattr("_entries")?.cast_into::<PyList>()?;
        let entry: (u32, bool) = entries.get_item(entries.len() - 1)?.extract()?;
        self.native_body(m, entry, address)?.ok_or_else(|| port_error(m.py(), format!("no native routine {address}")))
    }
    fn __traverse__(&self, visit: PyVisit<'_>) -> Result<(), PyTraverseError> {
        visit.call(&self.memory)?; visit.call(&self.generator_type)?; visit.call(&self.call_type)?; visit.call(&self.noop)?;
        if let Ok(ports) = self.ports.try_borrow() { for p in ports.values() { p.traverse(&visit)?; } }
        if let Ok(frames) = self.frames.try_borrow() { for f in frames.iter() {
            f.port.traverse(&visit)?; visit.call(&f.done)?; visit.call(&f.gen)?; visit.call(&f.waiting)?;
        } }
        Ok(())
    }
    fn __clear__(&self) { self.ports.borrow_mut().clear(); self.frames.borrow_mut().clear(); }
}

impl MachineCore {
    fn seg(&self, p: u16) -> u16 { self.load.wrapping_add(p) }
    fn parsed(address: &str) -> PyResult<(u16, u16)> {
        let (s, o) = address.split_once(':').ok_or_else(|| PyValueError::new_err("expected segment:offset"))?;
        Ok((u16::from_str_radix(s, 16).map_err(|e| PyValueError::new_err(e.to_string()))?,
            u16::from_str_radix(o, 16).map_err(|e| PyValueError::new_err(e.to_string()))?))
    }
    fn lin(&self, address: &str) -> PyResult<u32> { let (s, o) = Self::parsed(address)?; Ok(mem::lin(self.seg(s), o)) }
    fn set(&self, m: &Bound<'_, PyAny>, name: &str, v: u32) -> PyResult<()> {
        let (i, shift, mask, clears) = alias(m.py(), name)?;
        {
            let mut r = self.regs.borrow_mut();
            if clears { r[i] = 0; }
            r[i] = (r[i] & !(mask << shift)) | ((v & mask) << shift);
            if i == 8 { r[i] |= 2; }
        }
        let tap = m.getattr("io_tap")?;
        if !tap.is_none() { tap.call1(("s", name, v))?; }
        Ok(())
    }
    fn bytes<'py>(&self, py: Python<'py>, linear: u32, n: usize) -> PyResult<Bound<'py, PyBytes>> {
        let b = self.memory.bind(py);
        // No Python call or callback may run with this slice borrowed.
        let bytes = unsafe { b.as_bytes() };
        if !mem::in_bounds(linear, n as u32) || linear as usize + n > bytes.len() { return Err(port_error(py, format!("plain-memory read/write outside mapped range: {linear}+{n}"))); }
        Ok(PyBytes::new(py, &bytes[linear as usize..linear as usize + n]))
    }
    fn put(&self, py: Python<'_>, linear: u32, data: &[u8]) -> PyResult<()> {
        // No Python code runs while the mutable bytearray slice is borrowed.
        if !mem::put(unsafe { self.memory.bind(py).as_bytes_mut() }, linear, data) { return Err(port_error(py, format!("plain-memory read/write outside mapped range: {linear}+{}", data.len()))); }
        Ok(())
    }
    fn stack_word(&self, m: &Bound<'_, PyAny>, offset: u32) -> PyResult<u32> {
        let linear = self.reg(m, "ss")? * 16 + (self.reg(m, "sp")?.wrapping_add(offset) & 0xffff);
        let data = self.bytes(m.py(), linear, 2)?;
        let tap = m.getattr("io_tap")?;
        if !tap.is_none() { tap.call1(("r", linear, &data))?; }
        Ok(u16::from_le_bytes(data.as_bytes().try_into().unwrap()) as u32)
    }
    fn raise_pending(&self, m: &Bound<'_, PyAny>) -> PyResult<()> {
        let error = m.getattr("error")?;
        if !error.is_none() { m.setattr("error", m.py().None())?; return Err(PyErr::from_value(error)); }
        Ok(())
    }
    fn placeholder(&self, m: &Bound<'_, PyAny>, lin: u32) -> PyResult<()> {
        let handlers = m.getattr("_handlers")?.cast_into::<PyDict>()?;
        if !handlers.contains(lin)? { m.call_method1("at_linear", (lin, self.noop.bind(m.py())))?; }
        Ok(())
    }
    fn handlers(&self, m: &Bound<'_, PyAny>, lin: u32, replay: bool, fired: bool) -> PyResult<bool> {
        let py = m.py();
        let handlers = m.getattr("_handlers")?.cast_into::<PyDict>()?;
        let list = match handlers.get_item(lin)? { Some(v) => v, None => return Ok(false) };
        // Freeze this site's handlers before calling any of them (registration is reentrant).
        let hs: Vec<Py<PyAny>> = list.try_iter()?.map(|h| h.map(Bound::unbind)).collect::<PyResult<_>>()?;
        let tap = if hs.iter().any(|h| !h.bind(py).is(self.noop.bind(py))) { m.getattr("site_tap")? } else { py.None().into_bound(py) };
        let kwargs = PyDict::new(py);
        if fired { kwargs.set_item("fired", true)?; }
        if !tap.is_none() { tap.call_method("site_enter", (lin, replay), Some(&kwargs))?; }
        let mut stopped = false;
        let result: PyResult<()> = (|| {
            for h in hs {
                h.bind(py).call1((replay,))?;
                if fired { self.raise_pending(m)?; }
                else if !m.getattr("stop_reason")?.is_none() || !m.getattr("error")?.is_none() { stopped = true; break; }
            }
            Ok(())
        })();
        // fire has a finally clause; _dispatch does NOT deliver site_leave on exceptions.
        if (fired || result.is_ok()) && !tap.is_none() { tap.call_method("site_leave", (lin, stopped), Some(&kwargs))?; }
        result?;
        Ok(stopped)
    }
    fn listeners(&self, m: &Bound<'_, PyAny>, linear: u32, n: usize, value: &Bound<'_, PyAny>, at: &Bound<'_, PyAny>) -> PyResult<()> {
        let py = m.py();
        let (lo, hi): (i64, i64) = m.getattr("_writes_span")?.extract()?;
        if !(lo <= linear as i64 && linear as i64 <= hi) { return Ok(()); }
        let saved = m.getattr("_pc_override")?; m.setattr("_pc_override", at)?;
        let result = (|| {
            let writes = m.getattr("_writes_now")?.cast_into::<PyTuple>()?;
            for (index, w) in writes.iter().enumerate() {
                let (begin, end, f, recorder): (u32, u32, Py<PyAny>, bool) = w.extract()?;
                if begin <= linear && linear <= end && (recorder || !m.getattr("muted")?.is_truthy()?) {
                    let tap = if recorder { py.None().into_bound(py) } else { m.getattr("listen_tap")? };
                    if tap.is_none() { f.bind(py).call1((linear, n, value))?; }
                    else {
                        let token = tap.call_method1("listen_enter", (index, linear, n, value))?;
                        let call = f.bind(py).call1((linear, n, value));
                        tap.call_method1("listen_leave", (token,))?;
                        call?;
                    }
                    self.raise_pending(m)?;
                }
            }
            Ok(())
        })();
        m.setattr("_pc_override", saved)?;
        result
    }
    fn write_native(&self, m: &Bound<'_, PyAny>, linear: u32, data: &[u8], at: u32) -> PyResult<()> {
        let py = m.py();
        if !mem::in_bounds(linear, data.len() as u32) { return Err(port_error(py, format!("plain-memory read/write outside mapped range: {linear}+{}", data.len()))); }
        let value = data.iter().enumerate().fold(0u64, |v, (k, b)| v | ((*b as u64) << (8 * k)));
        self.listeners(m, linear, data.len(), &value.into_pyobject(py)?.into_any(), &at.into_pyobject(py)?.into_any())?;
        self.put(py, linear, data)
    }
    fn start_port(&self, m: &Bound<'_, PyAny>, port: Port, done: Py<PyAny>) -> PyResult<()> {
        let py = m.py();
        let address = port.entry.bind(py).getattr("address")?;
        let calls = port.calls.bind(py);
        let n: u64 = calls.get_item(&address)?.map(|v| v.extract()).transpose()?.unwrap_or(0);
        calls.set_item(&address, n + 1)?;
        // Preserve the Python constructor's left-to-right register reads.
        let ss = self.reg(m, "ss")?; let sp = self.reg(m, "sp")?; let bp = self.reg(m, "bp")?;
        let frame = Frame { port, done, ss, sp, bp, gen: None, waiting: None, ret_lin: None, expect_sp: None, after_sp: None };
        let entries = frame.port.mem.bind(py).getattr("_entries")?.cast_into::<PyList>()?;
        let far: bool = frame.port.entry.bind(py).getattr("far")?.extract()?;
        entries.append((sp, far))?;
        let result = (|| {
            if self.native && frame.port.variant.bind(py).is_none() && self.native_body(m, (sp, far), &address.extract::<String>()?)?.is_some() {
                *self.native_calls.borrow_mut().entry(address.extract()?).or_insert(0) += 1;
                return Ok(py.None().into_bound(py));
            }
            frame.port.entry.bind(py).getattr("fn")?.call1((frame.port.mem.bind(py), frame.port.variant.bind(py)))
        })();
        entries.call_method0("pop")?;
        let value = result?;
        if value.is_instance(self.generator_type.bind(py))? {
            let mut frame = frame; frame.gen = Some(value.unbind());
            self.step(m, frame, &py.None().into_bound(py))
        } else { self.finish(m, frame, value) }
    }
    fn step(&self, m: &Bound<'_, PyAny>, frame: Frame, sent: &Bound<'_, PyAny>) -> PyResult<()> {
        let py = m.py();
        let entries = frame.port.mem.bind(py).getattr("_entries")?.cast_into::<PyList>()?;
        let far: bool = frame.port.entry.bind(py).getattr("far")?.extract()?;
        entries.append((frame.sp, far))?;
        let result = frame.gen.as_ref().unwrap().bind(py).call_method1("send", (sent,));
        entries.call_method0("pop")?;
        match result {
            Ok(request) => {
                if !request.is_instance(self.call_type.bind(py))? {
                    let address: String = frame.port.entry.bind(py).getattr("address")?.extract()?;
                    return Err(port_error(py, format!("port {address} yielded {}: a port yields mem.call(...) only", request.repr()?)));
                }
                self.issue(m, frame, request)
            }
            Err(e) if e.is_instance_of::<PyStopIteration>(py) => {
                let value = e.value(py).getattr("value")?;
                self.finish(m, frame, value)
            }
            Err(e) => Err(e),
        }
    }
    fn issue(&self, m: &Bound<'_, PyAny>, mut f: Frame, c: Bound<'_, PyAny>) -> PyResult<()> {
        let py = m.py();
        let ret_to: String = c.getattr("ret_to")?.extract()?;
        let target: String = c.getattr("target")?.extract()?;
        let (rs, roff) = Self::parsed(&ret_to)?;
        let (ts, toff) = Self::parsed(&target)?;
        let far: bool = c.getattr("far")?.extract()?;
        if !far && (self.seg(ts) as u32 != self.reg(m, "cs")? || self.seg(rs) as u32 != self.reg(m, "cs")?) {
            let address: String = f.port.entry.bind(py).getattr("address")?.extract()?;
            let cs = (self.reg(m, "cs")? as u16).wrapping_sub(self.load);
            return Err(port_error(py, format!("port {address}: a near call of {target} returning to {ret_to} from CS {cs:04X}: a near call stays in its segment")));
        }
        let mut sp = self.reg(m, "sp")?;
        f.after_sp = Some(sp);
        let args = c.getattr("args")?.cast_into::<PyTuple>()?;
        let mut words = Vec::with_capacity(args.len() + 2);
        for arg in args.iter() { words.push(arg.call_method1("__and__", (0xffff,))?.extract::<u16>()?); }
        if far { words.push(self.seg(rs)); }
        words.push(roff);
        for (i, w) in words.into_iter().enumerate() {
            sp = sp.wrapping_sub(2) & 0xffff;
            let ss = self.reg(m, "ss")?;
            // Mutant 1 corrupts a guest-call return's saved IP; a machine error.
            let w = if self.mutant == 1 && i == args.len() + usize::from(far) { w.wrapping_add(1) } else { w };
            self.write_native(m, ss * 16 + sp, &w.to_le_bytes(), self.lin(&ret_to)?)?;
        }
        self.set(m, "sp", sp)?;
        f.expect_sp = Some(if c.getattr("caller_pops")?.is_truthy()? { f.after_sp.unwrap().wrapping_sub(2 * args.len() as u32) & 0xffff } else { f.after_sp.unwrap() });
        f.ret_lin = Some(mem::lin(self.seg(rs), roff)); f.waiting = Some(c.unbind());
        self.set(m, "cs", self.seg(ts) as u32)?;
        self.set(m, "eip", toff as u32)?;
        self.placeholder(m, f.ret_lin.unwrap())?;
        self.frames.borrow_mut().push(f);
        Ok(())
    }
    fn finish(&self, m: &Bound<'_, PyAny>, f: Frame, value: Bound<'_, PyAny>) -> PyResult<()> {
        let py = m.py(); let entry = f.port.entry.bind(py);
        let delta: i64 = entry.getattr("return_stack_delta")?.extract()?;
        self.set(m, "sp", (f.sp as i64 + delta) as u32 & 0xffff)?;
        self.set(m, "bp", f.bp)?;
        if !value.is_none() {
            let v = py.get_type::<pyo3::types::PyInt>().call1((&value,))?;
            self.set(m, "ax", v.call_method1("__and__", (0xffff,))?.extract()?)?;
            if entry.getattr("long")?.is_truthy()? {
                self.set(m, "dx", v.call_method1("__rshift__", (16,))?.call_method1("__and__", (0xffff,))?.extract()?)?;
            }
        }
        self.return_from(m, entry.getattr("far")?.extract()?, entry.getattr("pop")?.extract()?)?;
        if !f.done.bind(py).is_none() {
            let view = f.describe(py)?; view.setattr("value", value)?;
            f.done.bind(py).call1((view,))?;
        }
        Ok(())
    }
    fn native_body(&self, m: &Bound<'_, PyAny>, entry: (u32, bool), address: &str) -> PyResult<Option<()>> {
        let mut h = NativeHost { core: self, m: m.clone(), entry };
        use crate::geometry as g;
        match address {
            "0791:2BE5" => g::direction(&mut h)?, "0791:2B51" => g::slot_is_on_ball_side(&mut h)?,
            "0791:26D7" => g::player_effective_tactic(&mut h)?, "0791:045D" => g::keeper(&mut h)?,
            "0791:2C29" => g::slot_is_idle_ball_slot(&mut h)?, "0791:2CEC" => g::player_at_ball(&mut h)?,
            "0791:2974" => g::side(&mut h)?, _ => return Ok(None),
        }
        Ok(Some(()))
    }
}

struct NativeHost<'a, 'py> { core: &'a MachineCore, m: Bound<'py, PyAny>, entry: (u32, bool) }
impl Host for NativeHost<'_, '_> {
    type Err = PyErr;
    fn reg(&mut self, r: Reg) -> PyResult<u32> { self.core.reg(&self.m, r.name()) }
    fn set_reg(&mut self, r: Reg, v: u32) -> PyResult<()> { self.core.set(&self.m, r.name(), v) }
    fn u8(&mut self, l: u32) -> PyResult<u8> {
        mem::u8_at(unsafe { self.core.memory.bind(self.m.py()).as_bytes() }, l).ok_or_else(|| port_error(self.m.py(), format!("plain-memory read/write outside mapped range: {l}+1")))
    }
    fn u16(&mut self, l: u32) -> PyResult<u16> {
        mem::u16_at(unsafe { self.core.memory.bind(self.m.py()).as_bytes() }, l).ok_or_else(|| port_error(self.m.py(), format!("plain-memory read/write outside mapped range: {l}+2")))
    }
    fn write(&mut self, l: u32, data: &[u8], at: u32) -> PyResult<()> { self.core.write_native(&self.m, l, data, at) }
    fn ss_lin(&mut self, off: u32) -> PyResult<u32> { Ok(self.reg(Reg::Ss)? * 16 + (off & 0xffff)) }
    fn ds(&self) -> u16 { self.core.load.wrapping_add(0x2581) }
    fn seg(&self, p: u16) -> u16 { self.core.seg(p) }
    fn entry(&self) -> (u32, bool) { self.entry }
    fn store_order(&mut self, inserted: &[Reg]) -> PyResult<Vec<Reg>> {
        if self.m.getattr("io_tap")?.is_none() { return Ok(inserted.to_vec()); }
        let set = PySet::empty(self.m.py())?;
        for r in inserted { set.add(r.name())?; }
        set.iter().map(|s| { let name: String = s.extract()?; Ok(*inserted.iter().find(|r| r.name() == name).unwrap()) }).collect()
    }
    fn port_error(&self, what: String) -> PyErr { port_error(self.m.py(), what) }
}
