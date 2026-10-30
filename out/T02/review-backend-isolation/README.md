# T02 review #6 F1: supported backend isolation

The roadmap already chooses separate processes for Python/Rust comparisons.
`engine/README.md` now states that supported contract explicitly: install once
per Rust worker, keep the plain port in fresh workers, and identify the actual
backend in evidence. Same-process coexistence and uninstallation are unsupported;
the existing demonstrated limitation is not claimed fixed.

`test_backend_processes.py` starts three child processes with the current
interpreter: plain, Rust, then plain again. They construct through the kit's
factory and install its real geometry/entrypoint registries, execute a real
native routine on synthetic memory and return only outcome hashes/registers
and backend identity. The test checks:

- both plain workers are identical, with the oracle machine and no native calls;
- Rust selects its machine and records exactly one native 0791:2BE5 entry;
- full-memory digest, registers, ordered IO/write callback digest, guest entry
  counts, final return PC and SP agree between backends;
- the parent process's factory and runner objects remain unchanged.

All nine public tests pass on CPython and PyPy. The CPython transcript is
`tests-cpython-v1.log`. The PyPy result (9 tests, 2.171 seconds, OK) was observed
directly in the tool output; no separate PyPy log file was produced here.

```sh
PYTHONHASHSEED=0 PYTHONPATH=engine/python:.cache/goal2-archaeology/runtime \
  .venv/bin/python -B -m unittest discover -s engine/tests -v
PYTHONHASHSEED=0 PYTHONPATH=.cache/goal2-archaeology/runtime \
  .venv-pypy/bin/python -B -m unittest discover -s engine/tests -v
```

No production source, oracle pin or old proof receipt changed. This is one
synthetic routine per worker, not a new match/family fidelity result. Real
isolated state-input drive/replay preparation is in `out/roadmap/`; T03 still
requires its full accepted-pin gates. Old lifecycle/F40 receipts were not
retroactively given backend markers.
