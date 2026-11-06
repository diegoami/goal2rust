"""Exclusive development pipeline after genuine capture; stops at first failure.

No canonical freeze,final acceptance,merge or post-writer audit is performed.
"""
import fcntl,hashlib,json,os,subprocess,time
from pathlib import Path
import capture_support as pure
from host_gate import wait_idle
B=pure.BASE;O=B/'out/T29';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def sources():
 files=set(O.glob('*.py'))|set(O.glob('*.rs'))|set((B/'engine/src').glob('*.rs'))|set((B/'engine/tests').glob('*.py'))|set((B/'engine/python').rglob('*.py'))
 files.update(B/'engine'/n for n in ['Cargo.toml','Cargo.lock','pyproject.toml'])
 return {str(p.relative_to(B)):sha(p) for p in sorted(files)}
def journal(row):
 with (O/'development-jobs-v1.jsonl').open('a') as f:f.write(json.dumps(dict(time=time.time(),**row),sort_keys=True)+'\n')
def main():
 pure.verify();assert not (O/'development-controller-v1.json').exists() and not (O/'development-jobs-v1.jsonl').exists()
 lock=(B/'.cache/T29-development.lock').open('a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);lock.seek(0);lock.truncate();lock.write(str(os.getpid()));lock.flush()
 initial=sources();archive=B/'.cache/T29-development-controller-sources';archive.mkdir(exist_ok=True);saved={}
 for path,h in initial.items():
  dest=archive/h
  if not dest.exists():
   with dest.open('xb') as f:f.write((B/path).read_bytes())
  assert sha(dest)==h;saved[path]=str(dest.relative_to(B))
 journal(dict(event='controller',pid=os.getpid(),source_sha256=initial,preserved_source_map=saved))
 while not (O/'captures-v1.json').exists():
  pid=int((B/'.cache/T29-capture.lock').read_text());cmd=Path(f'/proc/{pid}/cmdline')
  assert cmd.exists() and b'out/T29/capture.py' in cmd.read_bytes(),'Capture exited without receipt; preserve its log/shards'
  print('WAIT GENUINE CAPTURE',pid,flush=True);time.sleep(20)
 cap=json.loads((O/'captures-v1.json').read_text());pid=cap['pid']
 while Path(f'/proc/{pid}/cmdline').exists() and Path(f'/proc/{pid}/cmdline').read_bytes():
  assert b'out/T29/capture.py' in Path(f'/proc/{pid}/cmdline').read_bytes(),'Capture PID reused'
  time.sleep(2)
 assert sources()==initial
 cp=str(B/'.venv/bin/python');pp=str(B/'.venv-pypy/bin/python');mat=str(B/'.venv/bin/maturin')
 env=dict(os.environ,PYTHONHASHSEED='0',PYTHONPATH=os.pathsep.join([str(B/'engine/python'),str(pure.ORACLE/'runtime')]),VIRTUAL_ENV=str(B/'.venv'))
 processes=[]
 def run(name,command,expected=0,allow_wiring=False,**extra):
  wait_idle();before=sources();assert before==current[0],('Source changed before stage',name)
  with (O/(name+'.log')).open('x') as log:
   child=subprocess.Popen(command,cwd=B,env=dict(env,**extra),stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
   journal(dict(event='start',name=name,pid=child.pid,command=command));print('START',name,child.pid,flush=True);code=child.wait()
  journal(dict(event='exit',name=name,pid=child.pid,code=code));processes.append(dict(name=name,pid=child.pid,code=code));print('EXIT',name,code,flush=True)
  assert code==expected,('Development stage failed; preserve epoch/log/journal',name,code,expected)
  after=sources()
  if allow_wiring:
   changed={p for p in set(before)|set(after) if before.get(p)!=after.get(p)};assert changed=={'engine/src/lib.rs','engine/src/machine.rs','engine/src/near_zone.rs','engine/tests/test_near_zone.py'},changed
   wiring_map={}
   for path,h in after.items():
    dest=archive/h
    if not dest.exists():
     with dest.open('xb') as f:f.write((B/path).read_bytes())
    assert sha(dest)==h;wiring_map[path]=str(dest.relative_to(B))
   journal(dict(event='wiring-source-epoch',source_sha256=after,preserved_source_map=wiring_map));current[0]=after
  else:assert after==before,('Source changed while stage ran',name)
 current=[initial]
 run('capture-input-audit-v1',[cp,'-B','out/T29/capture_input_audit.py'])
 run('before-native-v1',[cp,'-B','-m','unittest','discover','-s','out/T29','-p','test_near_zone.py','-k','test_complete_native_body','-v'],expected=1)
 negative=(O/'before-native-v1.log').read_text();assert 'AssertionError: None != 1' in negative and 'Ran 1 test' in negative
 run('apply-native-v1',[cp,'-B','out/T29/apply_native.py'],allow_wiring=True)
 run('build-cpython-development-v1',[mat,'develop','--release','--locked','--manifest-path','engine/Cargo.toml'])
 run('near-zone-development-v1',[cp,'-B','-m','unittest','discover','-s','engine/tests','-p','test_near_zone.py','-v'])
 run('development-probe-v1',[cp,'-B','out/T29/development_probe.py'])
 run('public-cpython-development-v1',[cp,'-B','-m','unittest','discover','-s','engine/tests','-v'])
 run('rust-development-v1',['cargo','test','--locked','--manifest-path','engine/Cargo.toml'])
 wheels=B/'.cache/T29-development-pypy-wheels-v1';assert not wheels.exists()
 run('build-pypy-development-v1',[mat,'build','--release','--locked','--manifest-path','engine/Cargo.toml','--interpreter',pp,'--out',str(wheels)])
 paths=sorted(wheels.glob('*.whl'));assert len(paths)==1
 run('install-pypy-development-v1',[pp,'-m','pip','install','--no-index','--no-deps','--force-reinstall',str(paths[0])])
 run('public-pypy-development-v1',[pp,'-B','-m','unittest','discover','-s','engine/tests','-v'],PYTHONPATH=str(pure.ORACLE/'runtime'))
 for label in ['cpython','pypy']:
  text=(O/f'public-{label}-development-v1.log').read_text();assert 'Ran 110 tests' in text and text.rstrip().endswith('OK')
 report=dict(pass_all=True,development_only=True,accepted_canonical_evidence=False,controller_pid=os.getpid(),processes=processes,initial_source_sha256=initial,initial_preserved_source_map=saved,final_source_sha256=current[0],source_unchanged_after_wiring=sources()==current[0],next='Live callback matrix and sealed positive proof plan required before final combined campaign')
 with (O/'development-controller-v1.json').open('x') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
 print('Development complete; live matrix/proof-plan/final artifact campaign still required',flush=True)
if __name__=='__main__':main()
