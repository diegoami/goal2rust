# T19 depth-adjustment closure

Read docs/tasks/T19.md, contract.md, inventory-v1.json and the latest checkpoint #1
before any build or producer. Baseline .cache/T19-baseline is the actual accepted
T18, preserved before builds and bound by baseline-snapshot-v1.json (54 files).
All 417 prior source/input/artifact and 230 evidence bindings matched first.
Historical .cache/T18-baseline is T17; never use it as the T19 comparator.

Same accepted 2cbeb36f oracle and private T07 state-v2/tables. No original bytes
are committed. Five new bodies, 23 real guest return sites; variants stay Python.
Inventory follows finite guest targets and references passed to inline helpers.
Per-body/integrated preflight does not replace final combined-artifact proofs.

Freeze explicit executable source/input allowlists before canonical runs. Keep
source/binaries/private inputs fixed; generated profile/text files are outputs.
Archive both CPython and PyPy binaries only after both installations finish and
pass preflight. Preserve all completed/rejected receipts and actual prior baseline.
Timing needs three complete simultaneous rotated four-arm rounds with unchanged
guards, quiet gates and all outcomes retained. Actual PID/PGID checks run in the
host namespace. Consult checkpoint #1 for the exact live controller/resume state;
never restart a live producer or overwrite a completed output.

## Frozen campaign

`freeze-v1.json` binds 466 sources, binaries and inputs. The combined artifact
passed CPython/PyPy preflight before `artifact-archive-v1.json` was copied.
`source-inputs-v1.json` explicitly selects executable proof sources and excludes
generated reports; the generated text exclusion probe passes. Do not edit those
inputs or rebuild while the controller runs.

Canonical controller (check checkpoint #1 and the live lock before any start):
`PYTHONHASHSEED=0 .venv/bin/python -u -B out/T19/supervise.py`. It appends
`jobs-v1.jsonl` and `supervisor-v1.log`, preserves verified completed receipts and
runs the entire prior43/new5 campaign on the fixed artifact. Timings additionally
append `timing-jobs-v1.jsonl`. No completed receipt is overwritten.

New fixed plan: 16,480 normal pairs, 10,480 body controls, 4,192 output/flag
controls, 3,680 comparisons for 23 individually reached guest-return controls,
1,280 branch pairs, 19,520 injected errors across 122 selectors, 112 variants
and 10,480 scoped native-lifetime checks. Three live matrices retain T17/T18
coverage and add 1,280 new source-specific alias pairs. Full prior43 proofs remain
mandatory. Generated profile outputs are under `generated/`.

After controller exit, run `process_closure.py` in the actual host namespace,
then `post_exit_audit.py` and `validate.py out/T19/validation-final-v1.json`.
Expected clean campaign: 62 canonical groups plus 12 timing groups, all exited,
and the supervisor PID gone. Any rejected attempt requires preserved evidence
and versioned recovery; do not suppress a source-stability assertion or reuse
an incomplete timing campaign as a headline. Exact-head CI, squash merge, main
CI, merged binding audit and checkpoint complete the task.
