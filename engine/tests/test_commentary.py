"""T26 complete offside/commentary closure, including all nested source code."""
import hashlib
import importlib
import inspect
import json
import random
import sys
import types
import unittest
from pathlib import Path
from original_match.port import Entry, load
from original_match.port.engine import PortMachine as Oracle
from original_match.port.guest import PortFrame
from original_match.port import runtime
from goal2rust.machine import PortMachine, BridgeRunner

BASE = Path(__file__).resolve().parents[2]
INV = json.loads((BASE / 'out/T26/inventory-v1.json').read_text())
NEW = tuple(sorted(INV['bodies']))
ENTRIES = {a: e for registry, _ in load(['all']) for a, e in registry.entries.items()}
RETURNS = tuple(s['ret_to'] for s in INV['guest_sites'])
SITES = tuple(dict.fromkeys(NEW + tuple(INV['boundaries']) + RETURNS))
OWNED = {}
for module in {'.'.join(row['symbol'].split('.')[:3]) for row in INV['owned_code_objects'].values()}:
    for fn in vars(importlib.import_module(module)).values():
        if not inspect.isfunction(fn) or fn.__module__ != module:
            continue
        todo = [fn.__code__]
        while todo:
            code = todo.pop()
            name = module + '.' + code.co_qualname + ':' + str(code.co_firstlineno)
            if name in INV['owned_code_objects']:
                OWNED[code] = name
            todo += [v for v in code.co_consts if isinstance(v, types.CodeType)]
assert len(OWNED) == 31
OUTPUTS = tuple((root, 264 + i * 7 + j) for i, root in enumerate(NEW) for j in range(7))


def exercise(cls, case, *, root='0791:56D9', tapped=True, listener=True, pause=None,
             failure=None, variant=None, mutant=0, direct=False, snapshot=None,
             controlled=False, mutations=False, profile=False):
    rng = random.Random(case)
    m = cls(bytes(0x110000), 0x823, mutant=mutant) if cls is PortMachine else cls(bytes(0x110000), 0x823)
    mem = m.port_memory()
    ds = m.DS * 16
    calls, log, visits, done = {}, [], [], []
    scope = dict(active=False, owned={}, outside=0)
    state = dict(writes={}, mutations=0, read_index=0, write_index=0)

    def put(at, value, n=1):
        m._memory[at:at+n] = (value & ((1 << (8*n))-1)).to_bytes(n, 'little')

    for ad, original in ENTRIES.items():
        entry, v = original, variant if ad == root else None
        if controlled and ad != root:
            def abi(view, v, ad=ad):
                entry_sp, far = view._entries[-1]
                base = view.ss_lin(entry_sp+(4 if far else 2))
                packet = tuple(view.u16(base+2*i) for i in range(ENTRIES[ad].pop//2))
                ret = next(f.waiting.ret_to for f in reversed(m.frames)
                           if f.waiting is not None and f.waiting.target == ad)
                log.append(('abi', ad, packet, ret))
                if ad == '0791:1D4A':
                    put(ds+0x80ee, [0, 1, 2, 32767, 32768, 65535][case % 6], 2)
                if ad == '23E4:0644':
                    _, off, seg, _, _ = packet
                    text = (b'\x01A\x01' if ret == '0791:1873' else b'X\x01' if ret == '0791:18BD'
                            else b'Y\x02' if ret == '0791:190E' else b'ZZ')
                    for k, byte in enumerate(bytes([len(text)])+text):
                        put(seg*16+((off+k) & 65535), byte)
                for reg, value in [('ax', [0, 1, 0xffff, 0x8000][case % 4]), ('dx', case ^ 0x1234)]:
                    view.set_reg(reg, value)
            entry = Entry(ad, original.ret, abi, 'controlled ' + ad, original.long,
                          original.stub, original.return_stack_delta)
            v = 'T26-controlled'
        if cls is Oracle:
            def runner(machine, entry=entry, v=v):
                calls[entry.address] = calls.get(entry.address, 0) + 1
                PortFrame(machine, mem, entry, v).start()
        else:
            runner = BridgeRunner(entry, v, mem, calls)
        m.port(ad, runner)
    sp = [0xff00, 0x100, 0, 2, 0xfffe, 0xffff][case % 6]
    if snapshot is None:
        for reg in ['eax', 'ebx', 'ecx', 'edx', 'esi', 'edi', 'ebp', 'eflags']:
            m.set_reg(reg, rng.randrange(1 << 32))
        for pointer, off, seg in [(0xa917, 0x100, 0x5000), (0xa91b, 0x200, 0x6000),
                                  (0x9b6c, 0x100, 0x7000), (0xa96a, 0x800, 0x8000),
                                  (0xa972, 0x1800, 0x9000), (0x7c16, 0x800, 0x8000)]:
            put(ds + pointer, off, 2)
            put(ds + pointer + 2, seg, 2)
        for side in range(2):
            put(ds + 0x668 + side, side * 11)
            put(ds + 0x9b34 + 2*side, side, 2)
            for slot in range(1, 12):
                put(0x50000 + 0x100 + side*0xbf + 2*slot-2, slot+side*11, 2)
        for slot in range(23):
            put(ds + ((0x80e8 + 22*slot + 13) & 65535), slot, 2)
            put(0x60000 + 0x200 + 20*slot + 18, (case*331+slot) & 65535, 2)
        for code in range(4):
            text = [b'', b'abc', b'\x01foo\x01', b'\x01bar\x02'][code]
            if code == 3 and case % 8 >= 4:
                text = b'Q'*35
            at = ds+0xbe+21*code
            for k, byte in enumerate(bytes([len(text)])+text):
                put(at+k, byte)
            put(ds+0x720+code, [0, 1, 255, 128][code])
        for name in range(24):
            for k, byte in enumerate(bytes([3])+b'XYZ'):
                put(0x70000+0x100+11*name+k, byte)
        put(m.seg(0x791)*16+0x1827, 1)
        put(m.seg(0x791)*16+0x1828, 32)
        put(ds+0x8319, case % 2)
        put(ds+0x831b, (case//2) % 2, 2)
        put(ds+0x7920, 1)
        put(ds+0x7921, 255)
        put(ds+0x830e, [0, 1, 12, 22][case % 4])
        put(ds+0x8329, (case//4) % 2)
        put(ds+0x832e, 7)
        put(ds+0x832f, 9)
        ring = [0, 1, 2, 199, 200][case % 5]
        put(ds+0x80ee, ring, 2)
        for index in range(201):
            at = ds+0x7c38+6*index
            put(at, (case % 4) ^ int((case//4) % 3 == 1))
            put(at+1, 1, 2)
            put(at+3, 2, 2)
            put(at+5, (case % 2) ^ int((case//6) % 2 == 1))
        parent = 0x600
        for k, value in [(4, case % 4), (6, (case//3) % 3), (8, (case//2) % 3), (10, case % 2)]:
            put(0x20000+parent+k, value, 2)
        if root in ['0791:1C78', '0791:1E53', '0791:56D9']:
            packet = [parent]
        elif root in ['0791:1EB5', '0791:1D4A']:
            packet = [case % 4, (case//3) % 3, (case//2) % 3, case % 2]
        elif root == '0791:1829':
            packet = [33, [1, 2, 4, 5, 255][case % 5], 1]
            if case % 11 == 10:
                put(ds+0x7c38+6, 255)
        elif root == '0791:26A0':
            packet = [case % 3]
        elif root == '0791:2B0F':
            packet = [case % 4]
        elif root == '214B:0018':
            count = [0, 1, 2, 3, 9, 256][case % 6]
            if case == 499:
                count = 65535
            packet = [case*277, count, [0x100, 65535, 65534, 0][case % 4], 0xa000]
        else:
            off = [0x100, 65535, 65534, 0][case % 4]
            put(0xa0000+off, [0, 1, 200, 65535][case % 4], 2)
            packet = [[0, 1, 65535, 32768, 32767][case % 5],
                      [200, 0, 65535][(case//5) % 3], [1, 0, 65535][(case//7) % 3], off, 0xa000]
        if ENTRIES[root].far:
            end = m.far_call(root, list(reversed(packet)), '000E:0300', 0x2000, sp)
        else:
            put(0x20000+sp, 0x300, 2)
            for i, word in enumerate(packet):
                put(0x20000+((sp+2+2*i) & 65535), word, 2)
            for reg, value in [('ss', 0x2000), ('sp', sp), ('ds', m.DS), ('es', m.DS),
                               ('cs', m.seg(0x791)), ('eip', int(root[5:], 16))]:
                m.set_reg(reg, value)
            end = m.lin('0791:0300')
    else:
        memory, regs, entry = snapshot
        m._memory[:] = memory
        m._registers.clear()
        m._registers.update(regs)
        sp, far = entry
        ss = regs['ss']*16
        ip = int.from_bytes(memory[ss+sp:ss+sp+2], 'little')
        cs = int.from_bytes(memory[ss+((sp+2) & 65535):ss+((sp+2) & 65535)+2], 'little') if far else regs['cs'] & 65535
        end = cs*16+ip

    class Tap:
        def site_enter(self, *a, **kw): log.append(('se', a, kw))
        def site_leave(self, *a, **kw): log.append(('sl', a, kw))
        def listen_enter(self, *a): log.append(('le', a)); return len(log)
        def listen_leave(self, token): log.append(('ll', token))
    if tapped:
        def io(kind, at, value):
            log.append(('io', kind, at, bytes(value) if isinstance(value, (bytes, bytearray)) else value))
            if kind == 'r':
                state['read_index'] += 1
                if failure == 'read-index:'+str(state['read_index']): raise ValueError('commentary read refused')
            if kind == 'g' and failure == 'reg:'+str(at): raise ValueError('commentary register refused')
        m.io_tap = io
        m.site_tap = m.listen_tap = Tap()
    if listener:
        def listen(at, n, value):
            state['write_index'] += 1
            pc = m.pc()
            log.append(('w', at, n, value, pc))
            state['writes'][pc] = state['writes'].get(pc, 0)+1
            if failure in ('write', 'write-index:'+str(state['write_index'])) or failure == 'write:'+str(pc):
                raise ValueError('commentary write refused')
            if mutations:
                m._registers['eflags'] ^= 0xc00
                m._registers['eax'] ^= 0x8100
                state['mutations'] += 1
        m.on_write(0, 0x10ffff, listen)
    for site in SITES:
        def handler(replay, site=site):
            if site == root: scope['active'] = True
            visits.append((site, replay))
            log.append(('state', site, hashlib.sha256(m._memory).hexdigest(), dict(m._registers)))
            log.append(('waiting', site, [(f.entry.address, f.waiting.target, tuple(f.waiting.args), f.waiting.ret_to)
                                         for f in m.frames if f.waiting is not None]))
            if failure == site: raise ValueError('commentary site refused')
            if pause == site and sum(s == site for s, _ in visits) == 1: m.stop('pause')
        m.at(site, handler)
    def profiler(frame, event, arg):
        if event == 'call' and frame.f_code in OWNED:
            if scope['active']:
                name = OWNED[frame.f_code]
                scope['owned'][name] = scope['owned'].get(name, 0)+1
            else:
                scope['outside'] += 1
    def finish(frame):
        scope['active'] = False
        done.append((frame.entry.address, frame.value))
    old_profile = sys.getprofile()
    error = suspended = None
    try:
        if profile: sys.setprofile(profiler)
        if direct:
            scope['active'] = True
            if cls is Oracle:
                calls[root] = 1
                PortFrame(m, mem, ENTRIES[root], variant, finish).start()
            else:
                BridgeRunner(ENTRIES[root], variant, mem, calls)(m, finish)
        reason = m.run(end, fresh=True)
        if reason == 'pause':
            suspended = [(f.entry.address, f.ss, f.sp, f.bp, f.ret_lin, f.expect_sp, f.after_sp,
                          None if f.waiting is None else (f.waiting.target, f.waiting.args, f.waiting.ret_to)) for f in m.frames]
            m.run(end)
    except Exception as exc:
        error = (type(exc).__name__, str(exc))
    finally:
        scope['active'] = False
        if profile: runtime.s16(0)
        sys.setprofile(old_profile)
    m.io_tap = None
    return dict(memory=hashlib.sha256(m._memory).hexdigest(), regs=dict(m._registers), log=log,
                calls=calls, visits=visits, done=done, error=error, suspended=suspended,
                state=state, entries=list(mem._entries), frames=[f.describe() for f in m.frames],
                running=m.running, no_replay_at=m.no_replay_at), getattr(getattr(m, '_core', None), 'native_calls', {}), scope


class CommentaryTests(unittest.TestCase):
    def test_body_and_output_controls(self):
        for index, root in enumerate(NEW):
            p, _, _ = exercise(Oracle, 3, root=root)
            r, _, _ = exercise(PortMachine, 3, root=root, mutant=254+index)
            self.assertIsNone(p['error'])
            self.assertNotEqual(p, r)
        for root, control in OUTPUTS:
            p, _, _ = exercise(Oracle, 3, root=root)
            r, _, _ = exercise(PortMachine, 3, root=root, mutant=control)
            self.assertNotEqual(p, r, (root, control))

    def test_real_return_controls(self):
        for index, site in enumerate(INV['guest_sites']):
            for case in range(48):
                p, _, _ = exercise(Oracle, case, root=site['caller'])
                self.assertIsNone(p['error'])
                if site['ret_to'] in {s for s, _ in p['visits']}:
                    r, _, _ = exercise(PortMachine, case, root=site['caller'], mutant=334+index)
                    self.assertNotEqual(p, r, (site['ret_to'], case))
                    break
            else:
                self.fail('unreached real return '+site['ret_to'])

    def test_native_complete_tree(self):
        for root in NEW:
            with self.subTest(root=root):
                for case in range(12):
                    opts = dict(root=root, profile=True, direct=case % 3 == 0,
                                pause=root if case % 5 == 0 else None, mutations=case % 7 == 0)
                    p, _, ps = exercise(Oracle, case, **opts)
                    r, native, rs = exercise(PortMachine, case, **opts)
                    self.assertIsNone(p['error'], (root, case, p['error']))
                    self.assertEqual(p, r, (root, case))
                    self.assertEqual(native.get(root), 1)
                    self.assertTrue(ps['owned'])
                    self.assertFalse(rs['owned'])
                    self.assertGreater(rs['outside'], 0)

    def test_variant_and_error_scope(self):
        for root in NEW:
            for failure in [root, 'reg:ss', 'write']:
                opts = dict(root=root, failure=failure)
                p, _, _ = exercise(Oracle, 1, **opts)
                r, _, _ = exercise(PortMachine, 1, **opts)
                self.assertIsNotNone(p['error'])
                self.assertEqual(p, r)
            p, _, _ = exercise(Oracle, 1, root=root, variant='identity')
            r, native, rs = exercise(PortMachine, 1, root=root, variant='identity', profile=True)
            self.assertEqual(p, r)
            self.assertNotIn(root, native)
            self.assertTrue(rs['owned'])


if __name__ == '__main__':
    unittest.main()
