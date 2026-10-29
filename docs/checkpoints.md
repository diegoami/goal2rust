# Checkpoints

Until the GitHub repository exists, the latest entry here is where the work stands.

## 2026-10-29 T01 M1 reached: the crate and its bindings

- `engine/` (crate `goal2rust-engine`, PyO3 0.30.1, built by maturin 1.15.0 pinned in `requirements-build.txt`):
  `mem` (typed u8/u16/i16 accessors, explicit 16-bit offset wrap, linear bounds as PortMachine._bounds), `host`
  (what a routine may ask of the machine), `regs` (port/runtime.py's `Regs`, faithfully), `py` (the zero-copy
  `GuestMemory` over PortMachine._memory and the `PyHost` over `_PortMemory`). `cargo test` in `engine/` runs the
  accessor and Regs tests with no interpreter linked; CI workflow written (`.github/workflows/build.yml`), not yet run
  (no GitHub repository).
- Build: `python3.12 -m venv .venv && .venv/bin/pip install -r requirements-build.txt && . .venv/bin/activate &&
  cd engine && maturin develop --release`; the oracle's interpreter imports it with
  `PYTHONPATH=runtime:<goal2rust>/bindings:<goal2rust>/.venv/lib/python3.12/site-packages`.
- The hook clone: `.cache/goal2-archaeology-spike` at d3cf46a3, branch `spike/rust-hook` (commit ce1d0256):
  `GOAL2_PORT_OVERRIDES=goal2rust_overrides` replaces registered port functions by address, names and call counts
  unchanged; the diff is `out/T01/rust-hook-v1.patch` (18 lines, port/__init__.py only).
- Next: M2, the first routine equal on the taps receipt.
