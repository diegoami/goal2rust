"""Supervised, resumable final gate orchestration. No publishing or new task.

Waits for the existing append-only F40 run and kit check, refuses any failed
record, compares F40, verifies M2 source hashes, waits for a quiet machine, then
runs the three paired CPU receipts. Existing complete CPU receipts are compared;
incomplete attempts are preserved and refused, never silently overwritten.
"""
import json
import os
import subprocess
import time
from pathlib import Path

G2R=Path(__file__).resolve().parents[2]
ROOT=G2R/'.cache/goal2-archaeology'
PY=G2R/'.venv/bin/python'
FAMILY=G2R/'out/T02/family-F40-rust-v1.jsonl'
CHECK=G2R/'out/T02/check-rust-v1.json'
last=None
while True:
    rows=[json.loads(line) for line in FAMILY.read_text().splitlines()] if FAMILY.exists() else []
    assert not any(r['error'] for r in rows), 'F40 runner errors: preserve records and inspect'
    status=(len(rows),CHECK.exists())
    if status!=last:
        print('F40 records',status[0],'/40; lifecycle report complete',status[1],flush=True)
        last=status
    if len(rows)==40 and CHECK.exists(): break
    time.sleep(30)
checks=json.loads(CHECK.read_text())
assert all(c['pass'] for c in checks['checks'].values()), 'kit checks failed; inspect receipt'
compare_log=G2R/'out/T02/compare-F40-rust-v1.log'
compare_status=G2R/'out/T02/compare-F40-rust-v1.status.json'
cmd=[str(PY),'-B','experiments/E036-match-port/compare.py','--family','F40','--no-screen','--candidate',str(FAMILY)]
if not compare_log.exists():
    with compare_log.open('x') as log:
        result=subprocess.run(cmd,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    with compare_status.open('x') as status:
        json.dump(dict(returncode=result.returncode,command=cmd),status,indent=2)
assert compare_status.exists(), 'comparison log without exit status: preserve and inspect'
assert json.loads(compare_status.read_text())['returncode']==0, 'F40 comparison failed: inspect log'
# A final source/evidence ledger is exclusive. Never reuse a failed/partial log.
manifest=G2R/'out/T02/validation-v1.json'
if not manifest.exists(): subprocess.run([str(PY),'out/T02/validation_manifest_v1.py',str(manifest)],cwd=G2R,check=True)
# Require three quiet observations after validation ends. Preserve the observed
# load, rather than claiming there were no other users on a shared host.
quiet=0
while quiet<3:
    load=os.getloadavg()
    quiet=quiet+1 if load[0]<4 else 0
    print('quiet observation',quiet,'/3; load',load,flush=True)
    time.sleep(20)
receipts=[G2R/'out/T02'/f'cpu-{name}-v1.json' for name in ('python','pypy-python','rust')]
if not any(p.exists() for p in receipts):
    subprocess.run(['bash','out/T02/paired_v1.sh'],cwd=G2R,check=True)
else:
    assert all(p.exists() for p in receipts), 'partial timing attempt: preserve and inspect'
for baseline in receipts[:2]:
    subprocess.run([str(PY),'out/T01/compare_receipts.py',str(baseline),str(receipts[2])],cwd=G2R,check=True)
print('All local T02 gates passed; commit/push receipts and recheck final-head CI.',flush=True)
