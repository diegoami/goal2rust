# T01 go/no-go: hot port routines in Rust

For the owner. [designed: T01, 2026-10-29] Every figure below is measured on this machine (32 CPUs, shared, WSL2)
at goal2-archaeology `d3cf46a3`, unless marked as a derived estimate; the files are under `out/T01/`.

## What was built

- `engine/`: a Rust crate with PyO3 0.30.1 bindings, built by maturin 1.15.0. Its pieces are the port's guest
  memory as a zero-copy view of `PortMachine._memory`, typed `u8`/`u16`/`i16` accessors with explicit 16-bit wrap,
  and the port's `Regs` model translated statement by statement. Python's set order for the dirty registers is
  reproduced, so the tapped `set_reg` order is the same. The host over `_PortMemory` reads registers in place
  when untapped and through `PortMachine.reg`/`set_reg` when an io_tap listens. A write inside the kit's listener
  span goes through `PortMachine.write_as`, so every listener and listen_tap fires as before.
- Seven routines of one subsystem are translated: the geometry queries on one pitch record and their pilot entry
  points, `0791:2BE5`, `2B51`, `26D7`, `2C29`, `2CEC`, `045D` and `2974` (pinned in `PROVENANCE.md`). They are the
  plain hot routines of the fresh profile (`profile-d3cf46a3-v1.txt`). The hottest routine of the same group, `2956`
  (185k calls), is a generator: it makes a guest call. It stays in Python (see Hazards).
- The hook is 18 lines in `port/__init__.py` of a clone (`out/T01/rust-hook-v1.patch`, branch
  `spike/rust-hook` at `ce1d0256`). `GOAL2_PORT_OVERRIDES` names modules that map an address to a function, and
  that function replaces the registered port's function, under the same PortFrame. Port names and call counts do
  not change, so results and saves are unchanged. If this approach went on, the hook would become a request to
  goal2-archaeology.

## Equality (Done-when 1)

- E034-03's straight drive, taps mode, `PYTHONHASHSEED=0`, all seven routines in Rust (`taps-rust-all-v1.json`),
  matches the pristine clone (`dev-taps-python-d3cf46a3.json`). Events (831, `aa402fb8…`), result (`b08217df…`),
  full memory (`f308151e…`), 553 stretches and the ordered tap hash `76ac2f95…` are all equal: 158,092,779 io calls,
  114,492 listener and 81,134 site calls. The first routine alone (`2BE5`, `dev-taps-rust-2be5.json`) was equal
  in the same way (M2).
- F40 with all seven in Rust (`family-F40-rust-v1.jsonl`, `compare-F40-rust-v1.log`): TBD.
- In-process differential (`differential-v1.json`, producer `differential_v1.py`): each routine ran from 500
  randomised states, in four modes (io_tap off/on × a write listener over the stack off/on). That is 2000 runs per
  routine, all equal to Python on full memory, every register, the ordered tap and listener calls, and errors.

### The falsifiers (mutants)

| Mutant | Drive receipts (events, result, memory, taps) | Differential |
| --- | --- | --- |
| 1: 2B51 leaves its dead frame byte `[bp-1]` unwritten | **not caught**: every field equal (`taps-rust-mutant1-v1.json`) | caught: 44/400 equal (`differential-mutant1-v1.json`) |
| 2: 2974 counts slot 0xC as side 0 (in `2974`, `2B51`, `26D7`, `2BE5`) | caught: score 1-11 against 1-1, every field differs (`taps-rust-mutant2-v1.json`) | caught in 4 routines (`differential-mutant2-v1.json`) |

Mutant 1 is the lesson. A difference in a dead stack byte is overwritten before the match ends, so the end-of-drive
full-memory digest never sees it. The taps never see it either, because no kit listener covers the stack. The
receipts prove the drive equal; they do not prove each routine equal. Every translated routine therefore needs the
per-call differential too, not only the receipts.

## Speed (Done-when 2 and 3)

### The drive

TBD (paired receipts `cpu-python-v1.json`, `cpu-rust-v1.json`).

### Per routine, and the crossing (`crossing-v1.json`, ns per call, best of 5 × 50,000)

The setup is in-process on the drive's state after 60 events, untapped. "Bare" is `fn(mem, None)`. "Framed" is
the whole port call as the dispatcher makes it, `PortFrame.start`: the entry, the function, `_finish` and
`return_from`. A register restore of 143 ns per call is subtracted.

| Routine | Python bare | Rust bare | Body speed-up | Python framed | Rust framed | Call speed-up | Calls in the drive | Saved in the drive (derived) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2BE5 | 18,019 | 921 | 19.6× | 24,763 | 4,544 | 5.5× | 247,014 | 4.2 s |
| 2B51 | 16,123 | 752 | 21.4× | 20,885 | 4,327 | 4.8× | 161,484 | 2.5 s |
| 26D7 | 28,036 | 991 | 28.3× | 34,341 | 4,645 | 7.4× | 132,774 | 3.6 s |
| 2C29 | 6,556 | 562 | 11.7× | 10,381 | 4,143 | 2.5× | 112,141 | 0.7 s |
| 2CEC | 6,530 | 537 | 12.2× | 10,318 | 4,057 | 2.5× | 93,450 | 0.6 s |
| 045D | 6,754 | 540 | 12.5× | 10,060 | 3,275 | 3.1× | 90,495 | 0.6 s |
| 2974 | 7,787 | 655 | 11.9× | 11,987 | 4,362 | 2.7× | 43,146 | 0.3 s |

- The Python/Rust crossing itself is cheap. A bare call of an empty Rust function costs 19 ns more than the
  restore loop. Building the host (getattr of the machine, memory, registers, io_tap, DS, load and the entry) costs
  99 ns. Even on the smallest routine, the crossing is well under the routine's own cost.
- The port machinery around every call is not cheap. A Python no-op run through PortFrame costs **3,424 ns**,
  3 to 6 times what the Rust body costs. The drive makes 3.10 M port calls and 3.10 M guest calls (profile).
  Measured per call, the framing alone is about 10.6 s of the drive (derived: 3.10 M × 3.42 µs). Guest-call
  issue, dispatch and resume add to that. The profile puts guest.py, the dispatcher and `machine.py`'s
  return path at about a fifth of all time.
- The Rust bodies still spend most of their 0.5 to 1 µs on Python objects: register dict lookups and int
  conversions, plus `_writes_span` read on every write. That could be cut further, but it is already small next
  to the framing.

### Cost of translating and proving, per routine

- Shared machinery, written once: `regs.rs` (285 lines), `host.rs` (70), `py.rs` (300), `mem.rs` (156), and the
  three producers (`differential_v1.py`, `crossing_v1.py`, `compare_receipts.py`). That took about 30 minutes of
  agent time.
- Per routine: 10 to 55 lines of Rust, about 2 to 8 minutes of agent time to transcribe from the Python routine.
  The listing is cited, but in practice the structure came from the Python routine, which already follows the
  listing line by line. The work is mechanical once `Regs` exists, and every Python evaluation order that touches
  a register or a write has to be kept. No routine needed a second attempt. Two test-helper mistakes (argument
  order, AL replacement) were in the unit tests, not in the routines.
- Proof, per change:
  - the differential: about 1 minute per 2000 runs of all seven routines;
  - one taps receipt: about 215 to 240 s CPU;
  - F40: about 40 × 155 s CPU, roughly 55 minutes of wall time with 2 workers.
  The receipts and F40 are paid per batch of routines, not per routine; the differential is per routine.

## Hazards met

- **Tap order.** With an io_tap, every first use of a register in `Regs` is a tapped `reg`, every `store` is a
  tapped `set_reg` in Python's set order, and every `ss_lin` is a tapped read of SS. The Rust routine reproduces
  each of them in the same order: the host calls the machine's own `reg`/`set_reg` and builds a real Python set
  for the store order. The order of Python's evaluation inside one statement (`R.al = 1 if R.al == ... else 0`)
  decides when AX is first read, so the translation keeps it.
- **Listeners.** A write must reach every listener whose range holds its address, with `pc()` set to the writing
  instruction. Outside the listener span the host writes directly, exactly as `write_as`'s own fast path does.
  Inside it, the host calls `write_as`, and it re-reads `io_tap` after any Python callback.
- **Stack frames.** The stack frames (saved BP, locals, pushed arguments and return addresses, Regs' flush in runs)
  are part of the full-memory digest. Only the differential catches a stack byte that is later overwritten
  (mutant 1).
- **16-bit signedness and wrap.** `s8`/`cbw`, offsets wrapping inside a segment while linear addresses do not
  (`pilot.pitch_slot_side` reads `seg*16+off+6` unwrapped, while `side_core`'s flag read wraps), `mul` into DX:AX,
  and a 16-bit SP wrap below zero (the differential draws SP down to 0).
- **Generators.** A port that makes a guest call is a Python generator. The hook cannot give it a Rust body,
  because `PortFrame.start` checks `inspect.isgenerator`. So `2956`, and every routine that calls the original's
  code, stays out of reach of this hook as written.

## Recommendation

**Change the approach; do not continue routine by routine on the Python dispatcher.**

Reasons:
1. The ceiling is low. TBD (the measured drive speed-up). The seven hottest plain routines save a measured
   ~12 s of a ~120 s drive (derived from the per-call table). The other plain routines are colder, and the
   generator routines cannot be hooked at all.
2. After translation, each call costs about 4.3 µs, and only 0.5 to 1 µs of that is the routine. The rest is the
   Python machinery around a port call: PortFrame, `return_from`, dispatch, guest-call issue and resume. The drive
   pays for it 3.1 M times over, and moving leaves to Rust does not remove it.
3. Translation itself is cheap and reliable once `Regs` exists: a few minutes per routine, all seven first-time
   equal on the strictest receipt. The proof harness (receipts, F40, the per-call differential) works and catches
   what it should, with the caveat of mutant 1.

What to do instead, in order:
- (a) Move the machinery into Rust: the dispatcher (`PortMachine.run`/`_dispatch`), `PortFrame`, guest-call issue
  and return. A Rust routine that calls another Rust routine then calls it directly, with no frame object and no
  dispatcher pass. Python ports stay callable through the bridge, with taps and listeners as now.
- (b) Translate by call tree, bottom up, so that hot callers (for example ball.py's `find_nearest_to_ball`, or
  contests.py, which call 2BE5/2956/26D7 hundreds of thousands of times) become single Rust calls.
- (c) Keep the per-call differential as a required gate for every translated routine, besides the receipts and F40.

This is a design decision for the owner. Stopping is also defensible if 1.1 to 1.2× is all the Python-hosted path
can give; the evidence above says the large factor is in (a), not in more leaves.
