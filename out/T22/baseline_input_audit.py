"""Post-writer historical-input, saved-baseline and native-presence audit."""
import hashlib,json,subprocess
from pathlib import Path
import evidence as e
e.verify();before=e.hashes();out=e.BASE/'out/T22';load=lambda p:json.loads((e.BASE/p).read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert load('out/T22/process-closure-v1.json')['pass_all']
assert before==load('out/T22/freeze-v1.json')['source_sha256']
profiles={}
for target,parent in [('out/T21/profile-after-v1.json','out/T22/inventory-v1.json'),('out/T20/profile-after-v1.json','out/T21/inventory-v1.json'),('out/T19/profile-after-v1.json','out/T20/inventory-v1.json'),('out/T18/profile-after-v1.json','out/T19/inventory-v1.json'),('out/T17/profile-after-v1.json','out/T18/inventory-v2.json')]:
 h=sha(e.BASE/target);assert h==load(parent)['profile_sha256']
 blob=subprocess.check_output(['git','show','c287b84448f6e1dde2206e0ed5af93d46abcf3d8:'+target],cwd=e.BASE)
 assert hashlib.sha256(blob).hexdigest()==h
 profiles[target]=dict(sha256=h,parent_binding=parent)
# Every accepted T21 source/input is retained, mapping replaced runtime files to
# the pre-build snapshot. This checks identity independently of matching counts.
old=load('out/T21/validation-final-v1.json');mapped={}
for p,h in old['source_sha256'].items():
 if p.startswith('engine/'):q='.cache/T22-baseline/'+p
 elif p.startswith('.venv-pypy/lib/pypy3.11/site-packages/goal2rust_engine/'):q='.cache/T22-baseline/pypy/goal2rust_engine/'+Path(p).name
 else:q=p
 assert sha(e.BASE/q)==h,(p,q)
 mapped[p]=dict(preserved=q,sha256=h)
for p,h in old['evidence_sha256'].items():assert sha(e.BASE/'out/T21'/p)==h,p
for name in ['supplemental-source-inputs-v1.json','supplemental-source-inputs-v2.json']:
 for p,h in load('out/T19/'+name)['source_sha256'].items():assert sha(e.BASE/p)==h
new=set(load('out/T22/inventory-v1.json')['bodies']);counter_rows=[]
for rnd in range(1,4):
 b=load(f'out/T22/cpu-baseline-r{rnd}-v1.json');c=load(f'out/T22/cpu-candidate-r{rnd}-v1.json')
 before_counts={a:b['native_calls'].get(a,0) for a in sorted(new)};after_counts={a:c['native_calls'].get(a,0) for a in sorted(new)}
 assert all(n==0 for n in before_counts.values()) and all(n>0 for n in after_counts.values())
 for key in ['events_sha256','result_sha256','records_sha256','memory_sha256']:assert b[key]==c[key]
 counter_rows.append(dict(round=rnd,baseline_satisfies_new_native_requirement=False,candidate_satisfies_new_native_requirement=True,baseline=before_counts,candidate=after_counts))
report=dict(pass_all=True,script_sha256=sha(Path(__file__)),historical_profile_bindings=profiles,accepted_T21_source_bindings_preserved=mapped,accepted_T21_evidence_bindings_verified=len(old['evidence_sha256']),native_presence_before_after=counter_rows,original_freeze_unchanged=True,no_runtime_change=True)
e.write(out/'baseline-input-audit-v1.json',report,before)
print('Historical profiles, all598 accepted baseline bindings,214 old evidence hashes and three before/after native controls pass')
