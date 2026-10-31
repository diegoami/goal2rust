# T04: first complete native availability call tree

All unchanged T04 Done-when gates pass. PR #15 / checkpoint #1 hold live
merge and stop/resume status. Accepted oracle remains
`e0270981883f02ce46a31391e7070079977bbfef`; T03's historical evidence and
measured binaries remain intact. No original bytes, state or tables are shipped.

## Implementation and choice

The fresh sealed-input profile confirms `0791:2956` (availability of an on-pitch
player) and its only guest callee `1771:3216` as the bounded first tree.
Their 418,459 entries were 18.8% of T03's remaining Python guest entries.
The inventory and exact stack/register/callback contract are in `contract.md`.
Later upstream extraction/checkpoint-table fixes were inspected; they do not
change these bodies. This translation retains T03's validated pin and explicit
tables-after-load contract rather than silently changing its compatibility input.

The caller now has explicit Rust start/return continuation state. It issues an
observable guest call through the existing dispatcher, retaining the callee's
frame, argument and return writes, sites, suspension and ordered callbacks.
The callee reproduces the optimized Python body's signed energy/flag tests,
multiply AH/DX effects and exact retained stack bytes. Nondefault variants
use their original Python bodies. Other callers still hold Python generators;
site/listener callbacks and the rest of the game remain Python.

## Correctness and artifact gates

| Gate | Result |
| --- | --- |
| Public synthetic suite | 14 tests pass on CPython and PyPy; direct body values, completion callbacks, caller/callee variant fallback, stack wrapping, site/listener errors and suspended frames included. 11 Rust tests pass. |
| Real/random/edge differential | 3,224/3,224 equal, eight real captures per routine plus 500 synthetic inputs, full memory/all registers/errors/callbacks, bodies and complete guest frames. |
| Body control | Corrupting the callee's retained result-local byte is caught in all 3,224 comparisons. |
| Caller-return control | Incrementing the saved guest return IP is caught in all 1,096 caller comparisons. Direct callee cases have no guest call and remain equal in this control. |
| Mapping errors | 15 supplemental authored mapping-boundary cases agree on the exception and complete partial state. |
| Ordered sealed drive | All 831 events, result, returned records, full memory, 553 stretches and complete IO/site/listener sequence equal. |
| Sealed lifecycle | Engine, interactive save/load, goals and knockout/replay pass under upstream's positive original-file/Unicorn denial; 11 independently attested Rust machines. |
| F40 | Strict unchanged comparator: 40/40 expected matches identical, zero failures, default limits. Independent attestation accounts for all 40 Rust machines. |
| Final audit | `validation-v1.json` binds every canonical receipt's source/extension hashes and recursive evidence after all 11 producers and the supervisor exited. All producer process groups are empty. |

The ordered stream retains T03's hash
`afcb5ec2ad3800a7d969f8cda6a513577d3e39feff886a441a48cbd814d0f191`:
158,092,780 IO calls, 114,492 listener pairs, 81,134 site pairs, four writes.
Rust records 1,298,963 native entries across nine bodies. Total guest entries
stay 3,103,685; remaining Python entries fall from 2,223,181 to **1,804,722**.
This is an entry-count reduction, not code-completion coverage or exact FFI counts.

`post-exit-audit-v1.json` additionally verifies the 10/20/30-match snapshots
byte-for-byte against the completed family, their line hashes, both archived
binaries and supplemental/public proof receipts. The measured extensions remain
in ignored `.cache/T04-artifacts`, indexed in `artifact-archive-v1.json`.

## Quiet paired performance

All three state-input drives started together after three observations with
both 1m/5m load below four and after every correctness producer finished. Default
60-second CPU-mode stretch guards remain. Outputs and source bindings agree.

| Backend | CPU seconds |
| --- | ---: |
| Plain CPython | 138.220 |
| Plain PyPy | 46.985 |
| Rust machine, nine native bodies, CPython bridge | 98.833 |

Rust is **1.399 times as fast as CPython** and uses **2.104 times
PyPy's CPU** in this pair. It has not beaten PyPy. This is one paired drive,
not a timing distribution or a controlled incremental speed comparison with
T03's different-day receipts. Instrumented profile times establish no speed gain.

## Preserved failures and limits

The failed profile-v1 import-name collision, initial done-registration test-helper
mistake, pause-counter helper mistake and first supplemental SP-fixture setup
error are retained. Helpers were corrected; production equality assertions and
Done-when were not weakened. The baseline's native-entry assertions fail as
expected before translation. Earlier narrower passing differentials remain
historical; v2 is the final full body/frame proof. Raw logs are preserved.

This accepts one subtree. It does not close the later engine milestone's ALL75
and explicit A700 gates, or known A700 ref-121 noncompletion. T03's earlier ALL75
proof is not relabelled as validation of this new artifact. Existing #6 backend
isolation and allocator-audit limits remain; use separate plain/Rust workers.
The refreshed profile is available for the next tree's selection; no later
translation has started and no automatic model review was launched.
