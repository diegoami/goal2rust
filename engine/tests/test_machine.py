"""Machine differentials against d3cf46a3, using synthetic state (no private image).

PYTHONPATH=engine/python:.cache/goal2-archaeology/runtime .venv/bin/python -m unittest discover -s engine/tests -v
"""
import unittest

from original_match.port import Entry, load
from original_match.port.engine import PortMachine as Oracle
from original_match.port.guest import PortFrame, call
from goal2rust.machine import PortMachine, BridgeRunner


class MachineTests(unittest.TestCase):
    def run_case(self, cls, *, far=True, caller_pops=False, tapped=True, stop=False, sp=0x100, value=None):
        m = cls(bytes(0x110000), 0x823)
        log = []
        if tapped:
            m.io_tap = lambda *x: log.append(('io',) + x)
        class Tap:
            def site_enter(self, *x, **kw): log.append(('se', x, kw))
            def site_leave(self, *x, **kw): log.append(('sl', x, kw))
            def listen_enter(self, *x):
                log.append(('le',) + x)
                return len(log)
            def listen_leave(self, x): log.append(('ll', x))
        m.site_tap = m.listen_tap = Tap()
        m.on_write(0, 0x10ffff, lambda a, n, v: log.append(('w', a, n, v, m.pc())))
        mem = m.port_memory()
        def outer(mem, _):
            yield call('0791:0200', 0x12345, -1, ret_to='0791:0110', far=far, caller_pops=caller_pops)
            yield call('0791:0200', 7, 8, ret_to='0791:0110', far=far, caller_pops=caller_pops)
            return value
        def leaf(mem, _):
            # A local frame whose bytes remain after its return.
            mem.enter(2, '0791:0200').w16(-2, 0xbeef, '0791:0201')
            return 0x89abcdef
        entries = [Entry('0791:0100', 'retf 4', outer, 'outer', long=True),
                   Entry('0791:0200', ('retf' if far else 'ret') + ('' if caller_pops else ' 4'), leaf, 'leaf', long=True)]
        calls = {}
        for entry in entries:
            if cls is Oracle:
                def run(machine, e=entry):
                    calls[e.address] = calls.get(e.address, 0) + 1
                    PortFrame(machine, mem, e, None).start()
            else:
                run = BridgeRunner(entry, None, mem, calls)
            m.port(entry.address, run)
        visits = []
        def site(replay):
            visits.append(replay)
            if stop and len(visits) == 1: m.stop('decision')
        m.at('0791:0200', site)
        end = m.far_call('0791:0100', [3, 4], '000E:0300', 0x3000, sp)
        m.set_reg('ebp', 0x12344321)
        log.clear()
        reason = m.run(end, fresh=True)
        frames = [(f.entry.address, f.ss, f.sp, f.bp, f.ret_lin, f.expect_sp, f.after_sp,
                   f.waiting.target) for f in m.frames]
        if stop:
            self.assertEqual(reason, 'decision')
            self.assertTrue(frames)
            m.run(end)
        return (m.snapshot(), log, calls, visits, frames, m.no_replay_at, m.running)

    def test_nested_calls_full_state_and_ordered_taps(self):
        for far in (False, True):
            for caller_pops in (False, True):
                for tapped in (False, True):
                    for stop in (False, True):
                        for sp in (0, 2, 0x100):
                            for value in (None, -2, 0x12345678):
                                with self.subTest(far=far, caller_pops=caller_pops, tapped=tapped,
                                                  stop=stop, sp=sp, value=value):
                                    args = dict(far=far, caller_pops=caller_pops, tapped=tapped,
                                                stop=stop, sp=sp, value=value)
                                    self.assertEqual(self.run_case(Oracle, **args), self.run_case(PortMachine, **args))

    def test_register_aliases(self):
        p, r = Oracle(bytes(0x110000), 0), PortMachine(bytes(0x110000), 0)
        for name in ('eax', 'AX', 'ah', 'al', 'eip', 'ip', 'eflags', 'FLAGS', 'ss', 'gs'):
            for value in (0, -1, 0x123456789abcdef):
                p.set_reg(name, value); r.set_reg(name, value)
                self.assertEqual(p.snapshot(), r.snapshot())
                self.assertEqual(p.reg(name), r.reg(name))

    def test_listener_and_site_reentrancy_and_errors(self):
        def run(cls, fail):
            m = cls(bytes(0x110000), 0x823)
            log = []
            class Tap:
                def site_enter(self, *a, **kw): log.append(('se', m.pc(), a, kw))
                def site_leave(self, *a, **kw): log.append(('sl', m.pc(), a, kw))
                def listen_enter(self, *a):
                    log.append(('le', m.pc(), a))
                    return len(log)
                def listen_leave(self, token): log.append(('ll', m.pc(), token))
            m.site_tap = m.listen_tap = Tap()
            m.set_reg('cs', 0x823); m.set_reg('eip', 0x1234)
            def listener(a, n, v):
                log.append(('w', m.pc(), m.read(a, n)))
                m.on_write(10, 10, lambda *a: log.append(('added', a)))
                if fail == 'write': raise ValueError('write refused')
            m.on_write(10, 10, listener)
            def site(replay):
                log.append(('site', replay, m.pc()))
                m.at('0791:0100', lambda r: log.append(('added_site', r)))
                m.stop('events')
                if fail == 'site': raise ValueError('site refused')
            m.at('0791:0100', site)
            errors = []
            for i in range(2):
                for operation in (lambda: m.write_as(10, 2, -1, m.lin('0791:0200')),
                                  lambda: m.fire('0791:0100')):
                    try: operation()
                    except Exception as e: errors.append((type(e).__name__, str(e)))
            return m.snapshot(), log, errors, m._pc_override
        for fail in ('none', 'write', 'site'):
            with self.subTest(fail=fail):
                self.assertEqual(run(Oracle, fail), run(PortMachine, fail))

    def test_dispatch_error_and_cleanup(self):
        def run(cls, kind):
            m = cls(bytes(0x110000), 0x823)
            mem = m.port_memory()
            def body(mem, _):
                if kind == 'yield': yield 123
                elif kind == 'near': yield call('1771:0200', ret_to='0791:0110', far=False)
                elif kind == 'raise': raise ValueError('body refused')
            entry = Entry('0791:0100', 'retf', body, 'body')
            if kind != 'missing':
                runner = (lambda machine: PortFrame(machine, mem, entry, None).start()) if cls is Oracle else BridgeRunner(entry, None, mem, {})
                m.port(entry.address, runner)
            end = m.far_call(entry.address, [], '000E:0300', 0x3000, 0x100)
            try: m.run(end, fresh=True)
            except Exception as e: error = type(e).__name__, str(e)
            else: error = None
            return m.snapshot(), error, mem._entries, m.running
        for kind in ('yield', 'near', 'raise', 'missing'):
            with self.subTest(kind=kind): self.assertEqual(run(Oracle, kind), run(PortMachine, kind))

    def test_native_seven_full_frames_and_arbitrary_width_listener_values(self):
        import goal2rust_engine
        entries = {ad: e for registry, _ in load(['geometry', 'entrypoints'])
                   for ad, e in registry.entries.items() if ad in goal2rust_engine.PORTS}
        observed_wide = False
        for address, entry in sorted(entries.items()):
            for tapped in (False, True):
                results = []
                for cls in (Oracle, PortMachine):
                    m = cls(bytes(0x110000), 0x823)
                    ds, off = m.DS, 0x8100
                    m._memory[ds*16+off+6] = 12
                    args = [12] if address == '0791:045D' else ([6, ds, off] if address == '0791:26D7' else [ds, off])
                    m.far_call(address, args, '000E:0300', 0x3000, 0x100)
                    mem, log = m.port_memory(), []
                    def listener(a, n, v): log.append(('write', a, n, v, m.pc()))
                    m.on_write(0x30000, 0x3ffff, listener)
                    if tapped: m.io_tap = lambda *x: log.append(('io',) + x)
                    if cls is Oracle: PortFrame(m, mem, entry, None).start()
                    else:
                        # A native routine must bypass its Python body completely.
                        old = entry.fn
                        def forbidden(*args): raise AssertionError('native routine crossed into Python')
                        try:
                            entry.fn = forbidden
                            BridgeRunner(entry, None, mem, {})(m)
                        finally: entry.fn = old
                        self.assertEqual(m._core.native_calls, {address: 1})
                    m.io_tap = None
                    results.append((m.snapshot(), log))
                    observed_wide |= any(x[0] == 'write' and x[2] > 8 and x[3] > 2**64 for x in log)
                with self.subTest(address=address, tapped=tapped): self.assertEqual(*results)
        self.assertTrue(observed_wide, 'must exercise a >64-bit coalesced stack listener value')


if __name__ == '__main__':
    unittest.main()
