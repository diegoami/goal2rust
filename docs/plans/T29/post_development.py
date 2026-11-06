"""Exclusive continuation after the current T29 development controller exits.

This installs prepared proof templates, then runs live development and preseal
plan gates. It does not build, freeze, run canonical producers or merge.
"""
import fcntl,hashlib,json,os,subprocess,sys,time
from pathlib import Path
B=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent;O=B/'out/T29'
sys.path.insert(0,str(O))
import capture_support as pure
from host_gate import wait_idle
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
TEMPLATES=('branch_probe.py','live_observers.py','plan_proofs.py','near_zone_differential.py')
def append(row):
 with (O/'post-development-jobs-v1.jsonl').open('a') as stream:stream.write(json.dumps(dict(time=time.time(),**row),sort_keys=True)+'\n')
def stopped(pid,marker):
 command=Path(f'/proc/{pid}/cmdline')
 if not command.exists():return True
 data=command.read_bytes()
 if not data:return True
 assert marker.encode() in data,('PID reused',pid)
 return False
def archive(mapping):
 folder=B/'.cache/T29-post-development-sources';folder.mkdir(exist_ok=True);saved={}
 for path,h in mapping.items():
  dest=folder/h
  if not dest.exists():
   with dest.open('xb') as stream:stream.write((B/path).read_bytes())
  assert sha(dest)==h;saved[path]=str(dest.relative_to(B))
 return saved
def hashes():
 files=set(O.glob('*.py'))|set(O.glob('*.rs'))|set((B/'engine/src').glob('*.rs'))|set((B/'engine/tests').glob('*.py'))|set((B/'engine/python').rglob('*.py'))|set((B/'engine/python').rglob('*.so'))
 files.update(B/'engine'/name for name in ['Cargo.toml','Cargo.lock','pyproject.toml'])
 files.update(P/name for name in TEMPLATES);files.add(Path(__file__))
 return {str(p.relative_to(B)):sha(p) for p in sorted(files)}
def main():
 pure.verify();assert not (O/'post-development-jobs-v1.jsonl').exists() and not (O/'post-development-v1.json').exists()
 lock=(B/'.cache/T29-post-development.lock').open('a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);lock.seek(0);lock.truncate();lock.write(str(os.getpid()));lock.flush()
 pid=int((B/'.cache/T29-development.lock').read_text());initial={str(p.relative_to(B)):sha(p) for p in [Path(__file__),*(P/name for name in TEMPLATES)]}
 append(dict(event='controller',pid=os.getpid(),dependency_pid=pid,template_sha256=initial,preserved_source_map=archive(initial)))
 while not (O/'development-controller-v1.json').exists():
  assert not stopped(pid,'out/T29/develop.py'),'Development exited without success receipt; preserve failure epoch'
  print('WAIT EXISTING DEVELOPMENT',pid,flush=True);time.sleep(20)
 while not stopped(pid,'out/T29/develop.py'):time.sleep(2)
 report=json.loads((O/'development-controller-v1.json').read_text());assert report['pass_all'] and report['source_unchanged_after_wiring'] and report['controller_pid']==pid
 for path,h in report['final_source_sha256'].items():assert sha(B/path)==h,path
 for path,h in initial.items():assert sha(B/path)==h,path
 for name in TEMPLATES:
  with (O/name).open('xb') as stream:stream.write((P/name).read_bytes())
 before=hashes();saved=archive(before);append(dict(event='source-epoch',source_sha256=before,preserved_source_map=saved,development_controller_stopped=pid))
 cp=str(B/'.venv/bin/python');env=dict(os.environ,PYTHONHASHSEED='0',PYTHONPATH=os.pathsep.join([str(B/'engine/python'),str(pure.ORACLE/'runtime')]))
 jobs=[]
 for name,command in [('live-development-v1',[cp,'-u','-B','out/T29/live_observers.py','--development','--out','out/T29/live-development-v1.json']),('plan-proofs-v1',[cp,'-u','-B','out/T29/plan_proofs.py','--out','out/T29/proof-plan-v1.json'])]:
  wait_idle();assert hashes()==before
  with (O/(name+'.log')).open('x') as stream:
   child=subprocess.Popen(command,cwd=B,env=env,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
   append(dict(event='start',name=name,pid=child.pid,command=command));print('START',name,child.pid,flush=True);code=child.wait()
  row=dict(name=name,pid=child.pid,code=code);jobs.append(row);append(dict(event='exit',**row));print('EXIT',name,code,flush=True)
  assert code==0,('Failed post-development stage; preserve source/artifact/log/journal epoch before versioned retry',name,code)
  assert hashes()==before
 live=json.loads((O/'live-development-v1.json').read_text());assert live['pass_all'] and live['comparisons']==800 and len(live['scenarios'])==5
 assert all(row['comparisons']==row['effect_witnesses']==160 and row['hits'] and all(row['hits'].values()) for row in live['scenarios'].values())
 plan=json.loads((O/'proof-plan-v1.json').read_text());assert plan['distinct_error_selectors']==len(plan['preseal_reached_errors'])>0
 assert len(plan['branch_outcomes'])==8
 result=dict(pass_all=True,development_only=True,accepted_canonical_evidence=False,controller_pid=os.getpid(),development_controller_stopped=pid,jobs=jobs,source_sha256=before,preserved_source_map=saved,source_unchanged=hashes()==before,live_comparisons=800,distinct_error_selectors=plan['distinct_error_selectors'],branch_outcomes=plan['branch_outcomes'],next='Prepare fresh combined-artifact final harness; retain every prior87-body proof/12 live matrices and full task gates')
 with (O/'post-development-v1.json').open('x') as stream:json.dump(result,stream,indent=2,sort_keys=True);stream.write('\n')
 print('Live development and positive preseal plan complete; canonical acceptance still required',flush=True)
if __name__=='__main__':main()
