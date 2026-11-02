"""Resume same fixed artifact after rejected outside-helper probe configuration."""
import fcntl,hashlib,json,os,subprocess,sys,time
from pathlib import Path
import evidence_v2 as e
OUT=e.BASE/'out/T18';PY=str(e.BASE/'.venv/bin/python');e.verify()
lock=(e.BASE/'.cache/T18-supervisor-v2.lock').open('a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);lock.seek(0);lock.truncate();lock.write(str(os.getpid()));lock.flush()
original=json.loads((OUT/'freeze-v1.json').read_text())['source_sha256']
assert all(hashlib.sha256((e.BASE/p).read_bytes()).hexdigest()==h for p,h in original.items())
assert json.loads((OUT/'outside-probe-disposition-v1.json').read_text())['production_changed'] is False
jobs={}
def append(row):
 with (OUT/'jobs-v2.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
def start(name,script,flags=(),receipt=None,env_extra=None):
 target=OUT/(receipt or name+'.json')
 if target.exists():
  r=json.loads(target.read_text());assert r['source_unchanged']
  for p,h in r['source_sha256'].items():assert hashlib.sha256((e.BASE/p).read_bytes()).hexdigest()==h,p
  print('ALREADY COMPLETE',name,flush=True);return
 log=(OUT/(name+'.log')).open('a');command=[PY,'-u','-B','out/T18/producer_v2.py',script,*flags]
 p=subprocess.Popen(command,cwd=e.BASE,env=dict(os.environ,PYTHONHASHSEED='0',**(env_extra or {})),stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 jobs[name]=(p,log);append(dict(event='start',name=name,pid=p.pid,command=command,time=time.time()));print('START',name,p.pid,flush=True)
def wait(names):
 previous=0
 while any(n in jobs for n in names):
  for name in list(jobs):
   p,log=jobs[name];code=p.poll()
   if code is not None:log.close();del jobs[name];append(dict(event='exit',name=name,pid=p.pid,code=code,time=time.time()));print('EXIT',name,code,flush=True);assert code==0,name
  family=OUT/'family-ALL-rust-v1.jsonl';lines=family.read_bytes().splitlines(keepends=True) if family.exists() else [];n=sum(x.endswith(b'\n') for x in lines)
  for count in (10,20,30,60):
   if n>=count and not (OUT/f'compare-progress-{count}-v1.json').exists():
    if not (OUT/f'family-progress-{count}-v1.json').exists():subprocess.run([PY,'-B','out/T18/producer_v2.py','progress_snapshot.py',str(count)],check=True)
    subprocess.run([PY,'-B','out/T18/producer_v2.py','compare_progress.py',str(count)],check=True)
  if time.monotonic()-previous>30:print('PROGRESS',n,'/75;',','.join(jobs),flush=True);previous=time.monotonic()
  if any(n in jobs for n in names):time.sleep(5)
for suite in ('normal','body','output','returns'):
 name='destination-'+suite+'-v2';start(name,'destination_differential_v2.py',['--suite',suite,'--out','out/T18/'+name+'.json']);wait([name])
for name,script in [('prior-live-observers-v1','prior_live_observers.py'),('live-observers-v1','live_observers.py')]:start(name,script,['--out','out/T18/'+name+'.json']);wait([name])
start('taps-rust-v1','run_receipt.py',['--backend','rust','--mode','taps','--out','out/T18/taps-rust-v1.json']);wait(['taps-rust-v1'])
quiet=0
while quiet<3:
 load=os.getloadavg();quiet=quiet+1 if max(load[:2])<4 else 0;print('QUIET GATE',load,quiet,'/3',flush=True)
 if quiet<3:time.sleep(10)
start('family-ALL-v1','run_family.py',['--out','out/T18/family-ALL-rust-v1.jsonl','--attest','out/T18/attest-family-ALL-v1'],'attest-family-ALL-v1-invocation.json')
extra=dict(GOAL2RUST_T18='1',GOAL2RUST_T18_ATTEST='out/T18/attest-check-v1',PYTHONPATH=os.pathsep.join([str(OUT),str(e.BASE/'engine/python'),str(e.ORACLE/'runtime')]))
start('check-v1','run_check.py',['--out','out/T18/check-v1.json'],env_extra=extra)
start('profile-after-v1','profile_machine.py',['--out','out/T18/profile-after-v1.json']);wait(['family-ALL-v1','check-v1','profile-after-v1'])
if not (OUT/'compare-F40-v1.status.json').exists():subprocess.run([PY,'-B','out/T18/producer_v2.py','finish_family.py'],check=True)
start('performance-v1','performance.py');wait(['performance-v1'])
print('ALL V2 WRITERS EXITED; run actual-host shutdown/final audits after this controller exits',flush=True)
