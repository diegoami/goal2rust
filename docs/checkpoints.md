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

## 2026-10-29 T01 M3 in progress: taps equal, F40 37/40 (3 over the wall-time limit under foreign load)

- `taps-rust-all-v1.json` (all seven routines in Rust) equals `dev-taps-python-d3cf46a3.json` on events, result,
  full memory, stretches and the ordered tap hash (PYTHONHASHSEED=0): Done-when 1's drive half is met.
- Mutants: `taps-rust-mutant1-v1.json` (2B51's dead frame byte) is NOT caught by the receipts (every field equal),
  caught by `differential-mutant1-v1.json`; `taps-rust-mutant2-v1.json` (2974 slot 0xC) caught everywhere.
- `family-F40-rust-v1.jsonl`: `compare-F40-rust-v1.log` 37 identical, 3 NOT COMPLETED on family.py's 300 s wall-time
  limit (edit-b4d2, edit-d00d, edit-face) when another session started 12 parallel A700 matches on this machine
  (load 22): no difference found in any completed match. Next: rerun when the machine is quiet (family.py with a new
  --out), then M4's paired receipts (`out/T01/paired_v1.sh v1`) on a quiet machine.
- `crossing-v1.json`: per-call costs; `docs/go-no-go.md` drafted (TBD: drive speed-up, F40).

## 2026-10-29 T01 paused (owner's instruction: T79's 700-match port run needs the machine)

No run of T01 is running; nothing was interrupted. State: M1 and M2 reached; M3's drive half met
(`taps-rust-all-v1.json` equal to `dev-taps-python-d3cf46a3.json`); F40 37/40 identical, 3 not completed on the
300 s wall-time limit under foreign load (no difference in any completed match). `docs/go-no-go.md` is a draft
with TBD for the drive speed-up and F40.

Left, in order, on a quiet machine:
1. The 3 F40 reruns, into a new file (the v1 file keeps its error records and is not rewritten), from the hook
   clone: `cd .cache/goal2-archaeology-spike && PYTHONHASHSEED=0 GOAL2_PORT_OVERRIDES=goal2rust_overrides
   PYTHONPATH=runtime:<goal2rust>/bindings:<goal2rust>/.venv/lib/python3.12/site-packages python3.12 -B
   experiments/E036-match-port/family.py --family F40 --engine port --no-unicorn --only
   F40/edit-b4d2,F40/edit-d00d,F40/edit-face --out <goal2rust>/out/T01/family-F40-rust-v1-rerun.jsonl`. Then
   either a documented 40-record candidate (the 37 completed v1 lines + the 3 rerun lines, byte for byte) or a
   full new 40-match run (`family-F40-rust-v2.jsonl`), and `compare.py --family F40 --no-screen --candidate ...`
   into a new log.
2. M4: `out/T01/paired_v1.sh v1` (pristine and hook clone at once; writes `cpu-{python,rust}-v1.json` with source
   hashes), only with no foreign load.
3. M5: fill the TBDs in `docs/go-no-go.md` (drive speed-up from the paired receipts, F40 result), final
   checkpoint, report.

## 2026-10-29 T01 resumed; M3 reached: F40 identical 40/40

- The 3 matches over the time limit rerun on the quiet machine (`family-F40-rust-v1-rerun.jsonl`, all completed);
  `family-F40-rust-v2.jsonl` = v1's 37 completed records + the 3 reruns, byte for byte (`assemble_f40_v2.py`);
  `compare-F40-rust-v2.log`: 40 matches expected identical, 40 pass. With the taps receipt, Done-when 1 is met.
- Next: M4, `out/T01/paired_v1.sh v1`; a PyPy baseline if measurable; then M5.
