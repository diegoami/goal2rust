"""Pinned T03 evidence utilities. Private state/tables never leave ignored cache."""
import builtins
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

BASE = Path(__file__).resolve().parents[2]
ORACLE = BASE / '.cache/goal2-archaeology'
PIN = 'e0270981883f02ce46a31391e7070079977bbfef'
TABLES = BASE / '.cache/T03-tables'
STATE = BASE / '.cache/T03-state-v1.json'
sys.path[:0] = [str(ORACLE), str(ORACLE / 'runtime')]
if platform.python_implementation() == 'CPython':
    sys.path.insert(0, str(BASE / 'engine/python'))


def git(*args, root=BASE):
    return subprocess.check_output(['git', *args], cwd=root, text=True).strip()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=repr).encode()).hexdigest()


def hashes():
    import goal2rust_engine
    import goal2rust.machine
    # Installed pure-Python adapter must match the sources, including on PyPy.
    assert Path(goal2rust.machine.__file__).read_bytes() == (BASE / 'engine/python/goal2rust/machine.py').read_bytes()
    files = (sorted((BASE / 'engine/src').glob('*.rs'))
             + sorted((BASE / 'engine/python').rglob('*.py'))
             + sorted((BASE / 'engine/tests').glob('*.py'))
             + sorted((ORACLE / 'runtime/original_match').rglob('*.py'))
             + sorted((BASE / 'out/T03').glob('*.py'))
             + [BASE / 'out/T02/differential_v1.py', BASE / 'out/T02/differential_helpers.py',
                BASE / 'out/T02/mutant_v1.py', ORACLE / 'experiments/E033-original-match-kit/save_boundaries.py']
             + [BASE / 'engine/Cargo.toml', BASE / 'engine/Cargo.lock'])
    result = {str(p.relative_to(BASE)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    for p in Path(goal2rust_engine.__file__).parent.glob('*.so'):
        result[str(p.relative_to(BASE))] = hashlib.sha256(p.read_bytes()).hexdigest()
    return result


def verify():
    assert git('rev-parse', 'HEAD', root=ORACLE) == PIN
    assert not git('status', '--porcelain', 'runtime', root=ORACLE)
    assert os.environ.get('PYTHONHASHSEED') == '0'


def deny_original():
    spec = importlib.util.spec_from_file_location('seal_test', ORACLE / 'tests/test_port_seal.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    exec(module.BOOTSTRAP.split("sys.argv = ['original_match.check']")[0], {})


def image():
    from original_match import Image
    from original_match.port import tables
    return Image.from_state(json.loads(STATE.read_text()), tables.load(TABLES))


def select(backend):
    if backend == 'rust':
        from goal2rust import install
        install()


def identity(match):
    core = getattr(match.m, '_core', None)
    return dict(machine_type=type(match.m).__module__ + '.' + type(match.m).__name__,
                native_calls={} if core is None else core.native_calls)


def write(path, report, before):
    report.update(oracle=PIN, source_sha256=before, source_unchanged=before == hashes(),
                  python=sys.version, node=platform.node())
    with Path(path).open('x') as f:
        json.dump(report, f, indent=2, sort_keys=True)
    assert report['source_unchanged'], 'evidence sources changed during run'
