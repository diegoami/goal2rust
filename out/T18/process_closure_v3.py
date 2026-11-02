"""Run after supervisor exits, in the actual host PID namespace."""
import hashlib,json,os,platform,sys,time
from pathlib import Path
import evidence_v3 as e
e.verify();before=e.hashes();out=e.BASE/'out/T18';load=lambda n:json.loads((out/(n+'.json')).read_text())
jobs=[json.loads(x) for name in ['jobs-v1.jsonl','jobs-v2.jsonl','jobs-v3.jsonl'] for x in (out/name).read_text().splitlines()];starts=[r for r in jobs if r['event']=='start'];exits=[r for r in jobs if r['event']=='exit']
assert len(starts)==len(exits)==59
bad=[r for r in exits if r['code']];assert len(bad)==2 and {r['name'] for r in bad}=={'destination-normal-v1','performance-v1'} and all(r['code']==1 for r in bad)
assert {r['pid'] for r in starts}=={r['pid'] for r in exits}
perf=load('performance-v2');assert len(perf['starts'])==len(perf['exits'])==12 and all(r['code']==0 for r in perf['exits'])
groups=[dict(kind='canonical',name=r['name'],pid=r['pid']) for r in starts]+[dict(kind='timing',name=r['arm'],pid=r['pid']) for r in perf['starts']]
groups += [dict(kind='rejected-timing',name=r['arm'],pid=r['pid']) for r in load('timing-disposition-v1')['starts']]
assert len(groups)==len({r['pid'] for r in groups})==83
for r in groups:
 try:os.killpg(r['pid'],0)
 except ProcessLookupError:r['empty']=True
 else:raise AssertionError(('group still alive',r))
supervisors=[int((e.BASE/p).read_text()) for p in ['.cache/T18-supervisor.lock','.cache/T18-supervisor-v2.lock','.cache/T18-timing-v2.lock']]
for supervisor in supervisors:
 try:os.kill(supervisor,0)
 except ProcessLookupError:pass
 else:raise AssertionError(('supervisor still alive',supervisor))
report=dict(pass_all=True,node=platform.node(),supervisor_pids=supervisors,supervisor_exited=True,groups=groups,script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),time_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()))
e.write(out/'process-closure-v3.json',report,before);print('All83 producer groups and supervisor exited')
