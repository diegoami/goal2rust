"""State-input drive: exclusive hashes/counts, default CPU guards, ordered taps."""
import argparse
import hashlib
import importlib.util
import json
import os
import time
import evidence as common


class Recorder:
    def __init__(self):
        self.h, self.counts, self.token = hashlib.sha256(), {}, 0

    def add(self, kind, *values):
        self.counts[kind] = self.counts.get(kind, 0) + 1
        self.h.update(repr((kind,) + values).encode())

    def io(self, kind, a, b):
        self.add('io', kind, a, bytes(b) if isinstance(b, (bytes, bytearray)) else b)

    def write(self, linear, data): self.add('write', linear, bytes(data))
    def site_enter(self, linear, replay, fired=False): self.add('site_enter', linear, replay, fired)
    def site_leave(self, linear, stopped, fired=False): self.add('site_leave', linear, stopped, fired)

    def listen_enter(self, index, address, size, value):
        self.token += 1
        self.add('listen_enter', index, address, size, value)
        return self.token

    def listen_leave(self, token): self.add('listen_leave', token)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--backend', choices=['python', 'rust'], required=True)
    ap.add_argument('--mode', choices=['cpu', 'taps'], required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    assert not common.Path(a.out).exists()
    common.verify()
    common.select(a.backend)
    common.deny_original()
    from original_match import Match, Fixture
    before = common.hashes()
    m = Match(common.image(), Fixture(7, 19, index=9, kind=200), managed=7,
              substitutions=None, engine='port', record_draws=True)
    assert (hasattr(m.m, '_core')) == (a.backend == 'rust')
    assert m.timeout_s == 60
    if a.mode == 'taps':
        m.timeout_s = 10 ** 6  # instrumentation-only guard, as upstream T167
        recorder = Recorder()
        m.m.io_tap, m.m.write_tap, m.m.site_tap, m.m.listen_tap = recorder.io, recorder.write, recorder, recorder
    else:
        recorder = None
    stretches, advance = [], m._advance

    def timed():
        cpu, wall = time.process_time(), time.monotonic()
        try: return advance()
        finally: stretches.append((time.process_time() - cpu, time.monotonic() - wall))

    m._advance = timed
    spec = importlib.util.spec_from_file_location('boundaries', common.ORACLE / 'experiments/E033-original-match-kit/save_boundaries.py')
    harness = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(harness)

    def policy(match, data):
        match.answer(quick=True) if data['context'] == 'half_time' else match.answer()

    load = os.getloadavg()
    cpu, wall = time.process_time(), time.monotonic()
    events = harness.drive(m, policy, ())
    elapsed = time.process_time() - cpu, time.monotonic() - wall
    result = m.result()
    report = dict(mode=a.mode, backend=a.backend, **common.identity(m),
                  events=len(events), events_sha256=common.digest(events),
                  result_sha256=common.digest(result), records_sha256=common.digest(m.records_after()),
                  memory_sha256=hashlib.sha256(m.m.read(0, 0x110000)).hexdigest(),
                  score=result.get('score'), draws=result.get('draws'),
                  stretches=len(stretches), longest_stretch_cpu_s=max(x[0] for x in stretches),
                  drive_cpu_s=elapsed[0], drive_wall_s=elapsed[1],
                  load_before=load, load_after=os.getloadavg(),
                  input_state_sha256=hashlib.sha256(common.STATE.read_bytes()).hexdigest(),
                  taps=None if recorder is None else dict(sha256=recorder.h.hexdigest(), counts=recorder.counts))
    common.write(a.out, report, before)
    print(json.dumps({k: report[k] for k in ['backend', 'mode', 'events', 'drive_cpu_s', 'taps']}), flush=True)


if __name__ == '__main__': main()
