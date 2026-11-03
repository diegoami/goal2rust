"""Run after supervisor exits, in the actual host PID namespace."""
import hashlib,json,os,platform,sys,time
from pathlib import Path
import evidence as e
e.verify();before=e.hashes();out=e.BASE/'out/T24';load=lambda n:json.loads((out/(n+'.json')).read_text())
jobs=[json.loads(x) for x in (out/'jobs-v1.jsonl').read_text().splitlines()];starts=[r for r in jobs if r['event']=='start'];exits=[r for r in jobs if r['event']=='exit']
assert len(starts)==len(exits)==87 and all(r['code']==0 for r in exits)
assert {r['pid'] for r in starts}=={r['pid'] for r in exits}
selection=load('performance-selection-v1');perf=load('performance-'+selection['selected_version']);assert perf['quiet_complete'] and len(perf['starts'])==len(perf['exits'])==12 and all(r['code']==0 for r in perf['exits'])
groups=[dict(kind='canonical',name=r['name'],pid=r['pid']) for r in starts]+[dict(kind='timing',name=r['arm'],pid=r['pid']) for campaign in selection['campaigns'] for r in load('performance-'+campaign['version'])['starts']]
assert len(groups)==len({r['pid'] for r in groups})==87+12*len(selection['campaigns'])
for r in groups:
 try:os.killpg(r['pid'],0)
 except ProcessLookupError:r['empty']=True
 else:raise AssertionError(('group still alive',r))
supervisor=int((e.BASE/'.cache/T24-supervisor.lock').read_text())
try:os.kill(supervisor,0)
except ProcessLookupError:pass
else:raise AssertionError(('supervisor still alive',supervisor))
report=dict(pass_all=True,node=platform.node(),supervisor_pid=supervisor,supervisor_exited=True,groups=groups,script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),time_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()))
e.write(out/'process-closure-v1.json',report,before);print('All canonical and timing producer groups and supervisor exited')
