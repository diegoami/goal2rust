"""T05 actual near caller and complete native closure; authored state only."""
import hashlib
import random
import unittest

from original_match.port import load
from original_match.port.engine import PortMachine as Oracle
from original_match.port.guest import PortFrame
from goal2rust.machine import PortMachine, BridgeRunner

ROOT = '0791:2FB1'
ENTRIES = {ad: entry for registry, _ in load(['all']) for ad, entry in registry.entries.items()
           if ad in (ROOT, '0791:2956', '1771:3216', '0791:2BE5')}
SITES = (ROOT, '0791:2956', '1771:3216', '0791:2968', '0791:3013',
         '0791:2BE5', '0791:3090', '0791:30A3')


def exercise(cls, case, *, tapped=True, listener=True, pause=None, failure=None,
             root_variant=None, callee_variant=None, mutant=0, direct=False,
             snapshot=None, boundary_snapshots=True):
    rng = random.Random(case)
    m = cls(bytes(range(256)) * (0x110000 // 256), 0x823, mutant=mutant) if cls is PortMachine else cls(bytes(range(256)) * (0x110000 // 256), 0x823)
    log, calls, done, visits = [], {}, [], []
    mem = m.port_memory()
    for ad, entry in ENTRIES.items():
        variant = root_variant if ad == ROOT else callee_variant if ad == '1771:3216' else None
        if cls is Oracle:
            def runner(machine, entry=entry, variant=variant):
                calls[entry.address] = calls.get(entry.address, 0) + 1
                PortFrame(machine, mem, entry, variant).start()
        else: runner = BridgeRunner(entry, variant, mem, calls)
        m.port(ad, runner)
    if snapshot is None:
        ds = m.DS * 16
        def put(off, value, size=1): m._memory[ds + off:ds + off + size] = value.to_bytes(size, 'little')
        put(0xa91b, 0x50000000 | [0, 0xfff0, rng.randrange(65536)][case % 3], 4)
        pointer = int.from_bytes(m._memory[ds+0xa91b:ds+0xa91f], 'little')
        put(0x668, [0, 240, rng.randrange(256)][case % 3])
        put(0x669, [11, 255, rng.randrange(256)][case % 3])
        put(0x830b, 255 if case == 0 else rng.randrange(24))
        put(0x82f6, [0, 127, 128, 255, rng.randrange(256)][case % 5])
        put(0x82f7, [0, 128, 127, 255, rng.randrange(256)][case % 5])
        put(0x80fb, case % 2)
        for i in range(267):
            off = (0x80e8 + i * 22) & 65535
            player = rng.choice([i, rng.randrange(65536)])
            record = bytearray(rng.randbytes(22))
            record[0] = rng.choice([0, 127, 128, 255, rng.randrange(256)])
            record[1] = rng.choice([0, 127, 128, 255, rng.randrange(256)])
            record[6] = i % 23
            record[13:15] = player.to_bytes(2, 'little')
            record[18] = 0 if case == 0 else rng.choice([0, 13, rng.randrange(256)])
            m._memory[ds + off:ds + off + 22] = record
            p = (pointer & 65535) + player * 20
            m._memory[0x50000 + ((p+14)&65535)] = 1 if case == 0 else 0 if case == 1 else rng.choice([0,1,127,128,255])
            m._memory[0x50000 + ((p+16)&65535)] = 0 if case == 0 else rng.choice([0,4,16,32,128,255])
        for reg in ('eax','ebx','ecx','edx','esi','edi','ebp','eflags'):
            m.set_reg(reg, rng.randrange(1 << 32))
        sp = [0,2,8,16,0x100,0xfffa,0xfffe][case % 7]
        end = m.far_call(ROOT, [], '0791:0200', 0x3000, sp)
    else:
        memory, regs, entry = snapshot
        m._memory[:] = memory
        m._registers.clear(); m._registers.update(regs)
        sp, far = entry
        assert not far
        ss = regs['ss'] & 65535
        ip = int.from_bytes(memory[ss*16+sp:ss*16+sp+2], 'little')
        end = (regs['cs'] & 65535) * 16 + ip
    class Tap:
        def site_enter(self,*x,**kw): log.append(('se',x,kw))
        def site_leave(self,*x,**kw): log.append(('sl',x,kw))
        def listen_enter(self,*x):
            log.append(('le',x)); return len(log)
        def listen_leave(self,x): log.append(('ll',x))
    if tapped:
        m.io_tap = lambda *x: log.append(('io',x))
        m.site_tap = m.listen_tap = Tap()
    if listener:
        def write(a,n,v):
            log.append(('w',a,n,v,m.pc()))
            if failure == 'write': raise ValueError('nearest write refused')
        m.on_write(0,0x10ffff,write)
    for site in SITES:
        def handler(replay,site=site):
            visits.append((site,replay))
            if boundary_snapshots:
                log.append(('state',site,hashlib.sha256(m._memory).hexdigest(),dict(m._registers)))
            if failure == site: raise ValueError('nearest site refused')
            if pause == site and sum(x[0]==site for x in visits)==1: m.stop('pause')
        m.at(site,handler)
    error, suspended = None, None
    try:
        if direct:
            callback = lambda f: done.append((f.entry.address,f.value))
            if cls is Oracle:
                calls[ROOT] = 1; PortFrame(m,mem,ENTRIES[ROOT],root_variant,callback).start()
            else: BridgeRunner(ENTRIES[ROOT],root_variant,mem,calls)(m,callback)
        reason=m.run(end,fresh=True)
        if reason=='pause':
            suspended=[(f.entry.address,f.ss,f.sp,f.bp,f.ret_lin,f.expect_sp,f.after_sp,
                        None if f.waiting is None else (f.waiting.target,f.waiting.args,f.waiting.ret_to)) for f in m.frames]
            m.run(end)
    except Exception as exc: error=(type(exc).__name__,str(exc))
    m.io_tap=None
    state=dict(memory=hashlib.sha256(m._memory).hexdigest(),regs=dict(m._registers),
               log=log,calls=calls,done=done,visits=visits,error=error,suspended=suspended,
               entries=list(mem._entries),frames=[f.describe() for f in m.frames],
               no_replay_at=m.no_replay_at,running=m.running)
    return state,getattr(getattr(m,'_core',None),'native_calls',{})


class NearestBallTests(unittest.TestCase):
    def test_full_frames_and_continuations(self):
        # This assertion fails before the translation; equality already holds through the bridge.
        p,_=exercise(Oracle,0);r,native=exercise(PortMachine,0)
        self.assertEqual(p,r);self.assertEqual(native.get(ROOT),1)
        for case in range(40):
            for tapped in (False,True):
                opts=dict(tapped=tapped,pause=SITES[case%len(SITES)])
                with self.subTest(case=case,**opts):
                    p,_=exercise(Oracle,case,**opts);r,native=exercise(PortMachine,case,**opts)
                    self.assertEqual(p,r);self.assertEqual(native.get(ROOT),1)
                    self.assertEqual(r['calls']['0791:2956'],20)

    def test_errors_variants_and_done(self):
        for opts in [dict(failure=s) for s in ('write',)+SITES]+[
            dict(root_variant='launch-reverse-x'),dict(callee_variant='unavailable-bit-6'),dict(direct=True)]:
            with self.subTest(**opts):
                p,_=exercise(Oracle,0,**opts);r,native=exercise(PortMachine,0,**opts)
                self.assertEqual(p,r)
                if opts.get('root_variant'): self.assertNotIn(ROOT,native)


if __name__=='__main__':unittest.main()
