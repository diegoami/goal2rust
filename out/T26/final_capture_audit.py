"""Verify the preserved pre-implementation capture without rerunning its epoch."""
import hashlib
import json
import os
import pickle
from pathlib import Path
import evidence as e

O = e.BASE/'out/T26'
load = lambda name:json.loads((O/(name+'.json')).read_text())
sha = lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
e.verify()
before = e.hashes()
assert load('process-closure-v1')['pass_all']
old = load('capture-input-audit-v1')
manifest, receipt = load('capture-inputs-v1'), load('captures-v1')
assert old['pass_all'] and old['accepted_T25_runtime_still_unchanged']
assert old['script_sha256'] == sha(O/'capture_input_audit.py')
assert old['source_manifest_sha256'] == receipt['source_manifest_sha256'] == sha(O/'capture-inputs-v1.json')
assert old['capture_receipt_sha256'] == sha(O/'captures-v1.json')
assert old['drive_journal_sha256'] == sha(O/'capture-drives-v1.jsonl')
assert len(manifest['source_sha256']) == 49 and manifest['pure_oracle_only'] and manifest['no_candidate_or_candidate_test_imports']
for p, digest in manifest['source_sha256'].items():assert sha(e.BASE/p) == digest
assert receipt['source_sha256'] == manifest['source_sha256'] and receipt['source_unchanged']
assert sha(e.BASE/receipt['private_file']) == receipt['sha256']
bundle = pickle.loads((e.BASE/receipt['private_file']).read_bytes())
assert len(bundle) == 10 and all(len(values) == 8 for values in bundle.values())
shards = {root:[] for root in bundle}
for p, digest in sorted(receipt['private_shards'].items()):
    assert sha(e.BASE/p) == digest
    row = pickle.loads((e.BASE/p).read_bytes())
    assert row['oracle'] == e.PIN and row['source_manifest_sha256'] == receipt['source_manifest_sha256']
    shards[row['root']].append(row['state'])
assert len(receipt['private_shards']) == 80 and shards == bundle
try:os.kill(receipt['pid'], 0)
except ProcessLookupError:pass
else:raise AssertionError('Capture producer remains alive')
e.write(O/'capture-final-audit-v1.json', dict(pass_all=True, capture_source_bindings=49,
        actual_entry_shards=80, actual_drives=1, initial_runtime_epoch_preserved=True,
        capture_pids_stopped=[receipt['pid']], script_sha256=sha(Path(__file__))), before)
print('49 pure-oracle bindings/80 genuine shards and original capture epoch verified;producer stopped')
