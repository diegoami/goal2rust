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
ap.add_argument('--proof-receipt',type=Path,default=G2R/'out/T02/taps-rust-v1.json')
ap.add_argument('--check-file',type=Path,default=G2R/'out/T02/check-rust-v1.json')
ap.add_argument('--differential-file',type=Path,default=G2R/'out/T02/differential-v2.json')
ap.add_argument('--mutant-file',type=Path,default=G2R/'out/T02/mutant-v2.json')
ap.add_argument('--tests-file',type=Path,default=G2R/'out/T02/tests-v3.log')
ap.add_argument('--extra-evidence',type=Path,action='append',default=[])
a=ap.parse_args()
taps=json.loads(a.proof_receipt.read_text())
oracle=json.loads((G2R/'out/T01/dev-taps-python-d3cf46a3.json').read_text())
keys=['events','events_sha256','score','draws','result_sha256','memory_sha256','stretches','taps']
assert taps['mode']=='taps' and all(taps[k]==oracle[k] for k in keys)
assert taps['goal2rust']['backend']=='rust' and taps['goal2rust']['native']
assert taps['goal2rust']['machine_mutant']==0
assert taps['source_unchanged'] and taps['goal2rust']['source_unchanged']
assert taps['goal2rust']['native_calls']==json.loads((G2R/'out/T02/taps-rust-v1.json').read_text())['goal2rust']['native_calls']
assert json.loads(a.differential_file.read_text())['all_equal']
assert json.loads(a.mutant_file.read_text())['caught']
recorded=taps['goal2rust']['source_sha256']
current={name:hashlib.sha256((G2R/name).read_bytes()).hexdigest() for name in recorded}
assert current==recorded, [k for k in current if current[k]!=recorded[k]]
family=a.family_file
rows=[json.loads(l) for l in family.read_text().splitlines()]
assert len(rows)==40 and len({r['id'] for r in rows})==40
assert all(r['error'] is None and r['stopped_at_board'] and not r['strays'] and r['engine']=='port' for r in rows)
check=a.check_file
checks=json.loads(check.read_text())
assert all(c['pass'] for c in checks['checks'].values())
status=G2R/'out/T02'/f'{a.compare_stem}.status.json'
assert json.loads(status.read_text())['returncode']==0
paths=[family,check,G2R/'out/T02'/f'{a.compare_stem}.log',a.differential_file,
       a.mutant_file,a.tests_file,a.proof_receipt,G2R/'out/T02/next-subtrees.md',
       G2R/'out/T02/run_family_v1.sh',G2R/'out/T02/sitecustomize.py',status,
       G2R/'out/T02/paired_v1.sh',G2R/'out/T02/finish_v1.py',Path(__file__).resolve()]
paths += a.extra_evidence
if (G2R/'out/T02/assembly-v2.json').exists():
    paths += [G2R/'out/T02/assembly-v2.json',G2R/'out/T02/family-F40-rust-v1.jsonl',
              G2R/'out/T02/family-F40-rust-v1-rerun.jsonl',G2R/'out/T02/recover_quiet_v1.py',
              G2R/'out/T02/recovery-attempts-v1.jsonl']
report=dict(head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=G2R,text=True).strip(),
    family_count=len(rows),family_errors=0,kit_checks_pass=True,
    source_matches_validated_native_taps=True,proof_receipt=str(a.proof_receipt.relative_to(G2R)),source_sha256=current,
    evidence_sha256={str(p.relative_to(G2R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
with a.out.open('x') as f:json.dump(report,f,indent=2)
print('F40 40/40 completed; kit checks pass; implementation/extension hashes match validated native taps')
