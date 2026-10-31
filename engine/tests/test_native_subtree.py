"""T04: actual availability tree, synthetic states, observable calls and pauses."""
import hashlib
import random
import unittest

from original_match.port import load
from original_match.port.engine import PortMachine as Oracle
from original_match.port.guest import PortFrame
from goal2rust.machine import PortMachine, BridgeRunner

ENTRIES = {ad: entry for registry, _ in load(['all'])
           for ad, entry in registry.entries.items()
           if ad in ('0791:2956', '1771:3216')}


def exercise(cls, case, *, root='0791:2956', tapped=True, pause=None,
             variant=None, failure=None, mutant=0):
    rng = random.Random(case)
    # Authored memory, including nonzero untouched/dead bytes.
    memory = bytes(range(256)) * (0x110000 // 256)
    m = cls(memory, 0x823, mutant=mutant) if cls is PortMachine else cls(memory, 0x823)
    log, calls, done = [], {}, []
    mem = m.port_memory()
    for ad, entry in ENTRIES.items():
        v = variant if ad == '1771:3216' else None
        if cls is Oracle:
            def runner(machine, e=entry, v=v):
                calls[e.address] = calls.get(e.address, 0) + 1
                PortFrame(machine, mem, e, v).start()
        else:
            runner = BridgeRunner(entry, v, mem, calls)
        m.port(ad, runner)
    off = [0, 0xfff0, 0xffff, rng.randrange(65536)][case % 4]
    seg = 0x4000
    player = [0, 1, 0xffff, 0xccc, rng.randrange(65536)][case % 5]
    ptr_off = [0, 0xfff8, rng.randrange(65536)][case % 3]
    player_seg = 0x5000
    m._memory[m.DS * 16 + 0xa91b:m.DS * 16 + 0xa91f] = (player_seg << 16 | ptr_off).to_bytes(4, 'little')
    p = player_seg * 16 + ((ptr_off + player * 20 + 14) & 65535)
    m._memory[p] = [0, 1, 127, 128, 255][case % 5]
    flags = [0, 128, 32, 4, 255, 16, rng.randrange(256)][case % 7]
    m._memory[player_seg * 16 + ((ptr_off + player * 20 + 16) & 65535)] = flags
    rec = seg * 16 + ((off + 13) & 65535)
    m._memory[rec:rec + 2] = player.to_bytes(2, 'little')
    for reg in ('eax', 'ebx', 'ecx', 'edx', 'esi', 'edi', 'ebp', 'eflags'):
        m.set_reg(reg, rng.randrange(1 << 32))
    sp = [0, 2, 8, 16, 0x100, 0xfffe][case % 6]
    end = m.far_call(root, [seg, off] if root == '0791:2956' else [player],
                     '000E:0300', 0x3000, sp)
    class Tap:
        def site_enter(self, *x, **kw): log.append(('se', x, kw))
        def site_leave(self, *x, **kw): log.append(('sl', x, kw))
        def listen_enter(self, *x):
            log.append(('le', x))
            return len(log)
        def listen_leave(self, x): log.append(('ll', x))
    if tapped:
        m.io_tap = lambda *x: log.append(('io', x))
        m.listen_tap = m.site_tap = Tap()
    def listener(a, n, v):
        log.append(('w', a, n, v, m.pc()))
        if failure == 'write': raise ValueError('subtree write refused')
    m.on_write(0, 0x10ffff, listener)
    visits = []
    for site in ('0791:2956', '1771:3216', '0791:2968'):
        def handler(replay, site=site):
            visits.append((site, replay))
            if failure == site: raise ValueError('subtree site refused')
            if pause == site and visits.count((site, replay)) == 1: m.stop('pause')
        m.at(site, handler)
    error, suspended = None, None
    try:
        reason = m.run(end, fresh=True)
        if reason == 'pause':
            suspended = [(f.entry.address, f.ss, f.sp, f.bp, f.ret_lin, f.expect_sp,
                          f.after_sp, None if f.waiting is None else
                          (f.waiting.target, f.waiting.args, f.waiting.ret_to)) for f in m.frames]
            m.run(end)
    except Exception as e:
        error = type(e).__name__, str(e)
    m.io_tap = None
    state = (hashlib.sha256(m._memory).hexdigest(), dict(m._registers), log,
             calls, visits, done, error, suspended, list(mem._entries),
             m.no_replay_at, m.running)
    return state, getattr(getattr(m, '_core', None), 'native_calls', {})


class NativeSubtreeTests(unittest.TestCase):
    def test_tree_state_callbacks_and_suspension(self):
        for case in range(100):
            for root in ENTRIES:
                for tapped in (False, True):
                    pause = [None, '1771:3216', '0791:2968'][case % 3]
                    opts = dict(root=root, tapped=tapped, pause=pause)
                    with self.subTest(case=case, **opts):
                        p, _ = exercise(Oracle, case, **opts)
                        r, native = exercise(PortMachine, case, **opts)
                        self.assertEqual(p, r)
                        self.assertEqual(native.get(root), 1)
                        if root == '0791:2956': self.assertEqual(native.get('1771:3216'), 1)

    def test_errors_and_variant_bridge(self):
        for case in range(12):
            for failure in (None, 'write', '0791:2956', '1771:3216', '0791:2968'):
                for variant in (None, 'unavailable-bit-6'):
                    opts = dict(failure=failure, variant=variant)
                    with self.subTest(case=case, **opts):
                        p, _ = exercise(Oracle, case, **opts)
                        r, native = exercise(PortMachine, case, **opts)
                        self.assertEqual(p, r)
                        if variant: self.assertNotIn('1771:3216', native)


if __name__ == '__main__': unittest.main()
