# T02 evidence and experiment continuation

## IT13 continuation, 2026-10-29

The owner resumed T02 on IT13 at `64e1033`. The pinned oracle and verified
reference image are now provisioned in the ignored cache. Rust and PyPy are
project-local too; see `host2-environment-v1.json` for versions and the rebuilt
CPython extension digest. Production sources are unchanged.

Fresh `host2-v1` proofs: 11 Rust tests, six synthetic tests on each interpreter,
the CPython installed-wheel tests, 28,224/28,224 per-call/body/frame comparisons,
and the caught guest-return-IP mutant. The native ordered-tap drive is now equal
on every required field, including the complete ordered tap hash and exactly
880,504 native calls across the seven permitted addresses (`taps-rust-host2-v1.json`,
`compare-rust-host2-v1.log`). The fresh kit lifecycle suite has also passed all
four checks: engine, interactive save/load, goals and knockout replay
(`check-rust-host2-v1.json`); its producer (tool session 58762) finished normally.

The first F40 attempt on IT13 preserves two complete timeout records in
`family-F40-rust-host2-v1.jsonl`: `F40/e032-0101` (300.206 CPU / 300.349 wall s)
and `F40/e032-1234` (300.065 CPU / 300.179 wall s). Host load was about 15;
the workers each received approximately a full CPU core. The family process
group was verified and stopped after these failures. No other family match
completed, and no timing receipt has started. A quiet-host retry must use a new
append-only filename and the unchanged limits; these failures stay as evidence.
T02 remains incomplete and PR #5 remains draft.

The owner selected waiting for IT13 to become quiet. The continuation supervisor
is `continue_host2_v1.py` (current tool session 37276; append-only
`continue-host2-v1.log`). It verifies the fresh native artifact hashes, waits for
three load observations below 4, runs all 40 matches into the new
`family-F40-rust-host2-v2.jsonl`, compares them with the unchanged oracle, waits
for the existing lifecycle producer, and runs the artifact-aware ledger. Only
after those gates and another quiet wait does it run the three paired timings.
It stops on any failure; no limit/assertion is relaxed. Do not start a duplicate
supervisor. If it stops, inspect the outputs and active processes before resuming
the same command:
`.venv/bin/python -u -B out/T02/continue_host2_v1.py >> out/T02/continue-host2-v1.log 2>&1`.

At 19:16 UTC the host load rose above 13 again. The verified family/supervisor
process group (199482) was stopped with **16 complete v2 records and no runner
errors**; no group members remained. `host2-interruptions-v1.jsonl` records the
stop. The lifecycle producer was left running and subsequently passed. The new supervisor above is
waiting for quiet, then resumes the same append-only v2 file's missing matches;
there is no failed v2 record to replace. Previous tool session 26456 is stopped.

At 19:39 UTC another sustained load increase caused a second verified family
stop (group 207048), before the unchanged timeout. **22 complete v2 records, no
runner errors**, remain intact. Old supervisor session 87377 is stopped; the
current session 37276 above waits for quiet before resuming missing matches.
The second stop is recorded in the same append-only interruptions file.

Toolchain commands on IT13 need
`CARGO_HOME="$PWD/.cache/cargo" RUSTUP_HOME="$PWD/.cache/rustup"`
and `$PWD/.cache/cargo/bin` on `PATH`. The PyPy environment is `.venv-pypy`.

## Previous computer's handover (historical)

**Owner wind-down, 2026-10-29:** all T02 experiment processes on this computer
are stopped, including the recovery process group. The owner will start the
experiments from another computer. Do not auto-restart experiments here or start
T03. PR [#5](https://github.com/diegoami/goal2rust/pull/5) is draft; **T02 is not
done**. Recheck its live head/CI and the latest comment on checkpoint issue #1.

## New-session prompt

> Resume goal2rust T02 on branch `task/T02-machine`; fetch its latest pushed head.
> Read `AGENTS.md`, `CLAUDE.md`, `docs/tasks/T02.md`, and `out/T02/README.md`, then
> recheck PR #5 and checkpoint issue #1. Experiments on the previous computer are
> stopped. Follow the cross-computer instructions: preserve existing evidence and
> hash assertions, rebuild and validate the artifact, complete F40 40/40 and paired
> CPython/PyPy/Rust CPU receipts on a quiet machine. Keep the Done-when unchanged;
> do not start T03.

## What is proved

The oracle is pristine at `d3cf46a3e87f0ba04916867b5b231c4646a0c2bd`.
The production code and this computer's CPython extension still hash exactly as
in `taps-rust-v1.json`.

| Gate | Evidence |
| --- | --- |
| All bodies bridged, ordered straight drive equal | `taps-bridge-v1.json`, `compare-bridge-v1.log` |
| Seven T01 bodies native, ordered straight drive equal | `taps-rust-v1.json`, `compare-rust-v1.log`; exactly 880,504 native calls across exactly seven addresses |
| Per-call/body/full-frame differential | `differential-v2.json`: 28,224/28,224 equal; 500 random and four captured real inputs per routine, four tap/listener modes, body and whole-frame execution |
| Machine mutant caught | `mutant-v2.json`: pushed guest-call return IP incremented; the synthetic machine differential catches `PortError: no registered port/return at 0791:0111` |
| Kit engine and lifecycle | `check-rust-v1.json`: engine, interactive save/load, goals, knockout all pass; straight/resumed/expected digests agree, including extra time and shootout-order replay |
| Synthetic tests and installed wheels | `tests-v3.log`, `wheel-tests-v3.log`, `wheel-tests-pypy-v3.log`: six tests pass on CPython 3.12 / PyPy 3.11; includes 144 call combinations, recursion sharing a return address, stop/replay, callback reentrancy/errors, native bypass and wide listener values |
| Next-subtree proposal | `next-subtrees.md`, `profile-subtrees-v2.json` (planning only) |

The wide-stack listener differential initially failed (`differential-v1.json`).
Rust had truncated a coalesced write's listener value to u64 for runs longer than
eight bytes. Memory remained equal. The corrected host constructs the integer
from the entire run. Keep this stronger full-stack coverage and the failing
receipt; full memory alone would not have exposed that observable error.
`tests-before-v1.log` records the new machine tests failing before implementation.

## What remains

1. F40 must be `compare.py --family F40 --no-screen` identical **40/40**.
2. `cpu-{python,pypy-python,rust}-v1.json` must run together on one quiet machine,
   with source/extension hashes. None of these CPU receipts has started.
3. Publish the final evidence/timing assessment, finalize the profile-based plan,
   and pass CI on the exact final PR head. Follow CLAUDE.md's review/merge rules;
   do not start another task. The Done-when in `docs/tasks/T02.md` is unchanged.

## F40 interruption: preserve the failure

`family-F40-rust-v1.jsonl` has **34 complete lines: 33 completed matches and one
TimeLimit** (`F40/edit-3a5c`, 300.189 CPU / 300.202 wall s). Host load had risen to
about 16 with only our two family workers active. The runner and verified workers
were stopped; no partial JSON line was left. The old final supervisor correctly
refused this error (`finish-v1.log`). No semantic difference has been established;
the completed matches have not yet had their final full-family comparison.

When load fell, recovery launched the seven failed/missing IDs, but the owner
then requested this handover. It was stopped before producing any match record.
There is **no** rerun JSONL yet. `recovery-attempts-v1.jsonl` and the rerun/recovery
logs preserve its launch and interruption. No experiment process remains active.
Old tool sessions 17713/57926 stopped, 33178 finished successfully, and 81157 was
interrupted and terminated its child process group. These session IDs are history,
not commands to resume on the next computer.

For the **same built artifact**, `recover_quiet_v1.py` implements T01's accepted
recovery pattern: wait for three quiet observations, rerun only the failed/six
missing IDs under the unchanged default limits, assemble the 33 completed v1 lines
and seven rerun lines byte-for-byte into v2, then require all 40 to compare equal.
`assembly-v2.json` would record every source line and digest. The failed v1 record
stays in git. Do not increase limits, omit a match or replace a completed match
because its comparison differs.

## Starting on the other computer

Read `CLAUDE.md`, `AGENTS.md`, `docs/tasks/T02.md`, this file, and the live PR/#1
checkpoint. Check out `task/T02-machine` and fetch its latest pushed head.
Prerequisites are Rust, CPython 3.12, PyPy 3.11, and the pinned oracle clone. Verify:

```sh
git -C .cache/goal2-archaeology rev-parse HEAD
# must be d3cf46a3e87f0ba04916867b5b231c4646a0c2bd
```

If the clone is absent, obtain goal2-archaeology and check out that exact commit.
Provision the owner's reference image privately under its `.cache/dl`, as
`original_match.assets.reference_image` expects. Images/checkpoints are never in
git. Do not amend the oracle to load Rust; the process-local adapter does that.
Build the extension as in `engine/README.md`. Build/install the PyPy wheel too,
since the paired producer fingerprints its interpreter's installed extension:

```sh
pypy3.11 -m venv .venv-pypy
CARGO_TARGET_DIR=/tmp/goal2rust-T02-target-pypy .venv/bin/maturin build \
  --release --locked --manifest-path engine/Cargo.toml \
  -i .venv-pypy/bin/python -o /tmp/goal2rust-T02-wheels-pypy
.venv-pypy/bin/pip install --no-index --force-reinstall /tmp/goal2rust-T02-wheels-pypy/*.whl
```

**A rebuild may change the extension digest. Do not bypass the old artifact hash
assertion.** Give the new build fresh proof receipts and run a fresh full F40 for
that artifact, retaining this computer's receipts as evidence. The commands below
use the new `host2-v1` names; refuse/choose another version if any output exists.
Run them from the repository root, on a quiet machine. Long family output is
append-only; repeat its command to resume after verifying no old runner is active.

```sh
export PYTHONHASHSEED=0
export PYTHONPATH="$PWD/engine/python:$PWD/.cache/goal2-archaeology/runtime"
.venv/bin/python -B -m unittest discover -s engine/tests -v > out/T02/tests-host2-v1.log 2>&1
.venv/bin/python -B out/T02/differential_v1.py --trials 500 --out out/T02/differential-host2-v1.json > out/T02/differential-host2-v1.log 2>&1
.venv/bin/python -B out/T02/mutant_v1.py out/T02/mutant-host2-v1.json > out/T02/mutant-host2-v1.log 2>&1
.venv/bin/python -B out/T02/run_receipt_v1.py --backend rust --native 1 --mode taps --out out/T02/taps-rust-host2-v1.json > out/T02/taps-rust-host2-v1.log 2>&1
.venv/bin/python out/T01/compare_receipts.py out/T01/dev-taps-python-d3cf46a3.json out/T02/taps-rust-host2-v1.json
out/T02/run_family_v1.sh family-F40-rust-host2-v1.jsonl >> out/T02/family-F40-rust-host2-v1.log 2>&1
PYTHONPATH="$PWD/out/T02:$PYTHONPATH" GOAL2RUST_MACHINE=1 .venv/bin/python -B -m original_match.check --engine port --no-unicorn --cache .cache/goal2-archaeology/.cache/dl --json out/T02/check-rust-host2-v1.json >> out/T02/check-rust-host2-v1.log 2>&1
```

The lifecycle check can run alongside the two family workers on a quiet host;
wait for both to finish before timing. Record the full-family comparison and its
exit status (the ledger refuses a log without a successful status receipt):

```sh
.venv/bin/python - <<'PY'
import json, subprocess
from pathlib import Path
root=Path.cwd()
stem=root/'out/T02/compare-F40-rust-host2-v1'
cmd=[str(root/'.venv/bin/python'),'-B','experiments/E036-match-port/compare.py',
     '--family','F40','--no-screen','--candidate',str(root/'out/T02/family-F40-rust-host2-v1.jsonl')]
with stem.with_suffix('.log').open('x') as log:
    code=subprocess.run(cmd,cwd=root/'.cache/goal2-archaeology',stdout=log,stderr=subprocess.STDOUT).returncode
with Path(str(stem)+'.status.json').open('x') as f: json.dump(dict(returncode=code,command=cmd),f,indent=2)
assert code==0
PY
.venv/bin/python out/T02/validation_manifest_v1.py out/T02/validation-host2-v1.json \
  --family-file "$PWD/out/T02/family-F40-rust-host2-v1.jsonl" \
  --compare-stem compare-F40-rust-host2-v1 \
  --proof-receipt "$PWD/out/T02/taps-rust-host2-v1.json" \
  --check-file "$PWD/out/T02/check-rust-host2-v1.json" \
  --differential-file "$PWD/out/T02/differential-host2-v1.json" \
  --mutant-file "$PWD/out/T02/mutant-host2-v1.json" \
  --tests-file "$PWD/out/T02/tests-host2-v1.log"
```

The ledger verifies the new native taps against the original on every required
field, verifies native call counts, successful differential/mutant/check receipts,
and exact current source/extension hashes. It does not accept a new binary merely
because its source looks similar.

Finally, with no validation work or foreign heavy load active, collect three quiet
load observations and run `out/T02/paired_v1.sh`. It starts CPython Python, PyPy
Python and the CPython Rust machine together, clears overrides/mutant flags,
records load before/after, and writes all required `cpu-*-v1.json` with source and
extension hashes. Existing/incomplete timing outputs must be preserved and
inspected, not overwritten. Compare both baselines with Rust (the script does),
report measured results against **PyPy** too, commit/push receipts, update draft
PR #5 and the GitHub checkpoint, and recheck the final head's CI. No T03 work.
