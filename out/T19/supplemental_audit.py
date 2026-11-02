"""Post-writer historical-input, saved-baseline and native-presence audit."""
import hashlib,json,subprocess
from pathlib import Path
import evidence as e
e.verify();before=e.hashes();out=e.BASE/'out/T19';load=lambda p:json.loads((e.BASE/p).read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert load('out/T19/process-closure-v1.json')['pass_all']
assert before==load('out/T19/freeze-v1.json')['source_sha256']
manifest=load('out/T19/supplemental-source-inputs-v1.json')
for p,h in manifest['source_sha256'].items():assert sha(e.BASE/p)==h
assert manifest['source_sha256'][str(Path(__file__).resolve().relative_to(e.BASE))]==sha(Path(__file__))
profiles={}
for target,parent in [('out/T18/profile-after-v1.json','out/T19/inventory-v1.json'),('out/T17/profile-after-v1.json','out/T18/inventory-v2.json')]:
 h=sha(e.BASE/target);assert h==load(parent)['profile_sha256']
 blob=subprocess.check_output(['git','show','00ca71402f12085f0600b8a51165f50478fd77f3:'+target],cwd=e.BASE)
 assert hashlib.sha256(blob).hexdigest()==h
 profiles[target]=dict(sha256=h,parent_binding=parent)
# Every accepted T18 source/input is retained, mapping replaced runtime files to
# the pre-build snapshot. This checks identity independently of matching counts.
old=load('out/T18/validation-final-v3.json');mapped={}
for p,h in old['source_sha256'].items():
 if p.startswith('engine/'):q='.cache/T19-baseline/'+p
 elif p.startswith('.venv-pypy/lib/pypy3.11/site-packages/goal2rust_engine/'):q='.cache/T19-baseline/pypy/goal2rust_engine/'+Path(p).name
 else:q=p
 assert sha(e.BASE/q)==h,(p,q)
 mapped[p]=dict(preserved=q,sha256=h)
for p,h in old['evidence_sha256'].items():assert sha(e.BASE/'out/T18'/p)==h,p
new=set(load('out/T19/inventory-v1.json')['bodies']);counter_rows=[]
for rnd in range(1,4):
 b=load(f'out/T19/cpu-baseline-r{rnd}-v1.json');c=load(f'out/T19/cpu-candidate-r{rnd}-v1.json')
 before_counts={a:b['native_calls'].get(a,0) for a in sorted(new)};after_counts={a:c['native_calls'].get(a,0) for a in sorted(new)}
 assert all(n==0 for n in before_counts.values()) and all(n>0 for n in after_counts.values())
 for key in ['events_sha256','result_sha256','records_sha256','memory_sha256']:assert b[key]==c[key]
 counter_rows.append(dict(round=rnd,baseline_satisfies_new_native_requirement=False,candidate_satisfies_new_native_requirement=True,baseline=before_counts,candidate=after_counts))
report=dict(pass_all=True,script_sha256=sha(Path(__file__)),supplemental_source_sha256=manifest['source_sha256'],historical_profile_bindings=profiles,accepted_T18_source_bindings_preserved=mapped,accepted_T18_evidence_bindings_verified=len(old['evidence_sha256']),native_presence_before_after=counter_rows,original_freeze_unchanged=True,no_runtime_change=True)
e.write(out/'supplemental-audit-v1.json',report,before)
print('Historical profiles, all417 accepted baseline bindings,230 old evidence hashes and three before/after native controls pass')
