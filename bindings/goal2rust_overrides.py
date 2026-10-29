"""goal2rust T01: the Rust routines (engine/, module goal2rust_engine) as port overrides for goal2-archaeology's
plain port, through the spike hook (out/T01/rust-hook-v1.patch: GOAL2_PORT_OVERRIDES=goal2rust_overrides).

    GOAL2RUST_ONLY=0791:2BE5,0791:2B51   only these addresses (default: every routine the crate has)
    GOAL2RUST_MUTANT=1                   a falsifier (engine/src/geometry.rs MUTANT), to show the checks catch it

Each override is fn(mem, variant), run by the port's own PortFrame in place of the Python function."""
import os

import goal2rust_engine as engine

_only = [a for a in os.environ.get("GOAL2RUST_ONLY", "").split(",") if a]
OVERRIDES = {a: f for a, f in engine.PORTS.items() if not _only or a in _only}
if _only and set(_only) - set(OVERRIDES):
    raise ValueError(f"GOAL2RUST_ONLY: no Rust routine at {sorted(set(_only) - set(OVERRIDES))}")
engine.set_mutant(int(os.environ.get("GOAL2RUST_MUTANT", "0")))
