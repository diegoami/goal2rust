"""Run after supervisor exits, in the actual host PID namespace."""
import hashlib,json,os,platform,sys,time
from pathlib import Path
import evidence as e
e.verify();before=e.hashes();out=e.BASE/'out/T27';load=lambda n:json.loads((out/(n+'.json')).read_text())
jobs=[json.loads(x) for x in (out/'jobs-v1.jsonl').read_text().splitlines()];starts=[r for r in jobs if r['event']=='start'];exits=[r for r in jobs if r['event']=='exit']
assert len(starts)==len(exits)==102 and all(r['code']==0 for r in exits)
assert {r['pid'] for r in starts}=={r['pid'] for r in exits}
selection=load('performance-selection-v1');perf=load('performance-'+selection['selected_version']);assert perf['quiet_complete'] and len(perf['starts'])==len(perf['exits'])==12 and all(r['code']==0 for r in perf['exits'])
groups=[dict(kind='canonical',name=r['name'],pid=r['pid']) for r in starts]+[dict(kind='timing',name=r['arm'],pid=r['pid']) for campaign in selection['campaigns'] for r in load('performance-'+campaign['version'])['starts']]
assert len(groups)==len({r['pid'] for r in groups})==102+12*len(selection['campaigns'])
for r in groups:
 try:os.killpg(r['pid'],0)
 except ProcessLookupError:r['empty']=True
 else:raise AssertionError(('group still alive',r))
supervisor=int((e.BASE/'.cache/T27-supervisor.lock').read_text())
try:os.kill(supervisor,0)
except ProcessLookupError:pass
else:raise AssertionError(('supervisor still alive',supervisor))
preparation=load('preparation-v3');assert preparation['pass_all'] and preparation['source_unchanged']
assert preparation['script_sha256']==hashlib.sha256((out/'prepare_final.py').read_bytes()).hexdigest()
for p,h in preparation['source_sha256'].items():
 assert hashlib.sha256((e.BASE/p).read_bytes()).hexdigest()==hashlib.sha256((e.BASE/preparation['preserved_source_map'][p]).read_bytes()).hexdigest()==h,p
prep_jobs=[json.loads(x) for x in (out/'preparation-jobs-v3.jsonl').read_text().splitlines()]
prep_starts=[r for r in prep_jobs if r['event']=='start'];prep_exits=[r for r in prep_jobs if r['event']=='exit']
assert len(prep_starts)==len(prep_exits)==8 and all(r['code']==0 for r in prep_exits)
assert {r['pid'] for r in prep_starts}=={r['pid'] for r in prep_exits}=={r['pid'] for r in preparation['processes']}
assert prep_jobs[0]['event']=='controller' and prep_jobs[0]['pid']==preparation['controller_pid']
assert prep_jobs[0]['source_sha256']==preparation['source_sha256']
for r in preparation['processes']:
 try:os.killpg(r['pid'],0)
 except ProcessLookupError:pass
 else:raise AssertionError(('preparation group still alive',r))
for pid in [preparation['controller_pid'],*preparation['preseal_wrappers']]:
 try:os.kill(pid,0)
 except ProcessLookupError:pass
 else:raise AssertionError(('preparation controller/wrapper still alive',pid))
for version in ['v1','v2']:
 rejected=load('rejected-preparation-'+version);assert not rejected['accepted'] and rejected['no_final_build_or_canonical_started']
 for pid in rejected['controllers_stopped']:
  try:os.kill(pid,0)
  except ProcessLookupError:pass
  else:raise AssertionError(('rejected controller/wrapper still alive',pid))
report=dict(pass_all=True,node=platform.node(),supervisor_pid=supervisor,supervisor_exited=True,groups=groups,script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),time_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()))
report.update(preparation_controller_stopped=preparation['controller_pid'],preparation_groups_stopped=[r['pid'] for r in preparation['processes']],preseal_wrappers_stopped=preparation['preseal_wrappers'])
e.write(out/'process-closure-v1.json',report,before);print('All canonical and timing producer groups and supervisor exited')
