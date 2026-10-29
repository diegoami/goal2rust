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
For oracle harnesses, call `goal2rust.install()` in the test process before
constructing/loading a kit match with `engine="port"`. This changes the factory
only in that process. It does not edit the oracle or change its default backend.

The machine owns the register bank and shared guest memory. Unported Python
bodies use the same state through the bridge. T01's seven bodies execute directly
in Rust; no other subtree has been translated. Site and write listeners remain
kit callbacks, with their original ordered taps and error/stop semantics.

Local checks that need no private image:

```sh
cargo test --locked --manifest-path engine/Cargo.toml
PYTHONHASHSEED=0 PYTHONPATH=.cache/goal2-archaeology/runtime \
  .venv/bin/python -B -m unittest discover -s engine/tests -v
```

The public synthetic differential covers frames and recursion, near/far calls,
caller/callee argument cleanup, wraparound, stop/replay, register aliases, native
body bypass, callbacks, >64-bit coalesced listener values, and error cleanup.
The real-drive, family, per-call, lifecycle and timing evidence and resume
commands are in `../out/T02/README.md`.
