"""Final validation ledger: bind the append-only family/check outputs to M2 sources.

Run after F40 and original_match.check complete; output is exclusive. The core
source hash and CPython extension must still be the ones used in M2's taps run.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

G2R=Path(__file__).resolve().parents[2]
taps=json.loads((G2R/'out/T02/taps-rust-v1.json').read_text())
recorded=taps['goal2rust']['source_sha256']
current={name:hashlib.sha256((G2R/name).read_bytes()).hexdigest() for name in recorded}
assert current==recorded, [k for k in current if current[k]!=recorded[k]]
family=G2R/'out/T02/family-F40-rust-v1.jsonl'
rows=[json.loads(l) for l in family.read_text().splitlines()]
assert len(rows)==40 and len({r['id'] for r in rows})==40
assert all(r['error'] is None and r['stopped_at_board'] and not r['strays'] and r['engine']=='port' for r in rows)
check=G2R/'out/T02/check-rust-v1.json'
checks=json.loads(check.read_text())
assert all(c['pass'] for c in checks['checks'].values())
status=G2R/'out/T02/compare-F40-rust-v1.status.json'
assert json.loads(status.read_text())['returncode']==0
paths=[family,check,G2R/'out/T02/compare-F40-rust-v1.log',G2R/'out/T02/differential-v2.json',
       G2R/'out/T02/mutant-v2.json',G2R/'out/T02/tests-v3.log',G2R/'out/T02/next-subtrees.md',
       G2R/'out/T02/run_family_v1.sh',G2R/'out/T02/sitecustomize.py',status,
       G2R/'out/T02/paired_v1.sh',G2R/'out/T02/finish_v1.py',Path(__file__).resolve()]
report=dict(head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=G2R,text=True).strip(),
    family_count=len(rows),family_errors=0,kit_checks_pass=True,
    source_matches_M2_taps=True,source_sha256=current,
    evidence_sha256={str(p.relative_to(G2R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
with Path(sys.argv[1]).open('x') as f:json.dump(report,f,indent=2)
print('F40 40/40 completed; kit checks pass; implementation/extension hashes match M2 taps')
