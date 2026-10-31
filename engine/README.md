# Rust match machine

The oracle is the pinned, unmodified clone described in `../PROVENANCE.md`.
Build the extension with the repository's declared maturin version:

```sh
python3.12 -m venv .venv
.venv/bin/pip install -r requirements-build.txt
. .venv/bin/activate
maturin develop --release --locked --manifest-path engine/Cargo.toml
```

Put `.cache/goal2-archaeology/runtime` on `PYTHONPATH`. `goal2rust.Match` takes the
same image, fixture and options as the kit's `original_match.Match`, and exposes
its events, decisions, result and replay-compatible save/load API:

```python
from goal2rust import Match
from original_match import Fixture

match = Match(image, Fixture(7, 19, index=9, kind=200), managed=7)
for event in match.events():
    if event.kind == "decision":
        match.answer()
result = match.result()
checkpoint = match.save()
resumed = Match.load(checkpoint)
```

`image` is an existing kit `Image`; game images and checkpoints stay outside git.

The accepted sealed-engine boundary also takes game state and verified tables:

```python
from original_match import Image
from original_match.port.tables import load as load_tables

tables = load_tables(private_tables_folder)
match = Match(Image.from_state(state, tables), fixture, managed=7)
for event in match.events():
    if event.kind == "decision":
        match.answer()
next_state = match.records_after()
checkpoint = match.save()
resumed = Match.load(checkpoint)
next_state_from_replay = resumed.records_after(tables)
```

Generate the tables locally with the pinned oracle's `tools/static/port_tables.py
extract --exe <owner's GOAL.EXE> --out <private folder>`, then copy its pinned
`static/goal-exe/tables/manifest.json` alongside `ds.hex` and `code_data.hex`.
Tables and state stay outside git and releases. The checkpoint loader does not
restore the tables object, so supply it explicitly to `records_after` after
load. [T03's evidence](../out/T03/README.md) covers this boundary; the engine
still bridges unported bodies to Python. T04 adds a native availability caller
and callee to the seven bodies measured by T03; T05 adds the nearest-to-ball
caller over those native callees, for ten default native bodies. Evidence is in
[out/T05](../out/T05/README.md), with the earlier tree in
[out/T04](../out/T04/README.md).

For oracle harnesses, call `goal2rust.install()` in the test process before
constructing/loading a kit match with `engine="port"`. This changes the factory
only in that process. It does not edit the oracle or change its default backend.

Select one port backend for the lifetime of each worker. `install()` permanently
replaces both the kit's port-machine factory and its port runner in that process;
it has no uninstall operation. A plain port-machine class captured before
installation cannot subsequently run with the replaced runner. Compare plain
Python and Rust in separate fresh subprocesses, installing Rust only in its
worker before constructing or loading matches. Each receipt should identify the
actual machine type and Rust native-call counts alongside source/extension hashes;
`engine="port"` alone does not distinguish the two implementations.

Constructing `goal2rust.Match` selects the Rust port backend and overwrites a
supplied `engine=` option. Its `load()` installs the adapter and delegates to the
kit's checkpoint loader, which reads the checkpoint's recorded backend; use
port checkpoints for Rust replay. Use the unchanged kit's `original_match.Match`
in a fresh worker for a plain-port baseline. Importing goal2rust alone does not
install the adapter; constructing/loading its Match or calling install() does.
Same-process backend coexistence is unsupported by the current adapter (review
[#6](https://github.com/diegoami/goal2rust/issues/6)); this contract does not
change the kit's default original/Unicorn backend or its checkpoint format.

The machine owns the register bank and shared guest memory. Unported Python
bodies use the same state through the bridge. The availability and nearest-ball
call trees execute in Rust alongside T01's seven bodies. Native callers suspend
as explicit Rust state through the guest call/return dispatcher; other callers
retain their Python generators. Site and write listeners remain
kit callbacks, with their original ordered taps and error/stop semantics.

Local checks that need no private image:

```sh
cargo test --locked --manifest-path engine/Cargo.toml
PYTHONHASHSEED=0 PYTHONPATH=.cache/goal2-archaeology/runtime \
  .venv/bin/python -B -m unittest discover -s engine/tests -v
```

The public synthetic differential covers frames and recursion, near/far calls,
caller/callee argument cleanup, wraparound, stop/replay, register aliases, native
body bypass, native availability and nearest-ball continuations, live stack words, guest-boundary
state snapshots and variant fallback,
callbacks, >64-bit coalesced listener values, and error cleanup.
The real-drive, family, per-call, lifecycle and timing evidence and resume
commands are in [out/T05](../out/T05/README.md); the accepted sealed-input
baseline remains in [out/T03](../out/T03/README.md). T01/T02 receipts are
historical and stay bound to their original source and artifacts.
