"""Post-writer genuine capture provenance and preserved inventory audit."""
import hashlib,json,os,pickle
from pathlib import Path
import evidence as e
B=e.BASE;O=B/'out/T25';load=lambda n:json.loads((O/(n+'.json')).read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
e.verify();before=e.hashes();assert load('process-closure-v1')['pass_all']
meta=load('captures-v1');manifest=load('capture-inputs-v1');assert meta['oracle']==e.PIN and meta['source_unchanged']
assert meta['source_manifest_sha256']==sha(O/'capture-inputs-v1.json') and meta['source_sha256']==manifest['source_sha256']
assert len(manifest['source_sha256'])==49 and manifest['pure_oracle_only'] and manifest['no_candidate_or_test_imports']
for p,h in manifest['source_sha256'].items():assert sha(B/p)==h,p
raw=B/meta['private_file'];assert sha(raw)==meta['sha256'];bundle=pickle.loads(raw.read_bytes());assert len(bundle)==6 and all(len(v)==8 for v in bundle.values())
shards={r:[] for r in bundle}
for p,h in sorted(meta['private_shards'].items()):
 assert sha(B/p)==h;pdata=pickle.loads((B/p).read_bytes());assert pdata['oracle']==e.PIN and pdata['source_manifest_sha256']==meta['source_manifest_sha256'];shards[pdata['root']].append(pdata['state'])
assert len(meta['private_shards'])==48 and all(shards[r]==bundle[r] for r in bundle)
for states in bundle.values():
 for memory,regs,entry in states:assert len(memory)==0x110000 and 0<=entry[0]<=65535 and isinstance(entry[1],bool) and all(isinstance(v,int) for v in regs.values())
rows=[json.loads(x) for x in (B/meta['actual_drive_journal']).read_text().splitlines()]
assert rows and all(r['guard_unchanged'] and r['source_unchanged'] and r['runner_idle'] for r in rows) and all(v==8 for v in rows[-1]['after'].values())
rejected=load('rejected-inventory-v1');assert not rejected['accepted'] and sha(B/rejected['receipt'])==rejected['receipt_sha256'] and sha(B/rejected['source_archive'])==rejected['source_sha256']
assert load('inventory-v1')['inventory_script_sha256']==rejected['source_sha256']
assert load('inventory-v2')['inventory_script_sha256']==sha(O/'inventory.py')
try:os.kill(meta['pid'],0)
except ProcessLookupError:pass
else:raise AssertionError(('capture producer alive',meta['pid']))
e.write(O/'capture-input-audit-v1.json',dict(pass_all=True,accepted_source_bindings=49,actual_entry_shards=48,actual_drives=len(rows),capture_pids_stopped=[meta['pid']],inventory_rejection_preserved=True,no_guard_change=True,script_sha256=sha(Path(__file__))),before)
print('All49 capture inputs/48 genuine entry shards/drive journal/old inventory provenance verified')
