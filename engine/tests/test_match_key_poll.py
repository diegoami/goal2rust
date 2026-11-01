"""T10 full caller proof with controlled external ABI/service boundaries."""
import hashlib,random,unittest
from original_match.port import Entry,load
from original_match.port.runtime import args
from original_match.port.engine import PortMachine as Oracle
from original_match.port.guest import PortFrame
from goal2rust.machine import PortMachine,BridgeRunner
ROOT='0791:9372'
TARGETS=('214B:0723','214B:1E8D','214B:08DD','23E4:19B2','0791:1A04','214B:1D6F','0791:0691','0791:ED8A','23E4:025D','16D6:0945','214B:1E5A','0791:92FC')
RETURNS=tuple('0791:'+x for x in ['93C2','93CE','93D3','93DC','93E3','9448','944B','945B','947D','9482','9497','94A2','94AC','94B9','94C5'])
SITES=(ROOT,)+TARGETS+RETURNS
ENTRIES={ad:e for reg,_ in load(['all']) for ad,e in reg.entries.items() if ad in (ROOT,)+TARGETS}
KEYS=(None,0x20,0xae,0xaf,0xac,0xb1,0x0d,0x1b,0x9f,0xa7,ord('r'),ord('R'),ord('x'))

def exercise(cls,case,*,tapped=True,listener=True,pause=None,failure=None,variant=None,mutant=0,direct=False,snapshot=None,mutations=False,clobber_return=False):
 rng=random.Random(case);m=cls(bytes(range(256))*(0x110000//256),0x823,mutant=mutant) if cls is PortMachine else cls(bytes(range(256))*(0x110000//256),0x823)
 mem=m.port_memory();log=[];calls={};visits=[];done=[];state=dict(loop_writes=0,mutations=0,return_mutations=0,saved_bp_mutations=0,copy_pointer_mutations=0);key=KEYS[case%len(KEYS)];ds=m.DS*16
 def put(a,v,n=1):m._memory[a:a+n]=(v&((1<<(8*n))-1)).to_bytes(n,'little')
 for ad,original in ENTRIES.items():
  if ad==ROOT:entry=original;v=variant
  else:
   def boundary(mem,v,ad=ad,original=original):
    actual=args(mem,original.pop//2);log.append(('call',ad,actual,hashlib.sha256(m._memory).hexdigest(),dict(m._registers)))
    if failure=='callee:'+ad:raise ValueError('key-poll boundary refused')
    if ad=='23E4:19B2':return original.fn(mem,None)
    value=(case*37+int(ad[-4:],16))&65535
    if ad=='214B:0723':value=(value&0xff00)|int(key is not None)
    elif ad=='214B:08DD':put(ds+0xa976,ord('x') if key is None else key);value=(value&0xff00)|(ord('x') if key is None else key)
    elif ad=='0791:92FC':mem.wds8(0x9a3e,case%2,'0791:9356')
    for reg,value2 in [('ax',value),('di',value^0xdead),('es',0x5000),('eflags',(case*0x1234567)&0xffffffff)]:mem.set_reg(reg,value2)
   entry=Entry(ad,original.ret,boundary,'controlled '+ad,original.long,return_stack_delta=original.return_stack_delta);v='T10-controlled-boundary'
  if cls is Oracle:
   def runner(machine,entry=entry,v=v):calls[entry.address]=calls.get(entry.address,0)+1;PortFrame(machine,mem,entry,v).start()
  else:runner=BridgeRunner(entry,v,mem,calls)
  m.port(ad,runner)
 if snapshot is None:
  off=[0,0xfff0,rng.randrange(65536)][case%3];seg=0x4000;toff=[0,0xfff0,rng.randrange(65536)][case%3];tseg=0x5000
  if case%7==0:tseg=seg;toff=(off+63-0xf2a)&65535
  put(ds+0xa923,off,2);put(ds+0xa925,seg,2);put(seg*16+((off+63)&65535),[0,1,4,5,6,127,255][case%7])
  put(ds+0x7c26,toff,2);put(ds+0x7c28,tseg,2);put(ds+0x882,rng.randrange(256));put(ds+0x883,rng.randrange(256))
  for a in [0x9a3e,0x7c38]:put(ds+a,(case//len(KEYS))%2)
  put(ds+0xa976,ord('x') if key is None else key);put(ds+0x7920,[0,1,127,128,255][case%5]);put(ds+0x7921,[255,128,127,1,0][case%5])
  for a in [0xa96a,0xa972]:put(ds+a,rng.randrange(65536),2);put(ds+a+2,0x6000,2)
  for reg in ['eax','ebx','ecx','edx','esi','edi','ebp','eflags']:m.set_reg(reg,rng.randrange(1<<32))
  sp=[0,2,8,16,0x100,0xfffa,0xfffe][case%7]
  for reg,value in [('ss',0x3000),('sp',sp),('cs',m.seg(0x791)),('eip',0x9372)]:m.set_reg(reg,value)
  put(0x30000+sp,0x200,2);end=m.lin('0791:0200')
 else:
  memory,regs,entry=snapshot;m._memory[:]=memory;m._registers.clear();m._registers.update(regs);sp,far=entry;assert not far
  at=(regs['ss']&65535)*16+sp;end=(regs['cs']&65535)*16+int.from_bytes(memory[at:at+2],'little')
 class Tap:
  def site_enter(self,*x,**kw):log.append(('se',x,kw))
  def site_leave(self,*x,**kw):log.append(('sl',x,kw))
  def listen_enter(self,*x):log.append(('le',x));return len(log)
  def listen_leave(self,x):log.append(('ll',x))
 if tapped:m.io_tap=lambda *x:log.append(('io',x));m.site_tap=m.listen_tap=Tap()
 if listener:
  def write(a,n,v):
   pc=m.pc();log.append(('w',a,n,v,pc))
   if pc==m.lin('0791:93B3'):
    state['loop_writes']+=1
    if mutations:
     current_off=int.from_bytes(m._memory[ds+0xa923:ds+0xa925],'little');current_seg=int.from_bytes(m._memory[ds+0xa925:ds+0xa927],'little')
     put(current_seg*16+((current_off+63)&65535),[255,0,5,1,6,4][state['loop_writes']-1]);m._registers['eax']^=0x1234;m._registers['eflags']^=0x400;state['mutations']+=1
   if failure=='write':raise ValueError('key-poll write refused')
  m.on_write(0,0x10ffff,write)
 for site in SITES:
  def handler(replay,site=site):
   visits.append((site,replay));log.append(('state',site,hashlib.sha256(m._memory).hexdigest(),dict(m._registers)))
   log.append(('waiting',site,[(f.entry.address,f.waiting.target,tuple(f.waiting.args),f.waiting.ret_to,f.waiting.far,f.waiting.caller_pops) for f in m.frames if f.waiting is not None]))
   if failure==site:raise ValueError('key-poll site refused')
   if clobber_return and site in ['0791:93C2','0791:93DC']:
    m.set_reg('ax',(0x1100|int(key is not None)) if site=='0791:93C2' else (0x2200|(ord('R') if key==ord('r') else (key or ord('x')))));state['return_mutations']+=1
   if mutations and site=='0791:93C2':
    ss=m.reg('ss')*16;bp=m.reg('bp');old=int.from_bytes(m._memory[ss+bp:ss+bp+2],'little');put(ss+bp,old^0x2468,2);state['saved_bp_mutations']+=1
   if mutations and site=='0791:9482':
    put(ds+0xa972,0xfff1,2);put(ds+0xa96a,0x1234,2);state['copy_pointer_mutations']+=1
   if pause==site and sum(s==site for s,_ in visits)==1:m.stop('pause')
  m.at(site,handler)
 error=suspended=None
 try:
  if direct:
   cb=lambda f:done.append((f.entry.address,f.value))
   if cls is Oracle:calls[ROOT]=1;PortFrame(m,mem,ENTRIES[ROOT],variant,cb).start()
   else:BridgeRunner(ENTRIES[ROOT],variant,mem,calls)(m,cb)
  reason=m.run(end,fresh=True)
  if reason=='pause':
   suspended=[(f.entry.address,f.ss,f.sp,f.bp,f.ret_lin,f.expect_sp,f.after_sp,None if f.waiting is None else (f.waiting.target,f.waiting.args,f.waiting.ret_to)) for f in m.frames];m.run(end)
 except Exception as exc:error=(type(exc).__name__,str(exc))
 m.io_tap=None
 return dict(memory=hashlib.sha256(m._memory).hexdigest(),regs=dict(m._registers),log=log,calls=calls,visits=visits,done=done,error=error,suspended=suspended,state=state,entries=list(mem._entries),frames=[f.describe() for f in m.frames],no_replay_at=m.no_replay_at,running=m.running),getattr(getattr(m,'_core',None),'native_calls',{})

class MatchKeyPollTests(unittest.TestCase):
 def test_native_caller(self):
  p,_=exercise(Oracle,0);r,n=exercise(PortMachine,0);self.assertEqual(p,r);self.assertEqual(n.get(ROOT),1)
 def test_all_branches_and_observers(self):
  for case in range(100):
   for tapped in [False,True]:
    opts=dict(tapped=tapped,pause=SITES[case%len(SITES)],mutations=case%3==0,clobber_return=case%5==0,direct=case%7==0)
    with self.subTest(case=case,**opts):self.assertEqual(exercise(Oracle,case,**opts)[0],exercise(PortMachine,case,**opts)[0])
 def test_errors_and_variant(self):
  for failure in ['write',ROOT,*TARGETS,*RETURNS]+['callee:'+a for a in TARGETS]:
   for case in [1,4,8,9,10]:
    with self.subTest(case=case,failure=failure):self.assertEqual(exercise(Oracle,case,failure=failure)[0],exercise(PortMachine,case,failure=failure)[0])
  p,_=exercise(Oracle,3,variant='speed-right-increments');r,n=exercise(PortMachine,3,variant='speed-right-increments');self.assertEqual(p,r);self.assertNotIn(ROOT,n)
if __name__=='__main__':unittest.main()
