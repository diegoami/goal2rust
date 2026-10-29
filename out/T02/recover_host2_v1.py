"""Recover fresh-artifact F40 failures/missing IDs without replacing a completion.

Same recovery rule as T01 and recover_quiet_v1.py. Inputs and every selected raw
line are hashed. Each failed attempt stays intact. For a later failed rerun, pass
all previous files with repeated --prior and choose a new --rerun and --version.
The fresh native proof's source/extension assertions are never bypassed.
"""
import argparse
import hashlib
import json
import os
import signal
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

G2R = Path(__file__).resolve().parents[2]
ROOT = G2R / '.cache/goal2-archaeology'
OUT = G2R / 'out/T02'
PY = G2R / '.venv/bin/python'
PROOF = OUT / 'taps-rust-host2-v1.json'
ap = argparse.ArgumentParser()
ap.add_argument('--prior', type=Path, action='append')
ap.add_argument('--rerun', type=Path, default=OUT / 'family-F40-rust-host2-v2-rerun-v1.jsonl')
ap.add_argument('--version', type=int, default=3)
a = ap.parse_args()
assert a.version >= 3
priors = [p.resolve() for p in (a.prior or [OUT / 'family-F40-rust-host2-v2.jsonl'])]
rerun = a.rerun.resolve()
assert rerun not in priors and len(set(priors)) == len(priors)
tag = f'host2-v{a.version}'
candidate = OUT / f'family-F40-rust-{tag}.jsonl'
assembly = OUT / f'assembly-{tag}.json'
attempts = OUT / f'recovery-attempts-{tag}.jsonl'
stem = f'compare-F40-rust-{tag}'
expected = [json.loads(l)['id'] for l in (G2R / 'out/T01/family-F40-rust-v2.jsonl').read_text().splitlines()]
assert len(expected) == len(set(expected)) == 40


def digest(data):
    return hashlib.sha256(data).hexdigest()


def records(path):
    if not path.exists():
        return {}
    result = {}
    for number, line in enumerate(path.read_bytes().splitlines(keepends=True), 1):
        assert line.endswith(b'\n'), f'partial line: preserve and inspect {path}'
        row = json.loads(line)
        assert row['id'] in expected and row['id'] not in result
        result[row['id']] = (row, line, path, number)
    return result


def source_check():
    proof = json.loads(PROOF.read_text())
    oracle = json.loads((G2R / 'out/T01/dev-taps-python-d3cf46a3.json').read_text())
    for key in ('events', 'events_sha256', 'score', 'draws', 'result_sha256',
                'memory_sha256', 'stretches', 'taps'):
        assert proof[key] == oracle[key], key
    assert proof['goal2rust']['backend'] == 'rust' and proof['goal2rust']['native']
    assert proof['goal2rust']['machine_mutant'] == 0
    assert proof['source_unchanged'] and proof['goal2rust']['source_unchanged']
    assert proof['goal2rust']['native_calls'] == json.loads((OUT / 'taps-rust-v1.json').read_text())['goal2rust']['native_calls']
    for name, sha in proof['goal2rust']['source_sha256'].items():
        assert digest((G2R / name).read_bytes()) == sha, name


def quiet():
    count = 0
    while count < 3:
        load = os.getloadavg()
        count = count + 1 if load[0] < 4 else 0
        print('quiet observation', count, '/3; load', load, flush=True)
        time.sleep(20)


def event(**data):
    with attempts.open('a') as output:
        output.write(json.dumps(dict(utc=datetime.now(timezone.utc).isoformat(), **data)) + '\n')


source_check()
good = {}
failed = []
for path in priors:
    assert path.is_file(), path
    for name, value in records(path).items():
        if value[0]['error'] is not None:
            failed.append(dict(id=name, source=str(path.relative_to(G2R)), line=value[3]))
        else:
            assert name not in good, f'duplicate completion: never choose between records for {name}'
            good[name] = value
needed = [name for name in expected if name not in good]
print('preserved completed', len(good), 'rerun failed/missing', needed, flush=True)
done = records(rerun)
assert set(done) <= set(needed)
assert all(value[0]['error'] is None for value in done.values()), 'rerun errors: preserve, use a new attempt'
if set(done) != set(needed):
    quiet()
    source_check()
    env = dict(os.environ)
    env.update(PYTHONHASHSEED='0', GOAL2RUST_MACHINE='1', GOAL2RUST_NATIVE='1',
               PYTHONPATH=f'{OUT}:{G2R}/engine/python:{ROOT}/runtime:{G2R}/.venv/lib/python3.12/site-packages')
    command = [str(PY), '-B', 'experiments/E036-match-port/family.py', '--family', 'F40',
               '--engine', 'port', '--no-unicorn', '--workers', '2', '--only', ','.join(needed),
               '--out', str(rerun)]
    event(phase='family_start', command=command, load=os.getloadavg())
    with rerun.with_suffix('.log').open('a') as output:
        process = subprocess.Popen(command, cwd=ROOT, env=env, stdout=output,
                                   stderr=subprocess.STDOUT, start_new_session=True)
        print('rerun process group', process.pid, flush=True)
        try:
            code = process.wait()
        except BaseException:
            os.killpg(process.pid, signal.SIGTERM)
            process.wait()
            raise
    event(phase='family_end', returncode=code, load=os.getloadavg())
    assert code == 0, 'rerun failed: preserve and inspect; do not overwrite'
source_check()
done = records(rerun)
assert set(done) == set(needed) and all(value[0]['error'] is None for value in done.values())
selected = {**good, **done}
assert set(selected) == set(expected)
raw = b''.join(selected[name][1] for name in expected)
if not candidate.exists():
    with candidate.open('xb') as output:
        output.write(raw)
    with assembly.open('x') as output:
        json.dump(dict(proof_receipt=str(PROOF.relative_to(G2R)), preserved_failed=failed,
                       inputs={str(p.relative_to(G2R)): digest(p.read_bytes()) for p in [*priors, rerun]},
                       candidate_sha256=digest(raw),
                       lines={name: dict(source=str(selected[name][2].relative_to(G2R)),
                                         line=selected[name][3], sha256=digest(selected[name][1]))
                              for name in expected}), output, indent=2)
assert candidate.read_bytes() == raw
assert json.loads(assembly.read_text())['candidate_sha256'] == digest(raw)
status = OUT / (stem + '.status.json')
log = OUT / (stem + '.log')
command = [str(PY), '-B', 'experiments/E036-match-port/compare.py', '--family', 'F40',
           '--no-screen', '--candidate', str(candidate)]
if not log.exists():
    with log.open('x') as output:
        code = subprocess.run(command, cwd=ROOT, stdout=output, stderr=subprocess.STDOUT).returncode
    with status.open('x') as output:
        json.dump(dict(returncode=code, command=command), output, indent=2)
assert json.loads(status.read_text())['returncode'] == 0
manifest = OUT / f'validation-{tag}.json'
if not manifest.exists():
    command = [str(PY), 'out/T02/validation_manifest_v1.py', str(manifest),
               '--family-file', str(candidate), '--compare-stem', stem,
               '--proof-receipt', str(PROOF), '--check-file', str(OUT / 'check-rust-host2-v1.json'),
               '--differential-file', str(OUT / 'differential-host2-v1.json'),
               '--mutant-file', str(OUT / 'mutant-host2-v1.json'),
               '--tests-file', str(OUT / 'tests-host2-v1.log')]
    for path in [*priors, rerun, assembly, attempts, Path(__file__).resolve(),
                 OUT / 'host2-environment-v1.json', OUT / 'host2-interruptions-v1.jsonl']:
        command.extend(['--extra-evidence', str(path)])
    subprocess.run(command, cwd=G2R, check=True)
quiet()
source_check()
receipts = [OUT / f'cpu-{name}-v1.json' for name in ('python', 'pypy-python', 'rust')]
if not any(p.exists() for p in receipts):
    subprocess.run(['bash', 'out/T02/paired_v1.sh'], cwd=G2R, check=True)
else:
    assert all(p.exists() for p in receipts), 'partial timing attempt: preserve and inspect'
for baseline in receipts[:2]:
    subprocess.run([str(PY), 'out/T01/compare_receipts.py', str(baseline), str(receipts[2])], cwd=G2R, check=True)
print('All local T02 gates passed; publish assessment/checkpoint and recheck final-head CI.', flush=True)
