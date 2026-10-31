"""Exclusive state-v2 compatibility producers. No final index while this writer runs."""
import fcntl,hashlib,json,os,subprocess,sys,time
import evidence as e
OUT=e.BASE/'out/T07';PY=str(e.BASE/'.venv/bin/python');e.verify()
lock=(e.BASE/'.cache/T07-supervisor.lock').open('a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
lock.seek(0);lock.truncate();lock.write(str(os.getpid()));lock.flush();jobs={}
def append(row):
    with (OUT/'jobs-v1.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
def start(name,args,receipt=None,extra=None):
    path=OUT/(receipt or name+'.json')
    if path.exists():
        row=json.loads(path.read_text());assert row['source_unchanged']
        for p,sha in row['source_sha256'].items():assert hashlib.sha256((e.BASE/p).read_bytes()).hexdigest()==sha,(name,p)
        print('ALREADY COMPLETE',name,flush=True);return
    log=(OUT/(name+'.log')).open('a');env=dict(os.environ,PYTHONHASHSEED='0',**(extra or {}))
    child=subprocess.Popen(args,env=env,cwd=e.BASE,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    jobs[name]=(child,log);append(dict(event='start',name=name,pid=child.pid,command=args,time=time.time()));print('START',name,child.pid,flush=True)
def wait(names):
    previous=0
    while any(n in jobs for n in names):
        for n in list(jobs):
            p,log=jobs[n];code=p.poll()
            if code is not None:
                log.close();del jobs[n];append(dict(event='exit',name=n,pid=p.pid,code=code,time=time.time()));print('EXIT',n,code,flush=True);assert code==0,n
        if time.monotonic()-previous>30:
            p=OUT/'family-ALL-rust-v1.jsonl';count=len(p.read_bytes().splitlines()) if p.exists() else 0
            print('PROGRESS',count,'/75;',','.join(jobs),flush=True);previous=time.monotonic()
        if any(n in jobs for n in names):time.sleep(5)
def producer(name,script,*args):start(name,[PY,'-u','-B','out/T07/'+script,*args,'--out','out/T07/'+name+'.json'])
start('family-ALL-v1',[PY,'-B','out/T07/run_family.py','--out','out/T07/family-ALL-rust-v1.jsonl','--attest','out/T07/attest-family-ALL-v1'],'attest-family-ALL-v1-invocation.json')
extra=dict(GOAL2RUST_T07='1',GOAL2RUST_T07_ATTEST='out/T07/attest-check-v1',PYTHONPATH=os.pathsep.join([str(OUT),str(e.BASE/'engine/python'),str(e.ORACLE/'runtime')]))
start('check-v1',[PY,'-B','out/T07/run_check.py','--out','out/T07/check-v1.json'],extra=extra)
producer('taps-python-v1','run_receipt.py','--backend','python','--mode','taps')
for name,flags in [('legacy-v1',[]),('legacy-body-v1',['--body-mutant','1'])]:
    producer(name,'run_legacy.py',*flags);wait([name])
for suite,controls in [('availability',[0,2,1]),('ball',[0,3,4]),('skill',[0,5,6])]:
    for mutant in controls:
        name=f'{suite}-'+('differential' if mutant==0 else 'body' if mutant==controls[1] else 'return')+'-v1'
        producer(name,'run_tree.py','--suite',suite,'--mutant',str(mutant));wait([name])
wait(['taps-python-v1'])
producer('taps-rust-v1','run_receipt.py','--backend','rust','--mode','taps');wait(['taps-rust-v1'])
producer('profile-after-v1','profile_machine.py');wait(['profile-after-v1','check-v1','family-ALL-v1'])
if not (OUT/'compare-F40-v1.status.json').exists():subprocess.run([PY,'-B','out/T07/finish_family.py'],check=True)
quiet=0
while quiet<3:
    loads=os.getloadavg();quiet=quiet+1 if max(loads[:2])<4 else 0
    with (OUT/'quiet-v1.jsonl').open('a') as f:f.write(json.dumps(dict(time=time.time(),load=loads,quiet=quiet))+'\n')
    print('QUIET',loads,quiet,flush=True)
    if quiet<3:time.sleep(10)
for name,interpreter,backend in [('python',PY,'python'),('pypy',str(e.BASE/'.venv-pypy/bin/python'),'python'),('rust',PY,'rust')]:
    start('cpu-'+name+'-v1',[interpreter,'-B','out/T07/run_receipt.py','--backend',backend,'--mode','cpu','--out',f'out/T07/cpu-{name}-v1.json'])
wait(['cpu-python-v1','cpu-pypy-v1','cpu-rust-v1'])
print('ALL PRODUCERS EXITED; audit and validate after this writer exits',flush=True)
