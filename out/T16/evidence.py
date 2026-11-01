"""Pinned T16 evidence utilities. Private state/tables never leave ignored cache."""
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
PIN = '2cbeb36fdd3feb369324aaa88e6e4d2aa3b3d99c'
TABLES = BASE / '.cache/T07-tables'
STATE = BASE / '.cache/T07-state-v2-v1.json'
BASELINE = os.environ.get('GOAL2RUST_BASELINE') == '1'
ENGINE = BASE / ('.cache/T16-baseline/engine' if BASELINE else 'engine')
sys.path[:0] = [str(ORACLE), str(ORACLE / 'runtime')]
if platform.python_implementation() == 'CPython':
    sys.path.insert(0, str(ENGINE / 'python'))


def git(*args, root=BASE):
    return subprocess.check_output(['git', *args], cwd=root, text=True).strip()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=repr).encode()).hexdigest()


def hashes():
    import goal2rust_engine
    import goal2rust.machine
    # Installed pure-Python adapter must match the sources, including on PyPy.
    assert Path(goal2rust.machine.__file__).read_bytes() == (ENGINE / 'python/goal2rust/machine.py').read_bytes()
    files = (sorted((ENGINE / 'src').glob('*.rs'))
             + sorted((ENGINE / 'python').rglob('*.py'))
             + sorted((BASE / 'engine/tests').glob('*.py'))
             + sorted((ORACLE / 'runtime/original_match').rglob('*.py'))
             + sorted((BASE / 'out/T03').glob('*.py'))
             + sorted((BASE / 'out/T04').glob('*.py'))
             + sorted((BASE / 'out/T05').glob('*.py'))
             + sorted((BASE / 'out/T06').glob('*.py'))
             + sorted((BASE / 'out/T07').glob('*.py'))
             + sorted((BASE / 'out/T08').glob('*.py'))
             + sorted((BASE / 'out/T09').glob('*.py'))
             + sorted((BASE / 'out/T10').glob('*.py'))
             + sorted((BASE / 'out/T11').glob('*.py'))
             + sorted((BASE / 'out/T12').glob('*.py'))
             + sorted((BASE / 'out/T13').glob('*.py'))
             + sorted((BASE / 'out/T14').glob('*.py'))
             + sorted((BASE / 'out/T15').glob('*.py'))
             + sorted((BASE / 'out/T16').glob('*.py'))
             + [BASE / 'out/T02/differential_v1.py', BASE / 'out/T02/differential_helpers.py',
                BASE / 'out/T02/mutant_v1.py', ORACLE / 'experiments/E033-original-match-kit/save_boundaries.py']
             + sorted((ORACLE / 'experiments/E036-match-port').glob('*.py'))
             + [ORACLE / 'tests/test_port_seal.py', ORACLE / 'tools/static/port_tables.py', STATE]
             + sorted(TABLES.iterdir())
             + [ENGINE / 'Cargo.toml', ENGINE / 'Cargo.lock', BASE / '.github/workflows/build.yml'])
    result = {str(p.relative_to(BASE)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    for p in Path(goal2rust_engine.__file__).parent.glob('*.so'):
        result[str(p.relative_to(BASE))] = hashlib.sha256(p.read_bytes()).hexdigest()
    return result


def verify():
    assert git('rev-parse', 'HEAD', root=ORACLE) == PIN
    assert not git('status', '--porcelain', root=ORACLE)
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
                native_calls={} if core is None else core.native_calls,
                arm=('baseline' if BASELINE else 'candidate') if core is not None else 'plain',
                bridge_fast_calls={} if core is None else getattr(core, 'bridge_fast_calls', {}))


def write(path, report, before):
    report.update(oracle=PIN, source_sha256=before, source_unchanged=before == hashes(),
                  python=sys.version, node=platform.node())
    with Path(path).open('x') as f:
        json.dump(report, f, indent=2, sort_keys=True)
    assert report['source_unchanged'], 'evidence sources changed during run'
