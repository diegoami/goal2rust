# T01 go/no-go: hot port routines in Rust

For the owner. [designed: T01, 2026-10-29] Every figure is measured on this machine (32 CPUs, shared, WSL2) at
goal2-archaeology `d3cf46a3`, unless marked *derived*. The files are under `out/T01/`. The owner has decided that
goal2rust goes on as the place to port the engine, and then the game, to Rust (2026-10-29). So this document
recommends **how**, not whether.

## What was built

- **The crate** `engine/`: Rust with PyO3 0.30.1 bindings, built by maturin 1.15.0. It holds:
  - the port's guest memory as a zero-copy view of `PortMachine._memory`;
  - typed `u8`/`u16`/`i16` accessors with explicit 16-bit wrap;
  - the port's `Regs` model translated statement by statement, including Python's set order for the dirty
    registers, so tapped `set_reg` calls come in the same order;
  - a host over `_PortMemory`. Untapped, it reads and writes registers in place. With an io_tap, it goes through the
    machine's `reg`/`set_reg`. A write inside the kit's listener span goes through `PortMachine.write_as`.
- **The builds.** The crate builds for CPython 3.12 (`.venv`) and for PyPy 3.11 (`maturin build -i pypy3.11`,
  `.venv-pypy`, through PyPy's cpyext layer).
- **The translated routines.** Seven routines of one subsystem, pinned in `PROVENANCE.md`: the geometry queries on
  one pitch record and their pilot entry points, `0791:2BE5`, `2B51`, `26D7`, `2C29`, `2CEC`, `045D` and `2974`.
  They are the plain hot routines of a fresh profile (`profile-d3cf46a3-v1.txt`). The hottest one in the same group,
  `2956` (185k calls), makes a guest call, which makes it a Python generator, and it stays Python (see Hazards).
- **The hook.** 18 lines in `port/__init__.py` of a clone of `d3cf46a3` (`out/T01/rust-hook-v1.patch`; branch
  `spike/rust-hook`, `ce1d0256`). `GOAL2_PORT_OVERRIDES` replaces a registered port's function by address. It runs
  under the same PortFrame, with names and call counts unchanged.

## Equality (Done-when 1: met)

- **E034-03's straight drive, taps mode, `PYTHONHASHSEED=0`.** With all seven routines in Rust
  (`taps-rust-all-v1.json`), it equals the pristine clone (`dev-taps-python-d3cf46a3.json`) on:
  - events (831, `aa402fb8…`);
  - result (`b08217df…`);
  - full memory (`f308151e…`);
  - 553 stretches;
  - the ordered tap hash `76ac2f95…`: 158,092,779 io calls, 114,492 listener and 81,134 site calls.

  M2's first routine (`2BE5` alone, `dev-taps-rust-2be5.json`) was equal in the same way.
- **F40.** `compare.py --family F40 --no-screen` reports 40 of 40 identical (`compare-F40-rust-v2.log`). The
  candidate `family-F40-rust-v2.jsonl` comes from two runs of the same command. 37 records are from
  `family-F40-rust-v1.jsonl`. The other 3 are reruns on the quiet machine (`family-F40-rust-v1-rerun.jsonl`): in v1
  those matches were recorded as over family.py's 300 s wall-time limit, because another session ran 12 matches at
  once. The lines are copied byte for byte (`assemble_f40_v2.py`).
- **The in-process differential** (`differential_v1.py`). Each routine is run against its Python port from 500
  randomised states in four modes (io_tap off/on × a write listener over the stack off/on). It compares full
  memory, every register, the ordered tap and listener calls, and errors. Results: 2000/2000 equal per routine
  under CPython (`differential-v1.json`), and 200/200 under PyPy (`differential-pypy-v1.json`).

### The falsifiers

| Mutant | Drive receipts (events, result, memory, taps) | Differential |
| --- | --- | --- |
| 1: 2B51 leaves its dead frame byte `[bp-1]` unwritten | **not caught**: every field equal (`taps-rust-mutant1-v1.json`) | caught: 44/400 equal (`differential-mutant1-v1.json`) |
| 2: 2974 counts slot 0xC as side 0 (in `2974`, `2B51`, `26D7`, `2BE5`) | caught: score 1-11 against 1-1, every field differs (`taps-rust-mutant2-v1.json`) | caught in 4 routines (`differential-mutant2-v1.json`) |

Mutant 1 matters. A wrong byte in a dead stack frame is overwritten before the match ends, and no kit listener
watches the stack. So the receipts prove the drive equal, not each routine. Every translated routine needs the
per-call differential as well.

## Speed (Done-when 2 and 3)

### The drive, paired receipts (each pair started together, on the quiet machine)

| Interpreter | Python port | With the seven Rust routines | Speed-up |
| --- | --- | --- | --- |
| CPython 3.12 (`cpu-python-v1.json`, `cpu-rust-v1.json`) | 116.7 s | 98.5 s | **1.185×** |
| PyPy 3.11 (`cpu-pypy-python-v1.json`, `cpu-pypy-rust-v1.json`) | 35.2 s | 46.2 s | **0.76× (slower)** |

Each pair had equal events, result, memory and stretches. Each receipt carries the clone's source hashes, and the
crate's and bindings' source hashes with the extension's sha256. The shootout stretch went from 21.96 s to 20.57 s
on CPython. The load average was 2.1 to 3.0 for the CPython pair; one foreign unit-suite process was running.
After the CPython receipts, `engine/pyproject.toml`'s `requires-python` was lowered from 3.12 to 3.11 for the
PyPy build. That is a metadata change only, so the CPython extension is unchanged.

Against the fastest Python baseline, the best Rust result is a loss. CPython with Rust (98.5 s) is 2.8 times slower
than plain PyPy (35.2 s). Under PyPy, every Python↔Rust crossing goes through cpyext and costs more than the JIT
already makes the routine cost.

### Per routine and the crossing (ns per call; best of 5 × 50,000)

Setup: in-process, on the drive's state after 60 events, untapped. "Bare" is `fn(mem, None)`. "Framed" is the
whole port call as the dispatcher makes it (`PortFrame.start`: entry, function, `_finish`, `return_from`). A
register-restore loop is subtracted: 143 ns under CPython, 103 ns under PyPy.

| Routine | CPython: Python bare | CPython: Rust bare | CPython: body speed-up | CPython: call speed-up, framed | PyPy: Python bare | PyPy: Rust bare | Calls in the drive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2BE5 | 18,019 | 921 | 19.6× | 5.5× | 3,222 | 6,487 | 247,014 |
| 2B51 | 16,123 | 752 | 21.4× | 4.8× | 3,164 | 5,086 | 161,484 |
| 26D7 | 28,036 | 991 | 28.3× | 7.4× | 5,479 | 5,593 | 132,774 |
| 2C29 | 6,556 | 562 | 11.7× | 2.5× | 1,234 | 4,219 | 112,141 |
| 2CEC | 6,530 | 537 | 12.2× | 2.5× | 1,292 | 4,647 | 93,450 |
| 045D | 6,754 | 540 | 12.5× | 3.1× | 1,127 | 3,395 | 90,495 |
| 2974 | 7,787 | 655 | 11.9× | 2.7× | 1,362 | 4,692 | 43,146 |

(`crossing-v1.json`, `crossing-pypy-v1.json`)

- **The crossing, CPython.** Calling an empty Rust function costs 19 ns. Building the host costs 99 ns: getattr of
  the machine, memory, registers, io_tap, DS, load and the entry. That is cheap next to any routine.
- **The crossing, PyPy.** The same host build costs 479 ns. Each register or memory access from Rust goes through
  cpyext, so the Rust bodies cost 3.4 to 6.5 µs, more than PyPy's own 1.1 to 5.5 µs.
- **The machinery around every port call** is the real cost. A Python no-op run through PortFrame costs 3,424 ns
  under CPython and 325 ns under PyPy. The drive makes 3.10 M port calls and as many guest calls. Under CPython the
  framing alone is about 10.6 s of the drive (*derived*: 3.10 M × 3.42 µs), before guest-call issue, dispatch and
  resume.
- **The seven routines' saving.** The routines save about 12.4 s on CPython (*derived* from this table and the
  call counts). The paired receipts measured 18.2 s.

### Cost of translating and proving

- **Shared machinery, written once.** `regs.rs` (285 lines), `host.rs` (70), `py.rs` (300), `mem.rs` (156), plus
  the producers `differential_v1.py`, `crossing_v1.py` and `compare_receipts.py`. That took about 30 minutes of
  agent time.
- **Per routine.** 10 to 55 lines of Rust and about 2 to 8 minutes of agent time to transcribe from the Python
  routine, which already follows the listing line by line. No routine needed a second attempt. The only two
  mistakes were in unit-test helpers. The care goes into keeping every Python evaluation order that touches a
  register or a write.
- **Proof, per change.**

| Check | Cost | Paid per |
| --- | --- | --- |
| Differential | about 1 minute for 2000 runs of each of the seven routines | routine |
| Taps receipt | 215 to 240 s CPU | batch of routines |
| F40 | about 40 × 155 s CPU, about 55 minutes of wall time with 2 workers | batch of routines |

## Hazards met

- **Tap order.** With an io_tap, these all happen in Python's order:
  - every first use of a register in `Regs` is a tapped `reg`;
  - every `store` is a tapped `set_reg`, in the iteration order of a Python set;
  - every `ss_lin` is a tapped read of SS.

  The Rust host calls the machine's own `reg`/`set_reg` and builds a real Python set for the store order. That
  reproduces CPython's hash order and PyPy's insertion order alike. Python's evaluation order inside one statement
  decides when AX is first read, and the translation keeps it.
- **Listeners.** A write must reach every listener whose range holds it, with `pc()` as the writing instruction.
  Outside the listener span the host writes directly, as `write_as`'s fast path does. Inside the span it calls
  `write_as`, and it re-reads `io_tap` after any Python callback.
- **Stack frames.** The saved BP, the locals, the pushed words and Regs' run-wise flush are all in the full-memory
  digest. A stack byte that is later overwritten is caught only by the differential (mutant 1).
- **16-bit signedness and wrap.**
  - `s8`/`cbw`.
  - Segment offsets wrap while linear addresses do not: `pilot.pitch_slot_side` reads `seg*16+off+6` unwrapped,
    while the flag read beside it wraps.
  - `mul` into DX:AX.
  - SP wrapping below 0 (the differential draws SP down to 0).
- **Generators.** A port that calls the original's code is a Python generator, and `PortFrame.start` tests
  `inspect.isgenerator`. This hook therefore cannot give such a port a Rust body. Of the 3.10 M port calls in the
  drive, every caller of a guest call is in that class.
- **Interpreter choice.** PyO3 runs on both CPython and PyPy, but on PyPy every crossing pays cpyext. A Rust engine
  called from PyPy must cross rarely.

## Recommendation: how to port

1. **Do not go on routine by routine under the Python dispatcher.** It is equal and cheap to write, but it is
   capped. The seven hottest plain routines give 1.185× on CPython. Under PyPy, the faster baseline that matters,
   it is a loss (0.76×). The cost left after translation is the Python machinery around each of 6.2 M calls and
   returns, and moving leaf routines does not remove it.
2. **Build the machine in Rust first.** That means one Rust process state: the memory image, the registers, the
   dispatcher (`PortMachine.run`/`_dispatch`), the port frames, and the guest calls with their returns. Inside it,
   a Rust routine calls another Rust routine directly, and a "generator" port becomes ordinary Rust control flow,
   because its callee is Rust too.
   - Keep the `Regs`-faithful model at first (stack bytes, flush runs, register effects). The full-memory digests
     depend on it.
   - Keep the observable surface as now: io/site/listen taps recorded in Rust in the receipts' format, and the kit's
     write listeners and sites as callbacks.
3. **Cross into Python at match granularity, not routine granularity.** Expose the match through PyO3 as the kit's
   `Match` does (advance to the next event, answer a decision, save/load), so the crossing happens per event, about
   800 times a match, instead of 6 M times. Then the build choice between CPython and PyPy stops mattering for speed.
4. **Port by call tree, bottom up, inside the Rust machine.** While a subtree is unported, it runs through a bridge
   that calls the Python port. The bridge is for proof, not speed. Order the subtrees by the profile (the
   `geometry`, `ball`, `contests` and `positioning` families first), so whole hot subtrees leave Python together.
5. **Keep three gates for every routine or subtree.**
   - The per-call differential against the Python port, mandatory because of mutant 1. Extend it to replay the
     inputs captured from real drives as well as random states.
   - The taps receipt, `PYTHONHASHSEED=0`.
   - F40 with `compare.py --no-screen`.

   Then the admitted 75-match family before each milestone review.
6. **Measure against PyPy (35 s for the drive), not CPython.** That is the bar a Rust engine must beat by a wide
   margin. The original under Unicorn is 6.1 s for the same drive.
7. **Then refactor.** Once the whole engine is Rust and equal, the `Regs`/stack faithfulness can be relaxed behind
   the same receipts, where a digest proves it unobservable. That is the step to a plain, fast Rust engine, and later
   the game around it.

The hook (`out/T01/rust-hook-v1.patch`) is no longer needed for speed. It stays useful as the proof bridge in
step 4, as a request to goal2-archaeology if the owner wants it there.
