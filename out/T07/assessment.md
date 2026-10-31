# T07: accepted state-v2 sealed-engine compatibility

All required compatibility gates pass. PR #21 / checkpoint #1 hold live merge
and stop/resume status. Current oracle/CI pin is archaeology PR640 merge
`2cbeb36fdd3feb369324aaa88e6e4d2aa3b3d99c`, whose tree equals the full-CI-tested
candidate 7e6f85b2. The old e0270981 clone, state-v1 inputs, receipts and T06 binary
archives are preserved. No Rust/adapter production source or measured extension
changed; there are still twelve default native routine bodies.

## New boundary and inputs

The accepted contract is `original_match.state/2`: changed code-data bytes travel
with the state, and initialised/code-data entries must be integer bytes inside
their declared tables. New sealed checkpoints retain validated tables, including
replay load; extraction writes a manifest alongside ds.hex/code_data.hex.
The loader refuses legacy schema-v1 inputs. Regenerate them from the private
source rather than renaming their schema or silently dropping code-data changes.

Private registered-source extraction produced .cache/T07-tables, whose table
bytes equal the old tables and whose generated manifest loads directly. Fresh
.cache/T07-state-v2-v1.json carries two code-data corrections; table-covered memory
matches the live source exactly. input-audit-v1.json records digests/offsets,
no raw values. All 30 translated routine/helper/machine/dispatcher files are
byte-identical across the oracle update. No original bytes/state/tables are tracked.
Goal2's table-policy exception remains specific to goal2.

## Fresh proof for the unchanged artifact

| Gate | Result |
| --- | --- |
| Public regressions | Three new authored-data tests fail on the old pin, pass on the new. Full 22 tests pass on CPython and PyPy: carried code-data, strict entry types/ranges, legacy refusal, Rust records, retained checkpoint tables and tamper refusal. |
| Upstream checks | Full 12 CI groups pass on the identical candidate tree. All 11 upstream state/table unit tests pass with registered fixture; extraction and read-map checks pass. Earlier optional-fixture skip and stale-origin fetch failure preserved. |
| Legacy seven | 28,448/28,448 equal body/full-frame cases: 500 random plus eight real captures per routine, four tap/listener modes and body/frame variants; dead-stack-byte control caught. |
| Availability tree | 3,224/3,224 equal; body and return controls caught. |
| Nearest-ball tree | 2,128/2,128 equal; body and return controls caught. |
| Effective-skill tree | 6,224/6,224 equal, including 400 overwritten saved-input/base and 144 AX-after-capture cases; body and caller-return controls caught in their expected scopes. |
| Equivalent-v2 ordered drive | All 831 events, result, returned state, full memory, 553 stretches and complete IO/site/listener stream equal. |
| Sealed lifecycle | Engine, interactive save/load, goals and knockout/replay pass under positive original-file/Unicorn denial; 11 independently attested Rust machines. |
| ALL/F40 | Unchanged strict comparators: **ALL 75/75 identical and F40 40/40 identical**, zero failures, original limits. F40 is an exact source-line selection from the one fresh ALL run, with line hashes. Independent attestation accounts for 75 Rust machines. |
| Final audit | validation-v2.json seals raw fresh-v2 comparisons, all controls/corpora, source/binary/private-input bindings, quiet/start records and all 19 canonical producer exits. Every process group empty; pristine oracle/harness and old/new archives verified. |

Total fresh differential comparisons: **40,024 equal** across all 12 bodies and
continuations. Full profile preserves 3,103,685 guest entries: 1,350,794 native,
1,752,891 Python remaining. The profile has 422 non-stub routine addresses,
12 default bodies native. This refresh changes compatibility, not translation
coverage or a whole-port completion percentage.

## Historical result identity: preserved failed assumption and exact proof

Raw fresh-v2 Python/Rust results, memory, records and taps agree without any
normalisation. The first historical diagnostic correctly exposed a changed
result digest. Match._finish includes image_sha256; retaining corrected bytes
changes that input identity as well as full-memory/record/tap hashes.

The isolated historical-result-bridge-v1.json proves that substituting only the
independently reconstructed old image identity reproduces T06's COMPLETE result
digest. No key is omitted, all other result fields and the event sequence match,
and neither canonical fresh-v2 receipts nor historical receipts are modified.

The original frozen validate.py and historical-result-check-v1.log retain the
over-broad direct historical-result assertion. After all writers exited, the
original validator failed exactly on result_sha256 (validator-original-v1.log),
and no validation-v1.json was created. Supplemental post-exit-audit.txt and the
source-hashed validate-v2.txt enforce the exact identity bridge and every original
required fresh-v2 equality/corpus/control/source/binary assertion. The final
ledger is **validation-v2.json**. No Done-when requirement was weakened.

## Quiet simultaneous CPU pair

All correctness jobs ended, three observations had both 1m/5m load below 4, then
all drives started together with default 60-second stretch guards. Raw outputs
and source/input bindings agree across all three backends.

| Backend | CPU seconds |
| --- | ---: |
| Plain CPython | 159.047 |
| Plain PyPy | 79.032 |
| Rust machine / twelve native bodies / CPython bridge | 116.643 |

Rust is **1.364x CPython speed** and uses **1.476x PyPy CPU** in this
pair; it has not beaten PyPy. One pair is not a distribution or a controlled
speed comparison with T06's different-time/input receipts. No speed improvement
is attributed to the schema refresh, source update or cProfile counts.

## Handoff and limits

Old state/input/source/receipt/artifact history stays immutable; reused measured
extensions are also preserved under .cache/T07-artifacts (artifact-archive-v1.json).
The authoritative post-writer index hashes 92 recursive evidence files; both validator
sources and diagnostic failure are retained. Read README.md and checkpoint #1
before any new run/build. Do not restart completed producers or overwrite receipts.

Existing #6 isolation/allocator/coverage limits remain; use separate backend
factory workers. A700 and owner-run engine-milestone review remain later gates,
with ref-121 noncompletion preserved. No later routine tree or automatic model
review started. Most match logic and the surrounding game remain untranslated.
