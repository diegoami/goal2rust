"""T29 complete near-player-zone path, all six actual source helpers."""
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
INV = json.loads((BASE / 'out/T29/inventory-v1.json').read_text())
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
assert len(OWNED) == 6
OUTPUTS = tuple((root, 437 + i * 7 + j) for i, root in enumerate(NEW) for j in range(7))


def exercise(cls, case, *, root='0791:44C1', tapped=True, listener=True, pause=None,
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
            v = 'T29-controlled'
        if cls is Oracle:
            def runner(machine, entry=entry, v=v):
                calls[entry.address] = calls.get(entry.address, 0) + 1
                PortFrame(machine, mem, entry, v).start()
        else:
            runner = BridgeRunner(entry, v, mem, calls)
        m.port(ad, runner)
    sp = [0xe000, 0x100, 0, 0xfffe][case % 4]
    if snapshot is None:
        for reg in ['eax','ebx','ecx','edx','esi','edi','ebp','eflags']:
            m.set_reg(reg,rng.randrange(1 << 32))
        ss=0x20000;mode=case%20
        off=[0x100,0xfff9,0xfffa,0xffff][(case//20)%4];seg=0x6000;p=seg*16+off
        x=[10,127,128,255][(case//80)%4];y=[10,128,127,255][(case//320)%4]
        tx=x;ty=y;slot=2;holder=1;kind=0
        direction=[1,255,0,2,128][(case//5)%5]
        if mode==0:kind=13
        if mode==2:holder=slot
        if mode in (3,4,5,6):tx=(x+{3:3,4:4,5:-3,6:-4}[mode])&255
        if mode in (7,8):ty=(y+{7:5,8:6}[mode])&255
        if mode==9:x=127;tx=128
        if mode==10:y=128;ty=127
        if mode==11:y=246;ty=10;direction=255
        if mode>=12:
            x=rng.randrange(256);y=rng.randrange(256);tx=(x+rng.choice([-4,-3,0,3,4]))&255
            ty=rng.randrange(256)
        put(p,x);put(p+1,y);put(p+6,slot);put(p+0x12,kind)
        put(ds+0x830b,holder);put(ds+0x8319,0);put(ds+0x831b,0,2)
        put(ds+0x0668,12);put(ds+0x7920,direction);put(ds+0x7921,direction)
        put(ss+sp,0x300,2);put(ss+((sp+2)&65535),m.seg(0x791),2)
        for i,value in enumerate([off,seg,(ty<<8)|tx]):put(ss+((sp+4+i*2)&65535),value,2)
        for reg,value in [('ss',0x2000),('sp',sp),('ds',m.DS),('es',m.DS),('cs',m.seg(0x791)),('eip',0x44c1)]:
            m.set_reg(reg,value)
        end=m.lin('0791:0300')
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
                if failure == 'read-index:'+str(state['read_index']): raise ValueError('near-zone read refused')
            if kind == 'g' and failure == 'reg:'+str(at): raise ValueError('near-zone register refused')
        m.io_tap = io
        m.site_tap = m.listen_tap = Tap()
    if listener:
        def listen(at, n, value):
            state['write_index'] += 1
            pc = m.pc()
            log.append(('w', at, n, value, pc))
            state['writes'][pc] = state['writes'].get(pc, 0)+1
            if failure in ('write', 'write-index:'+str(state['write_index'])) or failure == 'write:'+str(pc):
                raise ValueError('near-zone write refused')
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
            if failure == site: raise ValueError('near-zone site refused')
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


class NearZoneTests(unittest.TestCase):
    def test_complete_native_body(self):
        p,_,_=exercise(Oracle,1)
        r,n,_=exercise(PortMachine,1)
        self.assertIsNone(p['error']);self.assertEqual(p,r)
        self.assertEqual(n.get('0791:44C1'),1)

    def test_paths_observers_and_suspension(self):
        for case in range(64):
            for tapped,listener in [(False,False),(True,False),(False,True),(True,True)]:
                for pause in [None,'0791:44C1','0791:2BE5','0791:4500']:
                    kw=dict(tapped=tapped,listener=listener,pause=pause)
                    p,_,_=exercise(Oracle,case,**kw);r,_,_=exercise(PortMachine,case,**kw)
                    self.assertIsNone(p['error'],case);self.assertEqual(p,r,(case,kw))
        for case in range(16):
            for kw in [dict(controlled=True),dict(mutations=True),dict(direct=True)]:
                p,_,_=exercise(Oracle,case,**kw);r,_,_=exercise(PortMachine,case,**kw)
                self.assertIsNone(p['error']);self.assertEqual(p,r,(case,kw))

    def test_variants_errors_and_closure(self):
        source=set()
        for case in range(16):
            p,_,ps=exercise(Oracle,case,profile=True);r,n,rs=exercise(PortMachine,case,profile=True)
            self.assertEqual(p,r);source.update(ps['owned']);self.assertFalse(rs['owned'])
            for variant in ['depth-plus-one','marking-no-copy','keeper-no-state']:
                p,_,_=exercise(Oracle,case,variant=variant);r,n,scope=exercise(PortMachine,case,variant=variant,profile=True)
                self.assertEqual(p,r);self.assertNotIn('0791:44C1',n);self.assertTrue(scope['owned'])
        self.assertEqual(source,set(INV['owned_code_objects']))
        for failure in ['write','0791:44C1','0791:2BE5','0791:4500','reg:ax','read-index:1']:
            p,_,_=exercise(Oracle,1,failure=failure);r,_,_=exercise(PortMachine,1,failure=failure)
            self.assertIsNotNone(p['error'],failure);self.assertEqual(p,r,failure)

    def test_body_output_return_controls(self):
        p,_,_=exercise(Oracle,1)
        self.assertIsNone(p['error'])
        for mutant in range(436,445):
            r,_,_=exercise(PortMachine,1,mutant=mutant)
            self.assertNotEqual(p,r,mutant)

if __name__=='__main__':unittest.main()
