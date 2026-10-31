"""Post-writer audit, exclusive ledger. Never repairs or rewrites receipts."""
import hashlib
import json
import os
import sys
import evidence as e

OUT = e.BASE / 'out/T05'
e.verify()

def load(name): return json.loads((OUT / name).read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

names = ['differential-v1', 'return-mutant-v1', 'body-mutant-v1', 'check-v1',
         'taps-python-v1', 'taps-rust-v1', 'profile-after-v1',
         'cpu-python-v1', 'cpu-pypy-v1', 'cpu-rust-v1', 'attest-family-F40-v1-invocation']
for name in names:
    row = load(name + '.json')
    assert row['source_unchanged'], name
    for path, digest in row['source_sha256'].items(): assert sha(e.BASE / path) == digest, (name, path)
assert load('differential-v1.json')['all_equal']
for name in ['return-mutant-v1.json', 'body-mutant-v1.json']:
    assert not load(name)['all_equal'] and load(name)['differences'], name
check = load('check-v1.json')
assert check['state'] and check['exit_code'] == 0
assert set(check['checks']) == {'engine', 'interactive', 'goals', 'knockout'}
assert all(row['pass'] for row in check['checks'].values())
comparisons = []
for nameset in [['taps-python-v1', 'taps-rust-v1'], ['cpu-python-v1', 'cpu-pypy-v1', 'cpu-rust-v1']]:
    rows = [load(n + '.json') for n in nameset]
    for field in ['oracle', 'input_state_sha256', 'events', 'events_sha256', 'result_sha256',
                  'records_sha256', 'memory_sha256', 'stretches', 'taps']:
        assert all(r[field] == rows[0][field] for r in rows), (nameset, field)
    comparisons.append(dict(files=nameset, equal=True))
for name in ['cpu-rust-v1.json', 'taps-rust-v1.json']:
    counts = load(name)['native_calls']
    assert len(counts) == 10 and sum(counts.values()) == 1304110
    assert counts['0791:2FB1'] == 5147
    assert counts['0791:2956'] == 184872 and counts['1771:3216'] == 233587
for name in ['cpu-python-v1.json', 'cpu-pypy-v1.json', 'taps-python-v1.json']:
    assert load(name)['native_calls'] == {}
profile = load('profile-after-v1.json')
assert profile['equal_to_T04'] and profile['total_guest_entries'] == 3103685
assert profile['python_guest_entries'] == 1799575
family = [json.loads(line) for line in (OUT / 'family-F40-rust-v1.jsonl').read_bytes().splitlines()]
assert len(family) == len({r['id'] for r in family}) == 40
assert all(r['family'] == 'F40' and not r['error'] and r['stopped_at_board'] for r in family)
assert load('compare-F40-v1.status.json')['exit_code'] == 0
attest = {}
for label, count in [('check', 11), ('family-F40', 40)]:
    rows = [json.loads(p.read_text()) for p in (OUT / ('attest-' + label + '-v1')).glob('*.json')]
    assert sum(r['machines'] for r in rows) == count
    assert all(r['oracle'] == e.PIN and r['backend'] == 'rust' for r in rows)
    calls = {ad: sum(r['native_calls'].get(ad, 0) for r in rows) for ad in ['0791:2956', '1771:3216']}
    assert all(calls.values())
    attest[label] = dict(machines=count, new_native_calls=calls)
jobs = [json.loads(line) for line in (OUT / 'jobs-v1.jsonl').read_text().splitlines()]
starts, exits = [r for r in jobs if r['event'] == 'start'], [r for r in jobs if r['event'] == 'exit']
assert len(starts) == len(exits) == 11 and all(r['code'] == 0 for r in exits)
assert {r['pid'] for r in starts} == {r['pid'] for r in exits}
for row in starts:
    try: os.killpg(row['pid'], 0)
    except ProcessLookupError: pass
    else: raise AssertionError(('producer process group remains', row))
cpustarts = [r['time'] for r in starts if r['name'].startswith('cpu-')]
assert max(cpustarts) - min(cpustarts) < 5
quiet = [json.loads(line) for line in (OUT / 'quiet-v1.jsonl').read_text().splitlines()]
assert len(quiet) >= 3 and all(max(r['load'][:2]) < 4 for r in quiet[-3:])
ledger = dict(pass_all=True, all_writers_finished=True, comparisons=comparisons,
              attestation=attest, python_entries_removed=5147, python_entries_remaining=1799575,
              evidence_sha256={str(p.relative_to(OUT)): sha(p) for p in sorted(OUT.rglob('*'))
                               if p.is_file() and p.suffix in ('.json', '.jsonl', '.log', '.prof', '.txt')
                               and not p.name.startswith('validation-')})
e.write(sys.argv[1], ledger, e.hashes())
print('T05 all gates pass, writers exited, hashes bound')
