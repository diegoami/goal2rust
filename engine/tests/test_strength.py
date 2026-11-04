"""T27 complete quick-result strength closure, including all nested source code."""
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
INV = json.loads((BASE / 'out/T27/inventory-v1.json').read_text())
NEW = tuple(sorted(INV['bodies']))
ENTRIES = {a: e for registry, _ in load(['all']) for a, e in registry.entries.items()}
RETURNS = tuple(s['ret_to'] for s in INV['guest_sites'])
SITES = tuple(dict.fromkeys(NEW + tuple(INV['boundaries']) + RETURNS))
OWNED = {}
for module in {'.'.join(row['symbol'].split('.')[:3]) for row in INV['owned_code_objects'].values()}:
    for obj in vars(importlib.import_module(module)).values():
        members = list(vars(obj).values()) if inspect.isclass(obj) and obj.__module__ == module else [obj]
        for fn in members:
            if not inspect.isfunction(fn) or fn.__module__ != module:
                continue
            todo = [fn.__code__]
            while todo:
                code = todo.pop()
                name = module + '.' + code.co_qualname + ':' + str(code.co_firstlineno)
                if name in INV['owned_code_objects']:
                    OWNED[code] = name
                todo += [v for v in code.co_consts if isinstance(v, types.CodeType)]
assert len(OWNED) == 27
OUTPUTS = tuple((root, 366 + i * 7 + j) for i, root in enumerate(NEW) for j in range(7))


def exercise(cls, case, *, root='1771:0BC4', tapped=True, listener=True, pause=None,
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
                for reg, value in [('ax', [0, 1, 0xffff, 0x8000][case % 4]), ('dx', case ^ 0x1234)]:
                    view.set_reg(reg, value)
            entry = Entry(ad, original.ret, abi, 'controlled ' + ad, original.long,
                          original.stub, original.return_stack_delta)
            v = 'T27-controlled'
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
                                  (0xa91f, 0x100, 0x7000)]:
            put(ds+pointer, off, 2)
            put(ds+pointer+2, seg, 2)
        for country in range(3):
            at = 0x50100+country*0xbf
            put(at+0x2e, (country+case)%4)
            put(at+0x2d, [0, 1, 0x55, 0xff][case%4])
            for slot in range(1, 12):
                player = slot if (slot+case)%5 else 0
                put(at+2*(slot-1), player, 2)
        for manager in range(4):
            put(0x70100+3*manager+1, [0, 7, 8, 255][(manager+case)%4])
        for player in range(12):
            at = 0x60200+20*player
            for off, values in [(0,[0,1,2]),(2,[0,1,15,16,255]),(4,[0,61,62,255]),
                                (5,[0,1,15,16,255]),(6,[0,1,3,4,7,8,10,11,12,13,255]),
                                (7,[0,1,7,13,255]),(12,[0,31,32,127,128,255]),
                                (14,[0,1,31,127,128,255]),(15,[0,1,31,224,255]),
                                (16,[0,0,0,128,32,4])]:
                put(at+off, values[(case+player+off)%len(values)])
            if (case+player)%5 == 0:
                put(at+5,15);put(at+2,15)
            if (case+player)%4 == 0:
                put(at+14,64);put(at+16,0);put(at+4,128)
        for pos in range(256):put(ds+0xd4e+pos,(pos+case)%6)
        for k in range(284):put(ds+0xe60+k,(k+case)%2)
        for k in range(3):put(ds+0xe7c+k,k)
        for off, value in [(0x3139,0x55),(0x3159,0xaa),(0xba4,0x7e)]:
            put(m.seg(0x1771)*16+off,value)
        if root=='1771:0BC4':
            packet=[case%3,(case//3)%2,case%3]
        elif root=='1771:0AA7':
            packet=[case%3]
        elif root=='214B:0C57':
            value=[0,1,0xffff,0x8000,rng.randrange(65536)][case%5]
            k=[0,1,2,15,16,17,31,32,33,255,256,65535][case%12]
            packet=[value,k]
        else:
            packet=[1+case%11]
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
        if profile: runtime.shift_count(0)
        sys.setprofile(old_profile)
    m.io_tap = None
    return dict(memory=hashlib.sha256(m._memory).hexdigest(), regs=dict(m._registers), log=log,
                calls=calls, visits=visits, done=done, error=error, suspended=suspended,
                state=state, entries=list(mem._entries), frames=[f.describe() for f in m.frames],
                running=m.running, no_replay_at=m.no_replay_at), getattr(getattr(m, '_core', None), 'native_calls', {}), scope


class StrengthTests(unittest.TestCase):
    def test_body_and_output_controls(self):
        for index, root in enumerate(NEW):
            p, _, _ = exercise(Oracle, 3, root=root)
            r, _, _ = exercise(PortMachine, 3, root=root, mutant=359+index)
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
                    r, _, _ = exercise(PortMachine, case, root=site['caller'], mutant=415+index)
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
