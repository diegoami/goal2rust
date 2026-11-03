"""After canonical writers exit,verify genuine capture provenance and historical maps."""
import hashlib,json,os,pickle
from pathlib import Path
import evidence as e
B=e.BASE;O=B/'out/T24';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda n:json.loads((O/(n+'.json')).read_text())
e.verify();before=e.hashes();assert load('process-closure-v1')['pass_all'];meta=load('captures-v3');manifest=load('capture-inputs-v3')
assert meta['oracle']==e.PIN and meta['source_unchanged'] and meta['source_manifest_sha256']==sha(O/'capture-inputs-v3.json')
assert meta['source_sha256']==manifest['source_sha256'];mapped={}
for p,h in manifest['source_sha256'].items():
 q=B/'.cache/T24-capture-v2-source/evidence.py' if p=='out/T24/evidence.py' else B/p
 assert sha(q)==h,(p,q);mapped[p]=str(q.relative_to(B))
assert len(mapped)==47
raw=B/meta['private_file'];assert sha(raw)==meta['sha256'];bundle=pickle.loads(raw.read_bytes());assert len(bundle)==4 and all(len(v)==8 for v in bundle.values())
shards={r:[] for r in bundle}
for p,h in sorted(meta['private_shards'].items()):
 assert sha(B/p)==h,p;r=pickle.loads((B/p).read_bytes());assert r['oracle']==e.PIN and r['source_manifest_sha256']==meta['source_manifest_sha256'];shards[r['root']].append(r['state'])
assert len(meta['private_shards'])==32 and all(shards[r]==bundle[r] for r in bundle)
for root,states in bundle.items():
 for memory,regs,entry in states:assert len(memory)==0x110000 and 0<=entry[0]<=65535 and entry[1] is True and all(isinstance(x,int) for x in regs.values())
rows=[json.loads(x) for x in (B/meta['actual_drive_journal']).read_text().splitlines()];assert rows and all(r['guard_unchanged'] and r['source_unchanged'] for r in rows)
assert all(v==8 for v in rows[-1]['after'].values()) and any(r['exit']=='genuine-prefix-after-needed-entries' for r in rows)
# Failed/empty predecessors are immutable and never treated as accepted entries.
first=load('rejected-capture-v1');assert not first['accepted'] and first['original_dispatch_guard_unchanged'] and sha(B/first['log'])==first['log_sha256']
for p,h in first['source_sha256'].items():
 if p.startswith('engine/') and (B/'.cache/T24-baseline'/p).exists():q=B/'.cache/T24-baseline'/p
 elif p.startswith('.venv-pypy/lib/pypy3.11/site-packages/goal2rust_engine/'):q=B/'.cache/T24-baseline/pypy/goal2rust_engine'/Path(p).name
 elif p in ['out/T24/evidence.py','out/T24/capture.py','out/T24/inventory.py','engine/tests/test_keyboard.py']:
  q=B/'.cache/T24-capture-v1-sources'/p
 else:q=B/p
 assert sha(q)==h,(p,q)
second=load('superseded-capture-v2');assert not second['accepted'] and second['entries_collected']==second['private_shards_created']==0 and second['exit_code']==130
assert sha(B/second['log'])==second['log_sha256'] and sha(B/second['source_manifest'])==second['source_manifest_sha256']
for pid in [615651,627115,meta['pid']]:
 try:os.kill(pid,0)
 except ProcessLookupError:pass
 else:raise AssertionError(('capture producer alive',pid))
e.write(O/'capture-input-audit-v1.json',dict(pass_all=True,accepted_source_bindings=len(mapped),historical_capture_source_map=mapped,actual_entry_shards=32,actual_drives=len(rows),failed_initial_source_bindings=len(first['source_sha256']),superseded_empty_attempt_preserved=True,capture_pids_stopped=[615651,627115,meta['pid']],no_guard_change=True),before)
print('Genuine32 entry shards,47 capture-source inputs and both rejected/superseded attempts verified')
