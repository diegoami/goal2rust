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
