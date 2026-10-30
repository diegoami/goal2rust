# T02 review #6: negative return-stack delta coverage

This followup resolves only F4's missing `return_stack_delta=-2` synthetic case.
It changes tests, not the production engine or accepted oracle. T03/T04's
contracts and upstream dependencies remain unchanged; all other #6 findings
remain tracked separately.

`engine/tests/test_negative_return_delta.py` runs the pinned oracle's real
`menus.dos_msdos` (`235C:0000`, retf 6, return-stack delta -2) against the Rust
machine. All memory is synthetic: INT 21h's vector targets a synthetic
IRET-like port. The test verifies input registers at that port and its writes
back into the DOS register record. It compares full guest snapshots, ordered
IO/write/site/listener callbacks, call counts, stop/resume visits, suspended
frames and errors. Direct assertions check the final return PC, caller's SP,
record updates and empty frame stacks.

Sixteen cases cover SP 0, 2, 0x100 and 0xFFFE; IO taps off/on; and uninterrupted
versus a stop at the interrupt handler and resume. The shifted far return and
argument cleanup cross the 16-bit stack boundary in the boundary cases.

The negative control changes only the Rust runner's copied entry metadata to
delta 0. It fails to return correctly; the differential and direct completion
assertions therefore detect omission of the delta. `control-v1.json` records
the resulting error and source/extension hashes. This falsifies a machine
mutation; it is not a production defect reproduced before a fix. The existing
implementation already handled the delta, as the owner review stated.

Validation: all eight public machine tests pass on CPython 3.12 and PyPy 3.11
(`tests-cpython-v1.log`, `tests-pypy-v1.log`). The initial PyPy invocation with
`engine/python` on PYTHONPATH selected the local CPython extension package and
failed import; `tests-pypy-path-failure-v1.log` preserves it. Using PyPy's
installed wheel avoids that shadowing; no code, test assertion or limit changed.

```sh
PYTHONHASHSEED=0 PYTHONPATH=engine/python:.cache/goal2-archaeology/runtime \
  .venv/bin/python -B -m unittest discover -s engine/tests -v
PYTHONHASHSEED=0 PYTHONPATH=.cache/goal2-archaeology/runtime \
  .venv-pypy/bin/python -B -m unittest discover -s engine/tests -v
```

No real-image experiment or rebuild is needed for this test-only addition.
The accepted pin remains d3cf46a3; engine source and old proof receipts are
unchanged. Full shifted-DOS behavior against original code and wider IVT paths
are outside this synthetic Rust-versus-port coverage claim.
