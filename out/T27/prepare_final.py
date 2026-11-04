"""Resume final builds/freeze/canonical gates only after both pre-seal checks pass.

Exclusive logs and an append-only process journal preserve partial attempts.
This controller performs no merge and no post-writer acceptance audit.
"""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import capture_support as pure
from host_gate import wait_idle

B, O = pure.BASE, pure.BASE/'out/T27'
sha = lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def source_hashes():
    files = set(O.glob('*.py'))
    files.update((B/'engine/src').glob('*.rs'))
    files.update((B/'engine/tests').glob('*.py'))
    files.update((B/'engine/python').rglob('*.py'))
    files.update(B/'engine'/name for name in ['Cargo.toml', 'Cargo.lock', 'pyproject.toml'])
    return {str(p.relative_to(B)):sha(p) for p in sorted(files)}


def append(row):
    with (O/'preparation-jobs-v1.jsonl').open('a') as stream:
        stream.write(json.dumps(dict(time=time.time(), **row), sort_keys=True)+'\n')


def wait_receipt(name, pid, marker):
    path = O/name
    while not path.exists():
        command = Path(f'/proc/{pid}/cmdline')
        assert command.exists() and marker.encode() in command.read_bytes(), (
            'Pre-seal wrapper exited without its receipt; inspect preserved log', name, pid)
        print('WAIT PRE-SEAL', name, pid, flush=True)
        time.sleep(30)
    # The receipt is published by a worker before it exits. Wait for its owned
    # wrapper too, so a late worker assertion cannot be mistaken for completion.
    while Path(f'/proc/{pid}/cmdline').exists():
        command = Path(f'/proc/{pid}/cmdline').read_bytes()
        if not command:
            break  # exited zombie, waiting for the tool host to reap it
        assert marker.encode() in command, ('PID reused', pid)
        time.sleep(2)
    return json.loads(path.read_text())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--plan-wrapper', type=int, required=True)
    parser.add_argument('--live-wrapper', type=int, required=True)
    args = parser.parse_args()
    pure.verify()
    lock = (B/'.cache/T27-preparation.lock').open('a+')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    assert not (O/'preparation-jobs-v1.jsonl').exists(), 'Partial attempt: preserve/audit before retry'
    assert not (O/'preparation-v1.json').exists() and not (O/'freeze-v1.json').exists()
    lock.seek(0)
    lock.truncate()
    lock.write(str(os.getpid()))
    lock.flush()
    before = source_hashes()
    archive = B/'.cache/T27-preparation-sources'
    archive.mkdir(exist_ok=True)
    preserved = {}
    for name, digest in before.items():
        target = archive/digest
        if not target.exists():
            with target.open('xb') as stream:
                stream.write((B/name).read_bytes())
        assert sha(target) == digest
        preserved[name] = str(target.relative_to(B))
    append(dict(event='controller', pid=os.getpid(), source_sha256=before,
                preserved_source_map=preserved,
                plan_wrapper=args.plan_wrapper, live_wrapper=args.live_wrapper))
    plan = wait_receipt('proof-plan-v1.json', args.plan_wrapper, 'plan-admission-v2.log')
    live = wait_receipt('live-development-v1.json', args.live_wrapper, 'live-admission-v1.log')
    assert plan['distinct_error_selectors'] == plan['error_execution_rows'] == len(plan['preseal_reached_errors'])
    assert all(row['error'] is not None for row in plan['preseal_reached_errors'].values())
    assert plan['test_source_sha256'] == sha(B/'engine/tests/test_strength.py')
    assert plan['branch_probe_sha256'] == sha(O/'branch_probe.py')
    assert plan['inventory_sha256'] == sha(O/'inventory-v1.json')
    assert live['pass_all'] and live['comparisons'] == 1280 and len(live['scenarios']) == 8
    assert live['development_only'] and not live['accepted_canonical_evidence']
    for original, digest in live['executed_source_sha256'].items():
        assert sha(B/original) == sha(B/live['preserved_source_map'][original]) == digest, original
    for name, digest in json.loads((O/'capture-inputs-v1.json').read_text())['source_sha256'].items():
        assert sha(B/name) == digest, name
    assert source_hashes() == before, 'Sources changed while waiting; inspect and preserve this attempt'

    common = dict(os.environ, PYTHONHASHSEED='0', CARGO_HOME=str(B/'.cache/cargo'),
                  RUSTUP_HOME=str(B/'.cache/rustup'),
                  PATH=str(B/'.cache/cargo/bin')+os.pathsep+os.environ['PATH'])
    rows = []

    def run(name, command, **extra):
        wait_idle()
        assert source_hashes() == before, ('Prepared source changed', name)
        with (O/(name+'.log')).open('x') as log:
            child = subprocess.Popen(command, cwd=B, env=dict(common, **extra), stdout=log,
                                     stderr=subprocess.STDOUT, start_new_session=True)
            row = dict(name=name, pid=child.pid, command=command)
            rows.append(row)
            append(dict(event='start', **row))
            print('START', name, child.pid, flush=True)
            code = child.wait()
        append(dict(event='exit', name=name, pid=child.pid, code=code))
        print('EXIT', name, code, flush=True)
        assert code == 0, ('Failed preparation stage; preserve log and journal', name, code)
        assert source_hashes() == before, ('Source changed during preparation', name)

    maturin = str(B/'.venv/bin/maturin')
    cp, pp = str(B/'.venv/bin/python'), str(B/'.venv-pypy/bin/python')
    run('build-cpython-final-v1', [maturin, 'develop', '--release', '--locked',
        '--manifest-path', 'engine/Cargo.toml'], VIRTUAL_ENV=str(B/'.venv'))
    wheels = B/'.cache/T27-final-pypy-wheels-v1'
    assert not wheels.exists(), 'Preserve an existing final wheel directory'
    run('build-pypy-final-v1', [maturin, 'build', '--release', '--locked',
        '--manifest-path', 'engine/Cargo.toml', '--interpreter', pp, '--out', str(wheels)])
    paths = sorted(wheels.glob('*.whl'))
    assert len(paths) == 1
    run('install-pypy-final-v1', [pp, '-m', 'pip', 'install', '--no-index', '--no-deps',
        '--force-reinstall', str(paths[0])])
    for name, interpreter, paths in [('cpython', cp, [B/'engine/python', pure.ORACLE/'runtime']),
                                     ('pypy', pp, [pure.ORACLE/'runtime'])]:
        run('public-'+name+'-preflight-v1', [interpreter, '-B', '-m', 'unittest',
            'discover', '-s', 'engine/tests', '-v'], PYTHONPATH=os.pathsep.join(map(str, paths)))
        text = (O/('public-'+name+'-preflight-v1.log')).read_text()
        assert 'Ran 102 tests' in text and text.rstrip().endswith('OK')
    run('archive-artifacts-v1', [cp, '-B', 'out/T27/archive_artifacts.py'])
    run('freeze-v1', [cp, '-B', 'out/T27/freeze.py'])
    # Every source is now frozen. The canonical controller applies its own idle
    # and quiet/load rules; it never rebuilds or replaces a completed receipt.
    run('supervisor-v1', [cp, '-u', '-B', 'out/T27/supervise.py'])
    assert source_hashes() == before
    report = dict(pass_all=True, controller_pid=os.getpid(), processes=rows,
                  preseal_wrappers=[args.plan_wrapper, args.live_wrapper],
                  source_sha256=before, source_unchanged=True, script_sha256=sha(Path(__file__)),
                  preserved_source_map=preserved,
                  post_writer_audits_pending=True, merge_performed=False)
    with (O/'preparation-v1.json').open('x') as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print('Canonical controller exited; run actual-host post-writer audits after this controller exits', flush=True)


if __name__ == '__main__':
    main()
