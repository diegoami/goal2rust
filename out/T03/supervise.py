"""One resumable T03 supervisor. Refuse overwrites; append status; retain failures."""
import json
import os
import subprocess
import sys
import time
import common
import fcntl

OUT = common.BASE / 'out/T03'
PY = str(common.BASE / '.venv/bin/python')
common.verify()
lock = (common.BASE / '.cache/T03-supervisor.lock').open('a+')
fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
lock.seek(0)
lock.truncate()
lock.write(str(os.getpid()))
lock.flush()
jobs = {}


def start(name, args, extra=None):
    receipt = OUT / (name + '.json')
    if name == 'family-ALL-v1': receipt = OUT / 'attest-family-ALL-v1-invocation.json'
    if receipt.exists():
        row = json.loads(receipt.read_text())
        assert row.get('source_unchanged') and row.get('exit_code', 0) == (1 if name == 'body-mutant-v1' else 0), name
        for path, sha in row['source_sha256'].items():
            import hashlib
            assert hashlib.sha256((common.BASE / path).read_bytes()).hexdigest() == sha, name
        jobs[name] = None, None
        print('ALREADY COMPLETE', name, flush=True)
        return
    env = dict(os.environ, PYTHONHASHSEED='0')
    if extra: env.update(extra)
    log = (OUT / f'{name}.log').open('a')
    process = subprocess.Popen(args, cwd=common.BASE, env=env, stdout=log, stderr=subprocess.STDOUT,
                               start_new_session=True)
    jobs[name] = process, log
    with (OUT / 'jobs-v1.jsonl').open('a') as f:
        f.write(json.dumps(dict(event='start', name=name, pid=process.pid, command=args, time=time.time())) + '\n')
    print('START', name, process.pid, flush=True)
    return process


def wait(names):
    pending = set(names)
    while pending:
        for name in list(pending):
            process, log = jobs[name]
            code = 0 if process is None else process.poll()
            if code is not None:
                if log is None:
                    pending.remove(name)
                    continue
                log.close()
                with (OUT / 'jobs-v1.jsonl').open('a') as f:
                    f.write(json.dumps(dict(event='exit', name=name, pid=process.pid, code=code, time=time.time())) + '\n')
                print('EXIT', name, code, flush=True)
                assert code == 0, name
                pending.remove(name)
        if pending: time.sleep(5)


start('family-ALL-v1', [PY, '-B', 'out/T03/run_family.py', '--out', 'out/T03/family-ALL-rust-v1.jsonl',
                      '--attest', 'out/T03/attest-family-ALL-v1'])
start('check-v1', [PY, '-B', 'out/T03/run_check.py', '--out', 'out/T03/check-v1.json'],
      dict(GOAL2RUST_T03='1', GOAL2RUST_T03_ATTEST='out/T03/attest-check-v1',
           PYTHONPATH=os.pathsep.join([str(OUT), str(common.BASE / 'engine/python'), str(common.ORACLE / 'runtime')])))
start('differential-v1', [PY, '-B', 'out/T03/run_differential.py', '--out', 'out/T03/differential-v1.json'])
wait(['differential-v1'])
start('body-mutant-v1', [PY, '-B', 'out/T03/run_differential.py', '--body-mutant', '1', '--out', 'out/T03/body-mutant-v1.json'])
start('machine-mutant-v1', [PY, '-B', 'out/T03/run_machine_mutant.py', 'out/T03/machine-mutant-v1.json'])
wait(['body-mutant-v1', 'machine-mutant-v1'])
for backend in ['python', 'rust']:
    start('taps-' + backend + '-v1', [PY, '-B', 'out/T03/run_receipt.py', '--backend', backend, '--mode', 'taps',
                                    '--out', f'out/T03/taps-{backend}-v1.json'])
    wait(['taps-' + backend + '-v1'])
wait(['taps-python-v1', 'taps-rust-v1', 'check-v1', 'family-ALL-v1'])
if not (OUT / 'compare-F40-v1.status.json').exists():
    subprocess.run([PY, '-B', 'out/T03/finish.py', 'family'], check=True)
quiet = 0
while quiet < 3:
    loads = os.getloadavg()
    quiet = quiet + 1 if max(loads[:2]) < 4 else 0
    with (OUT / 'quiet-v1.jsonl').open('a') as f: f.write(json.dumps(dict(time=time.time(), load=loads, quiet=quiet)) + '\n')
    print('QUIET', loads, quiet, flush=True)
    if quiet < 3: time.sleep(10)
for name, interpreter, backend in [('python', PY, 'python'), ('pypy', str(common.BASE / '.venv-pypy/bin/python'), 'python'), ('rust', PY, 'rust')]:
    start('cpu-' + name + '-v1', [interpreter, '-B', 'out/T03/run_receipt.py', '--backend', backend, '--mode', 'cpu',
                                '--out', f'out/T03/cpu-{name}-v1.json'])
wait(['cpu-python-v1', 'cpu-pypy-v1', 'cpu-rust-v1'])
if not (OUT / 'validation-v1.json').exists():
    subprocess.run([PY, '-B', 'out/T03/finish.py', 'final'], check=True)
print('ALL T03 PRODUCER GATES PASS', flush=True)
