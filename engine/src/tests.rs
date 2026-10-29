//! Unit tests of the Regs model and the routines on a plain host. The expected values are derived by hand from the
//! Python port's semantics (port/runtime.py Regs, geometry.py, entrypoints.py at d3cf46a3); equality with the port
//! itself is shown on the drive receipts (out/T01), never by these alone.
use crate::geometry;
use crate::host::Reg;
use crate::mem::{self, lin};
use crate::regs::{sub_flags, Regs, PF, ZF};
use crate::testhost::{Ev, TestHost};

const LOAD: u16 = 0x0100;
const SS: u16 = 0x3000;

fn host() -> TestHost {
    let mut h = TestHost::new(LOAD);
    h.regs[Reg::Bp as usize] = 0x0BB0;
    h.regs[Reg::Ax as usize] = 0xAB00;
    h
}

fn writes(h: &TestHost) -> Vec<(u32, Vec<u8>)> {
    h.log.iter().filter_map(|e| if let Ev::Write(a, d, _) = e { Some((*a, d.clone())) } else { None }).collect()
}

fn sets(h: &TestHost) -> Vec<(Reg, u32)> {
    h.log.iter().filter_map(|e| if let Ev::Set(r, v) = e { Some((*r, *v)) } else { None }).collect()
}

#[test]
fn flush_writes_runs_in_address_order_later_writes_win() {
    let mut h = host();
    h.call_far(SS, 0x100, &[]);
    let mut r = Regs::new(false);
    r.enter(&mut h, 2).unwrap(); // bp at FE, bp := FE, sp := FC
    r.local8(&mut h, -1, 7).unwrap(); // FD
    r.push(&mut h, 0x1234).unwrap(); // FA
    r.push(&mut h, 0x5678).unwrap(); // F8
    r.local16(&mut h, -6, 0x9999).unwrap(); // F8 again: later wins
    r.flush(&mut h).unwrap();
    let base = SS as u32 * 16;
    assert_eq!(
        writes(&h),
        vec![(base + 0xF8, vec![0x99, 0x99, 0x34, 0x12]), (base + 0xFD, vec![7, 0xB0, 0x0B])]
    );
    // the stack write names 214B:0000
    assert!(h.log.iter().all(|e| !matches!(e, Ev::Write(_, _, at) if *at != lin(LOAD + 0x214B, 0))));
}

#[test]
fn registers_are_read_once_and_stored_in_insertion_order_without_sp_bp() {
    let mut h = host();
    h.call_far(SS, 0x100, &[]);
    let mut r = Regs::new(false);
    r.enter(&mut h, 0).unwrap();
    r.set_al(&mut h, 0x42).unwrap();
    r.set(Reg::Dx, 0x1_0005); // masked
    r.set_i(Reg::Cx, -1);
    r.leave(&mut h).unwrap();
    r.store(&mut h, false).unwrap();
    // SP of a fresh frame comes from the entry, not the machine: no Get(Sp)
    let gets: Vec<Reg> = h.log.iter().filter_map(|e| if let Ev::Get(r, _) = e { Some(*r) } else { None }).collect();
    assert_eq!(gets, vec![Reg::Bp, Reg::Ss, Reg::Ax]);
    assert_eq!(sets(&h), vec![(Reg::Ax, 0xAB42), (Reg::Dx, 5), (Reg::Cx, 0xFFFF)]);
}

#[test]
fn slot_is_on_ball_side_2b51() {
    let mut h = host();
    let ds = h.ds;
    h.memory[lin(ds, 0x830B) as usize] = 3; // ball slot 3: side flag 1
    h.memory[lin(ds, 0x8100 + 6) as usize] = 5; // the record's slot 5: side 1
    h.call_far(SS, 0x200, &[0x8100, ds]); // arg 0 the offset, nearest the return address
    geometry::slot_is_on_ball_side(&mut h).unwrap();
    let base = SS as u32 * 16;
    let cs = LOAD + 0x791;
    let mut expect1 = vec![1u8]; // 1EF: 2974's local; then its saved BP, the return, CS, off, seg, the pushed AX
    for w in [0x01FEu16, 0x2B64, cs, 0x8100, ds, 0xAB01] {
        expect1.extend_from_slice(&w.to_le_bytes());
    }
    assert_eq!(writes(&h), vec![(base + 0x1EF, expect1), (base + 0x1FD, vec![1, 0xB0, 0x0B])]);
    assert_eq!(sets(&h), vec![(Reg::Ax, 0xAB01), (Reg::Es, ds as u32), (Reg::Di, 0x8100), (Reg::Dx, 0xAB01)]);
    // the other side: AL 0
    let mut h2 = host();
    h2.memory[lin(ds, 0x830B) as usize] = 0xD;
    h2.memory[lin(ds, 0x8100 + 6) as usize] = 5;
    h2.call_far(SS, 0x200, &[0x8100, ds]);
    geometry::slot_is_on_ball_side(&mut h2).unwrap();
    assert_eq!(sets(&h2)[0], (Reg::Ax, 0xAB00));
}

#[test]
fn keeper_045d_sets_flags_of_its_compare() {
    for (slot, al, flags) in [(12u16, 1u32, sub_flags(12, 12, 16)), (1, 1, sub_flags(1, 1, 16)), (7, 0, sub_flags(7, 12, 16))] {
        let mut h = host();
        h.regs[Reg::Eflags as usize] = 0x0202 | 0x0001; // IF, CF set before
        h.call_near(SS, 0x300, &[slot]);
        geometry::keeper(&mut h).unwrap();
        let s = sets(&h);
        assert_eq!(s[0], (Reg::Ax, 0xAB00 | al));
        let ef = s.last().unwrap();
        assert_eq!(ef.0, Reg::Eflags);
        assert_eq!(ef.1, (0x0203 & !crate::regs::ARITH) | flags);
    }
    assert_eq!(sub_flags(12, 12, 16), ZF | PF);
}

#[test]
fn direction_2be5_indexes_the_table_by_flag_xor_side() {
    // half = DS:8319 = -1 (flag 1), side of slot 5 = 1: index 0; DS:7920[0] = 0xFF
    let mut h = host();
    let ds = h.ds;
    h.memory[lin(ds, 0x8319) as usize] = 0xFF;
    mem::put_u16(&mut h.memory, lin(ds, 0x831B), 0x1234);
    h.memory[lin(ds, 0x8100 + 6) as usize] = 5;
    h.memory[lin(ds, 0x7920) as usize] = 0xFF;
    h.memory[lin(ds, 0x7921) as usize] = 0x01;
    h.call_far(SS, 0x200, &[0x8100, ds]);
    geometry::direction(&mut h).unwrap();
    let s = sets(&h);
    let get = |r: Reg| s.iter().find(|(x, _)| *x == r).map(|(_, v)| *v);
    assert_eq!(get(Reg::Ax), Some(0x00FF)); // AX = s8(0) = 0, AL := 0xFF
    assert_eq!(get(Reg::Di), Some(0));
    assert_eq!(get(Reg::Cx), Some(0xFFFF));
    assert_eq!(get(Reg::Bx), Some(0xFFFF));
    assert_eq!(get(Reg::Dx), Some(0x1201)); // the pushed AX: DS:831B with AL := flag 1
    // slot 13 (side 0): index 1
    let mut h = host();
    h.memory[lin(ds, 0x8319) as usize] = 0xFF;
    h.memory[lin(ds, 0x8100 + 6) as usize] = 13;
    h.memory[lin(ds, 0x7921) as usize] = 0x01;
    h.call_far(SS, 0x200, &[0x8100, ds]);
    geometry::direction(&mut h).unwrap();
    let s = sets(&h);
    assert_eq!(s.iter().find(|(x, _)| *x == Reg::Ax).unwrap().1, 0x0001);
}

#[test]
fn out_of_range_reads_are_errors_not_panics() {
    let mut h = host();
    h.call_far(0xFFFF, 0xFFF8, &[]);
    // args at SS:FFFC: FFFF0 + FFFC is inside the HMA; a record at FFFF:FFFF + 6 wraps in its segment
    h.memory.truncate(0x100);
    assert!(geometry::slot_is_on_ball_side(&mut h).is_err());
}
