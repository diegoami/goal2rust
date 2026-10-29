"""Kit adapter for the Rust machine; semantics pinned to archaeology d3cf46a3.

The inherited methods are address helpers, kit registration/watch helpers, and
snapshot/restore. Execution, register storage, memory IO, frames, guest calls,
returns, sites, and listener delivery live in MachineCore. No oracle source is
patched. install() is process-local and opt-in, including for Match.load replay.
"""
import os

from original_match.machine import Machine
from original_match.port.engine import _PortMemory
from goal2rust_engine import MachineCore


class BridgeRunner:
    def __init__(self, entry, variant, mem, calls):
        self.entry, self.variant, self.mem, self.calls = entry, variant, mem, calls

    def __call__(self, machine, done=None):
        return machine._core.start(machine, self.entry, self.variant, self.mem, self.calls, done)


class _FrameView:
    def __init__(self, **state): self.__dict__.update(state)
    def describe(self):
        if self.waiting is None: return self.entry.address
        return (f'{self.entry.address} waiting on its call of {self.waiting.target} '
                f'(returning to {self.waiting.ret_to})')


class PortMachine(Machine):
    def __init__(self, memory, load, *, native=None, mutant=None):
        self._core = MachineCore(memory, load,
                                 os.environ.get('GOAL2RUST_NATIVE', '1') == '1' if native is None else native,
                                 int(os.environ.get('GOAL2RUST_MACHINE_MUTANT', '0')) if mutant is None else mutant)
        self._memory, self._registers = self._core.memory, self._core.registers
        self.load, self.DS = load, load + 0x2581
        self.proving, self.foreign_hooks, self._recorder = False, 0, None
        self.stop_reason = self.error = None
        self._handlers = {}
        self._resume_lin = self._pc_override = self.no_replay_at = None
        self._writes, self._writes_now, self._writes_span = [], (), (1, 0)
        self.muted = self.running = False
        self.muted_hook = self.site_tap = self.write_tap = self.io_tap = self.listen_tap = None

    @property
    def frames(self):
        return self._core.frames

    def port_memory(self, keys=None): return _PortMemory(self, keys)
    def _bounds(self, linear, n): return self._core.bounds(linear, n)
    def reg(self, name): return self._core.reg(self, name)
    def set_reg(self, name, value): return self._core.set_reg(self, name, value)
    def read(self, linear, n): return self._core.read(self, linear, n)
    def write(self, linear, data): return self._core.write(self, linear, data)
    def write_as(self, linear, size, value, at): return self._core.write_as(self, linear, size, value, at)
    def pc(self): return self._core.pc(self)
    def return_from(self, far, pop=0): return self._core.return_from(self, far, pop)
    def stop(self, reason): self.stop_reason = reason
    def run(self, until, timeout_s=600, fresh=False): return self._core.run(self, until, timeout_s, fresh)
    def _dispatch(self, linear): return self._core.dispatch(self, linear)
    def fire(self, address): return self._core.fire(self, address)
    def at_linear(self, linear, handler): self._handlers.setdefault(linear, []).append(handler)

    def _add_write(self, begin, end, fn, recorder):
        self._writes.append((begin, end, fn, recorder))
        self._writes_now = tuple(self._writes)
        self._writes_span = min(w[0] for w in self._writes), max(w[1] for w in self._writes)

    def watch(self, linear, size, handler):
        def hook(address, wsize, value):
            if address + wsize <= linear or address >= linear + size: return
            old = self.read(linear, size)
            new = bytearray(old)
            for i in range(wsize):
                j = address + i - linear
                if 0 <= j < size: new[j] = value >> (8 * i) & 255
            try: handler(old, bytes(new))
            except Exception as error: self.error = error
        self.on_write(max(0, linear - 3), linear + size - 1, hook)

    def port(self, address, runner):
        if not isinstance(runner, BridgeRunner):
            raise TypeError('Rust machine requires BridgeRunner metadata')
        self._core.port(self, address, runner.entry, runner.variant, runner.mem, runner.calls)


_installed = False


def install():
    """Select the Rust machine for the unmodified kit's engine='port' factory."""
    global _installed
    if not _installed:
        from original_match import port
        from original_match.port import engine
        engine.PortMachine = PortMachine
        port.runner = BridgeRunner
        _installed = True
