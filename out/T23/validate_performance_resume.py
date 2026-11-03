"""Select a fully quiet repeat while preserving all primary fidelity/v1 evidence."""
import hashlib,json,os,statistics,sys
from pathlib import Path
import evidence as e
OUT=e.BASE/'out/T23';attempt=int(sys.argv[1]);assert attempt>=2;version='v'+str(attempt)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda n:json.loads((OUT/(n+'.json')).read_text())
e.verify();assert not e.BASELINE;before=e.hashes();assert before==load('freeze-v1')['source_sha256']
old=load('validation-final-v1');assert old['pass_all'] and old['source_sha256']==before
for p,h in old['evidence_sha256'].items():assert sha(OUT/p)==h,p
manifest=load('performance-resume-inputs-v2');manifest_sha=sha(OUT/'performance-resume-inputs-v2.json')
def supplements():
 for key in ['source_sha256','input_sha256']:
  for p,h in manifest[key].items():assert sha(e.BASE/p)==h,p
 assert sha(OUT/'performance-resume-inputs-v2.json')==manifest_sha
supplements();rejection=load('rejected-performance-v1');assert not rejection['accepted_for_performance']
assert max(load('cpu-python-r3-v1')['load_after'][:2])>=4
perf=load('performance-'+version);assert perf['measurement_complete'] and perf['outputs_equal'] and perf['quiet_complete'] and perf['source_unchanged']
assert perf['base_source_sha256']==before and perf['supplemental_source_sha256']==manifest['source_sha256'] and perf['supplemental_input_sha256']==manifest['input_sha256'] and perf['source_manifest_sha256']==manifest_sha
assert len(perf['starts'])==len(perf['exits'])==12 and all(r['code']==0 for r in perf['exits'])
reference=load('taps-python-v1');ratios=[];comparisons=[old['comparisons'][0]]
for rnd in range(1,4):
 rows={arm:load(f'cpu-{arm}-r{rnd}-{version}') for arm in ['baseline','candidate','python','pypy']}
 for arm,row in rows.items():
  assert row['source_unchanged']
  for p,h in row['source_sha256'].items():assert sha(e.BASE/p)==h,(arm,p)
  for key in ['oracle','input_state_sha256','events','events_sha256','result_sha256','records_sha256','memory_sha256','stretches']:assert row[key]==reference[key],(rnd,arm,key)
  assert max(row['load_before'][:2])<4 and max(row['load_after'][:2])<4,(rnd,arm,'not quiet')
  if arm in ['baseline','candidate']:
   assert len(row['native_calls'])==(56 if arm=='baseline' else 59) and sum(row['native_calls'].values())==(2593590 if arm=='baseline' else 2610122)
   assert row['arm']==arm and row['bridge_fast_calls'] and all(row['bridge_fast_calls'].values())
  else:assert row['arm']=='plain' and not row['native_calls']
 start=[r for r in perf['starts'] if r['round']==rnd];assert len(start)==4 and len({r['cpu'] for r in start})==4 and max(r['time'] for r in start)-min(r['time'] for r in start)<5
 quiet=[r for r in perf['quiet_observations'] if r['round']==rnd];assert len(quiet)>=3 and all(max(r['load'][:2])<4 for r in quiet[-3:])
 trace=[r for r in perf['continuous_load'] if r['round']==rnd];assert trace and all(max(r['load'][:2])<8 for r in trace)
 quality=[r for r in perf['quiet_quality'] if r['round']==rnd];assert len(quality)==1 and quality[0]['all_arm_ends_quiet'] and quality[0]['continuous_total_load_below8']
 ratio=rows['candidate']['drive_cpu_s']/rows['baseline']['drive_cpu_s'];ratios.append(ratio);r=perf['rounds'][rnd-1];assert r['round']==rnd and r['candidate_to_baseline']==ratio
 assert r['baseline_to_pypy']==rows['baseline']['drive_cpu_s']/rows['pypy']['drive_cpu_s'] and r['candidate_to_pypy']==rows['candidate']['drive_cpu_s']/rows['pypy']['drive_cpu_s'] and r['cpython_to_candidate']==rows['python']['drive_cpu_s']/rows['candidate']['drive_cpu_s']
 comparisons.append(dict(files=[f'cpu-{a}-r{rnd}-{version}' for a in rows],equal=True))
assert perf['ratios']==ratios and perf['median_ratio']==statistics.median(ratios)
for column,field in [('baseline_to_pypy','median_baseline_to_pypy'),('candidate_to_pypy','median_candidate_to_pypy'),('cpython_to_candidate','median_cpython_to_candidate')]:assert perf[field]==statistics.median(r[column] for r in perf['rounds'])
# Check every original group and every repeated campaign/arm after the writers exited.
closure=load('process-closure-v1');assert closure['pass_all'] and len(closure['groups'])==94
groups=[r['pid'] for r in closure['groups']];campaigns=[]
for n in range(2,attempt+1):
 p=load('performance-v'+str(n));campaigns.append(dict(attempt=n,quiet_complete=p['quiet_complete'],accepted=n==attempt))
 if n<attempt:assert not p['quiet_complete']
 assert len(p['starts'])==len(p['exits'])==12 and all(r['code']==0 for r in p['exits'])
 groups += [r['pid'] for r in p['starts']]+[p['pgid']]
for pgid in groups:
 try:os.killpg(pgid,0)
 except ProcessLookupError:pass
 else:raise AssertionError(('producer group alive',pgid))
try:os.kill(closure['supervisor_pid'],0)
except ProcessLookupError:pass
else:raise AssertionError('original controller alive')
# Saved baseline/current artifacts and historical source/evidence remain independently checked.
for p,h in load('baseline-snapshot-v1')['source_and_binary_sha256'].items():assert sha(e.BASE/p)==h,p
for r in load('artifact-archive-v1')['artifacts']:assert sha(e.BASE/r['archive'])==sha(e.BASE/r['original'])==r['sha256']
assert load('post-exit-audit-v1')['pass_all'] and load('baseline-input-audit-v1')['pass_all']
supplements();assert e.hashes()==before
report=dict(old);report.update(pass_all=True,selected_performance_version=version,rejected_original_performance=True,rejected_original_reason=rejection['reason'],primary_fidelity_ledger_sha256=sha(OUT/'validation-final-v1.json'),supplemental_source_sha256=manifest['source_sha256'],supplemental_input_sha256=manifest['input_sha256'],source_manifest_sha256=manifest_sha,supplemental_source_unchanged=True,comparisons=comparisons,performance_ratios=ratios,median_performance_ratio=statistics.median(ratios),all_rounds_improve=all(r<1 for r in ratios),performance_campaigns=campaigns,groups_stopped=len(groups),controller_stopped=True,all_writers_finished=True,evidence_sha256={str(p.relative_to(OUT)):sha(p) for p in sorted(OUT.rglob('*')) if p.is_file() and p.suffix in ['.json','.jsonl','.log','.txt','.prof'] and p.name!='validation-final-v2.json'})
e.write(OUT/'validation-final-v2.json',report,before);print('Final selection',version,'primary731;groups',len(groups),'supplemental sources',len(manifest['source_sha256']),'PASS')
