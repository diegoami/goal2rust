# T02 review #6 F2: shared slice during bytes construction

Investigated 2026-10-30. Outcome: no reentrancy defect demonstrated, and the
normal paths inspected do not substantiate the proposed automatic user-finalizer
callback during this copy. This is a source audit of specific implementations,
not a general safety guarantee for every interpreter, allocator or build.
No production change or old-evidence reinterpretation follows from this audit.

## The actual call

`MachineCore::bytes` borrows the shared bytearray, checks the range and calls
`PyBytes::new` with a subslice. The locked PyO3 0.30.1 implementation directly
calls `PyBytes_FromStringAndSize` with the borrowed pointer and length. The
borrow therefore spans that C-API call. PyO3's bytearray safety contract requires
avoiding interpreter operations that could mutate the buffer during the borrow;
the GIL alone does not establish that condition.

Sources: [PyO3 bytes construction](https://github.com/PyO3/pyo3/blob/v0.30.1/src/types/bytes.rs),
[PyO3 bytearray contract](https://github.com/PyO3/pyo3/blob/v0.30.1/src/types/bytearray.rs).
The installed Cargo registry sources for exactly 0.30.1 were inspected too.

## CPython 3.12.15

For a nonempty input of length greater than one, `PyBytes_FromStringAndSize`
calls `_PyBytes_FromSize`, which uses `PyObject_Malloc` and initializes the
bytes object; the constructor then copies the input with `memcpy`. Zero/one
byte cases use cached bytes. This is not the tracked-object allocation path
that triggers cyclic GC. No Python callback appears in this normal successful
construction path. That observation does not establish a contract for arbitrary
custom allocator hooks, other Python versions or all failure paths.

Source: [CPython v3.12.15 bytesobject.c](https://github.com/python/cpython/blob/v3.12.15/Objects/bytesobject.c#L72).
The local interpreter reports CPython 3.12.15; its distributor's complete build
and allocator configuration were not independently audited.

## PyPy 8.0.0 / Python 3.11

The local interpreter reports Python 3.11.16, PyPy 8.0.0, revision
`78565394c9b5`. Inspected upstream release tag `release-pypy3.11-v8.0.0`,
Git mirror commit `4389fd309cd02fe42f458fa5d624aa1bc36a9570`. This identifies
the release source examined; it is not a bit-for-bit attestation of the installed
binary or a proof that its reported Mercurial revision maps to this Git commit.

Its C-API constructor converts the supplied pointer into an RPython string,
then constructs and references the Python bytes object. The string conversion
allocates before copying, so allocation exists while the borrowed pointer is
live. However, allocation alone does not show arbitrary Python execution.

Sources: [bytesobject.py](https://github.com/pypy/pypy/blob/4389fd309cd02fe42f458fa5d624aa1bc36a9570/pypy/module/cpyext/bytesobject.py#L127),
[rffi.charpsize2str](https://github.com/pypy/pypy/blob/4389fd309cd02fe42f458fa5d624aa1bc36a9570/rpython/rtyper/lltypesystem/rffi.py#L1051).

The ordinary user-finalizer queue schedules `UserDelAction`; it does not directly
fetch or finalize objects during the GC trigger. The queue's implementation
explicitly places that processing between bytecodes. The inspected C-API wrapper
does not dispatch that action around this constructor. This argues against the
review's specific ordinary-finalizer scenario on these source paths; it is an
inference from the implementations, not a reproduced failure or universal proof.

Sources: [finalizer queue](https://github.com/pypy/pypy/blob/4389fd309cd02fe42f458fa5d624aa1bc36a9570/pypy/interpreter/executioncontext.py#L720),
[C-API wrapper](https://github.com/pypy/pypy/blob/4389fd309cd02fe42f458fa5d624aa1bc36a9570/pypy/module/cpyext/api.py#L1071).

## Disposition

F2 remains recorded as a potential soundness question without a demonstrated
defect. Do not claim bytes allocation inevitably runs a mutating finalizer.
The existing match evidence remains valid within its stated coverage.

If this borrow becomes harder to justify under a supported interpreter change,
the bounded alternative is to copy just the requested range into Rust-owned
storage, end the bytearray borrow, then allocate Python bytes from that copy.
That removes this borrowed-input window at the cost of another copy. Such a
production change needs the normal fresh artifact-bound correctness and timing
proofs; this documentation task makes none. It also does not audit other unsafe
sites, free-threaded execution, adversarial allocator hooks or asynchronous
extension behavior. No new engine safety contract is declared here.
