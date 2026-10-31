"""Three quiet four-arm rounds, rotated physical cores/order; exclusive outputs."""
import json,os,statistics,subprocess,sys,time
from pathlib import Path
BASE=Path(__file__).resolve().parents[2];OUT=BASE/'out/T08'
assert not (OUT/'performance-v1.json').exists()
allowed=sorted(os.sched_getaffinity(0));cores=[];seen=set();topology={}
for cpu in allowed:
 p=Path(f'/sys/devices/system/cpu/cpu{cpu}/topology');key=((p/'physical_package_id').read_text().strip(),(p/'core_id').read_text().strip())
 topology[str(cpu)]=dict(package=key[0],core=key[1],siblings=(p/'thread_siblings_list').read_text().strip())
 if key not in seen:seen.add(key);cores.append(cpu)
assert len(cores)>=4;cores=cores[:4]
observations=[];starts=[];exits=[]
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
  receipt=OUT/f'cpu-{name}-r{round_index+1}-v1.json';assert not receipt.exists()
  log=(OUT/f'cpu-{name}-r{round_index+1}-v1.log').open('x')
  cmd=['taskset','-c',str(assignments[name]),str(interpreter),'-B','out/T08/run_receipt.py','--backend',backend,'--mode','cpu','--out',str(receipt)]
  child=subprocess.Popen(cmd,cwd=BASE,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);jobs.append((name,child,log))
  starts.append(dict(round=round_index+1,arm=name,pid=child.pid,cpu=assignments[name],time=time.time(),command=cmd));print('START',round_index+1,name,child.pid,flush=True)
 for name,p,log in jobs:
  code=p.wait();log.close();exits.append(dict(round=round_index+1,arm=name,pid=p.pid,code=code,time=time.time()));assert code==0,(round_index,name,code)
 rows={name:json.loads((OUT/f'cpu-{name}-r{round_index+1}-v1.json').read_text()) for name in arms}
 for key in ['oracle','input_state_sha256','events','events_sha256','result_sha256','records_sha256','memory_sha256','stretches']:
  assert all(r[key]==rows['candidate'][key] for r in rows.values()),(round_index,key)
 assert not rows['baseline']['bridge_fast_calls'] and all(v>0 for v in rows['candidate']['bridge_fast_calls'].values())
 print('ROUND',round_index+1,{name:r['drive_cpu_s'] for name,r in rows.items()},flush=True)
ratios=[];samples=[]
for r in range(1,4):
 rows={name:json.loads((OUT/f'cpu-{name}-r{r}-v1.json').read_text()) for name in ['baseline','candidate','python','pypy']}
 ratio=rows['candidate']['drive_cpu_s']/rows['baseline']['drive_cpu_s'];ratios.append(ratio)
 samples.append(dict(round=r,cpu_s={name:row['drive_cpu_s'] for name,row in rows.items()},candidate_to_baseline=ratio,candidate_to_pypy=rows['candidate']['drive_cpu_s']/rows['pypy']['drive_cpu_s']))
report=dict(outputs_equal=True,threshold=0.95,rounds=samples,ratios=ratios,median_ratio=statistics.median(ratios),all_rounds_improve=all(r<1 for r in ratios),pass_performance=all(r<1 for r in ratios) and statistics.median(ratios)<=0.95,quiet_observations=observations,starts=starts,exits=exits,topology=topology,selected_physical_cores=cores)
with (OUT/'performance-v1.json').open('x') as f:json.dump(report,f,indent=2)
assert report['pass_performance'],'repeatable performance threshold failed; no merge'
print('PERFORMANCE GATE PASS',report['median_ratio'],flush=True)
