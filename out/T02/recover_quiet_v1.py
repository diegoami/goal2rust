"""T02 recovery under the UNCHANGED family limits, following T01's accepted pattern.

Preserve v1 including its timeout. Wait for a quiet machine, rerun only failed or
missing IDs into a separate append-only receipt, then assemble all 40 completed
lines byte-for-byte and run the original comparison. Never replace a completed
match after seeing its comparison result; never relax a limit or assertion.
"""
import hashlib
import json
import os
import signal
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

G2R=Path(__file__).resolve().parents[2]
ROOT=G2R/'.cache/goal2-archaeology'
PY=G2R/'.venv/bin/python'
OUT=G2R/'out/T02'
original=OUT/'family-F40-rust-v1.jsonl'
rerun=OUT/'family-F40-rust-v1-rerun.jsonl'
candidate=OUT/'family-F40-rust-v2.jsonl'
expected=[json.loads(l)['id'] for l in (G2R/'out/T01/family-F40-rust-v2.jsonl').read_text().splitlines()]
assert len(expected)==len(set(expected))==40

def records(path):
    if not path.exists(): return {}
    raw=path.read_bytes().splitlines(keepends=True)
    assert all(line.endswith(b'\n') for line in raw), f'partial line: preserve and inspect {path}'
    out={}
    for line in raw:
        row=json.loads(line)
        assert row['id'] in expected and row['id'] not in out
        out[row['id']]=(row,line)
    return out

def source_check():
    receipt=json.loads((OUT/'taps-rust-v1.json').read_text())
    for name,digest in receipt['goal2rust']['source_sha256'].items():
        assert hashlib.sha256((G2R/name).read_bytes()).hexdigest()==digest,name

def quiet():
    count=0
    while count<3:
        load=os.getloadavg()
        count=count+1 if load[0]<4 else 0
        print('quiet observation',count,'/3; load',load,flush=True)
        time.sleep(20)

def log_event(**data):
    with (OUT/'recovery-attempts-v1.jsonl').open('a') as f:
        f.write(json.dumps(dict(utc=datetime.now(timezone.utc).isoformat(),**data))+'\n')

source_check()
old=records(original)
good={k:v for k,v in old.items() if v[0]['error'] is None}
needed=[k for k in expected if k not in good]
print('preserved completed',len(good),'rerun failed/missing',needed,flush=True)
if not candidate.exists():
    done=records(rerun)
    assert not any(row['error'] for row,line in done.values()), 'rerun has errors: preserve and inspect'
    if set(done)!=set(needed):
        quiet();source_check()
        env=os.environ.copy()
        env.update(PYTHONHASHSEED='0',GOAL2RUST_MACHINE='1',GOAL2RUST_NATIVE='1',
            PYTHONPATH=f'{OUT}:{G2R}/engine/python:{ROOT}/runtime:{G2R}/.venv/lib/python3.12/site-packages')
        cmd=[str(PY),'-B','experiments/E036-match-port/family.py','--family','F40','--engine','port',
             '--no-unicorn','--workers','2','--only',','.join(needed),'--out',str(rerun)]
        log_event(phase='family_start',command=cmd,load=os.getloadavg())
        with (OUT/'family-F40-rust-v1-rerun.log').open('a') as log:
            p=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            print('rerun process group',p.pid,flush=True)
            try: code=p.wait()
            except BaseException:
                os.killpg(p.pid,signal.SIGTERM);p.wait();raise
        log_event(phase='family_end',returncode=code,load=os.getloadavg())
        assert code==0,'rerun failed: preserve and inspect'
    source_check()
    new=records(rerun)
    assert set(new)==set(needed) and all(row['error'] is None for row,line in new.values())
    assembled={**good,**new}
    assert set(assembled)==set(expected)
    with candidate.open('xb') as f:
        for k in expected:f.write(assembled[k][1])
    with (OUT/'assembly-v2.json').open('x') as f:
        json.dump(dict(preserved_failed=[k for k,(r,l) in old.items() if r['error']],
            inputs={str(p.relative_to(G2R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (original,rerun)},
            lines={k:dict(source='v1' if k in good else 'rerun',sha256=hashlib.sha256(assembled[k][1]).hexdigest()) for k in expected}),f,indent=2)
rows=records(candidate)
assert len(rows)==40 and all(row['error'] is None for row,line in rows.values())
source_check()
log=OUT/'compare-F40-rust-v2.log'
status=OUT/'compare-F40-rust-v2.status.json'
cmd=[str(PY),'-B','experiments/E036-match-port/compare.py','--family','F40','--no-screen','--candidate',str(candidate)]
if not log.exists():
    with log.open('x') as f:code=subprocess.run(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT).returncode
    with status.open('x') as f:json.dump(dict(returncode=code,command=cmd),f,indent=2)
assert status.exists() and json.loads(status.read_text())['returncode']==0,'comparison did not pass: inspect receipts'
manifest=OUT/'validation-v2.json'
if not manifest.exists():
    subprocess.run([str(PY),'out/T02/validation_manifest_v1.py',str(manifest),'--family-file',str(candidate),
                    '--compare-stem','compare-F40-rust-v2'],cwd=G2R,check=True)
quiet();source_check()
receipts=[OUT/f'cpu-{n}-v1.json' for n in ('python','pypy-python','rust')]
if not any(p.exists() for p in receipts):subprocess.run(['bash','out/T02/paired_v1.sh'],cwd=G2R,check=True)
else:
    assert all(p.exists() for p in receipts),'partial timing attempt: preserve and inspect'
    for baseline in receipts[:2]:subprocess.run([str(PY),'out/T01/compare_receipts.py',str(baseline),str(receipts[2])],cwd=G2R,check=True)
print('All local T02 gates passed; final receipts and final-head CI remain to publish.',flush=True)
