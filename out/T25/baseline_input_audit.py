"""Post-writer accepted T24/baseline/historical/development/native-presence audit."""
import hashlib,json,subprocess
from pathlib import Path
import evidence as e
B=e.BASE;O=B/'out/T25';load=lambda p:json.loads((B/p).read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
e.verify();before=e.hashes();assert load('out/T25/process-closure-v1.json')['pass_all'] and before==load('out/T25/freeze-v1.json')['source_sha256']
profiles={}
for target,parent in [('out/T24/profile-after-v1.json','out/T25/inventory-v2.json'),('out/T23/profile-after-v1.json','out/T24/inventory-v1.json'),('out/T22/profile-after-v1.json','out/T23/inventory-v1.json'),('out/T21/profile-after-v1.json','out/T22/inventory-v1.json'),('out/T20/profile-after-v1.json','out/T21/inventory-v1.json'),('out/T19/profile-after-v1.json','out/T20/inventory-v1.json'),('out/T18/profile-after-v1.json','out/T19/inventory-v1.json'),('out/T17/profile-after-v1.json','out/T18/inventory-v2.json')]:
 h=sha(B/target);assert h==load(parent)['profile_sha256']
 blob=subprocess.check_output(['git','show','d51430b6ae9f3dfdd8fa39e9e7bdd02c1c6da62e:'+target],cwd=B);assert hashlib.sha256(blob).hexdigest()==h;profiles[target]=dict(sha256=h,parent_binding=parent)
old=load('out/T24/validation-final-v1.json');assert old['pass_all'] and len(old['source_sha256'])==852 and len(old['evidence_sha256'])==281;mapped={}
for p,h in old['source_sha256'].items():
 q='.cache/T25-baseline/'+p if p.startswith('engine/') else '.cache/T25-baseline/pypy/goal2rust_engine/'+Path(p).name if p.startswith('.venv-pypy/lib/pypy3.11/site-packages/goal2rust_engine/') else p
 assert sha(B/q)==h,(p,q);mapped[p]=dict(preserved=q,sha256=h)
for p,h in old['evidence_sha256'].items():assert sha(B/'out/T24'/p)==h,p
snapshot=load('out/T25/baseline-snapshot-v1.json')['source_and_binary_sha256'];assert len(snapshot)==75
for p,h in snapshot.items():assert sha(B/p)==h,p
sup=load('out/T24/supplemental-source-inputs-v1.json');assert len(sup['source_sha256'])==1 and len(sup['input_sha256'])==4
for key in ['source_sha256','input_sha256']:
 for p,h in sup[key].items():assert sha(B/p)==h,p
pa=load('out/T24/profile-reference-audit-v1.json');assert pa['pass_all'] and pa['source_manifest_sha256']==sha(B/'out/T24/supplemental-source-inputs-v1.json')
older=load('out/T23/validation-final-v2.json')
for key,count in [('supplemental_source_sha256',2),('supplemental_input_sha256',5)]:
 assert len(older[key])==count
 for p,h in older[key].items():assert sha(B/p)==h,p
for task,name in [('T22','supplemental-source-inputs-v1.json'),('T19','supplemental-source-inputs-v1.json'),('T19','supplemental-source-inputs-v2.json')]:
 for p,h in load('out/'+task+'/'+name)['source_sha256'].items():assert sha(B/p)==h,p
dev=load('out/T25/development-provenance-v1.json');assert sha(B/dev['receipt'])==dev['receipt_sha256'];receipt=load(dev['receipt'])
for p,h in receipt['source_sha256'].items():assert sha(B/dev['preserved_source_map'].get(p,p))==h,p
assert dev['verified_bindings']==len(receipt['source_sha256']) and dev['development_only'] and not dev['accepted_canonical_evidence']
archives=[]
for stage in range(7,26):
 for manifest in sorted((B/f'out/T{stage:02}').glob('artifact-archive-v*.json')):
  for row in json.loads(manifest.read_text())['artifacts']:
   assert sha(B/row['archive'])==row['sha256'];archives.append(row['archive'])
   if stage==25:assert sha(B/row['original'])==row['sha256']
assert len(archives)==40
profile=load('out/T25/profile-after-v1.json');reference=load('out/T25/taps-python-v1.json');candidate=load('out/T25/taps-rust-v1.json')
assert all(profile['observed'][k]==reference[k]==candidate[k] for k in profile['observed']) and profile['native_calls']==candidate['native_calls']
assert 'out/T24/taps-rust-v1.json' in before
version=load('out/T25/performance-selection-v1.json')['selected_version'];new=set(load('out/T25/inventory-v2.json')['bodies']);controls=[]
for rnd in range(1,4):
 b=load(f'out/T25/cpu-baseline-r{rnd}-{version}.json');c=load(f'out/T25/cpu-candidate-r{rnd}-{version}.json')
 bc={a:b['native_calls'].get(a,0) for a in sorted(new)};cc={a:c['native_calls'].get(a,0) for a in sorted(new)};assert all(v==0 for v in bc.values()) and all(v>0 for v in cc.values())
 for k in ['events_sha256','result_sha256','records_sha256','memory_sha256']:assert b[k]==c[k]
 controls.append(dict(round=rnd,baseline=bc,candidate=cc,baseline_satisfies_new_native_requirement=False,candidate_satisfies_new_native_requirement=True))
e.write(O/'baseline-input-audit-v1.json',dict(pass_all=True,script_sha256=sha(Path(__file__)),historical_profile_bindings=profiles,accepted_T24_source_bindings_preserved=mapped,accepted_T24_evidence_bindings_verified=281,accepted_T24_supplemental_sources=1,accepted_T24_supplemental_inputs=4,baseline_bindings=75,archive_bindings=40,development_source_bindings_verified=len(receipt['source_sha256']),profile_matches_fresh_python_and_rust=True,native_presence_before_after=controls,original_freeze_unchanged=True,no_runtime_change=True),before)
print('Accepted852+281/1+4,baseline75,all40 artifacts,historical/development inputs and native-presence controls pass')
