"""Versioned whole three-round campaigns;strict load quality;no selective replacement."""
import fcntl,hashlib,json,os,statistics,subprocess,sys,time
from pathlib import Path
import evidence as e
BASE=e.BASE;OUT=BASE/'out/T24';e.verify();before=e.hashes();assert before==json.loads((OUT/'freeze-v1.json').read_text())['source_sha256']
lock=(BASE/'.cache/T24-performance.lock').open('a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);lock.seek(0);lock.truncate();lock.write(str(os.getpid()));lock.flush()
allowed=sorted(os.sched_getaffinity(0));cores=[];seen=set();topology={}
for cpu in allowed:
 p=Path(f'/sys/devices/system/cpu/cpu{cpu}/topology');key=((p/'physical_package_id').read_text().strip(),(p/'core_id').read_text().strip());topology[str(cpu)]=dict(package=key[0],core=key[1],siblings=(p/'thread_siblings_list').read_text().strip())
 if key not in seen:seen.add(key);cores.append(cpu)
assert len(cores)>=4;cores=cores[:4];campaigns=[]
for attempt in range(1,33):
 version='v'+str(attempt);path=OUT/f'performance-{version}.json'
 if path.exists():
  report=json.loads(path.read_text());assert report['measurement_complete'] and report['source_unchanged']
  for p,h in report['source_sha256'].items():assert hashlib.sha256((BASE/p).read_bytes()).hexdigest()==h,p
  print('PRESERVED COMPLETE CAMPAIGN',version,'accepted',report['quiet_complete'],flush=True)
 else:
  assert not list(OUT.glob(f'cpu-*-r*-{version}.json')) and not (OUT/f'timing-jobs-{version}.jsonl').exists(),'partial attempt:preserve/audit before selecting fresh version'
  observations=[];starts=[];exits=[];monitor=[];quality=[]
  def journal(row):
   with (OUT/f'timing-jobs-{version}.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
  for index in range(3):
   quiet=0
   while quiet<3:
    loads=os.getloadavg();quiet=quiet+1 if max(loads[:2])<4 else 0;observations.append(dict(round=index+1,time=time.time(),load=loads,quiet=quiet))
    print('WAIT TIMING QUIET',version,index+1,loads,quiet,'/3',flush=True)
    if quiet<3:time.sleep(10)
   assignment=dict(baseline=cores[index%2],candidate=cores[1-index%2],python=cores[2+index%2],pypy=cores[3-index%2]);order=['baseline','candidate','python','pypy'] if index%2==0 else ['candidate','baseline','pypy','python'];jobs=[]
   for arm in order:
    env=dict(os.environ,PYTHONHASHSEED='0',GOAL2RUST_BASELINE='1' if arm=='baseline' else '0',GOAL2RUST_FAST='1');interpreter=BASE/('.venv-pypy/bin/python' if arm=='pypy' else '.venv/bin/python');backend='python' if arm in ['python','pypy'] else 'rust';receipt=OUT/f'cpu-{arm}-r{index+1}-{version}.json';assert not receipt.exists();log=(OUT/f'cpu-{arm}-r{index+1}-{version}.log').open('x')
    cmd=['taskset','-c',str(assignment[arm]),str(interpreter),'-B','out/T24/run_receipt.py','--backend',backend,'--mode','cpu','--out',str(receipt)];child=subprocess.Popen(cmd,cwd=BASE,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);jobs.append((arm,child,log));row=dict(round=index+1,arm=arm,pid=child.pid,cpu=assignment[arm],time=time.time(),command=cmd);starts.append(row);journal(dict(event='start',**row));print('START',version,index+1,arm,child.pid,flush=True)
   while any(p.poll() is None for _,p,_ in jobs):
    monitor.append(dict(round=index+1,time=time.time(),load=os.getloadavg(),active=[arm for arm,p,_ in jobs if p.poll() is None]));time.sleep(5)
   for arm,p,log in jobs:
    code=p.wait();log.close();row=dict(round=index+1,arm=arm,pid=p.pid,code=code,time=time.time());exits.append(row);journal(dict(event='exit',**row));assert code==0,(version,index,arm,code)
   rows={arm:json.loads((OUT/f'cpu-{arm}-r{index+1}-{version}.json').read_text()) for arm in order}
   for key in ['oracle','input_state_sha256','events','events_sha256','result_sha256','records_sha256','memory_sha256','stretches']:assert all(r[key]==rows['candidate'][key] for r in rows.values()),(version,index,key)
   quality.append(dict(round=index+1,all_arm_ends_quiet=all(max(r['load_before'][:2])<4 and max(r['load_after'][:2])<4 for r in rows.values()),continuous_total_load_below8=all(max(r['load'][:2])<8 for r in monitor if r['round']==index+1)))
   print('ROUND',version,index+1,{a:r['drive_cpu_s'] for a,r in rows.items()},quality[-1],flush=True)
  samples=[];ratios=[]
  for rnd in range(1,4):
   rows={a:json.loads((OUT/f'cpu-{a}-r{rnd}-{version}.json').read_text()) for a in ['baseline','candidate','python','pypy']};c={a:r['drive_cpu_s'] for a,r in rows.items()};ratio=c['candidate']/c['baseline'];ratios.append(ratio);samples.append(dict(round=rnd,cpu_s=c,candidate_to_baseline=ratio,baseline_to_pypy=c['baseline']/c['pypy'],candidate_to_pypy=c['candidate']/c['pypy'],cpython_to_candidate=c['python']/c['candidate']))
  report=dict(attempt=attempt,outputs_equal=True,measurement_complete=True,quiet_complete=all(r['all_arm_ends_quiet'] and r['continuous_total_load_below8'] for r in quality),quiet_quality=quality,continuous_load=monitor,quiet_observations=observations,starts=starts,exits=exits,topology=topology,selected_physical_cores=cores,rounds=samples,ratios=ratios,median_ratio=statistics.median(ratios),median_baseline_to_pypy=statistics.median(r['baseline_to_pypy'] for r in samples),median_candidate_to_pypy=statistics.median(r['candidate_to_pypy'] for r in samples),median_cpython_to_candidate=statistics.median(r['cpython_to_candidate'] for r in samples),all_rounds_improve=all(x<1 for x in ratios),incremental_port_no_magnitude_minimum=True)
  e.write(path,report,before)
 campaigns.append(dict(version=version,accepted=report['quiet_complete'],sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
 if report['quiet_complete']:
  e.write(OUT/'performance-selection-v1.json',dict(pass_all=True,selected_version=version,campaigns=campaigns,every_campaign_three_complete_four_arm_rounds=True,no_selective_replacement=True),before);print('SELECTED QUIET CAMPAIGN',version,report['median_ratio'],flush=True);break
 print('REJECTED LOADED WHOLE CAMPAIGN',version,'all samples retained;repeat all3 rounds',flush=True)
else:raise AssertionError('campaign budget exhausted;all receipts preserved;owner review of host required')
