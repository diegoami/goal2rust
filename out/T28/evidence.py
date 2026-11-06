"""T28 evidence bindings, including exact accepted T25 and preserved epochs."""
import hashlib
import json
import os
import platform
import subprocess
import sys
from pathlib import Path
import capture_support as pure

BASE, ORACLE, PIN, TABLES, STATE = pure.BASE, pure.ORACLE, pure.PIN, pure.TABLES, pure.STATE
BASELINE = os.environ.get('GOAL2RUST_BASELINE') == '1'
ENGINE = BASE / ('.cache/T28-baseline/engine' if BASELINE else 'engine')
if platform.python_implementation() == 'CPython':
    sys.path.insert(0, str(ENGINE / 'python'))
verify, image, deny_original = pure.verify, pure.image, pure.deny_original


def git(*args, root=BASE):
    return subprocess.check_output(['git', *args], cwd=root, text=True).strip()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=repr).encode()).hexdigest()


def source_names():
    path = BASE / 'out/T28/source-inputs-v1.json'
    assert path.exists(), 'Seal the explicit producer source allowlist before canonical execution'
    return json.loads(path.read_text())['proof_sources']


def accepted_path(name):
    if name.startswith('engine/'):
        return '.cache/T28-baseline/' + name
    if name.startswith('.venv-pypy/lib/pypy3.11/site-packages/goal2rust_engine/'):
        return '.cache/T28-baseline/pypy/goal2rust_engine/' + Path(name).name
    return name


def hashes():
    import goal2rust_engine
    import goal2rust.machine
    assert Path(goal2rust.machine.__file__).read_bytes() == (ENGINE/'python/goal2rust/machine.py').read_bytes()
    files=set()
    old=json.loads((BASE/'out/T27/validation-final-v1.json').read_text())
    files.update(BASE/accepted_path(p) for p in old['source_sha256'])
    files.update(BASE/'out/T27'/p for p in old['evidence_sha256'])
    files.update(BASE/p for p in ['out/T27/validation-final-v1.json','.cache/T27-merged-binding-audit.py','.cache/T27-merged-binding-audit-v1.json'])
    saved=json.loads((BASE/'out/T28/baseline-snapshot-v1.json').read_text())
    files.update(BASE/p for p in saved['source_and_binary_sha256'])
    files.update((ENGINE/'src').glob('*.rs'))
    files.update((ENGINE/'python').rglob('*.py'))
    files.update((ENGINE/'python').rglob('*.so'))
    files.update((BASE/'engine/tests').glob('*.py'))
    files.update([ENGINE/'Cargo.toml',ENGINE/'Cargo.lock',BASE/'.github/workflows/build.yml'])
    files.update(BASE/'out/T28'/p for p in source_names())
    for name in ['baseline-snapshot-v1.json','inventory-v1.json','capture-inputs-v1.json','capture-drives-v1.jsonl','captures-v1.json','capture-input-audit-v1.json','proof-plan-v1.json','development-probe-v1.json','live-development-v3.json']:
        files.add(BASE/'out/T28'/name)
    capture=json.loads((BASE/'out/T28/captures-v1.json').read_text())
    files.add(BASE/capture['private_file']);files.update(BASE/p for p in capture['private_shards'])
    for name in ['development-probe-v1.json','live-development-v3.json','rejected-live-development-v1.json','rejected-live-development-v2.json']:
        path=BASE/'out/T28'/name;report=json.loads(path.read_text());files.add(path)
        files.update(BASE/p for p in report['preserved_source_map'].values())
    for name in ['before-native-v1.log','receiver-development-v1.log','development-probe-v1.log','live-development-v1.log','live-development-v2.log','live-development-v3.log','public-cpython-development-v1.log','public-pypy-development-v1.log','rust-development-v1.log','plan-proofs-v1.log']:
        files.add(BASE/'out/T28'/name)
    journal=BASE/'out/T28/preparation-jobs-v1.jsonl'
    with journal.open() as stream:prepared=json.loads(next(stream))
    assert prepared['event']=='controller'
    files.update(BASE/p for p in prepared['preserved_source_map'].values())
    for name in ['source-inputs-v1.json','artifact-archive-v1.json']:
        path=BASE/'out/T28'/name
        if path.exists():
            files.add(path)
            if name=='artifact-archive-v1.json':files.update(BASE/row['archive'] for row in json.loads(path.read_text())['artifacts'])
    files.update((BASE/'.venv-pypy/lib/pypy3.11/site-packages/goal2rust_engine').glob('*.so'))
    files.update(Path(goal2rust_engine.__file__).parent.glob('*.so'))
    return {str(p.relative_to(BASE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}


def select(backend):
    if backend == 'rust':
        from goal2rust import install
        install()


def identity(match):
    core = getattr(match.m, '_core', None)
    return dict(machine_type=type(match.m).__module__ + '.' + type(match.m).__name__,
                native_calls={} if core is None else core.native_calls,
                arm=('baseline' if BASELINE else 'candidate') if core is not None else 'plain',
                bridge_fast_calls={} if core is None else getattr(core, 'bridge_fast_calls', {}))


def write(path, report, before):
    report.update(oracle=PIN, source_sha256=before, source_unchanged=before == hashes(),
                  python=sys.version, node=platform.node())
    with Path(path).open('x') as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
    assert report['source_unchanged'], 'Evidence bindings changed during producer execution'
