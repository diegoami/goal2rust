"""Three quiet four-arm rounds, rotated physical cores/order; exclusive outputs."""
import json,os,statistics,subprocess,sys,time
from pathlib import Path
BASE=Path(__file__).resolve().parents[2];OUT=BASE/'out/T23'
ATTEMPT=int(sys.argv[1]) if len(sys.argv)>1 else 2
assert ATTEMPT>=2
VERSION='v'+str(ATTEMPT)
import hashlib
import evidence as e
if os.getpgrp()!=os.getpid():os.setsid()
e.verify();assert not e.BASELINE
base_before=e.hashes();assert base_before==json.loads((OUT/'freeze-v1.json').read_text())['source_sha256']
manifest_path=OUT/'performance-resume-inputs-v2.json'
manifest=json.loads(manifest_path.read_text());manifest_sha=hashlib.sha256(manifest_path.read_bytes()).hexdigest()
def supplement():
 for field in ['source_sha256','input_sha256']:
  for path,expected in manifest[field].items():assert hashlib.sha256((BASE/path).read_bytes()).hexdigest()==expected,path
 assert hashlib.sha256(manifest_path.read_bytes()).hexdigest()==manifest_sha
supplement();assert json.loads((OUT/'process-closure-v1.json').read_text())['pass_all']
assert not (OUT/f'performance-{VERSION}.json').exists()
allowed=sorted(os.sched_getaffinity(0));cores=[];seen=set();topology={}
for cpu in allowed:
 p=Path(f'/sys/devices/system/cpu/cpu{cpu}/topology');key=((p/'physical_package_id').read_text().strip(),(p/'core_id').read_text().strip())
 topology[str(cpu)]=dict(package=key[0],core=key[1],siblings=(p/'thread_siblings_list').read_text().strip())
 if key not in seen:seen.add(key);cores.append(cpu)
assert len(cores)>=4;cores=cores[:4]
observations=[];starts=[];exits=[];monitor=[];quality=[]
def journal(row):
 with (OUT/f'timing-jobs-{VERSION}.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
for round_index in range(3):
 quiet=0
 while quiet<3:
  loads=os.getloadavg();quiet=quiet+1 if max(loads[:2])<4 else 0;observations.append(dict(round=round_index+1,time=time.time(),load=loads,quiet=quiet))
  if quiet<3:time.sleep(10)
 assignments={'baseline':cores[round_index%2],'candidate':cores[1-round_index%2],'python':cores[2+round_index%2],'pypy':cores[3-round_index%2]}
 arms=['baseline','candidate','python','pypy'] if round_index%2==0 else ['candidate','baseline','pypy','python'];jobs=[]
 for name in arms:
  env=dict(os.environ,PYTHONHASHSEED='0',GOAL2RUST_BASELINE='1' if name=='baseline' else '0',GOAL2RUST_FAST='1')
  interpreter=BASE/('.venv-pypy/bin/python' if name=='pypy' else '.venv/bin/python');backend='python' if name in ['python','pypy'] else 'rust'
  receipt=OUT/f'cpu-{name}-r{round_index+1}-{VERSION}.json';assert not receipt.exists()
  log=(OUT/f'cpu-{name}-r{round_index+1}-{VERSION}.log').open('x')
  cmd=['taskset','-c',str(assignments[name]),str(interpreter),'-B','out/T23/run_receipt.py','--backend',backend,'--mode','cpu','--out',str(receipt)]
  child=subprocess.Popen(cmd,cwd=BASE,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);jobs.append((name,child,log))
  starts.append(dict(round=round_index+1,arm=name,pid=child.pid,cpu=assignments[name],time=time.time(),command=cmd));journal(dict(event='start',**starts[-1]));print('START',round_index+1,name,child.pid,flush=True)
 while any(p.poll() is None for _,p,_ in jobs):
  monitor.append(dict(round=round_index+1,time=time.time(),load=os.getloadavg(),active=[name for name,p,_ in jobs if p.poll() is None]));time.sleep(5)
 for name,p,log in jobs:
  code=p.wait();log.close();exits.append(dict(round=round_index+1,arm=name,pid=p.pid,code=code,time=time.time()));journal(dict(event='exit',**exits[-1]));assert code==0,(round_index,name,code)
 rows={name:json.loads((OUT/f'cpu-{name}-r{round_index+1}-{VERSION}.json').read_text()) for name in arms}
 for key in ['oracle','input_state_sha256','events','events_sha256','result_sha256','records_sha256','memory_sha256','stretches']:
  assert all(r[key]==rows['candidate'][key] for r in rows.values()),(round_index,key)
 assert all(rows[arm]['bridge_fast_calls'] and all(v>0 for v in rows[arm]['bridge_fast_calls'].values()) for arm in ['baseline','candidate'])
 quiet_ends=all(max(row['load_before'][:2])<4 and max(row['load_after'][:2])<4 for row in rows.values())
 quiet_trace=all(max(row['load'][:2])<8 for row in monitor if row['round']==round_index+1)
 quality.append(dict(round=round_index+1,all_arm_ends_quiet=quiet_ends,continuous_total_load_below8=quiet_trace))
 print('ROUND',round_index+1,{name:r['drive_cpu_s'] for name,r in rows.items()},flush=True)
ratios=[];samples=[]
for r in range(1,4):
 rows={name:json.loads((OUT/f'cpu-{name}-r{r}-{VERSION}.json').read_text()) for name in ['baseline','candidate','python','pypy']}
 ratio=rows['candidate']['drive_cpu_s']/rows['baseline']['drive_cpu_s'];ratios.append(ratio)
 samples.append(dict(round=r,cpu_s={name:row['drive_cpu_s'] for name,row in rows.items()},candidate_to_baseline=ratio,baseline_to_pypy=rows['baseline']['drive_cpu_s']/rows['pypy']['drive_cpu_s'],cpython_to_candidate=rows['python']['drive_cpu_s']/rows['candidate']['drive_cpu_s'],candidate_to_pypy=rows['candidate']['drive_cpu_s']/rows['pypy']['drive_cpu_s']))
supplement();assert base_before==e.hashes()
report=dict(attempt=ATTEMPT,pid=os.getpid(),pgid=os.getpgrp(),quiet_complete=all(r['all_arm_ends_quiet'] and r['continuous_total_load_below8'] for r in quality),quiet_quality=quality,continuous_load=monitor,supplemental_source_sha256=manifest['source_sha256'],supplemental_input_sha256=manifest['input_sha256'],source_manifest_sha256=manifest_sha,base_source_sha256=base_before,source_unchanged=True,outputs_equal=True,incremental_port_no_magnitude_minimum=True,rounds=samples,ratios=ratios,median_ratio=statistics.median(ratios),median_baseline_to_pypy=statistics.median(r['baseline_to_pypy'] for r in samples),median_candidate_to_pypy=statistics.median(r['candidate_to_pypy'] for r in samples),median_cpython_to_candidate=statistics.median(r['cpython_to_candidate'] for r in samples),all_rounds_improve=all(r<1 for r in ratios),measurement_complete=True,quiet_observations=observations,starts=starts,exits=exits,topology=topology,selected_physical_cores=cores)
with (OUT/f'performance-{VERSION}.json').open('x') as f:json.dump(report,f,indent=2)
assert report['outputs_equal'] and len(report['rounds'])==3
print('ALL THREE MEASURED OUTCOMES RETAINED',report['median_ratio'],'QUIET_ACCEPTED',report['quiet_complete'],flush=True)
