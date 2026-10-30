"""Exercise the supported separate-process backend comparison contract."""
import json
import os
import subprocess
import sys
import unittest


WORKER = r'''
import hashlib, json, sys
from original_match import port
from original_match.port import engine

backend = sys.argv[1]
if backend == 'rust':
    from goal2rust import install
    install()

m = engine.PortMachine(bytes(0x110000), 0x823)
installed = port.install(m, ['geometry', 'entrypoints'])
address = '0791:2BE5'
ds, off = m.DS, 0x8100
m._memory[ds * 16 + off + 6] = 12
end = m.far_call(address, [ds, off], '000E:0300', 0x3000, 0x100)
log = []
m.io_tap = lambda *args: log.append(('io', args))
m.on_write(0x30000, 0x3ffff, lambda a, n, v: log.append(('write', a, n, v, m.pc())))
m.run(end, fresh=True)
m.io_tap = None
snapshot = m.snapshot()
digest = lambda value: hashlib.sha256(json.dumps(value, sort_keys=True, default=repr).encode()).hexdigest()
core = getattr(m, '_core', None)
print(json.dumps(dict(
    backend=backend,
    machine_type=type(m).__module__ + '.' + type(m).__name__,
    native_calls={} if core is None else core.native_calls,
    outcome=dict(memory_sha256=hashlib.sha256(snapshot['memory']).hexdigest(),
                 regs=snapshot['regs'], callbacks_sha256=digest(log),
                 guest_calls={ad: n for ad, n in installed.calls.items() if n},
                 end_pc=m.pc(), expected_end=end, final_sp=m.reg('sp')))))
'''


class BackendProcessTests(unittest.TestCase):
    def worker(self, backend):
        result = subprocess.run([sys.executable, '-B', '-c', WORKER, backend],
                                env=dict(os.environ, PYTHONHASHSEED='0'),
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def test_plain_and_rust_workers_are_independent_and_equal(self):
        from original_match import port
        from original_match.port import engine
        factory, runner = engine.PortMachine, port.runner
        plain_before = self.worker('python')
        rust = self.worker('rust')
        plain_after = self.worker('python')
        self.assertEqual(plain_before, plain_after)
        self.assertEqual(plain_before['machine_type'], 'original_match.port.engine.PortMachine')
        self.assertEqual(plain_before['native_calls'], {})
        self.assertEqual(rust['machine_type'], 'goal2rust.machine.PortMachine')
        self.assertEqual(rust['native_calls'], {'0791:2BE5': 1})
        self.assertEqual(plain_before['outcome'], rust['outcome'])
        self.assertEqual(rust['outcome']['guest_calls'], {'0791:2BE5': 1})
        self.assertEqual(rust['outcome']['end_pc'], rust['outcome']['expected_end'])
        self.assertEqual(rust['outcome']['final_sp'], 0x108)
        self.assertIs(engine.PortMachine, factory)
        self.assertIs(port.runner, runner)


if __name__ == '__main__':
    unittest.main()
