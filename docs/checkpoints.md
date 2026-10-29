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

## 2026-10-29 T01 M2 reached: the first routine equal

- Profile of E034-03's drive at d3cf46a3 (`out/T01/profile-d3cf46a3-v1.txt`, producer `profile_drive_v1.py`): 3.10 M
  port calls; most time is the machinery around each call (PortFrame, return_from, Regs, _set_plain, write_as, guest
  call issue). Chosen subsystem: the geometry queries on one pitch record and their pilot entry points, the plain
  (non-generator) hot routines 2BE5 (247k calls), 2B51 (161k), 26D7 (133k), 2C29 (112k), 2CEC (93k), 045D (90k),
  2974 (43k). 2956 (185k) is a generator (a guest call to 1771:3216) and stays Python.
- 2BE5 alone in Rust: `dev-taps-rust-2be5.json` equals `dev-taps-python-d3cf46a3.json` on events, result, memory,
  stretches and the ordered tap hash 76ac2f95... (158,092,779 io calls), both PYTHONHASHSEED=0.
- All seven translated: `dev-cpu-rust-all-r1.json` equals `dev-cpu-python-r1.json` (untapped, events/result/memory);
  in-process differential (`differential_v1.py`) 80/80 per routine over 4 tap/listener modes; mutants 1 and 2 caught.
- Next: M3 (taps receipt with all seven, F40 with all seven), started: `taps-rust-all-v1.json`,
  `family-F40-rust-v1.jsonl` (resume: rerun the same family.py command, it skips recorded matches).
