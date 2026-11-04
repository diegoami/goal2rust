"""Run the unchanged upstream lifecycle under its original-file denial bootstrap."""
import argparse
import json
import os
import runpy
import sys
import evidence as common

ap = argparse.ArgumentParser()
ap.add_argument('--out', required=True)
a = ap.parse_args()
common.verify()
common.select('rust')
common.deny_original()
before = common.hashes()
raw = common.Path(a.out).with_suffix('.raw.json')
assert not raw.exists() and not common.Path(a.out).exists()
sys.argv = ['original_match.check', '--engine', 'port', '--no-unicorn',
            '--state', str(common.STATE), '--tables', str(common.TABLES), '--json', str(raw)]
try:
    runpy.run_module('original_match.check', run_name='__main__')
except SystemExit as exc:
    status = exc.code
else: status = 0
report = json.loads(raw.read_text())
report['exit_code'] = status
report['denial'] = 'upstream positive Unicorn/.sav/.EXE/.DAT import/open denial'
common.write(a.out, report, before)
assert status == 0 and all(row['pass'] for row in report['checks'].values())
