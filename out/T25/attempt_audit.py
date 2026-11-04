"""After resumed writers exit,reconcile logical stages and preserve every attempt."""
import hashlib,json,os
from pathlib import Path
import evidence as e
B=e.BASE;O=B/'out/T25';load=lambda n:json.loads((O/(n+'.json')).read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
e.verify();before=e.hashes();assert before==load('freeze-v1')['source_sha256'];manifest=load('resume-source-inputs-v2')
for key in ['source_sha256','input_sha256']:
 for p,h in manifest[key].items():assert sha(B/p)==h,p
rejected=load('rejected-canonical-v1');assert not rejected['accepted'] and rejected['failed_before_proof'] and rejected['primary_freeze_unchanged'] and not rejected['production_changed']
old=[json.loads(x) for x in (O/'jobs-v1.jsonl').read_text().splitlines()];new=[json.loads(x) for x in (O/'jobs-v2.jsonl').read_text().splitlines()]
os_= [r for r in old if r['event']=='start'];oe=[r for r in old if r['event']=='exit'];ns=[r for r in new if r['event']=='start'];ne=[r for r in new if r['event']=='exit']
assert len(os_)==len(oe)==58 and len(ns)==len(ne)==35 and all(r['code']==0 for r in ne)
bad=[r for r in oe if r['code']];assert len(bad)==1 and bad[0]==rejected['failed'] and bad[0]['name']=='scoped-write-errors-v1'
good={r['pid'] for r in oe if r['code']==0};accepted=[r for r in old if r['pid'] in good]+new
starts=[r for r in accepted if r['event']=='start'];exits=[r for r in accepted if r['event']=='exit']
assert len(starts)==len(exits)==len({r['name'] for r in starts})==92 and all(r['code']==0 for r in exits)
assert {r['pid'] for r in starts}=={r['pid'] for r in exits}
fixed=[r for r in ns if r['name']=='scoped-write-errors-v1'];assert len(fixed)==1 and any(str(x).endswith('scoped_write_errors_current.py') for x in fixed[0]['command'])
original=(O/'prior_scoped_write_errors.py').read_text();corrected=(O/'scoped_write_errors_current.py').read_text();assert corrected==original.replace("OUT=e.BASE/'out/T24'","OUT=e.BASE/'out/T25'")
assert load('scoped-write-errors-v1')['pass_all'] and load('scoped-write-errors-v1')['comparisons']==640
controllers=[1006515,int((B/'.cache/T25-supervisor-v2.lock').read_text())]
for pid in controllers:
 try:os.kill(pid,0)
 except ProcessLookupError:pass
 else:raise AssertionError(('controller alive',pid))
for row in os_+ns:
 try:os.killpg(row['pid'],0)
 except ProcessLookupError:pass
 else:raise AssertionError(('canonical group alive',row))
path=O/'jobs-accepted-v2.jsonl'
with path.open('x') as f:
 for r in accepted:f.write(json.dumps(r)+'\n')
e.write(O/'attempt-audit-v2.json',dict(pass_all=True,logical_stages=92,physical_canonical_groups=93,preserved_failures=1,failed_before_proof=True,path_only_correction=True,controllers_stopped=controllers,source_manifest_sha256=sha(O/'resume-source-inputs-v2.json'),accepted_journal_sha256=sha(path),raw_journal_sha256={p.name:sha(p) for p in [O/'jobs-v1.jsonl',O/'jobs-v2.jsonl']},script_sha256=sha(Path(__file__))),before)
print('All92 required stages pass;93 physical attempts/two controllers stopped;one pre-proof failure preserved')
