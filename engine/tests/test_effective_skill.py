"""T06 effective-skill tree, authored data and observable continuations."""
import hashlib
import random
import unittest
from original_match.port import load
from original_match.port.engine import PortMachine as Oracle
from original_match.port.guest import PortFrame
from goal2rust.machine import PortMachine,BridgeRunner
ROOT,LEAF,RETURN='0791:278A','1771:3A06','0791:27EB'
ENTRIES={ad:e for reg,_ in load(['all']) for ad,e in reg.entries.items() if ad in (ROOT,LEAF)}
SITES=(ROOT,LEAF,RETURN)


def exercise(cls,case,*,root=ROOT,tapped=True,listener=True,pause=None,failure=None,
             root_variant=None,callee_variant=None,mutant=0,body=False,direct=False,
             snapshot=None,mutate_saved=False,clobber_sent=False):
    rng=random.Random(case)
    m=cls(bytes(range(256))*(0x110000//256),0x823,mutant=mutant) if cls is PortMachine else cls(bytes(range(256))*(0x110000//256),0x823)
    log,calls,done,visits=[],{},[],[];mem=m.port_memory()
    for ad,entry in ENTRIES.items():
        v=root_variant if ad==ROOT else callee_variant
        if cls is Oracle:
            def runner(machine,entry=entry,v=v):
                calls[entry.address]=calls.get(entry.address,0)+1;PortFrame(machine,mem,entry,v).start()
        else:runner=BridgeRunner(entry,v,mem,calls)
        m.port(ad,runner)
    if snapshot is None:
        def write(seg,off,v,n=1):
            at=seg*16+(off&65535);m._memory[at:at+n]=v.to_bytes(n,'little')
        off=[0,0xfff0,0xffff,rng.randrange(65536)][case%4];seg=0x4000
        player=[0,1,0xffff,0xccc,rng.randrange(65536)][case%5]
        element=[0,1,2,11,12,13,0xffff,rng.randrange(65536)][case%8]
        poff=[0,0xfff8,rng.randrange(65536)][case%3];pseg=0x5000;p=(poff+player*20)&65535
        write(m.DS,0xa91b,poff,2);write(m.DS,0xa91d,pseg,2)
        for k,v in [(4,[0,1,127,255][case%4]),(5,rng.randrange(256)),(7,rng.randrange(256)),
                    (12,[0,31,32,127,128,255][case%6]),(14,[0,1,127,128,255][case%5])]:write(pseg,p+k,v)
        write(seg,off+13,player,2);write(seg,off+19,case%3);write(seg,off+17,rng.randrange(256));write(seg,off+6,[0,11,12,255][case%4])
        write(m.DS,0x769+element,case%2);write(m.DS,0x8327,[0,3,4,255][case%4]);write(m.DS,0x80fc,case%3)
        at=m.seg(0x791)*16+0x276a;m._memory[at:at+32]=rng.randbytes(32)
        for reg in ['eax','ebx','ecx','edx','esi','edi','ebp','eflags']:m.set_reg(reg,rng.randrange(1<<32))
        sp=[0,2,8,16,0x100,0xfffa,0xfffe][case%7]
        end=m.far_call(root,[element,seg,off] if root==ROOT else [player,element],'000E:0300',0x3000,sp)
    else:
        memory,regs,entry=snapshot;m._memory[:]=memory;m._registers.clear();m._registers.update(regs)
        sp,far=entry;assert far;ss=regs['ss']&65535
        ip=int.from_bytes(memory[ss*16+sp:ss*16+sp+2],'little');cs_off=(sp+2)&65535
        cs=int.from_bytes(memory[ss*16+cs_off:ss*16+cs_off+2],'little');end=cs*16+ip
    flags=dict(ax_captured=False,clobbered=False,saved_mutated=False)
    class Tap:
        def site_enter(self,*x,**kw):log.append(('se',x,kw))
        def site_leave(self,*x,**kw):log.append(('sl',x,kw))
        def listen_enter(self,*x):log.append(('le',x));return len(log)
        def listen_leave(self,x):log.append(('ll',x))
    if tapped:
        def io(kind,x,v):
            log.append(('io',kind,x,bytes(v) if isinstance(v,(bytes,bytearray)) else v))
            if clobber_sent and root==ROOT and (m._registers['eip']&65535)==0x27eb:
                if kind=='g' and x=='ax':flags['ax_captured']=True
                elif kind=='s' and x=='sp' and flags['ax_captured'] and not flags['clobbered']:
                    m._registers['eax']=(m._registers['eax']&0xffff0000)|0xabcd;flags['clobbered']=True
        m.io_tap=io;m.site_tap=m.listen_tap=Tap()
    if listener:
        def on_write(a,n,v):
            log.append(('w',a,n,v,m.pc()))
            if failure=='write':raise ValueError('skill write refused')
        m.on_write(0,0x10ffff,on_write)
    for site in SITES:
        def handler(replay,site=site):
            visits.append((site,replay))
            if mutate_saved and root==ROOT and site==RETURN:
                ss=(m._registers['ss']&65535)*16
                for k,v in [(4,0xfff1),(6,0x1234),(8,0xffff)]:
                    a=ss+((sp+k)&65535);m._memory[a:a+2]=v.to_bytes(2,'little')
                a=ss+((m._registers['ebp']-4)&65535);m._memory[a:a+2]=b'\x67\x45';flags['saved_mutated']=True
            log.append(('state',site,hashlib.sha256(m._memory).hexdigest(),dict(m._registers)))
            if failure==site:raise ValueError('skill site refused')
            if pause==site and sum(s==site for s,_ in visits)==1:m.stop('pause')
        m.at(site,handler)
    error,suspended,value=None,None,None
    try:
        if body:
            mem._entries.append((sp,True))
            try:value=m._core.routine(m,mem,root) if cls is PortMachine else ENTRIES[root].fn(mem,callee_variant)
            finally:mem._entries.pop()
            reason=None
        else:
            if direct:
                callback=lambda f:done.append((f.entry.address,f.value))
                if cls is Oracle:calls[root]=1;PortFrame(m,mem,ENTRIES[root],root_variant,callback).start()
                else:BridgeRunner(ENTRIES[root],root_variant,mem,calls)(m,callback)
            reason=m.run(end,fresh=True)
        if reason=='pause':
            suspended=[(f.entry.address,f.ss,f.sp,f.bp,f.ret_lin,f.expect_sp,f.after_sp,
                        None if f.waiting is None else (f.waiting.target,f.waiting.args,f.waiting.ret_to)) for f in m.frames]
            m.run(end)
    except Exception as exc:error=(type(exc).__name__,str(exc))
    m.io_tap=None
    state=dict(memory=hashlib.sha256(m._memory).hexdigest(),regs=dict(m._registers),log=log,calls=calls,
               visits=visits,done=done,value=value,error=error,suspended=suspended,entries=list(mem._entries),
               frames=[f.describe() for f in m.frames],flags=flags,no_replay_at=m.no_replay_at,running=m.running)
    return state,getattr(getattr(m,'_core',None),'native_calls',{})


class EffectiveSkillTests(unittest.TestCase):
    def test_full_tree_and_retained_state(self):
        p,_=exercise(Oracle,1);r,n=exercise(PortMachine,1)
        self.assertEqual(p,r);self.assertEqual(n.get(ROOT),1)
        for case in range(100):
            for root in ENTRIES:
                for tapped in (False,True):
                    opts=dict(root=root,tapped=tapped,pause=SITES[case%3],mutate_saved=case%5==0,clobber_sent=case%7==0)
                    with self.subTest(case=case,**opts):
                        p,_=exercise(Oracle,case,**opts);r,n=exercise(PortMachine,case,**opts)
                        self.assertEqual(p,r);self.assertEqual(n.get(root),1)

    def test_direct_leaf_body_and_completion(self):
        for case in range(50):
            for opts in [dict(root=LEAF,body=True),dict(direct=True),dict(clobber_sent=True,mutate_saved=True)]:
                with self.subTest(case=case,**opts):
                    p,_=exercise(Oracle,case,**opts);r,_=exercise(PortMachine,case,**opts);self.assertEqual(p,r)
                    if opts.get('clobber_sent'):self.assertTrue(r['flags']['clobbered']);self.assertTrue(r['flags']['saved_mutated'])

    def test_errors_and_variants(self):
        opts=[dict(failure=s) for s in ('write',)+SITES]+[dict(root_variant=v) for v in ['skill-no-halving','keeper-gate-off']]+[dict(callee_variant='skill-divisor-31')]
        for opt in opts:
            with self.subTest(**opt):
                p,_=exercise(Oracle,1,**opt);r,n=exercise(PortMachine,1,**opt);self.assertEqual(p,r)
                if opt.get('root_variant'):self.assertNotIn(ROOT,n)
                if opt.get('callee_variant'):self.assertNotIn(LEAF,n)

if __name__=='__main__':unittest.main()
