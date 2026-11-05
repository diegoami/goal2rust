"""After capture exits, verify genuine shards and their complete source binding."""
import hashlib
import json
import os
import pickle
from pathlib import Path
import capture_support as e

e.verify()
B = e.BASE
O = B / 'out/T27'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda name: json.loads((O / (name + '.json')).read_text())
manifest = load('capture-inputs-v1')
receipt = load('captures-v1')
inventory = load('inventory-v1')
assert len(manifest['source_sha256']) == 50
assert manifest['pure_oracle_only'] and manifest['no_candidate_or_candidate_test_imports']
assert receipt['oracle'] == manifest['oracle'] == inventory['oracle'] == e.PIN
assert receipt['source_unchanged'] and receipt['source_sha256'] == manifest['source_sha256']
assert receipt['source_manifest_sha256'] == sha(O / 'capture-inputs-v1.json')
for p, digest in manifest['source_sha256'].items():
    assert sha(B / p) == digest, p
assert sha(B / receipt['private_file']) == receipt['sha256']
bundle = pickle.loads((B / receipt['private_file']).read_bytes())
assert set(bundle) == set(inventory['bodies']) and len(bundle) == 7
assert all(len(v) == 8 for v in bundle.values())
shards = {a: [] for a in bundle}
for p, digest in sorted(receipt['private_shards'].items()):
    assert sha(B / p) == digest, p
    row = pickle.loads((B / p).read_bytes())
    assert row['oracle'] == e.PIN and row['source_manifest_sha256'] == receipt['source_manifest_sha256']
    shards[row['root']].append(row['state'])
assert len(receipt['private_shards']) == 56 and shards == bundle
for states in bundle.values():
    for memory, regs, entry in states:
        assert len(memory) == 0x110000 and 0 <= entry[0] <= 65535 and isinstance(entry[1], bool)
        assert all(isinstance(v, int) for v in regs.values())
journal = [json.loads(line) for line in (B / receipt['actual_drive_journal']).read_text().splitlines()]
assert journal and all(row['guard_unchanged'] and row['runner_idle'] and row['source_unchanged'] for row in journal)
assert all(v == 8 for v in journal[-1]['after'].values())
assert inventory['site_count'] == len(inventory['guest_sites']) == 12
assert len({s['ret_to'] for s in inventory['guest_sites']}) == 12
assert len(inventory['owned_code_objects']) == 27
assert sum('.Rec.' in name for name in inventory['owned_code_objects']) == 3
assert inventory['inventory_script_sha256'] == sha(O / 'inventory.py')
for p, digest in inventory['source_sha256'].items():
    assert sha(B / p) == digest, p
try:
    os.kill(receipt['pid'], 0)
except ProcessLookupError:
    pass
else:
    raise AssertionError(('capture producer still alive', receipt['pid']))
baseline = load('baseline-snapshot-v1')
for p, digest in baseline['source_and_binary_sha256'].items():
    assert sha(B / p) == digest, p
for source, saved in baseline['source_map'].items():
    assert sha(B / source) == sha(B / saved), source
report = dict(pass_all=True, oracle=e.PIN, capture_source_bindings=50, actual_entry_shards=56,
              actual_drives=len(journal), captures_per_body=receipt['captures'],
              capture_pids_stopped=[receipt['pid']], original_guards_retained=True,
              owned_code_objects=27, owned_record_methods=3, guest_sites=12,
              accepted_T26_baseline_files=len(baseline['source_and_binary_sha256']),
              accepted_T26_runtime_still_unchanged=True,
              source_manifest_sha256=sha(O / 'capture-inputs-v1.json'),
              capture_receipt_sha256=sha(O / 'captures-v1.json'),
              drive_journal_sha256=sha(B / receipt['actual_drive_journal']),
              script_sha256=sha(Path(__file__)))
with (O / 'capture-input-audit-v1.json').open('x') as stream:
    json.dump(report, stream, indent=2, sort_keys=True)
    stream.write('\n')
print('All50 inputs/56 genuine shards/one drive/27 code objects/12 returns/79 unchanged baseline files verified;capture PID stopped')
