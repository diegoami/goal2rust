//! The guest memory as the port sees it: one flat image of `MEM_SIZE` bytes (PortMachine._memory),
//! little-endian words, 16-bit offsets that wrap inside their segment and linear addresses that do not.
//! Every accessor here is explicit about width, sign and wrap; nothing widens silently.
//! [confirmed: goal2-archaeology d3cf46a3, runtime/original_match/machine.py MEM_SIZE, port/engine.py
//! PortMachine._bounds, port/mem.py Mem.u8/u16/s8/s16/addr]

/// 1 MiB and the high memory area (machine.py MEM_SIZE).
pub const MEM_SIZE: u32 = 0x110000;
pub const M16: u32 = 0xFFFF;

/// The bounds check of PortMachine._bounds: `linear + n <= MEM_SIZE`.
#[inline]
pub fn in_bounds(linear: u32, n: u32) -> bool {
    (linear as u64) + (n as u64) <= MEM_SIZE as u64
}

/// seg:off as a linear address (Mem.addr): the offset is a 16-bit value, the sum is not wrapped.
#[inline]
pub fn lin(seg: u16, off: u16) -> u32 {
    (seg as u32) * 16 + off as u32
}

/// An offset `off + k` inside its segment (the listing's `[di + k]`): 16-bit wrap.
#[inline]
pub fn off_add(off: u16, k: u16) -> u16 {
    off.wrapping_add(k)
}

#[inline]
pub fn u8_at(m: &[u8], linear: u32) -> Option<u8> {
    if !in_bounds(linear, 1) || linear as usize >= m.len() {
        return None;
    }
    Some(m[linear as usize])
}

#[inline]
pub fn u16_at(m: &[u8], linear: u32) -> Option<u16> {
    if !in_bounds(linear, 2) || linear as usize + 2 > m.len() {
        return None;
    }
    let i = linear as usize;
    Some(u16::from_le_bytes([m[i], m[i + 1]]))
}

#[inline]
pub fn i16_at(m: &[u8], linear: u32) -> Option<i16> {
    u16_at(m, linear).map(|v| v as i16)
}

/// `n` bytes at `linear` as a little-endian unsigned value (n <= 8).
#[inline]
pub fn read_le(m: &[u8], linear: u32, n: u32) -> Option<u64> {
    if n > 8 || !in_bounds(linear, n) || (linear + n) as usize > m.len() {
        return None;
    }
    let mut v = 0u64;
    for k in (0..n as usize).rev() {
        v = (v << 8) | m[linear as usize + k] as u64;
    }
    Some(v)
}

/// Writes `data` at `linear` (no listener: the caller decides that); false when out of range.
#[inline]
pub fn put(m: &mut [u8], linear: u32, data: &[u8]) -> bool {
    let n = data.len() as u32;
    if !in_bounds(linear, n) || (linear + n) as usize > m.len() {
        return false;
    }
    m[linear as usize..(linear + n) as usize].copy_from_slice(data);
    true
}

#[inline]
pub fn put_u16(m: &mut [u8], linear: u32, value: u16) -> bool {
    put(m, linear, &value.to_le_bytes())
}

/// cbw / s8: a byte sign-extended (mem.s8).
#[inline]
pub fn s8(v: u8) -> i16 {
    v as i8 as i16
}

/// s16: a word read as signed (mem.s16).
#[inline]
pub fn s16(v: u16) -> i16 {
    v as i16
}

/// `cbw` as the listing does it: AL sign-extended into the 16-bit AX.
#[inline]
pub fn cbw(al: u8) -> u16 {
    al as i8 as i16 as u16
}

#[cfg(test)]
mod tests {
    use super::*;

    fn image() -> Vec<u8> {
        vec![0u8; MEM_SIZE as usize]
    }

    #[test]
    fn words_are_little_endian() {
        let mut m = image();
        m[0x100] = 0x34;
        m[0x101] = 0x12;
        assert_eq!(u16_at(&m, 0x100), Some(0x1234));
        assert_eq!(u8_at(&m, 0x101), Some(0x12));
        assert!(put_u16(&mut m, 0x200, 0xBEEF));
        assert_eq!(&m[0x200..0x202], &[0xEF, 0xBE]);
        assert_eq!(read_le(&m, 0x200, 2), Some(0xBEEF));
    }

    #[test]
    fn signed_views() {
        let mut m = image();
        put_u16(&mut m, 0x10, 0xFFFE);
        assert_eq!(i16_at(&m, 0x10), Some(-2));
        assert_eq!(s8(0x80), -128);
        assert_eq!(s8(0x7F), 127);
        assert_eq!(s16(0x8000), -32768);
        assert_eq!(cbw(0xFF), 0xFFFF);
        assert_eq!(cbw(0x7F), 0x007F);
    }

    #[test]
    fn offsets_wrap_in_segment_linear_does_not() {
        assert_eq!(off_add(0xFFFF, 6), 5);
        assert_eq!(lin(0x2581, off_add(0xFFFE, 4)), 0x25810 + 2);
        assert_eq!(lin(0xFFFF, 0xFFFF), 0x10FFEF); // FFFF:FFFF: inside the HMA, not wrapped to 0
        assert!(in_bounds(0x10FFFF, 1));
        assert!(!in_bounds(0x10FFFF, 2));
    }

    #[test]
    fn out_of_range_is_refused() {
        let mut m = image();
        assert_eq!(u8_at(&m, MEM_SIZE), None);
        assert_eq!(u16_at(&m, MEM_SIZE - 1), None);
        assert!(u16_at(&m, MEM_SIZE - 2).is_some());
        assert!(!put_u16(&mut m, MEM_SIZE - 1, 1));
        assert!(!put(&mut m, u32::MAX, &[1]));
    }

    #[test]
    fn wrapping_arithmetic_is_16_bit() {
        let a: u16 = 0xFFFF;
        assert_eq!(a.wrapping_add(1), 0);
        assert_eq!(0u16.wrapping_sub(2), 0xFFFE);
        assert_eq!((0x16u16).wrapping_mul(0x1000), 0x6000);
    }
}
