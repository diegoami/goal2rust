"""Run after supervisor exits, in the actual host PID namespace."""
import hashlib,json,os,platform,sys,time
from pathlib import Path
import evidence_v2 as e
e.verify();before=e.hashes();out=e.BASE/'out/T18';load=lambda n:json.loads((out/(n+'.json')).read_text())
jobs=[json.loads(x) for name in ['jobs-v1.jsonl','jobs-v2.jsonl'] for x in (out/name).read_text().splitlines()];starts=[r for r in jobs if r['event']=='start'];exits=[r for r in jobs if r['event']=='exit']
assert len(starts)==len(exits)==58
bad=[r for r in exits if r['code']];assert len(bad)==1 and bad[0]['name']=='destination-normal-v1' and bad[0]['code']==1
assert {r['pid'] for r in starts}=={r['pid'] for r in exits}
perf=load('performance-v1');assert len(perf['starts'])==len(perf['exits'])==12 and all(r['code']==0 for r in perf['exits'])
groups=[dict(kind='canonical',name=r['name'],pid=r['pid']) for r in starts]+[dict(kind='timing',name=r['arm'],pid=r['pid']) for r in perf['starts']]
assert len(groups)==len({r['pid'] for r in groups})==70
for r in groups:
 try:os.killpg(r['pid'],0)
 except ProcessLookupError:r['empty']=True
 else:raise AssertionError(('group still alive',r))
supervisors=[int((e.BASE/p).read_text()) for p in ['.cache/T18-supervisor.lock','.cache/T18-supervisor-v2.lock']]
for supervisor in supervisors:
 try:os.kill(supervisor,0)
 except ProcessLookupError:pass
 else:raise AssertionError(('supervisor still alive',supervisor))
report=dict(pass_all=True,node=platform.node(),supervisor_pids=supervisors,supervisor_exited=True,groups=groups,script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),time_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()))
e.write(out/'process-closure-v2.json',report,before);print('All70 producer groups and supervisor exited')
