"""Preflight merged T80b without changing the accepted oracle pin.

--prepare writes a private state only under .cache; each backend runs separately
under file/import denial. JSON evidence holds hashes and counts, never state.
This is an early compatibility check, not T03 acceptance or an oracle upgrade.
"""
import argparse
import builtins
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
PREVIEW = ROOT / '.cache/goal2-archaeology-seal-preview'
PIN = 'b46000bc5ef790696cfa3dc6eb905f2b28e5f057'
STATE = ROOT / '.cache/seal-preview-state-v1.json'


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=repr).encode()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--prepare', action='store_true')
    ap.add_argument('--backend', choices=['python', 'rust'])
    ap.add_argument('--out', type=Path)
    a = ap.parse_args()
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=PREVIEW, text=True).strip() == PIN
    assert not subprocess.check_output(['git', 'status', '--porcelain', 'runtime'], cwd=PREVIEW, text=True).strip()
    sys.path[:0] = [str(PREVIEW), str(PREVIEW / 'runtime'), str(ROOT / 'engine/python')]
    from original_match import Image, Fixture
    from original_match.port import tables
    t = tables.load(PREVIEW / 'static/goal-exe/tables')
    if a.prepare:
        from original_match.assets import reference_image
        image = Image.from_savestate(reference_image(ROOT / '.cache/goal2-archaeology/.cache/dl'))
        with STATE.open('x') as f:
            json.dump(image.state(t), f)
        print('prepared private state in ignored cache', flush=True)
        return
    assert a.backend and a.out and not a.out.exists()
    assert os.environ.get('PYTHONHASHSEED') == '0'
    spec = importlib.util.spec_from_file_location('seal_tests', PREVIEW / 'tests/test_port_seal.py')
    seal = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(seal)
    # Run exactly upstream's denial bootstrap, excluding its check invocation.
    exec(seal.BOOTSTRAP.split("sys.argv = ['original_match.check']")[0], {})
    if a.backend == 'rust':
        from goal2rust import Match
    else:
        from original_match import Match
    import goal2rust_engine
    files = (sorted((PREVIEW / 'runtime/original_match').rglob('*.py'))
             + sorted((ROOT / 'engine/src').glob('*.rs'))
             + sorted((ROOT / 'engine/python').rglob('*.py'))
             + sorted(Path(goal2rust_engine.__file__).parent.glob('*.so'))
             + [Path(__file__), PREVIEW / 'tests/test_port_seal.py'])

    def hashes():
        return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}

    before = hashes()
    with STATE.open() as f:
        state = json.load(f)
    image = Image.from_state(state, t)
    match = Match(image, Fixture(7, 19, index=9, kind=200), managed=7,
                  substitutions=None, engine='port', record_draws=True)
    assert (hasattr(match.m, '_core')) == (a.backend == 'rust')
    spec = importlib.util.spec_from_file_location('boundaries', PREVIEW / 'experiments/E033-original-match-kit/save_boundaries.py')
    harness = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(harness)

    def policy(m, data):
        m.answer(quick=True) if data['context'] == 'half_time' else m.answer()

    checkpoint = []

    def capture(index, event, phase):
        if not checkpoint and phase == 'event':
            checkpoint.append((index, match.save()))

    events = harness.drive(match, policy, (), on_event=capture)
    result, after = match.result(), match.records_after()
    # Match.load does not restore the tables object; its explicit tables argument
    # is part of the upstream records_after API and must be supplied after load.
    index, blob = checkpoint[0]
    loaded = Match.load(blob)
    tail = harness.drive(loaded, policy, (), start=index + 1)
    checks = dict(replay_events_equal=tail == events[index + 1:],
                  replay_result_equal=loaded.result() == result,
                  replay_records_equal=loaded.records_after(t) == after,
                  records_roundtrip_equal=Image.from_state(after, t).state() == after)
    core = getattr(match.m, '_core', None)
    receipt = dict(preview_only=True, oracle=PIN, backend=a.backend,
                   machine_type=type(match.m).__module__ + '.' + type(match.m).__name__,
                   native_calls={} if core is None else core.native_calls,
                   events=len(events), events_sha256=digest(events),
                   result_sha256=digest(result), records_sha256=digest(after),
                   memory_sha256=hashlib.sha256(match.m.read(0, 0x110000)).hexdigest(),
                   input_state_sha256=digest(state), checks=checks,
                   source_sha256=before, source_unchanged=before == hashes(),
                   denial='upstream BOOTSTRAP: unicorn imports and .sav/.exe/.dat opens refused',
                   checkpoint_event=index,
                   limitations='Merged T80b preview only; one drive and one replay boundary. Full sealed lifecycle/family, ordered taps, mutants, differential and paired CPU are pending T03.')
    with a.out.open('x') as f:
        json.dump(receipt, f, indent=2, sort_keys=True)
    assert all(checks.values()) and receipt['source_unchanged'], checks
    print(json.dumps({k: receipt[k] for k in ['backend', 'events', 'native_calls', 'checks']}), flush=True)


if __name__ == '__main__':
    main()
