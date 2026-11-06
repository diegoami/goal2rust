"""Seal actual pure-oracle capture inputs before any capture producer starts."""
import hashlib
import json
from pathlib import Path
import capture_support as e

e.verify()
B = e.BASE
O = B / 'out/T29'
inventory = json.loads((O / 'inventory-v1.json').read_text())
assert inventory['oracle'] == e.PIN
assert inventory['inventory_script_sha256'] == hashlib.sha256((O / 'inventory.py').read_bytes()).hexdigest()
files = sorted((e.ORACLE / 'runtime/original_match').rglob('*.py'))
files += [e.ORACLE / 'tests/test_port_seal.py', e.STATE] + sorted(e.TABLES.iterdir())
files += [B / 'out/T26/inventory.py']
files += [O / name for name in ['inventory.py', 'inventory-v1.json', 'capture.py', 'capture_support.py', 'host_gate.py']]
report = dict(oracle=e.PIN, pure_oracle_only=True, no_candidate_or_candidate_test_imports=True,
              capture_bodies=sorted(inventory['bodies']),
              source_sha256={str(p.relative_to(B)): hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in sorted(files)})
with (O / 'capture-inputs-v1.json').open('x') as stream:
    json.dump(report, stream, indent=2, sort_keys=True)
    stream.write('\n')
print('Sealed', len(report['source_sha256']), 'pure-oracle inputs for one-body capture')
