"""Final validation ledger: bind the append-only family/check outputs to M2 sources.

Run after F40 and original_match.check complete; output is exclusive. The core
source hash and CPython extension must still be the ones used in M2's taps run.
"""
import hashlib
import argparse
import json
import subprocess
import sys
from pathlib import Path

G2R=Path(__file__).resolve().parents[2]
ap=argparse.ArgumentParser()
ap.add_argument('out',type=Path)
ap.add_argument('--family-file',type=Path,default=G2R/'out/T02/family-F40-rust-v1.jsonl')
ap.add_argument('--compare-stem',default='compare-F40-rust-v1')
a=ap.parse_args()
taps=json.loads((G2R/'out/T02/taps-rust-v1.json').read_text())
recorded=taps['goal2rust']['source_sha256']
current={name:hashlib.sha256((G2R/name).read_bytes()).hexdigest() for name in recorded}
assert current==recorded, [k for k in current if current[k]!=recorded[k]]
family=a.family_file
rows=[json.loads(l) for l in family.read_text().splitlines()]
assert len(rows)==40 and len({r['id'] for r in rows})==40
assert all(r['error'] is None and r['stopped_at_board'] and not r['strays'] and r['engine']=='port' for r in rows)
check=G2R/'out/T02/check-rust-v1.json'
checks=json.loads(check.read_text())
assert all(c['pass'] for c in checks['checks'].values())
status=G2R/'out/T02'/f'{a.compare_stem}.status.json'
assert json.loads(status.read_text())['returncode']==0
paths=[family,check,G2R/'out/T02'/f'{a.compare_stem}.log',G2R/'out/T02/differential-v2.json',
       G2R/'out/T02/mutant-v2.json',G2R/'out/T02/tests-v3.log',G2R/'out/T02/next-subtrees.md',
       G2R/'out/T02/run_family_v1.sh',G2R/'out/T02/sitecustomize.py',status,
       G2R/'out/T02/paired_v1.sh',G2R/'out/T02/finish_v1.py',Path(__file__).resolve()]
if (G2R/'out/T02/assembly-v2.json').exists():
    paths += [G2R/'out/T02/assembly-v2.json',G2R/'out/T02/family-F40-rust-v1.jsonl',
              G2R/'out/T02/family-F40-rust-v1-rerun.jsonl',G2R/'out/T02/recover_quiet_v1.py',
              G2R/'out/T02/recovery-attempts-v1.jsonl']
report=dict(head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=G2R,text=True).strip(),
    family_count=len(rows),family_errors=0,kit_checks_pass=True,
    source_matches_M2_taps=True,source_sha256=current,
    evidence_sha256={str(p.relative_to(G2R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
with a.out.open('x') as f:json.dump(report,f,indent=2)
print('F40 40/40 completed; kit checks pass; implementation/extension hashes match M2 taps')
