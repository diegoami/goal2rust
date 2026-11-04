"""Unfrozen diagnostics, with archived executed sources; never canonical proof."""
import argparse
import hashlib
import json
import shutil
import sys
import time
from pathlib import Path
import capture_support as common

parser = argparse.ArgumentParser()
parser.add_argument('--out', required=True)
parser.add_argument('--cases', type=int, default=128)
args = parser.parse_args()
B = common.BASE
O = B / 'out/T26'
out = B / args.out
assert not out.exists()
common.verify()
common.deny_original()
sys.path[:0] = [str(B / 'engine/python'), str(B / 'engine/tests')]
from test_commentary import *
import goal2rust_engine
import pickle

sources = sorted((B / 'engine/src').glob('*.rs')) + sorted((B / 'engine/python').rglob('*.py'))
sources += [B / 'engine/tests/test_commentary.py', Path(__file__), O / 'inventory-v1.json']
sources += sorted(Path(goal2rust_engine.__file__).parent.glob('*.so'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
before = {str(p.relative_to(B)): sha(p) for p in sources}
archive = B / '.cache/T26-development-sources'
archive.mkdir(exist_ok=True)
source_map = {}
for p in sources:
    saved = archive / sha(p)
    if not saved.exists():
        with saved.open('xb') as stream:
            stream.write(p.read_bytes())
    assert sha(saved) == sha(p)
    source_map[str(p.relative_to(B))] = str(saved.relative_to(B))
meta = json.loads((O / 'captures-v1.json').read_text())
assert sha(B / meta['private_file']) == meta['sha256']
captures = pickle.loads((B / meta['private_file']).read_bytes())
counts, source_calls, returns = {}, {}, set()
start = time.monotonic()


def pair(root, case, kind, **options):
    p, _, ps = exercise(Oracle, case, root=root, profile=True, **options)
    r, native, rs = exercise(PortMachine, case, root=root, profile=True, **options)
    assert p['error'] is None, (root, case, kind, p['error'])
    assert p == r, (root, case, kind, [k for k in p if p[k] != r[k]])
    assert native.get(root) == 1 and ps['owned'] and not rs['owned'] and rs['outside'] > 0
    for name, count in ps['owned'].items():
        source_calls[name] = source_calls.get(name, 0)+count
    returns.update(site for site, _ in p['visits'] if site in RETURNS)
    counts[kind] = counts.get(kind, 0)+1


for root in NEW:
    for case in range(args.cases):
        for tapped in (False, True):
            for listener in (False, True):
                pair(root, case, 'authored', tapped=tapped, listener=listener,
                     pause=SITES[case % len(SITES)], direct=case % 3 == 0, mutations=case % 7 == 0)
    for case, snapshot in enumerate(captures[root]):
        for tapped in (False, True):
            for listener in (False, True):
                for schedule in range(3):
                    pair(root, case, 'real', snapshot=snapshot, tapped=tapped, listener=listener,
                         pause=root if schedule == 1 else None, direct=schedule == 2)
    if INV['bodies'][root]['sites']:
        for case in range(64):
            for tapped in (False, True):
                for listener in (False, True):
                    pair(root, case, 'controlled-ABI', controlled=True, tapped=tapped, listener=listener,
                         pause=RETURNS[case % len(RETURNS)], direct=case % 3 == 0)
    print('PASS', root, counts, flush=True)
assert set(source_calls) == set(INV['owned_code_objects'])
assert returns == set(RETURNS)
assert before == {str(p.relative_to(B)): sha(p) for p in sources}
report = dict(development_only=True, accepted_canonical_evidence=False, pass_all=True,
              source_unchanged=True, executed_source_sha256=before, preserved_source_map=source_map,
              real_capture_receipt_sha256=sha(O / 'captures-v1.json'),
              counts=counts, all_owned_source_calls=source_calls, real_returns_seen=sorted(returns),
              elapsed_s=time.monotonic()-start)
with out.open('x') as stream:
    json.dump(report, stream, indent=2, sort_keys=True)
    stream.write('\n')
print('Unfrozen diagnostic passes;all31 source code objects/25 returns witnessed', counts, flush=True)
