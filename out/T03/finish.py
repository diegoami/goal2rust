"""Strict final gates: family source lines, accepted comparator, proofs and paired drives."""
import hashlib
import json
import subprocess
import sys
import common

OUT = common.BASE / 'out/T03'
common.verify()


def load(name): return json.loads((OUT / name).read_text())


def compare(names):
    rows = [load(name) for name in names]
    fields = ['oracle', 'input_state_sha256', 'events', 'events_sha256', 'result_sha256',
              'records_sha256', 'memory_sha256', 'stretches', 'taps']
    for field in fields: assert all(row[field] == rows[0][field] for row in rows), field
    for row in rows: assert row['source_unchanged']
    return dict(files=names, equal_fields=fields, equal=True)


def proof_checks():
    for name in ['differential-v1.json', 'body-mutant-v1.json', 'machine-mutant-v1.json', 'check-v1.json']:
        report = load(name)
        assert report['source_unchanged'], name
        for path, sha in report['source_sha256'].items():
            assert hashlib.sha256((common.BASE / path).read_bytes()).hexdigest() == sha, (name, path)
    assert load('differential-v1.json')['all_equal']
    assert not load('body-mutant-v1.json')['all_equal']
    assert load('machine-mutant-v1.json')['caught']
    check = load('check-v1.json')
    assert check['state'] and check['exit_code'] == 0
    assert all(row['pass'] for row in check['checks'].values())
    assert set(check['checks']) == {'engine', 'interactive', 'goals', 'knockout'}
    for label in ['check', 'family-ALL']:
        receipts = [json.loads(p.read_text()) for p in (OUT / ('attest-' + label + '-v1')).glob('*.json')]
        assert receipts and sum(r['machines'] for r in receipts) > 0, label
        assert all(r['oracle'] == common.PIN and r['backend'] == 'rust' for r in receipts)
        assert sum(sum(r['native_calls'].values()) for r in receipts) > 0, label


if sys.argv[1] == 'family':
    path = OUT / 'family-ALL-rust-v1.jsonl'
    lines = path.read_bytes().splitlines(keepends=True)
    rows = [json.loads(line) for line in lines]
    assert len(rows) == len({r['id'] for r in rows}) == 75
    assert all(not r['error'] and r['stopped_at_board'] for r in rows)
    f40 = [(i, line) for i, (line, row) in enumerate(zip(lines, rows), 1) if row['family'] == 'F40']
    assert len(f40) == 40
    target = OUT / 'family-F40-rust-v1.jsonl'
    with target.open('xb') as f:
        for _, line in f40: f.write(line)
    with (OUT / 'F40-selection-v1.json').open('x') as f:
        json.dump(dict(source=path.name, sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                       lines=[dict(line=i, sha256=hashlib.sha256(line).hexdigest()) for i, line in f40]), f, indent=2)
    for family, candidate in [('ALL', path), ('F40', target)]:
        command = [sys.executable, '-B', 'experiments/E036-match-port/compare.py', '--family', family,
                   '--no-screen', '--candidate', str(candidate)]
        with (OUT / f'compare-{family}-v1.log').open('x') as log:
            code = subprocess.call(command, cwd=common.ORACLE, stdout=log, stderr=subprocess.STDOUT)
        with (OUT / f'compare-{family}-v1.status.json').open('x') as f:
            json.dump(dict(command=command, exit_code=code), f, indent=2)
        assert code == 0, family
elif sys.argv[1] == 'final':
    proof_checks()
    comparisons = [compare(['taps-python-v1.json', 'taps-rust-v1.json']),
                   compare(['cpu-python-v1.json', 'cpu-pypy-v1.json', 'cpu-rust-v1.json'])]
    for row in [load('taps-rust-v1.json'), load('cpu-rust-v1.json')]:
        assert sum(row['native_calls'].values()) == 880504 and len(row['native_calls']) == 7
    for name in ['taps-python-v1.json', 'taps-rust-v1.json', 'cpu-python-v1.json', 'cpu-pypy-v1.json', 'cpu-rust-v1.json', 'attest-family-ALL-v1-invocation.json']:
        for path, sha in load(name)['source_sha256'].items():
            assert hashlib.sha256((common.BASE / path).read_bytes()).hexdigest() == sha, (name, path)
    for family in ['ALL', 'F40']: assert load(f'compare-{family}-v1.status.json')['exit_code'] == 0
    evidence = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                for p in OUT.iterdir() if p.suffix in ['.json', '.jsonl', '.log'] and p.name != 'validation-v1.json'}
    common.write(OUT / 'validation-v1.json', dict(pass_all=True, comparisons=comparisons, evidence_sha256=evidence), common.hashes())
