//! A plain host for unit tests: a memory image, a register file, a log of every register read and set and
//! every write (with its `at`), in order. No interpreter.
use crate::host::{Host, Reg};
use crate::mem::{self, MEM_SIZE};

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Ev {
    Get(Reg, u32),
    Set(Reg, u32),
    Write(u32, Vec<u8>, u32),
}

pub struct TestHost {
    pub memory: Vec<u8>,
    pub regs: [u32; 11],
    pub log: Vec<Ev>,
    pub ds: u16,
    pub load: u16,
    pub entry: (u32, bool),
}

impl TestHost {
    pub fn new(load: u16) -> Self {
        TestHost {
            memory: vec![0; MEM_SIZE as usize],
            regs: [0; 11],
            log: vec![],
            ds: load.wrapping_add(0x2581),
            load,
            entry: (0, false),
        }
    }

    /// A far call's entry: SP at the return IP, CS above it, then `args` with arg 0 (pushed last) nearest.
    pub fn call_far(&mut self, ss: u16, sp: u16, args: &[u16]) {
        self.regs[Reg::Ss as usize] = ss as u32;
        let mut p = sp as u32 + 4;
        for a in args.iter() {
            mem::put_u16(&mut self.memory, ss as u32 * 16 + p, *a);
            p += 2;
        }
        self.regs[Reg::Sp as usize] = sp as u32;
        self.entry = (sp as u32, true);
    }

    pub fn call_near(&mut self, ss: u16, sp: u16, args: &[u16]) {
        self.regs[Reg::Ss as usize] = ss as u32;
        let mut p = sp as u32 + 2;
        for a in args.iter() {
            mem::put_u16(&mut self.memory, ss as u32 * 16 + p, *a);
            p += 2;
        }
        self.regs[Reg::Sp as usize] = sp as u32;
        self.entry = (sp as u32, false);
    }
}

impl Host for TestHost {
    type Err = String;
    fn reg(&mut self, r: Reg) -> Result<u32, String> {
        let v = self.regs[r as usize];
        self.log.push(Ev::Get(r, v));
        Ok(v)
    }
    fn set_reg(&mut self, r: Reg, value: u32) -> Result<(), String> {
        self.regs[r as usize] = value;
        self.log.push(Ev::Set(r, value));
        Ok(())
    }
    fn u8(&mut self, linear: u32) -> Result<u8, String> {
        mem::u8_at(&self.memory, linear).ok_or_else(|| format!("out of range {linear}+1"))
    }
    fn u16(&mut self, linear: u32) -> Result<u16, String> {
        mem::u16_at(&self.memory, linear).ok_or_else(|| format!("out of range {linear}+2"))
    }
    fn write(&mut self, linear: u32, data: &[u8], at: u32) -> Result<(), String> {
        if !mem::put(&mut self.memory, linear, data) {
            return Err(format!("out of range {linear}+{}", data.len()));
        }
        self.log.push(Ev::Write(linear, data.to_vec(), at));
        Ok(())
    }
    fn ss_lin(&mut self, off: u32) -> Result<u32, String> {
        let ss = self.reg(Reg::Ss)?;
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
    fn store_order(&mut self, inserted: &[Reg]) -> Result<Vec<Reg>, String> {
        Ok(inserted.to_vec())
    }
    fn port_error(&self, what: String) -> String {
        what
    }
}
