# T16 Player run-step body and inline movement closure

Translate pilot.player_run_step 0791:8889 (ret 2), hottest remaining Python
body after T15: 75,781 starts. Preserve actual T15/main a785f1e source, adapter
and extension before building. Same accepted 2cbeb36f / private T07 state-v2.

M1: the source is a plain function, with inline attack/side/keeper/set/target,
coin/rand and can_move helpers. No guest calls or frame prologue. Never invent
callee frames, register assignments or guest returns. Near argument is the
parent BP; one wrapped parent-frame base and contiguous farptr reads capture a
linear record address. Preserve captured dx/dy/random new-word versus live
record/global pointers, conditional reads, seed and movement writes and retries.
Variants use Python. No separately registered 86D0 or hardware claim.

M2: eight actual RAM entries plus 500 authored cases/four tap-listener modes;
full memory/all registers/ordered observers/errors/direct completion/entry pause/
variants agree. Positive coverage of all 13 write sites: offside target, five
initial direction sites, move reset/four steps, random retry and seed. Exercise
all skip/clamp/state/keeper gates, both coin choices and axis branches, every
movement acceptance/rejection (pitch, play, holders, position code, picture
attribute/blocking set), retries including direction five, signed/wrapping and
linear crossings, captured frame/record/deltas/random value versus live content
mutations. No loop cap added to production. Body mutant24 flips dead stack and
position mutant25 corrupts final position: both caught in every positive case.
There is no guest-return control because this source body has no guest calls.
An additional 160 source-line/return traces require every offside skip and
movement acceptance/rejection branch, including both holders, to be reached;
each traced source run also agrees with native. Tracing changes no source bytes
and is excluded from timings. Individually reached injected failures must agree; no unexpected-failure credit.

M3: public CPython/PyPy/Rust/GC, fresh existing22-body/control/error/observer
corpus, exact ordered full drive, positive-denial sealed lifecycle/backend
attestation, strict ALL75/exact-source F40, full profile, closed artifact/source/
input/evidence ledger, actual-host empty groups and three quiet rotated four-arm
rounds against saved T15/plain CPython/PyPy. Preserve and report every outcome,
including regressions; no arbitrary performance floor. Exact-head CI before
squash, main CI/checkpoint before wind-down. Freeze bound sources/binaries/inputs
during runs; never overwrite completed receipts. No original game data committed
or automatic model review. Engine milestone/A700/ref-121/#6/adoption separate.
