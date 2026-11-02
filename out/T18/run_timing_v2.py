"""Full timing campaign recovery; no partial round replacement."""
import fcntl,hashlib,json,os,subprocess,time
import evidence_v3 as e
e.verify();out=e.BASE/'out/T18'
original=json.loads((out/'freeze-v2.json').read_text())['source_sha256']
assert all(hashlib.sha256((e.BASE/p).read_bytes()).hexdigest()==h for p,h in original.items())
lock=(e.BASE/'.cache/T18-timing-v2.lock').open('a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);lock.seek(0);lock.truncate();lock.write(str(os.getpid()));lock.flush()
assert not (out/'performance-v2.json').exists() and not (out/'jobs-v3.jsonl').exists()
command=[str(e.BASE/'.venv/bin/python'),'-u','-B','out/T18/producer_v3.py','performance_v2.py']
with (out/'performance-v2.log').open('x') as log:
 p=subprocess.Popen(command,cwd=e.BASE,env=dict(os.environ,PYTHONHASHSEED='0'),stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 with (out/'jobs-v3.jsonl').open('a') as f:f.write(json.dumps(dict(event='start',name='performance-v2',pid=p.pid,command=command,time=time.time()))+'\n')
 code=p.wait()
 with (out/'jobs-v3.jsonl').open('a') as f:f.write(json.dumps(dict(event='exit',name='performance-v2',pid=p.pid,code=code,time=time.time()))+'\n')
 assert code==0,code
print('Full replacement timing campaign exited; run actual-host v3 audits',flush=True)
