# T08 common bridge contract and experiment selection

Baseline488b6e6, accepted oracle2cbeb36f, state/2; inputs/binaries from T07
remain preserved. Upstream641 only fixes folder vendoring, no kernel change;
retain the accepted pin for a controlled performance comparison.

The T07 diagnostic has20.3m bounds calls,11.8m u16 reads,9.6m Python register
writes and5.8m core.write_as calls. Authored primitive baseline: word read195ns,
word write497ns; existing direct word read56ns. Candidate primitive:67ns/129ns.
These costs include the call loop and do not predict a whole-drive gain. Pilot
matched all output/state hashes at84.571 baseline vs63.338 candidate CPU seconds
(ratio0.748934). Pilot source/binary/input receipts and failures are preserved;
only three independent confirmation rounds satisfy the performance gate.

## Implemented fast paths

1. Common lowercase register aliases and raw-bank names use static matching;
   Unicode/case normalization and unsupported-name errors retain fallback logic.
2. Python attribute NAME objects are interned; mutable attribute VALUES are
   fetched on every operation. Never cache taps, handlers, spans or stop/error
   state across callbacks. No callback, site, listener or native guest entry is
   removed. Normalization/tap values remain as in the oracle.
3. PortMemory retains the original memory-view helpers, keys and entry stack.
   Exact builtin-int u8/u16 addresses inside the fixed memory image use bound
   Rust reads with range checks; own port reads remain untapped. Non-exact or
   invalid inputs and resized buffers use the original methods, preserving
   operator calls and error messages. Public arbitrary-buffer GuestMemory APIs
   are unchanged. No raw memory slice lives across a Python callback/allocation.
4. write_as keeps original bounds/size validation first. Only exact builtin-int
   address/size/value/site, size1..8 and signed128-bit-convertible values take
   the small-write path. Values mask to the width, including negatives. Owned
   little-endian bytes feed the existing listener-before-write machinery.
   Everything else retains the original arbitrary-precision/operator path.
   Exceptions, listener mutation, dynamic tap installation and >64-bit writes
   remain observed. No write-tap event is invented for write_as.
5. GOAL2RUST_FAST=0 / PortMachine(fast=False) disables new memory/small-write
   paths for ablation; lookup/name improvements remain. Baseline comparison uses
   preserved old adapter/source/binary in .cache/T08-baseline/engine, not that
   ablation flag. Fast usage counters prove measured optimized paths execute.

Public parity covers full state/ordered IO/listeners, reentrant registration,
mutating taps, exceptions before write commitment, aliases/high halves, widths
0..16, negative/huge integers, invalid/custom inputs and resized read buffers.
Existing baseline behavior for unsupported numeric extension types is retained,
without claiming new oracle support or resolving #6. Before tests fail because
the optimized-path API/coverage is absent; all functional parity still required.
Initial build's receiver typo is retained and corrected in v2. No original
bytes/state/tables committed; no guest body or source pin changed.

## Confirmation design

After all fidelity jobs finish and three quiet observations meet1m/5m<4, run
three simultaneous four-arm rounds: preserved Rust baseline, candidate, plain
CPython, plain PyPy. Pin each to a separate physical core (0/2/4/6 primary
threads on this host), exchange baseline/candidate assignments and launch order
in round2; record actual affinity/topology. Keep60-second stretch guards. Every
round must have exact output equality, candidateCPU<baselineCPU and median
ratio<=0.95. Report all samples/PyPy outcomes, no microbenchmark-only speed claim.
No production merge on a failed/rejected performance gate. ALL75 and exact-source
F40, full12-body proofs/controls, ordered taps and sealed lifecycle remain required.
