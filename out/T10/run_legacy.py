"""Reuse the unchanged T02 full-frame differential with a fresh source manifest."""
import argparse
import json
import runpy
import sys
import evidence as common

ap = argparse.ArgumentParser()
ap.add_argument('--out', required=True)
ap.add_argument('--body-mutant', type=int, choices=[0, 1], default=0)
a = ap.parse_args()
common.verify()
before = common.hashes()
common.deny_original()
import goal2rust_engine
goal2rust_engine.set_mutant(a.body_mutant)
raw = common.BASE / '.cache/T10-raw' / common.Path(a.out).name
raw.parent.mkdir(parents=True, exist_ok=True)
assert not raw.exists() and not common.Path(a.out).exists()
sys.path.insert(0, str(common.BASE / 'out/T02'))
sys.argv = ['differential_v1.py', '--trials', '500', '--out', str(raw)]
try: runpy.run_path(str(common.BASE / 'out/T10/legacy_differential.py'), run_name='__main__')
except SystemExit as exc: status = exc.code
else: status = 0
report = json.loads(raw.read_text())
for row in report['routines'].values():
    for difference in row['differences']:
        difference['diff'] = {field: [common.digest(value) for value in values]
                              for field, values in difference['diff'].items()}
report['difference_values'] = 'SHA-256 of original repr values; raw diagnostic stays in ignored cache'
report['exit_code'], report['body_mutant'] = status, a.body_mutant
common.write(a.out, report, before)
assert (report['all_equal'] and status == 0) if not a.body_mutant else (not report['all_equal'] and status != 0)
