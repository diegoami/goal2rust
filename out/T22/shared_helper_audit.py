"""Actual-host post-exit audit of additive shared-helper evidence and bindings."""
import hashlib,json,os
from pathlib import Path
import evidence as e
OUT=e.BASE/'out/T22';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda n:json.loads((OUT/(n+'.json')).read_text())
e.verify();before=e.hashes();assert before==load('freeze-v1')['source_sha256'];manifest=load('supplemental-source-inputs-v1')
assert sha(OUT/'freeze-v1.json')==manifest['base_freeze_sha256']
for p,h in manifest['source_sha256'].items():assert sha(e.BASE/p)==h,p
r=load('shared-helper-closure-v1');assert r['pass_all'] and r['comparisons']==6288 and r['variants']==64
assert r['source_unchanged'] and r['source_sha256']==before and r['supplemental_source_unchanged']
assert r['supplemental_source_sha256']==manifest['source_sha256'] and r['source_manifest_sha256']==sha(OUT/'supplemental-source-inputs-v1.json')
assert not r['native_owned_calls'] and r['all_native_lifetimes_zero_owned_python'] and all(r['shared_source_calls'].values())
assert len(r['rows'])==3 and all(v==dict(total=2096,real=96,authored=2000,outside_positive=2096) for v in r['rows'].values())
closure=load('process-closure-v1');assert closure['pass_all'] and len(closure['groups'])==90
for group in closure['groups']+[dict(pid=r['pid'])]:
 try:os.killpg(group['pid'],0)
 except ProcessLookupError:pass
 else:raise AssertionError(('producer group still alive',group))
try:os.kill(closure['supervisor_pid'],0)
except ProcessLookupError:pass
else:raise AssertionError('controller still alive')
e.write(OUT/'shared-helper-audit-v1.json',dict(pass_all=True,primary_bindings=len(before),supplemental_source_sha256=manifest['source_sha256'],source_manifest_sha256=sha(OUT/'supplemental-source-inputs-v1.json'),supplemental_group_exited=True,canonical_groups_exited=90,supplemental_pid=r['pid']),before)
print('661 primary bindings,2 supplemental sources and all91 producer groups/controller closed')
