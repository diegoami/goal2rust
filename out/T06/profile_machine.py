"""Diagnostic post-T02 profile. No private state is written; outputs are exclusive.

Run with PYTHONHASHSEED=0 and engine/python on PYTHONPATH. The accepted sealed
oracle stays pinned; compare against the completed T03 state-input receipt.
cProfile costs are not production timings or exact Python/Rust crossing counts.
"""
import argparse
import cProfile
import hashlib
import importlib.util
import inspect
import io
import json
import os
from pathlib import Path
import platform
import pstats
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
ORACLE = ROOT / '.cache/goal2-archaeology'
PIN = 'e0270981883f02ce46a31391e7070079977bbfef'


def git(*args, cwd=ROOT):
    return subprocess.check_output(['git', *args], cwd=cwd, text=True).strip()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=repr).encode()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, required=True, help='new JSON; .prof and .txt alongside')
    args = ap.parse_args()
    paths = [args.out, args.out.with_suffix('.prof'), args.out.with_suffix('.txt')]
    assert not any(p.exists() for p in paths), paths
    assert os.environ.get('PYTHONHASHSEED') == '0'
    assert git('rev-parse', 'HEAD', cwd=ORACLE) == PIN
    assert not git('status', '--porcelain', 'runtime', cwd=ORACLE)
    sys.path[:0] = [str(ORACLE), str(ORACLE / 'runtime'), str(ROOT / 'engine/python')]
    import goal2rust_engine
    import evidence as common
    common.verify()
    common.deny_original()
    from goal2rust import Match
    from original_match import Image, Fixture
    from original_match.assets import reference_image
    from original_match.port import load
    files = (sorted((ORACLE / 'runtime/original_match').rglob('*.py'))
             + sorted((ROOT / 'engine/src').glob('*.rs'))
             + sorted((ROOT / 'engine/python').rglob('*.py'))
             + sorted(Path(goal2rust_engine.__file__).parent.glob('*.so'))
             + sorted((ROOT / 'out/T03').glob('*.py'))
             + [Path(__file__), ROOT / 'engine/Cargo.toml', ROOT / 'engine/Cargo.lock',
                ORACLE / 'experiments/E033-original-match-kit/save_boundaries.py'])

    def hashes():
        return common.hashes()

    before = hashes()
    spec = importlib.util.spec_from_file_location('boundaries', ORACLE / 'experiments/E033-original-match-kit/save_boundaries.py')
    harness = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(harness)
    match = Match(common.image(),
                  Fixture(7, 19, index=9, kind=200), managed=7,
                  substitutions=None, record_draws=True)
    # Diagnostic only: profiling must not trigger the ordinary stretch guard.
    match.timeout_s = 10 ** 6

    def policy(m, data):
        m.answer(quick=True) if data['context'] == 'half_time' else m.answer()

    profile = cProfile.Profile()
    start_cpu, start_wall, load_before = time.process_time(), time.monotonic(), os.getloadavg()
    profile.enable()
    events = harness.drive(match, policy, ())
    profile.disable()
    cpu, wall = time.process_time() - start_cpu, time.monotonic() - start_wall
    result = match.result()
    observed = dict(events=len(events), events_sha256=digest(events),
                    result_sha256=digest(result),
                    records_sha256=digest(match.records_after()),
                    memory_sha256=hashlib.sha256(match.m.read(0, 0x110000)).hexdigest())
    baseline = json.loads((ROOT / 'out/T05/cpu-rust-v1.json').read_text())
    equal = all(baseline[k] == v for k, v in observed.items())
    native = match.m._core.native_calls
    stats = pstats.Stats(profile)
    routines = {}
    for registry, _ in load(['all']):
        for address, entry in registry.entries.items():
            if entry.stub is not None:
                continue
            code = entry.fn.__code__
            _, nc, tt, ct, _ = stats.stats.get((code.co_filename, code.co_firstlineno, code.co_name), (0, 0, 0, 0, {}))
            entries = match.ports.calls.get(address, 0)
            routines[address] = dict(module=registry.name, function=code.co_name,
                                     guest_entries=entries, native_entries=native.get(address, 0),
                                     python_entries=entries - native.get(address, 0),
                                     python_calls_or_resumes=nc, body_self_s=tt, cumulative_s=ct)
    total = sum(match.ports.calls.values())
    report = dict(oracle=PIN, head=git('rev-parse', 'HEAD'), backend='rust',
                  native_calls=native, total_guest_entries=total,
                  python_guest_entries=total - sum(native.values()), routines=routines,
                  source_sha256=before, source_unchanged=before == hashes(),
                  observed=observed, equal_to_T05=equal,
                  machine=dict(node=platform.node(), python=sys.version, load_before=load_before,
                               load_after=os.getloadavg()), profile_cpu_s=cpu, profile_wall_s=wall,
                  limitations='Diagnostic cProfile on accepted sealed pin, one drive; self times exclude inline helpers and aggregate Rust cost. Generator counts include resumes; guest_entries are actual starts. Remaining Python entries are not exact FFI transition counts. Re-profile after translation; no speed claim.')
    stream = io.StringIO()
    summary = pstats.Stats(profile, stream=stream)
    summary.sort_stats('tottime').print_stats(70)
    summary.sort_stats('cumulative').print_stats(70)
    for address, row in sorted(routines.items(), key=lambda item: -item[1]['python_entries'])[:50]:
        print(address, json.dumps(row, sort_keys=True), file=stream)
    profile.dump_stats(str(paths[1]))
    with paths[2].open('x') as f:
        f.write(stream.getvalue())
    with paths[0].open('x') as f:
        json.dump(report, f, indent=2, sort_keys=True)
    assert report['source_unchanged'] and equal, 'profile changed source or match outcome'
    print(json.dumps({k: report[k] for k in ['total_guest_entries', 'python_guest_entries', 'native_calls', 'equal_to_T05', 'profile_cpu_s']}), flush=True)


if __name__ == '__main__':
    main()
