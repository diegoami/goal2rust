# T24 keyboard-service chunk

Status: all T24 fidelity, selected quiet-measurement and final post-writer
ledger gates pass. Performance regresses at the paired median: 1.00% more CPU
than saved T23, with one faster and two slower rounds. Exact-head CI, merge,
main CI and merged-audit status remain in checkpoint #1. Pause after completion;
no next task is included.

## Translation and semantics

At accepted oracle `2cbeb36fdd3feb369324aaa88e6e4d2aa3b3d99c`, the complete
chunk translates `menus.key_pressed` (214B:0723), `read_key` (214B:08DD),
`wait_key_clear` (214B:0983) and `push_back_key` (214B:0993), together with
all nine inventoried body/helper function code objects. The wait caller retains
its real read-key guest call and far return 214B:098A. Nondefault variants
remain Python. Generic memory-view key, read and stop primitives remain explicit
kit callbacks. No BIOS frame or automatic-answer policy is added.

The native dispatcher uses the actual per-port memory view, preserving its kit
callbacks. Return-site formatting reads the CS word through live SS first,
observes the current load, then reads IP through SS again. The subtraction keeps
the generic Python operator fallback for large/custom loads. Poll truth conversion
finishes before the live AX read. Unpushed read keeps its no-frame callback path,
including ignored provider return values and existing nondeferrable-stop checks.

Pushed read clears its flag before pending prologue writes flush; push-back sets
its flag before the cached frame flush and then reads its argument through live
SS. The wait caller stores before the actual guest suspension, resumes with
fresh Regs, ignores SENT and clears the key before the live leave/store sequence.
All source callback, register, frame and write ordering is retained.

## Comparator, capture and artifact preservation

Before builds, accepted T23's 731 primary bindings, 263 evidence hashes, two
additive sources and five supplementary inputs were verified. Actual T23 source,
tests, adapter and both interpreter artifacts are preserved in
`.cache/T24-baseline` (73 files). Historical `.cache/T23-baseline` is T22.
Both final interpreter builds/installs and all 88 public tests per interpreter
completed before the candidate binary archive. The canonical freeze binds 852
concrete source/input/binary files, including 59 explicit proof/audit sources.
Generated reports are excluded from that source allowlist.

The first genuine capture failed under external load at the unchanged dispatch
guard; its log, 747 input bindings and original harness snapshot remain.
The second worker was superseded while idle, having collected zero entries or
shards. Accepted v3 captures contain eight actual source entries per body in 32
private shards, obtained from eight genuine Match-drive prefixes with the same
source and guard. The completed journal and both predecessor attempts remain
immutable. No entry packet was fabricated.

The capture input manifest's historical `out/T24/evidence.py` maps only to its
exact archived version in `.cache/T24-capture-v2-source/evidence.py`; canonical
evidence bindings were extended after capture exited. The other 46 capture
inputs remain unchanged. Private state, tables, binaries and entry memory stay
in ignored cache; no original game bytes enter git.

## Completed per-body evidence

| Proof | Result |
| --- | ---: |
| Fresh prior 59 normal comparisons | 170,600 |
| New four normal comparisons | 10,384 |
| Combined normal comparisons | 180,984 |
| Real-state schedules: 4 × 8 × 4 × 3 | 384 |
| New body controls 185–188 | 8,384 |
| AX/EFLAGS output controls 189–196 | 16,768; 2,096 each |
| Guest-return control 197 at 214B:098A | 160 |
| Positive source branch pairs | 800 |
| New error comparisons | 12,320 |
| Error execution rows / distinct reached selectors | 77 / 77 |
| Nondefault variants | 64 |
| All-inventory scoped closure | 8,384 |
| Live callback matrices | Eight; 1,280 each |
| Public CPython / PyPy | 88 / 88 tests |
| Rust / GC / supplemental observer | 11 / 20 / 328 |

All nine owned function code objects are tracked from the first scoped probe,
with positive source/outside/nondefault witnesses and zero owned Python calls
inside native default lifetimes. Prior controls, error selectors, source branches,
variants and helper-closure assertions remain intact, including T19 scoped-write
errors, all T22 shared signed helpers and all seven T23 string helpers.

The new callback matrix positively witnesses poll truth/live AH, two separate
live SS reads, ignored read-provider values, pushed live key/AH, push flag before
cached flush/live SS, cached push AH, ignored wait SENT and stop refusal. These
are bounded semantic proofs, not a global branch or error coverage percentage.

## Complete ordered drive

The fresh Python and Rust drives match exactly: 831 events, 553 stretches,
result, records and full memory. The ordered observer counts match 158,092,780
IO, 114,492 listener enters/leaves, 81,134 site enters/leaves and four writes;
digest `096f56c262844705a0fcf7348fa4563c40e7d3ff4554b05c5224ffb0a7080ea9`.
The Rust drive reports 63 native bodies and 2,688,294 native entries.
Its instrumented CPU time is not a performance measurement.

The fresh full profile confirms 63 of 422 registered nonstub bodies (14.93% by
equal-weight count), 2,688,294 native and 415,391 Python entries out of
3,103,685 total: 86.61619978% native fixture entry frequency. The chunk moved
78,172 entries. The largest remaining Python-entry roots are handle_player_at_ball
(57,791), energy_chance_branch and offside_call (36,198 each),
pass_receiver_destination (35,723) and challenge_duel (35,193). These are
selection inputs for a future bounded-tree inventory, not a new task or CPU
speed forecast.

## Complete family and lifecycle evidence

All four sealed lifecycle gates (engine, interactive, goals and knockout) pass,
with 11 independently attested Rust machines and all 63 native bodies. All 75
admitted corpus records complete without errors and stop at the board. Strict
ALL and exact-source F40 comparisons pass. Immutable 10/20/30/60 snapshots and
strict prefix comparisons pass. Independent family attestation verifies 75 Rust
machines and all 63 native bodies. The full remaining-work profile also passes.

## Rejected complete original timing campaign (v1)

The first round began quiet, but external Python/PyPy workloads raised host load
during the round. Both arm-endpoint and continuous-load quality failed. All
three original four-arm rounds were completed and retained; the controller
waited for quiet IT13 before rounds two and three. The ENTIRE campaign is
rejected. Its two later quiet rounds are not substituted into the replacement.
No source, binary or private input changed and no unrelated workload was stopped.

| Round | Saved T23 CPU s | T24 CPU s | CPython CPU s | PyPy CPU s |
| --- | ---: | ---: | ---: | ---: |
| 1 | 35.909797661 | 32.785316048 | 186.057436747 | 51.386064621 |
| 2 | 30.765450059 | 31.166074222 | 129.378189844 | 49.739462714 |
| 3 | 30.480623093 | 31.272495679 | 130.018198894 | 47.488113206 |

| Round | Saved T23 / PyPy | T24 / PyPy | T24 / saved T23 | CPython / T24 |
| --- | ---: | ---: | ---: | ---: |
| 1 | 0.698823658 | 0.638019593 | 0.912990832 | 5.675023430 |
| 2 | 0.618532014 | 0.626586467 | 1.013021885 | 4.151250777 |
| 3 | 0.641857952 | 0.658533127 | 1.025979541 | 4.157589475 |
| Median of per-round ratios | 0.641857952 | 0.638019593 | 1.013021885 | 4.157589475 |

## Selected complete quiet replacement (v2)

All three simultaneous four-arm rounds were repeated on the SAME artifact and
saved T23 baseline, with physical-core/launch rotation and the original guards.
Every round passed three original quiet-start observations (max 1/5-minute
load below four), every arm's start/end load below four, and continuous
five-second total-load samples below eight. All outputs match the reference.
No selected arm or round was replaced. Both entire campaigns remain preserved.

| Round | Saved T23 CPU s | T24 CPU s | CPython CPU s | PyPy CPU s |
| --- | ---: | ---: | ---: | ---: |
| 1 | 30.655384892 | 30.195592424 | 126.967437340 | 45.495853187 |
| 2 | 30.280935934 | 30.583378480 | 127.748549712 | 48.588393908 |
| 3 | 31.181017620 | 31.977246327 | 134.051095199 | 52.556705998 |

| Round | Saved T23 / PyPy | T24 / PyPy | T24 / saved T23 | CPython / T24 |
| --- | ---: | ---: | ---: | ---: |
| 1 | 0.673806133 | 0.663699883 | 0.985001250 | 4.204833459 |
| 2 | 0.623213354 | 0.629437938 | 1.009987886 | 4.177058130 |
| 3 | 0.593283331 | 0.608433229 | 1.025535687 | 4.192077511 |
| Median of per-round ratios | 0.623213354 | 0.629437938 | 1.009987886 | 4.192077511 |

The paired median T24/T23 ratio is 1.009987886328: **1.00% more CPU**.
Round one uses 1.50% less; rounds two and three use 1.00% and 2.55% more,
respectively. This is a mixed outcome with a median regression, not an established
speed improvement. The predeclared incremental translation criteria require
fidelity and complete measurements, with no positive magnitude threshold or
all-round speed-improvement gate. No such criterion was changed after results.

Same-campaign saved T23/PyPy median is 0.623213354 (37.68% less CPU), while
T24/PyPy is 0.629437938 (37.06% less). CPython/T24 median CPU-speed ratio is
4.192077511. Each median is computed independently from its per-round column.
Do not divide independent medians or infer a regression trend from historical
standalone PyPy comparisons. This remains one-fixture performance evidence.

## Final ledger and process closure

All post-writer audits pass. validation-final-v1 binds 852 primary files and
281 evidence hashes. The unchanged 59-source canonical proof allowlist remains.
An additive profile-reference audit, sealed before execution, binds one source
and four immutable input receipts. The canonical profile's older T21 comparison
receipt was not directly enumerated among primary inputs; the audit verifies its
identity against accepted T21 evidence and accepted main's tree, then verifies
all profile observations/native counts against fresh T24 Python/Rust receipts.
The supplemental manifest and positive audit receipt are bound by the final
ledger, and their source/input hashes are required by the merged audit.

The capture audit independently verifies all 47 historical capture inputs, the
exact archived evidence.py mapping, all 32 genuine shards/bundle/journal, failed
v1's 747 input bindings and the empty superseded v2 attempt. All three historical
capture PIDs have exited. The baseline/input audit preserves all 731 accepted
T23 primary bindings, 263 evidence hashes, its two additive sources/five inputs,
older supplemental proofs, all historical profiles and the three before/after
new-native-presence witnesses. Actual saved T23 baseline contains 73 files.

All 87 canonical and 24 timing producer groups have exited: **111 groups**, plus
the exclusive controller and three capture PIDs. Shutdown checks use the actual
host PID namespace. The merged audit also verifies all 38 historical/current
artifact-archive bindings, exact checked/merged tree identity and green main CI.
Exact-head CI/merge/main-CI/merged-audit status remains in checkpoint #1/PR #57.

The owner requested a pause after this task finishes. No T25 is selected or
started; future scope must come from the fresh profile and a complete bounded
call-tree inventory.

## Limits

Fixture entry frequency, body count and proof-case counts do not establish
source-line coverage, CPU-time coverage, global test coverage or whole-port
completion. The hybrid still invokes Python and retains interpreter/GIL state.
Engine A700/ref-121 and the owner-run milestone review, issue 6, application pipe,
GIL/threading, target ABI/loading, save/load, cancellation and playtest gates
remain separate. Upstream's new first-key-poll decision concerns the separate
whole-game news harness; it does not change the pinned match-engine boundary.

The final-phase upstream check found goal2 `e44a66fe` and archaeology `82984287`:
new whole-season T170 requires T123 and the newly identified T124 round-end
stage builders/news. T119 is now split into harness and recorded-run tasks.
These commits add plans/static evidence and UI work; the selected runtime port
is unchanged. The broader roadmap now includes these missing dependencies,
while T24's frozen artifact and accepted oracle remain fixed.
