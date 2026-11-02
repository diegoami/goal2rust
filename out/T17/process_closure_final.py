"""Actual-host shutdown audit for all accepted and rejected T17 attempts."""
import hashlib,json,os,platform,sys,time
from pathlib import Path
sys.path.insert(0,'out/T17');import evidence as e
e.verify();before=e.hashes();out=e.BASE/'out/T17';load=lambda n:json.loads((out/(n+'.json')).read_text())
rows=[json.loads(x) for name in ['jobs-v1.jsonl','jobs-v2.jsonl'] for x in (out/name).read_text().splitlines()]
starts=[r for r in rows if r['event']=='start'];exits=[r for r in rows if r['event'] in ['exit','recovered-exit']]
assert len(starts)==len(exits)==48 and {r['pid'] for r in starts}=={r['pid'] for r in exits}
bad=[r for r in exits if r['code']];assert len(bad)==1 and bad[0]['name']=='check-v1' and bad[0]['code']==1
assert load('check-v1')['exit_code']==0 and not load('check-v1')['source_unchanged'] and all(r['pass'] for r in load('check-v1')['checks'].values())
assert load('profile-output-disposition-v1')['restored_original_input_set']
assert load('check-v2')['source_unchanged'] and load('check-v2-exec-exit')['observed_exec_exit_code']==0
assert load('recovery-exec-exit')['observed_exec_exit_code']==0
perf=load('performance-v1');assert len(perf['starts'])==len(perf['exits'])==12 and all(r['code']==0 for r in perf['exits'])
groups=[dict(kind='canonical',name=r['name'],pid=r['pid'],pgid=r.get('pgid',r['pid'])) for r in starts]
groups += [dict(kind='timing',name=r['arm'],pid=r['pid'],pgid=r['pid']) for r in perf['starts']]
live=load('live-observers-v1');assert live['pass_all'] and load('live-observers-exec-exit')['observed_exec_exit_code']==0
groups.append(dict(kind='supplement',name='live-observers-v1',pid=live['pid'],pgid=live['pgid']))
assert len(groups)==len({r['pgid'] for r in groups})==61
for r in groups:
 try:os.killpg(r['pgid'],0)
 except ProcessLookupError:r['empty']=True
 else:raise AssertionError(('still live group',r))
recovery=load('recovery-v2');assert recovery['pass_all']
controllers=[dict(name='original',pid=10009,pgid=9982,exit_code=1,reason='classified metadata rejection'),dict(name='recovery',pid=recovery['recovery_supervisor_pid'],pgid=recovery['recovery_supervisor_pgid'],exit_code=0)]
for r in controllers:
 for fn,arg in [(os.kill,r['pid']),(os.killpg,r['pgid'])]:
  try:fn(arg,0)
  except ProcessLookupError:pass
  else:raise AssertionError(('controller still live',r))
 r['exited']=True
report=dict(pass_all=True,node=platform.node(),time_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),supervisor_exited=True,controllers=controllers,groups=groups,canonical_attempts=48,accepted_canonical_attempts=47,classified_rejected_attempts=bad,timing_attempts=12,supplemental_attempts=1,script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
e.write(out/'process-closure-final-v2.json',report,before);print('Both controllers and all61 actual-host process groups exited; classified rejected attempt preserved')
