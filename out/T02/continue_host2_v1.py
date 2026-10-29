"""IT13 continuation after the preserved host2-v1 F40 timeouts.

Reuses the fresh native proof, never the old binary's partial family. Waits for
quiet, runs a new append-only full family with unchanged limits, then waits for
the separately running lifecycle suite before the ledger and paired timings.
No publishing, limit changes, source edits, or additional subtree translation.
"""
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'out/T02'
PY = ROOT / '.venv/bin/python'
ORACLE = ROOT / '.cache/goal2-archaeology'
PROOF = OUT / 'taps-rust-host2-v1.json'
FAMILY = OUT / 'family-F40-rust-host2-v2.jsonl'
CHECK = OUT / 'check-rust-host2-v1.json'
STEM = 'compare-F40-rust-host2-v2'


def verify_artifact():
    proof = json.loads(PROOF.read_text())
    original = json.loads((ROOT / 'out/T01/dev-taps-python-d3cf46a3.json').read_text())
    for key in ('events', 'events_sha256', 'score', 'draws', 'result_sha256',
                'memory_sha256', 'stretches', 'taps'):
        assert proof[key] == original[key], key
    assert proof['source_unchanged'] and proof['goal2rust']['source_unchanged']
    assert proof['goal2rust']['backend'] == 'rust' and proof['goal2rust']['native']
    assert proof['goal2rust']['machine_mutant'] == 0
    for name, digest in proof['goal2rust']['source_sha256'].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name


def quiet():
    count = 0
    while count < 3:
        load = os.getloadavg()
        count = count + 1 if load[0] < 4 else 0
        print('quiet observation', count, '/3; load', load, flush=True)
        time.sleep(20)


def run(command, *, cwd=ROOT, log=None):
    print('run', command, flush=True)
    if log is None:
        subprocess.run(command, cwd=cwd, check=True)
    else:
        with log.open('a') as output:
            subprocess.run(command, cwd=cwd, stdout=output,
                           stderr=subprocess.STDOUT, check=True)


verify_artifact()
quiet()
verify_artifact()
run(['bash', 'out/T02/run_family_v1.sh', FAMILY.name],
    log=OUT / 'family-F40-rust-host2-v2.log')
rows = [json.loads(line) for line in FAMILY.read_text().splitlines()]
assert len(rows) == 40 and len({r['id'] for r in rows}) == 40
assert all(r['error'] is None for r in rows), 'preserve failures; inspect before retrying'
command = [str(PY), '-B', 'experiments/E036-match-port/compare.py',
           '--family', 'F40', '--no-screen', '--candidate', str(FAMILY)]
status = OUT / (STEM + '.status.json')
log = OUT / (STEM + '.log')
if not log.exists():
    with log.open('x') as output:
        code = subprocess.run(command, cwd=ORACLE, stdout=output,
                              stderr=subprocess.STDOUT).returncode
    with status.open('x') as output:
        json.dump(dict(returncode=code, command=command), output, indent=2)
assert json.loads(status.read_text())['returncode'] == 0
while not CHECK.exists():
    print('F40 equal 40/40; waiting for the existing lifecycle producer', flush=True)
    time.sleep(30)
assert all(c['pass'] for c in json.loads(CHECK.read_text())['checks'].values())
verify_artifact()
manifest = OUT / 'validation-host2-v2.json'
if not manifest.exists():
    run([str(PY), 'out/T02/validation_manifest_v1.py', str(manifest),
         '--family-file', str(FAMILY), '--compare-stem', STEM,
         '--proof-receipt', str(PROOF), '--check-file', str(CHECK),
         '--differential-file', str(OUT / 'differential-host2-v1.json'),
         '--mutant-file', str(OUT / 'mutant-host2-v1.json'),
         '--tests-file', str(OUT / 'tests-host2-v1.log')])
quiet()
verify_artifact()
receipts = [OUT / f'cpu-{backend}-v1.json' for backend in ('python', 'pypy-python', 'rust')]
if not any(p.exists() for p in receipts):
    run(['bash', 'out/T02/paired_v1.sh'])
else:
    assert all(p.exists() for p in receipts), 'partial timings: preserve and inspect'
for baseline in receipts[:2]:
    run([str(PY), 'out/T01/compare_receipts.py', str(baseline), str(receipts[2])])
print('All local T02 gates passed. Publish assessment/checkpoint and recheck final-head CI.', flush=True)
