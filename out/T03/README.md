# T03 accepted sealed-engine validation

## Validation complete, 2026-10-31

All local gates and the post-exit audit pass; see
[assessment.md](assessment.md) for results and limits. The authoritative stable
index is `validation-v2.json`; its earlier pre-final-banner snapshot is retained.
No producer or child process remains active. Final PR-head CI and merge status
are tracked on PR #14 / checkpoint issue #1. Owner requested wind-down after
T03; T04 has not begun. Do not restart completed v1 producers.

The plan and in-progress resume procedure below are retained for provenance.
A new build needs fresh versioned receipts and source/artifact bindings; the
historical resume command is not a command to rerun this completed validation.

To verify the stable index without rerunning private experiments:

```sh
PYTHONHASHSEED=0 PYTHONPATH=out/T03 .venv/bin/python -B - <<'PY'
import hashlib, json
from pathlib import Path
root = Path.cwd()
evidence = root / 'out/T03'
report = json.loads((evidence / 'validation-v2.json').read_text())
assert report['pass_all'] and report['all_writers_finished']
for name, sha in report['evidence_sha256'].items():
    assert hashlib.sha256((evidence / name).read_bytes()).hexdigest() == sha, name
for name, sha in report['source_sha256'].items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == sha, name
print('T03 final evidence and source hashes match')
PY
```

This verifies the measured checkout/artifact. A later source or extension rebuild
will intentionally fail those source bindings; use the recorded revision and
archived binaries when inspecting historical evidence.

Contract: `docs/tasks/T03.md`, issue #8 and `docs/roadmap.md`'s three unchanged
Done-when gates. Oracle: accepted handover merge
`e0270981883f02ce46a31391e7070079977bbfef`; upstream #627/#628 merged with
passing checks. Old T02 oracle remains in `.cache/goal2-archaeology-T02` at
d3cf46a3. Old receipts are untouched; no production routine has changed.

## M1: pin and public contract

`input-audit-v1.json` records the old/new source audit, verified private input
digest and locally extracted table digests. Seven audited source files
(machine, port engine/guest/runtime, geometry, entrypoints and attributes) are
unchanged. CI and PROVENANCE.md now select the accepted sealed commit; routine
translation-origin pins remain historical.

The owner-supplied registered executable was read locally by upstream's
`port_tables.py extract`. Its output and manifest remain in ignored
`.cache/T03-tables`; state is `.cache/T03-state-v1.json`. The reference and both
finals source images are hash-verified in the oracle's private `.cache/dl`.
The connected Drive search did not find the private finals fixture; the exact
`goal2drive:` path in the pinned delivery metadata supplied it via configured
rclone. No private bytes, state, tables or saves enter tracked output.

Public `test_sealed_api.py` uses authored synthetic tables/memory only. It tests
invalid schema/table binding/module bytes, records output through Rust, and
checkpoint roundtrip with explicit tables after load. `public-before-v2.log`
shows the final test failing against the old oracle's missing tables API.
All ten tests pass on CPython (`public-cpython-v2.log`) and PyPy
(`public-pypy-v1.log`); Rust tests pass (`cargo-v1.log`). The first CPython run
(`public-cpython-v1.log`) exposed a missing sys import in the new test helper;
that helper was corrected, and the failure log is retained.

## Fresh private proofs (append-only)

`supervise.py` runs these stages, keeping exclusive receipt names, append-only
family/status output, source/extension manifests and original limits:

1. `run_family.py`: ALL's 75 matches from state/tables under the unchanged
   family runner, two workers and original time/stretch limits. Inputs retain
   the harness's verified source binding. No A700 is folded into ALL.
2. `run_check.py`: upstream engine, interactive save/load, goals and knockout
   checks from state/tables, under upstream's positive Unicorn/import and
   original-file-open denial. `sitecustomize.py` independently records Rust
   machines and native counts for lifecycle and family processes, without
   editing the oracle or comparison schema.
3. Reuse T02's full body/frame differential, 500 random + four real captures per
   routine, four tap/listener modes. Test body mutant 1 (missing dead stack byte)
   and the guest-return IP mutant. Raw mutation differences stay in ignored
   cache; tracked differences contain hashes rather than raw values.
4. State-input plain/Rust ordered drive receipts, including full memory,
   records output, events/result and complete ordered taps. Instrumentation
   alone uses upstream T117's lifted guard; CPU drives keep the 60-second guard.
5. Select F40's 40 source lines byte-for-byte from the fresh ALL output, record
   source line hashes, and run both unchanged comparators. One fresh ALL run
   supplies both required corpus gates; F40 is not rerun redundantly.
6. After producers finish and three observations have both 1m/5m load below 4,
   start plain CPython, plain PyPy and Rust CPU drives together. Keep all
   failures; never raise limits or bypass artifact/source assertions.
7. `finish.py final`: require all proof/control/comparison gates, rehash source
   manifests, compare receipts and bind the evidence in `validation-v1.json`.

## Historical in-progress resume procedure

Read the latest checkpoint on issue #1 before any command. `jobs-v1.jsonl`
records producer PIDs, commands and exits; `supervisor-v1.log` is append-only.
Check for live supervisor/producer processes before starting anything. The
supervisor holds `.cache/T03-supervisor.lock`, but an exited supervisor can
leave child process groups running: do not duplicate those.

For an interrupted, incomplete candidate only: if no existing job is active,
completed stages have valid manifests, and no
failed/partial receipt needs disposition, resume:

```sh
PYTHONHASHSEED=0 .venv/bin/python -u -B out/T03/supervise.py \
  >> out/T03/supervisor-v1.log 2>&1
```

The family command itself resumes missing IDs from its append-only JSONL; use
a fresh attestation-folder name for a separate invocation, retain all prior
receipts, and update the evidence ledger transparently. On any failure, stop
and inspect it; choose fresh versioned outputs for a new attempt, never delete
or rewrite a failed record or relax a required assertion. Do not edit producers
while evidence is running: their complete source set is hash-bound.

Status and completion live in GitHub, not this plan. M1 does not complete T03;
the full three-gate assessment and exact final-head CI still precede merge.
T04 remains after T03. No automatic model review is launched.
