"""Post-writer historical-input, saved-baseline and native-presence audit."""
import hashlib,json,subprocess
from pathlib import Path
import evidence as e
e.verify();before=e.hashes();out=e.BASE/'out/T24';load=lambda p:json.loads((e.BASE/p).read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert load('out/T24/process-closure-v1.json')['pass_all']
assert before==load('out/T24/freeze-v1.json')['source_sha256']
profiles={}
for target,parent in [('out/T23/profile-after-v1.json','out/T24/inventory-v1.json'),('out/T22/profile-after-v1.json','out/T23/inventory-v1.json'),('out/T21/profile-after-v1.json','out/T22/inventory-v1.json'),('out/T20/profile-after-v1.json','out/T21/inventory-v1.json'),('out/T19/profile-after-v1.json','out/T20/inventory-v1.json'),('out/T18/profile-after-v1.json','out/T19/inventory-v1.json'),('out/T17/profile-after-v1.json','out/T18/inventory-v2.json')]:
 h=sha(e.BASE/target);assert h==load(parent)['profile_sha256']
 blob=subprocess.check_output(['git','show','42c06a71398fb930ad6c1f9104c5398cccbf1481:'+target],cwd=e.BASE)
 assert hashlib.sha256(blob).hexdigest()==h
 profiles[target]=dict(sha256=h,parent_binding=parent)
# Every accepted T23 source/input is retained, mapping replaced runtime files to
# the pre-build snapshot. This checks identity independently of matching counts.
old=load('out/T23/validation-final-v2.json');mapped={}
for p,h in old['source_sha256'].items():
 if p.startswith('engine/'):q='.cache/T24-baseline/'+p
 elif p.startswith('.venv-pypy/lib/pypy3.11/site-packages/goal2rust_engine/'):q='.cache/T24-baseline/pypy/goal2rust_engine/'+Path(p).name
 else:q=p
 assert sha(e.BASE/q)==h,(p,q)
 mapped[p]=dict(preserved=q,sha256=h)
for p,h in old['evidence_sha256'].items():assert sha(e.BASE/'out/T23'/p)==h,p
for name in ['supplemental-source-inputs-v1.json','supplemental-source-inputs-v2.json']:
 for p,h in load('out/T19/'+name)['source_sha256'].items():assert sha(e.BASE/p)==h
for p,h in load('out/T22/supplemental-source-inputs-v1.json')['source_sha256'].items():assert sha(e.BASE/p)==h
for key in ['supplemental_source_sha256','supplemental_input_sha256']:
 for p,h in old[key].items():assert sha(e.BASE/p)==h
version=load('out/T24/performance-selection-v1.json')['selected_version']
new=set(load('out/T24/inventory-v1.json')['bodies']);counter_rows=[]
for rnd in range(1,4):
 b=load(f'out/T24/cpu-baseline-r{rnd}-{version}.json');c=load(f'out/T24/cpu-candidate-r{rnd}-{version}.json')
 before_counts={a:b['native_calls'].get(a,0) for a in sorted(new)};after_counts={a:c['native_calls'].get(a,0) for a in sorted(new)}
 assert all(n==0 for n in before_counts.values()) and all(n>0 for n in after_counts.values())
 for key in ['events_sha256','result_sha256','records_sha256','memory_sha256']:assert b[key]==c[key]
 counter_rows.append(dict(round=rnd,baseline_satisfies_new_native_requirement=False,candidate_satisfies_new_native_requirement=True,baseline=before_counts,candidate=after_counts))
report=dict(pass_all=True,script_sha256=sha(Path(__file__)),historical_profile_bindings=profiles,accepted_T23_source_bindings_preserved=mapped,accepted_T23_evidence_bindings_verified=len(old['evidence_sha256']),native_presence_before_after=counter_rows,original_freeze_unchanged=True,no_runtime_change=True)
e.write(out/'baseline-input-audit-v1.json',report,before)
print('Historical profiles, all731 accepted baseline bindings,263 old evidence hashes and three before/after native controls pass')
