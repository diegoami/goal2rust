"""Resume fixed T17 artifact after a classified generated-output metadata rejection.
Keep this driver outside out/T17's source glob until every canonical writer exits.
"""
import fcntl,hashlib,json,os,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/'out/T17'));import evidence as e
OUT=e.BASE/'out/T17';PY=str(e.BASE/'.venv/bin/python');e.verify()
lock=(e.BASE/'.cache/T17-recovery.lock').open('a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);lock.seek(0);lock.truncate();lock.write(str(os.getpid()));lock.flush()
freeze=json.loads((OUT/'freeze-v1.json').read_text())['source_sha256'];assert e.hashes()==freeze
reject=json.loads((OUT/'check-v1.json').read_text());assert reject['exit_code']==0 and not reject['source_unchanged'] and all(r['pass'] for r in reject['checks'].values())
disposition=json.loads((OUT/'profile-output-disposition-v1.json').read_text());assert disposition['restored_original_input_set'] and not disposition['changed_original_bindings']
assert hashlib.sha256((e.BASE/disposition['preserved']).read_bytes()).hexdigest()==disposition['sha256']
JOBS=OUT/'jobs-v2.jsonl';jobs=[]
def append(row):
 row['time']=time.time()
 with JOBS.open('a') as f:f.write(json.dumps(row)+'\n')
 jobs.append(row)
def empty_group(pgid):
 try:os.killpg(pgid,0)
 except ProcessLookupError:return True
 return False
def receipt(name):return json.loads((OUT/(name+'.json')).read_text())
def valid(name):
 r=receipt(name);assert r['source_unchanged'],name
 for p,h in r['source_sha256'].items():assert hashlib.sha256((e.BASE/p).read_bytes()).hexdigest()==h,(name,p)
 return r
assert not JOBS.exists(), 'Only resume this controller after inspecting its append-only ledger and completed receipts'
append(dict(event='adopt',name='family-ALL-v1',pid=16556,pgid=16556,original_ledger='jobs-v1.jsonl',basis='Original supervisor stopped on check-v1 metadata rejection; family producer continues unchanged.'))
append(dict(event='start',name='check-v2',pid=24006,pgid=24003,external_exec_session=79782,command=[PY,'-u','-B','out/T17/run_check.py','--out','out/T17/check-v2.json'],env=dict(GOAL2RUST_T17='1',GOAL2RUST_T17_ATTEST='out/T17/attest-check-v2',PYTHONHASHSEED='0')))
last=0
while True:
 p=OUT/'family-ALL-rust-v1.jsonl';lines=p.read_bytes().splitlines(keepends=True) if p.exists() else [];complete=[x for x in lines if x.endswith(b'\n')]
 for n in (10,20,30,60):
  if len(complete)>=n and not (OUT/f'compare-progress-{n}-v1.json').exists():
   if not (OUT/f'family-progress-{n}-v1.json').exists():subprocess.run([PY,'-B','out/T17/progress-snapshot.txt',str(n)],check=True)
   subprocess.run([PY,'-B','out/T17/compare-progress.txt',str(n)],check=True)
 family_ready=(OUT/'attest-family-ALL-v1-invocation.json').exists() and empty_group(16556)
 check_ready=(OUT/'check-v2.json').exists() and empty_group(24003)
 if time.monotonic()-last>30:print('RECOVERY PROGRESS',len(complete),'/75; family exited',family_ready,'check-v2 exited',check_ready,flush=True);last=time.monotonic()
 if family_ready and check_ready:break
 time.sleep(5)
f=valid('attest-family-ALL-v1-invocation');assert f['exit_code']==0
c=valid('check-v2');assert c['exit_code']==0 and all(r['pass'] for r in c['checks'].values())
append(dict(event='recovered-exit',name='family-ALL-v1',pid=16556,pgid=16556,code=0,status_basis='Source family CLI exit_code=0 sealed by fixed wrapper, unchanged sources, actual group empty; completion is independently rechecked below.'))
append(dict(event='exit',name='check-v2',pid=24006,pgid=24003,code=0,status_basis='Accepted receipt and empty actual group; external exec session exit is separately audited.'))
def run(name,args):
 log=(OUT/(name+'.log')).open('x');env=dict(os.environ,PYTHONHASHSEED='0')
 p=subprocess.Popen(args,cwd=e.BASE,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 append(dict(event='start',name=name,pid=p.pid,pgid=p.pid,command=args));print('START',name,p.pid,flush=True)
 code=p.wait();log.close();append(dict(event='exit',name=name,pid=p.pid,pgid=p.pid,code=code));print('EXIT',name,code,flush=True);assert code==0,name
 return p.pid
before_family_sha=hashlib.sha256((OUT/'family-ALL-rust-v1.jsonl').read_bytes()).hexdigest()
run('family-completion-v2',[PY,'-B','out/T17/run_family.py','--out','out/T17/family-ALL-rust-v1.jsonl','--attest','out/T17/attest-family-completion-v2'])
r=valid('attest-family-completion-v2-invocation');assert r['exit_code']==0
assert hashlib.sha256((OUT/'family-ALL-rust-v1.jsonl').read_bytes()).hexdigest()==before_family_sha
rows=[json.loads(x) for x in (OUT/'family-ALL-rust-v1.jsonl').read_bytes().splitlines()];assert len(rows)==75 and all(not r['error'] and r['stopped_at_board'] for r in rows)
assert not (OUT/'compare-ALL-v1.status.json').exists();subprocess.run([PY,'-B','out/T17/finish_family.py'],check=True)
run('performance-v1',[PY,'-u','-B','out/T17/performance.py'])
report=dict(pass_all=True,rejected_metadata_receipt='check-v1.json',accepted_lifecycle_receipt='check-v2.json',rejected_wrapper_code=1,original_frozen_bindings_unchanged=e.hashes()==freeze,family_rows=75,family_sha256=before_family_sha,completion_recheck_receipt='attest-family-completion-v2-invocation.json',original_supervisor_pid=10009,recovery_supervisor_pid=os.getpid(),recovery_supervisor_pgid=os.getpgrp(),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),jobs=jobs)
assert report['original_frozen_bindings_unchanged'];e.write(OUT/'recovery-v2.json',report,freeze);print('RECOVERY CANONICAL WRITERS COMPLETE; run supplemental proofs and actual-host shutdown audit after this controller exits',flush=True)
