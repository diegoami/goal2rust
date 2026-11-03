"""Actual-host closure of every original/resumed attempt and timing process."""
import hashlib,json,os,platform,time
from pathlib import Path
import evidence as e
B=e.BASE;O=B/'out/T25';load=lambda n:json.loads((O/(n+'.json')).read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
e.verify();before=e.hashes();attempt=load('attempt-audit-v2');assert attempt['pass_all'] and attempt['physical_canonical_groups']==93
selection=load('performance-selection-v1');perf=load('performance-'+selection['selected_version']);assert perf['quiet_complete']
groups=[]
for epoch in ['v1','v2']:
 for r in [json.loads(x) for x in (O/f'jobs-{epoch}.jsonl').read_text().splitlines()]:
  if r['event']=='start':groups.append(dict(kind='canonical',epoch=epoch,name=r['name'],pid=r['pid']))
assert len(groups)==93
for campaign in selection['campaigns']:
 r=load('performance-'+campaign['version']);assert len(r['starts'])==len(r['exits'])==12 and all(v['code']==0 for v in r['exits'])
 groups += [dict(kind='timing',epoch=campaign['version'],name=x['arm'],pid=x['pid']) for x in r['starts']]
assert len(groups)==len({r['pid'] for r in groups})==93+12*len(selection['campaigns'])
for r in groups:
 try:os.killpg(r['pid'],0)
 except ProcessLookupError:r['empty']=True
 else:raise AssertionError(('group alive',r))
for pid in attempt['controllers_stopped']:
 try:os.kill(pid,0)
 except ProcessLookupError:pass
 else:raise AssertionError(('controller alive',pid))
e.write(O/'process-closure-v1.json',dict(pass_all=True,node=platform.node(),supervisor_pid=attempt['controllers_stopped'][-1],supervisor_exited=True,controllers_stopped=attempt['controllers_stopped'],logical_stages=92,physical_canonical_groups=93,preserved_failed_attempts=1,groups=groups,script_sha256=sha(Path(__file__)),time_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())),before)
print('All original/resumed canonical and timing groups/two controllers exited')
