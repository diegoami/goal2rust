"""Pinned T24 evidence utilities. Private state/tables never leave ignored cache."""
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
ENGINE = BASE / ('.cache/T25-baseline/engine' if BASELINE else 'engine')
sys.path[:0] = [str(ORACLE), str(ORACLE / 'runtime')]
if platform.python_implementation() == 'CPython':
    sys.path.insert(0, str(ENGINE / 'python'))


def git(*args, root=BASE):
    return subprocess.check_output(['git', *args], cwd=root, text=True).strip()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=repr).encode()).hexdigest()


def source_names():
    manifest=BASE/'out/T25/source-inputs-v1.json'
    return json.loads(manifest.read_text())['proof_sources'] if manifest.exists() else sorted(p.name for p in (BASE/'out/T25').glob('*.py'))


def hashes():
    import goal2rust_engine
    import goal2rust.machine
    assert Path(goal2rust.machine.__file__).read_bytes()==(ENGINE/'python/goal2rust/machine.py').read_bytes()
    files=[]
    # Accepted primary bindings remain independently verifiable after replacing
    # runtime files: map only replaced engine/interpreter files to saved T24.
    old=json.loads((BASE/'out/T24/validation-final-v1.json').read_text())
    for name in old['source_sha256']:
        if name.startswith('engine/'):name='.cache/T25-baseline/'+name
        elif name.startswith('.venv-pypy/lib/pypy3.11/site-packages/goal2rust_engine/'):name='.cache/T25-baseline/pypy/goal2rust_engine/'+Path(name).name
        files.append(BASE/name)
    supplemental=json.loads((BASE/'out/T24/supplemental-source-inputs-v1.json').read_text())
    for key in ['source_sha256','input_sha256']:files += [BASE/p for p in supplemental[key]]
    saved=json.loads((BASE/'out/T25/baseline-snapshot-v1.json').read_text())
    files += [BASE/p for p in saved['source_and_binary_sha256']]
    files += sorted((ENGINE/'src').glob('*.rs'))+sorted((ENGINE/'python').rglob('*.py'))+sorted((BASE/'engine/tests').glob('*.py'))
    files += [ENGINE/'Cargo.toml',ENGINE/'Cargo.lock',BASE/'.github/workflows/build.yml']
    files += sorted((ORACLE/'runtime/original_match').rglob('*.py'))+sorted((ORACLE/'experiments/E036-match-port').glob('*.py'))
    family_dir=ORACLE/'experiments/E036-match-port/families'
    files += sorted(p for p in family_dir.rglob('*') if p.is_file() and p.suffix in ['.json','.py'])
    display_profile=json.loads((family_dir/'display/profile.json').read_text())
    files += [ORACLE/display_profile[k] for k in ['reference','proof']]
    files += [ORACLE/'tests/test_port_seal.py',ORACLE/'tools/static/port_tables.py',ORACLE/'experiments/E033-original-match-kit/save_boundaries.py',STATE]+sorted(TABLES.iterdir())
    for stage in range(3,25):files += sorted((BASE/f'out/T{stage:02}').glob('*.py'))
    files += [BASE/'out/T25'/n for n in source_names()]
    files += [BASE/p for p in ['out/T24/validation-final-v1.json','out/T24/supplemental-source-inputs-v1.json','out/T24/profile-reference-audit-v1.json','out/T24/baseline-snapshot-v1.json','out/T24/process-closure-v1.json','out/T24/performance-selection-v1.json','out/T24/performance-v1.json','out/T24/performance-v2.json','out/T24/profile-after-v1.json','out/T25/baseline-snapshot-v1.json','out/T25/inventory-v1.json','out/T25/rejected-inventory-v1.json','out/T25/inventory-v2.json','out/T25/capture-inputs-v1.json','out/T25/capture-drives-v1.jsonl','out/T25/captures-v1.json','.cache/T25-inventory-v1.py','.cache/T25-raw/captures-v1.pkl']]
    files += sorted((BASE/'.cache/T25-raw/capture-shards-v1').glob('*.pkl'))
    files += [BASE/p for p in ['.cache/T25-live-development-v1.json','.cache/T25-branch-probe-development-v1.py','.cache/T25-evidence-development-v1.py','out/T25/development-provenance-v1.json']]
    for name in ['source-inputs-v1.json','proof-plan-v1.json','artifact-archive-v1.json']:
        p=BASE/'out/T25'/name
        if p.exists():files.append(p)
    files += sorted((BASE/'.venv-pypy/lib/pypy3.11/site-packages/goal2rust_engine').glob('*.so'))
    files += sorted(Path(goal2rust_engine.__file__).parent.glob('*.so'))
    return {str(p.relative_to(BASE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(files))}


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
