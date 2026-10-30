"""Fresh guest-return mutation control, preserving the original producer."""
import json
import runpy
import sys
import common

common.verify()
out = common.Path(sys.argv[1])
raw = out.with_suffix('.raw.json')
assert not out.exists() and not raw.exists()
before = common.hashes()
sys.argv = ['mutant_v1.py', str(raw)]
try: runpy.run_path(str(common.BASE / 'out/T02/mutant_v1.py'), run_name='__main__')
except SystemExit as exc: assert exc.code == 0
report = json.loads(raw.read_text())
common.write(out, report, before)
assert report['caught']
