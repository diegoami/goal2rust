//! goal2rust T01: hot routines of goal2-archaeology's Python match port in Rust.
//! `mem` (accessors), `host` (what a routine asks of its machine), `regs` (the port's Regs model) and the
//! translated routines are plain Rust, tested by `cargo test`; `py` (feature `python`) binds them for the port.
pub mod ball;
pub mod speaker;
pub mod skill;
pub mod geometry;
pub mod host;
pub mod mem;
pub mod regs;
#[cfg(feature = "python")]
pub mod py;
#[cfg(feature = "python")]
pub mod machine;
#[cfg(test)]
pub mod testhost;
#[cfg(test)]
mod tests;

pub mod keys;

pub mod ball_draw;

pub mod sweep;

pub mod play;

pub mod player_update;
