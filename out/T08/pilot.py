"""Quiet paired baseline/candidate pilot. No candidate merge claim from one pair."""
import hashlib,json,os,subprocess,sys,time
from pathlib import Path
BASE=Path(__file__).resolve().parents[2];OUT=BASE/'out/T08'
assert not (OUT/'pilot-start-v1.json').exists()
quiet=0;observations=[]
while quiet<3:
 load=os.getloadavg();quiet=quiet+1 if max(load[:2])<4 else 0;observations.append(dict(time=time.time(),load=load,quiet=quiet))
 if quiet<3:time.sleep(10)
jobs=[];records=[]
for name,baseline in [('baseline',True),('candidate',False)]:
 env=dict(os.environ,PYTHONHASHSEED='0',GOAL2RUST_BASELINE='1' if baseline else '0')
 log=(OUT/('pilot-'+name+'-v1.log')).open('x');cmd=[str(BASE/'.venv/bin/python'),'-B','out/T08/run_receipt.py','--backend','rust','--mode','cpu','--out',str(OUT/('pilot-'+name+'-v1.json'))]
 p=subprocess.Popen(cmd,cwd=BASE,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);jobs.append((p,log));records.append(dict(name=name,pid=p.pid,command=cmd,baseline=baseline,time=time.time()))
with (OUT/'pilot-start-v1.json').open('x') as f:json.dump(dict(observations=observations,jobs=records),f,indent=2)
for p,log in jobs:code=p.wait();log.close();assert code==0,code
rows=[json.loads((OUT/('pilot-'+name+'-v1.json')).read_text()) for name in ['baseline','candidate']]
for key in ['events','events_sha256','result_sha256','records_sha256','memory_sha256','stretches']:assert rows[0][key]==rows[1][key],key
ratio=rows[1]['drive_cpu_s']/rows[0]['drive_cpu_s']
with (OUT/'pilot-assessment-v1.json').open('x') as f:json.dump(dict(outputs_equal=True,baseline_cpu_s=rows[0]['drive_cpu_s'],candidate_cpu_s=rows[1]['drive_cpu_s'],ratio=ratio,limitations='Single pilot; three paired rounds and complete fidelity gates still required'),f,indent=2)
print('Pilot CPU ratio candidate/baseline',ratio,flush=True)
