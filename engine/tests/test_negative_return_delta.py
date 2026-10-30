"""Review #6: exercise DOS's shifted far-return frame with synthetic memory."""
import copy
import unittest

from original_match.port import Entry, load
from original_match.port.engine import PortMachine as Oracle
from original_match.port.guest import PortFrame
from goal2rust.machine import BridgeRunner, PortMachine


class NegativeReturnDeltaTests(unittest.TestCase):
    def run_dos(self, cls, *, sp=0x100, tapped=True, stop=False, ignore_delta=False):
        machine = cls(bytes(0x110000), 0x823)
        mem, calls, log = machine.port_memory(), {}, []
        entry = copy.copy(load(['menus'])[0][0].entries['235C:0000'])
        self.assertEqual((entry.far, entry.pop, entry.return_stack_delta), (True, 6, -2))
        if ignore_delta:
            entry.return_stack_delta = 0

        # INT 21h's vector leads to a synthetic IRET-like port. DOS.MsDos itself
        # is the real pinned Python body, including its shifted return frame.
        target = '0791:0400'
        machine._memory[0x84:0x88] = b'\x00\x04' + machine.seg(0x0791).to_bytes(2, 'little')
        record = 0x28000 + 0x200
        words = [0x1234, 0x2345, 0x3456, 0x4567, 0x5678, 0x6789, 0x789a, 0x2890, 0x29a0]
        machine._memory[record:record + 18] = b''.join(w.to_bytes(2, 'little') for w in words)

        def interrupt(mem, _):
            self.assertEqual(mem.reg('ax'), words[0])
            self.assertEqual(mem.reg('ds'), words[7])
            mem.set_reg('ax', 0xabcd)
            mem.set_reg('dx', 0xdef0)

        handler = Entry(target, 'retf 2', interrupt, 'synthetic_interrupt')
        for current in (entry, handler):
            if cls is Oracle:
                def runner(m, e=current):
                    calls[e.address] = calls.get(e.address, 0) + 1
                    PortFrame(m, mem, e, None).start()
            else:
                runner = BridgeRunner(current, None, mem, calls)
            machine.port(current.address, runner)

        class Tap:
            def site_enter(self, *args, **kw): log.append(('site_enter', args, kw))
            def site_leave(self, *args, **kw): log.append(('site_leave', args, kw))
            def listen_enter(self, *args):
                log.append(('listen_enter', args))
                return len(log)
            def listen_leave(self, token): log.append(('listen_leave', token))

        machine.site_tap = machine.listen_tap = Tap()
        machine.on_write(0, 0x10ffff, lambda a, n, v: log.append(('write', a, n, v, machine.pc())))
        if tapped:
            machine.io_tap = lambda *args: log.append(('io', args))
        visits = []

        def at_interrupt(replay):
            visits.append(replay)
            if stop and len(visits) == 1:
                machine.stop('decision')

        machine.at(target, at_interrupt)
        end = machine.far_call(entry.address, [0x2800, 0x200], '000E:0300', 0x3000, sp)
        machine.set_reg('ebp', 0x12344321)
        log.clear()
        error, stopped_frames = None, []
        try:
            reason = machine.run(end, fresh=True)
            if stop:
                self.assertEqual(reason, 'decision')
                stopped_frames = [(f.entry.address, f.ss, f.sp, f.bp, f.ret_lin,
                                   f.expect_sp, f.after_sp, f.waiting.target) for f in machine.frames]
                self.assertEqual(len(stopped_frames), 1)
                machine.run(end)
        except Exception as exc:
            error = type(exc).__name__, str(exc)
        snapshot = machine.snapshot()
        returned_sp, returned_pc = machine.reg('sp'), machine.pc()
        # Two pointer words + a far return consume eight bytes in the caller,
        # despite this body's shifted frame and retf 6 metadata.
        if not ignore_delta:
            self.assertIsNone(error)
            self.assertEqual(returned_sp, (sp + 8) & 0xffff)
            self.assertEqual(returned_pc, end)
            self.assertEqual(machine.read(record, 2), b'\xcd\xab')
            self.assertEqual(machine.read(record + 6, 2), b'\xf0\xde')
            self.assertFalse(machine.frames)
            self.assertFalse(mem._entries)
        return snapshot, log, calls, visits, stopped_frames, error, returned_sp, returned_pc

    def test_real_dos_shifted_frame_full_state_and_ordered_callbacks(self):
        for sp in (0, 2, 0x100, 0xfffe):
            for tapped in (False, True):
                for stop in (False, True):
                    with self.subTest(sp=sp, tapped=tapped, stop=stop):
                        args = dict(sp=sp, tapped=tapped, stop=stop)
                        self.assertEqual(self.run_dos(Oracle, **args), self.run_dos(PortMachine, **args))

    def test_ignoring_negative_delta_is_detected(self):
        oracle = self.run_dos(Oracle)
        mutant = self.run_dos(PortMachine, ignore_delta=True)
        self.assertNotEqual(oracle, mutant)
        self.assertIsNotNone(mutant[5], 'wrong return frame must fail the drive')


if __name__ == '__main__':
    unittest.main()
