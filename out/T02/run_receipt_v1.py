"""Run the unmodified T117 producer; add T02 source and backend identity.

Use the selected interpreter and PYTHONPATH=engine/python:<oracle>/runtime.
--backend python|rust; --native 0 is M1's bridge-only machine. Output exclusive.
The oracle is unmodified. Original-game state never leaves the oracle cache.
"""
import argparse
import hashlib
import importlib.util
import json
import os
import platform
import runpy
import subprocess
import sys
from pathlib import Path

G2R = Path(__file__).resolve().parents[2]
ROOT = G2R / '.cache/goal2-archaeology'
PIN = 'd3cf46a3e87f0ba04916867b5b231c4646a0c2bd'

def git(*args, cwd=G2R):
    return subprocess.check_output(['git', *args], cwd=cwd, text=True).strip()

def hashes():
    files = (sorted((G2R / 'engine/src').glob('*.rs'))
             + sorted((G2R / 'engine/python').rglob('*.py'))
             + [G2R / 'engine/Cargo.toml', G2R / 'engine/Cargo.lock', G2R / 'engine/pyproject.toml', Path(__file__).resolve()])
    import goal2rust_engine
    files += sorted(Path(goal2rust_engine.__file__).parent.glob('*.so'))
    return {str(p.relative_to(G2R)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}

ap = argparse.ArgumentParser()
ap.add_argument('--backend', choices=['python', 'rust'], required=True)
ap.add_argument('--native', type=int, choices=[0, 1], default=1)
ap.add_argument('--mode', choices=['cpu', 'taps'], required=True)
ap.add_argument('--out', type=Path, required=True)
a = ap.parse_args()
assert os.environ.get('PYTHONHASHSEED') == '0'
assert git('rev-parse', 'HEAD', cwd=ROOT) == PIN
assert not git('status', '--porcelain', 'runtime', cwd=ROOT)
assert not a.out.exists(), a.out
before = hashes()
load = os.getloadavg()
sys.path[:0] = [str(ROOT), str(ROOT / 'runtime')]
if a.backend == 'rust':
    os.environ['GOAL2RUST_NATIVE'] = str(a.native)
    from goal2rust import install
    install()
from original_match import Match
created = []
original_init = Match.__init__
def capture(self, *args, **kwargs):
    original_init(self, *args, **kwargs)
    created.append(self)
Match.__init__ = capture
producer = ROOT / 'experiments/E036-match-port/out/T117/drive_receipt_v1.py'
raw = a.out.parent / 'raw' / a.out.name
raw.parent.mkdir(parents=True, exist_ok=True)
sys.argv = [str(producer), '--mode', a.mode, '--out', str(raw)]
try:
    runpy.run_path(str(producer), run_name='__main__')
except SystemExit as e:
    if e.code not in (None, 0): raise
receipt = json.loads(raw.read_text())
receipt['goal2rust'] = dict(native_calls=created[0].m._core.native_calls if a.backend == 'rust' else {}, backend=a.backend, native=bool(a.native) if a.backend == 'rust' else False,
    machine_mutant=int(os.environ.get('GOAL2RUST_MACHINE_MUTANT', '0')), head=git('rev-parse', 'HEAD'),
    source_sha256=before, source_unchanged=before == hashes(),
    machine=dict(node=platform.node(), cpus=os.cpu_count(), load_before=load, load_after=os.getloadavg()))
assert receipt['source_unchanged'] and receipt['goal2rust']['source_unchanged']
with a.out.open('x') as f: json.dump(receipt, f, indent=2)
print('wrote', a.out, flush=True)
