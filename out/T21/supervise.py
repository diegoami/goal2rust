"""Exclusive state-v2 compatibility producers. No final index while this writer runs."""
import fcntl,hashlib,json,os,subprocess,sys,time
import evidence as e
OUT=e.BASE/'out/T21';PY=str(e.BASE/'.venv/bin/python');e.verify();assert json.loads((OUT/'freeze-v1.json').read_text())['source_sha256']==e.hashes()
lock=(e.BASE/'.cache/T21-supervisor.lock').open('a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
lock.seek(0);lock.truncate();lock.write(str(os.getpid()));lock.flush();jobs={}
def append(row):
    with (OUT/'jobs-v1.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
def launch(name,args,receipt=None,extra=None):
    path=OUT/(receipt or name+'.json')
    if path.exists():
        row=json.loads(path.read_text())
        bound=[row]
        if name=='performance-v1':
            assert row['measurement_complete'] and row['outputs_equal'] and len(row['rounds'])==3 and len(row['exits'])==12 and all(v['code']==0 for v in row['exits'])
            bound=[json.loads((OUT/f'cpu-{arm}-r{rnd}-v1.json').read_text()) for rnd in range(1,4) for arm in ['baseline','candidate','python','pypy']]
        for record in bound:
            assert record['source_unchanged']
            for p,sha in record['source_sha256'].items():assert hashlib.sha256((e.BASE/p).read_bytes()).hexdigest()==sha,(name,p)
        print('ALREADY COMPLETE',name,flush=True);return
    log=(OUT/(name+'.log')).open('a');env=dict(os.environ,PYTHONHASHSEED='0',**(extra or {}))
    child=subprocess.Popen(args,env=env,cwd=e.BASE,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    jobs[name]=(child,log,e.hashes());append(dict(event='start',name=name,pid=child.pid,command=args,time=time.time()));print('START',name,child.pid,flush=True)
pending=[]
def start(name,args,receipt=None,extra=None):pending.append((name,args,receipt,extra))
def wait(names):pass
def producer(name,script,*args):start(name,[PY,'-u','-B','out/T21/'+script,*args,'--out','out/T21/'+name+'.json'])
def drain(limit):
    failed=[];previous=0
    while pending or jobs:
        while pending and len(jobs)<limit and not failed:launch(*pending.pop(0))
        for n in list(jobs):
            child,log,before=jobs[n];code=child.poll()
            if code is not None:
                log.close();del jobs[n];append(dict(event='exit',name=n,pid=child.pid,code=code,time=time.time()));print('EXIT',n,code,flush=True)
                if n in ['public-cpython-v1','public-pypy-v1','rust-unit-v1']:e.write(OUT/(n+'.status.json'),dict(exit_code=code),before)
                if code:failed.append((n,code))
        family=OUT/'family-ALL-rust-v1.jsonl'
        if family.exists():
            count=len(family.read_bytes().splitlines())
            for n in [10,20,30,60]:
                if count>=n and not (OUT/f'compare-progress-{n}-v1.json').exists():
                    if not (OUT/f'family-progress-{n}-v1.json').exists():subprocess.run([PY,'-B','out/T21/progress_snapshot.py',str(n)],check=True)
                    subprocess.run([PY,'-B','out/T21/compare_progress.py',str(n)],check=True)
        if time.monotonic()-previous>30:print('ACTIVE',','.join(jobs),'PENDING',len(pending),flush=True);previous=time.monotonic()
        if failed and not jobs:raise AssertionError(('Rejected stages; completed workers retained',failed))
        if pending or jobs:time.sleep(5)
start('public-cpython-v1',[PY,'-m','unittest','discover','-s','engine/tests','-v'],'public-cpython-v1.status.json',extra=dict(PYTHONPATH=str(e.BASE/'engine/python')+os.pathsep+str(e.ORACLE/'runtime')))
start('public-pypy-v1',[str(e.BASE/'.venv-pypy/bin/python'),'-m','unittest','discover','-s','engine/tests','-v'],'public-pypy-v1.status.json',extra=dict(PYTHONPATH=str(e.ORACLE/'runtime')))
start('gc-parity-v1',[PY,'-B','out/T21/gc_parity.py'])
start('observer-matrix-v2',[PY,'-B','out/T21/observer_matrix.py'])
start('rust-unit-v1',[str(e.BASE/'.cache/cargo/bin/cargo'),'test','--locked','--manifest-path','engine/Cargo.toml'],'rust-unit-v1.status.json',extra=dict(CARGO_HOME=str(e.BASE/'.cache/cargo'),RUSTUP_HOME=str(e.BASE/'.cache/rustup'),PATH=str(e.BASE/'.cache/cargo/bin')+os.pathsep+os.environ['PATH']))
producer('taps-python-v1','run_receipt.py','--backend','python','--mode','taps')
for name,flags in [('legacy-v1',[]),('legacy-body-v1',['--body-mutant','1'])]:
    producer(name,'run_legacy.py',*flags);wait([name])
for suite,controls in [('availability',[0,2,1]),('ball',[0,3,4]),('skill',[0,5,6])]:
    for mutant in controls:
        name=f'{suite}-'+('differential' if mutant==0 else 'body' if mutant==controls[1] else 'return')+'-v1'
        producer(name,'run_tree.py','--suite',suite,'--mutant',str(mutant));wait([name])
for mutant,label in [(0,'differential'),(7,'body'),(8,'root-return'),(9,'seed-return')]:
    name=f'speaker-{label}-v1';producer(name,'speaker_differential.py','--mutant',str(mutant));wait([name])
for mutant,label in [(0,'differential'),(10,'body'),(11,'return')]:
    name=f'keys-{label}-v1';producer(name,'keys_differential.py','--mutant',str(mutant));wait([name])
for mutant,label in [(0,'differential'),(12,'body'),(13,'return')]:
    name=f'draw-{label}-v1';producer(name,'draw_differential.py','--mutant',str(mutant));wait([name])
for mutant,label in [(0,'differential'),(16,'body'),(17,'return')]:
    name=f'sweep-{label}-v1';producer(name,'sweep_differential.py','--mutant',str(mutant));wait([name])
for mutant,label in [(0,'differential'),(18,'body'),(19,'return')]:
    name=f'play-{label}-v1';producer(name,'play_differential.py','--mutant',str(mutant));wait([name])
for mutant,label in [(0,'differential'),(20,'body'),(21,'return')]:
    name=f'update-{label}-v1';producer(name,'update_differential.py','--mutant',str(mutant));wait([name])
for mutant,label in [(0,'differential'),(22,'body'),(23,'return')]:
    name=f'sprite-{label}-v1';producer(name,'sprite_differential.py','--mutant',str(mutant));wait([name])
for mutant,label in [(0,'differential'),(24,'body'),(25,'position')]:
    name=f'run-{label}-v1';producer(name,'run_step_differential.py','--mutant',str(mutant));wait([name])
for suite in ['normal','body','output','returns']:
    name='marking-'+suite+'-v1';producer(name,'marking_differential.py','--suite',suite);wait([name])
for suite in ['normal','body','output','returns']:
    name='destination-'+suite+'-v1';producer(name,'destination_differential.py','--suite',suite);wait([name])
for suite in ['normal','body','output','returns']:
    name='depth-'+suite+'-v1';producer(name,'depth_differential.py','--suite',suite);wait([name])
producer('prior-destination-live-observers-v1','prior_destination_live_observers.py');wait(['prior-destination-live-observers-v1'])
producer('prior-live-observers-v1','prior_live_observers.py');wait(['prior-live-observers-v1'])
producer('prior-depth-live-observers-v1','prior_depth_live_observers.py');wait(['prior-depth-live-observers-v1'])
producer('scoped-write-errors-v1','prior_scoped_write_errors.py');wait(['scoped-write-errors-v1'])
for suite in ['normal','body','output','returns']:
    name='chase-'+suite+'-v1';producer(name,'chase_differential.py','--suite',suite);wait([name])
producer('prior-chase-live-observers-v1','prior_chase_live_observers.py');wait(['prior-chase-live-observers-v1'])
for suite in ['normal','body','output','returns']:
    name='travel-'+suite+'-v1';producer(name,'travel_differential.py','--suite',suite);wait([name])
producer('live-observers-v1','live_observers.py');wait(['live-observers-v1'])
drain(3)
producer('taps-rust-v1','run_receipt.py','--backend','rust','--mode','taps');drain(1)
quiet=0
while quiet<3:
    loads=os.getloadavg();quiet=quiet+1 if max(loads[:2])<4 else 0
    print('WAIT FOR QUIET HOST',loads,quiet,'/3',flush=True)
    if quiet<3:time.sleep(10)
start('family-ALL-v1',[PY,'-B','out/T21/run_family.py','--out','out/T21/family-ALL-rust-v1.jsonl','--attest','out/T21/attest-family-ALL-v1'],'attest-family-ALL-v1-invocation.json')
extra=dict(GOAL2RUST_T21='1',GOAL2RUST_T21_ATTEST='out/T21/attest-check-v1',PYTHONPATH=os.pathsep.join([str(OUT),str(e.BASE/'engine/python'),str(e.ORACLE/'runtime')]))
start('check-v1',[PY,'-B','out/T21/run_check.py','--out','out/T21/check-v1.json'],extra=extra)
producer('profile-after-v1','profile_machine.py');drain(3)
if not (OUT/'compare-F40-v1.status.json').exists():subprocess.run([PY,'-B','out/T21/finish_family.py'],check=True)
start('performance-v1',[PY,'-u','-B','out/T21/performance.py'])
drain(1)
print('ALL PRODUCERS EXITED; run post-exit audit after this writer exits',flush=True)
