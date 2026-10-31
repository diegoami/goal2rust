"""Exclusive T05 gate supervisor; receipts immutable, progress/status append-only."""
import fcntl
import hashlib
import json
import os
import subprocess
import sys
import time
import evidence as e

OUT = e.BASE / 'out/T05'
PY = str(e.BASE / '.venv/bin/python')
e.verify()
lock = (e.BASE / '.cache/T05-supervisor.lock').open('a+')
fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
lock.seek(0); lock.truncate(); lock.write(str(os.getpid())); lock.flush()
jobs = {}


def start(name, command, receipt=None, extra=None):
    path = OUT / (receipt or name + '.json')
    if path.exists():
        row = json.loads(path.read_text())
        assert row['source_unchanged'] and row.get('exit_code', 0) == 0
        for p, sha in row['source_sha256'].items():
            assert hashlib.sha256((e.BASE / p).read_bytes()).hexdigest() == sha, (name, p)
        print('COMPLETE', name, flush=True)
        return
    env = dict(os.environ, PYTHONHASHSEED='0', **(extra or {}))
    log = (OUT / (name + '.log')).open('a')
    child = subprocess.Popen(command, env=env, cwd=e.BASE, stdout=log,
                             stderr=subprocess.STDOUT, start_new_session=True)
    jobs[name] = child, log
    append(dict(event='start', name=name, pid=child.pid, command=command, time=time.time()))
    print('START', name, child.pid, flush=True)


def append(row):
    with (OUT / 'jobs-v1.jsonl').open('a') as f: f.write(json.dumps(row) + '\n')


def wait(names):
    previous = 0
    while any(name in jobs for name in names):
        for name in list(jobs):
            process, log = jobs[name]
            code = process.poll()
            if code is not None:
                log.close(); del jobs[name]
                append(dict(event='exit', name=name, pid=process.pid, code=code, time=time.time()))
                print('EXIT', name, code, flush=True)
                assert code == 0, name
        if time.monotonic() - previous > 30:
            family = OUT / 'family-F40-rust-v1.jsonl'
            count = len(family.read_bytes().splitlines()) if family.exists() else 0
            print('PROGRESS', count, '/40 family records;', ','.join(jobs), flush=True)
            previous = time.monotonic()
        if any(name in jobs for name in names): time.sleep(5)


def producer(name, script, *args):
    start(name, [PY, '-u', '-B', 'out/T05/' + script, *args, '--out', 'out/T05/' + name + '.json'])


attest_env = dict(GOAL2RUST_T05='1', GOAL2RUST_T05_ATTEST='out/T05/attest-check-v1',
                 PYTHONPATH=os.pathsep.join([str(OUT), str(e.BASE / 'engine/python'), str(e.ORACLE / 'runtime')]))
start('family-F40-v1', [PY, '-B', 'out/T05/run_family.py', '--out', 'out/T05/family-F40-rust-v1.jsonl',
                      '--attest', 'out/T05/attest-family-F40-v1'], 'attest-family-F40-v1-invocation.json')
start('check-v1', [PY, '-B', 'out/T05/run_check.py', '--out', 'out/T05/check-v1.json'], extra=attest_env)
producer('taps-python-v1', 'run_receipt.py', '--backend', 'python', '--mode', 'taps')
producer('differential-v1', 'differential.py')
wait(['differential-v1'])
for mutant, name in [(4, 'return-mutant-v1'), (3, 'body-mutant-v1')]:
    producer(name, 'differential.py', '--mutant', str(mutant)); wait([name])
wait(['taps-python-v1'])
producer('taps-rust-v1', 'run_receipt.py', '--backend', 'rust', '--mode', 'taps')
wait(['taps-rust-v1'])
producer('profile-after-v1', 'profile_machine.py')
wait(['profile-after-v1', 'check-v1', 'family-F40-v1'])
status = OUT / 'compare-F40-v1.status.json'
if not status.exists():
    command = [PY, '-B', 'experiments/E036-match-port/compare.py', '--family', 'F40',
               '--no-screen', '--candidate', str(OUT / 'family-F40-rust-v1.jsonl')]
    with (OUT / 'compare-F40-v1.log').open('x') as log:
        code = subprocess.call(command, cwd=e.ORACLE, stdout=log, stderr=subprocess.STDOUT)
    with status.open('x') as f: json.dump(dict(command=command, exit_code=code), f, indent=2)
    assert code == 0
quiet = 0
while quiet < 3:
    loads = os.getloadavg(); quiet = quiet + 1 if max(loads[:2]) < 4 else 0
    with (OUT / 'quiet-v1.jsonl').open('a') as f: f.write(json.dumps(dict(time=time.time(), load=loads, quiet=quiet)) + '\n')
    print('QUIET', loads, quiet, flush=True)
    if quiet < 3: time.sleep(10)
for name, interpreter, backend in [('python', PY, 'python'), ('pypy', str(e.BASE / '.venv-pypy/bin/python'), 'python'), ('rust', PY, 'rust')]:
    start('cpu-' + name + '-v1', [interpreter, '-B', 'out/T05/run_receipt.py', '--backend', backend,
                                '--mode', 'cpu', '--out', f'out/T05/cpu-{name}-v1.json'])
wait(['cpu-python-v1', 'cpu-pypy-v1', 'cpu-rust-v1'])
print('ALL PRODUCERS EXITED; run validate.py after this writer exits', flush=True)
