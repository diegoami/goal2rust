"""T15 immediate sprite caller and controlled registered callee ABI boundaries."""
import hashlib,random,unittest
from original_match.port import Entry,load
from original_match.port.runtime import args
from original_match.port.engine import PortMachine as Oracle
from original_match.port.guest import PortFrame
from goal2rust.machine import PortMachine,BridgeRunner
ROOT='0791:8537';TARGETS=('0791:2C29','0791:045D','0791:2EB8','0791:2BE5','0791:8F10')
RETURNS=('0791:8610','0791:862D','0791:8640','0791:8660','0791:8699');SITES=(ROOT,)+TARGETS+RETURNS
WRITE_SITES=tuple('0791:'+x for x in ['8537','859D','85AB','8602','861D','8660','866A','8674','867F','868B'])
ENTRIES={a:e for reg,_ in load(['all']) for a,e in reg.entries.items() if a in (ROOT,)+TARGETS};assert len(ENTRIES)==6

def exercise(cls,case,*,tapped=True,listener=True,pause=None,failure=None,variant=None,mutant=0,direct=False,snapshot=None,mutations=False,clobber_sent=False):
 rng=random.Random(case);m=cls(bytes(range(256))*(0x110000//256),0x823,mutant=mutant) if cls is PortMachine else cls(bytes(range(256))*(0x110000//256),0x823)
 mem=m.port_memory();ds=m.DS*16;log=[];calls={};visits=[];done=[];mode=case%8;state=dict(writes={},args_mutations=0,bp_mutations=0,sentinel_mutations=0,pointer_mutations=0,record_mutations=0,clamp_mutations=0,ds_mutations=0,sent_clobbers=0,armed=False)
 def put(a,v,n=1):m._memory[a:a+n]=(v&((1<<(8*n))-1)).to_bytes(n,'little')
 for ad,original in ENTRIES.items():
  if ad==ROOT:e=original;v=variant
  else:
   def boundary(mem,v,ad=ad,original=original):
    packet=args(mem,original.pop//2);log.append(('call',ad,packet,m.frames[-1].waiting.ret_to))
    if failure=='callee:'+ad:raise ValueError('sprite callee refused')
    value=0xa700|int(mode!=0)
    if ad=='0791:045D':value=0xb800|int(mode in (2,3))
    if ad=='0791:2EB8':value=0xc900|int(mode==3)
    if ad=='0791:2BE5':value=0xda00|([1,255,0,2][case%4])
    if ad=='0791:8F10':value=0xeb00|(case&255)
    for reg,x in [('ax',value),('dx',value^0x1234),('di',value^0xdead),('es',0x5000),('eflags',(case*0x1234567)&0xffffffff)]:mem.set_reg(reg,x)
   e=Entry(ad,original.ret,boundary,'controlled '+ad,original.long,original.stub,original.return_stack_delta);v='T15-controlled-boundary'
  if cls is Oracle:
   def runner(machine,e=e,v=v):calls[e.address]=calls.get(e.address,0)+1;PortFrame(machine,mem,e,v).start()
  else:runner=BridgeRunner(e,v,mem,calls)
  m.port(ad,runner)
 if snapshot is None:
  seg=0x4000;off=[0,0xfff0,0xffff,rng.randrange(65536)][case%4];rec=seg*16+off
  pos=[0x2620,0x2620,0xda80,0x8001,0x017f,0x7f00,0,0x640][case%8]
  old=[pos,pos^0x101,0x640,0xffff][(case//8)%4]
  sentinel=[0x640,old,pos,0xbeef][(case//32)%4]
  for k,v,n in [(0,pos,2),(2,old,2),(4,[1,0x1201,2,0xffff][case%4],2),(6,3,1),(15,[0,1,2,3,4,5,255][(case//4)%7],1)]:put(rec+k,v,n)
  put(ds+0x640,sentinel,2);put(ds+0x830b,3 if case%3 else 4);put(ds+0x82f6,0xbeef,2)
  for p,ps in [(0x7c16,0x5000),(0x7c1e,0x6000)]:put(ds+p,[0,0xfffe,0xffff,rng.randrange(65536)][case%4],2);put(ds+p+2,ps,2)
  for reg in ['eax','ebx','ecx','edx','esi','edi','ebp','eflags']:m.set_reg(reg,rng.randrange(1<<32))
  sp=[0,2,8,16,0x100,0xfffa,0xfffe][case%7];end=m.far_call(ROOT,[seg,off],'000E:0300',0x3000,sp)
  at=0x30000+((sp+4)&65535);put(at,off,2);put(at+2,seg,2)
 else:
  memory,regs,ent=snapshot;m._memory[:]=memory;m._registers.clear();m._registers.update(regs);sp,far=ent;assert far
  ss=(regs['ss']&65535)*16;ip=int.from_bytes(memory[ss+sp:ss+sp+2],'little');cs=int.from_bytes(memory[ss+((sp+2)&65535):ss+((sp+2)&65535)+2],'little');end=cs*16+ip
  at=ss+((sp+4)&65535);off=int.from_bytes(memory[at:at+2],'little');seg=int.from_bytes(memory[at+2:at+4],'little');rec=seg*16+off
 class Tap:
  def site_enter(self,*x,**kw):log.append(('se',x,kw))
  def site_leave(self,*x,**kw):log.append(('sl',x,kw))
  def listen_enter(self,*x):log.append(('le',x));return len(log)
  def listen_leave(self,x):log.append(('ll',x))
 if tapped:
  def io(kind,x,v):
   log.append(('io',kind,x,bytes(v) if isinstance(v,(bytes,bytearray)) else v));ip=m._registers['eip']&65535
   if clobber_sent and ip in [0x8610,0x862d,0x8640,0x8660]:
    if kind=='g' and x=='ax':state['armed']=True
    elif kind=='s' and x=='sp' and state['armed']:
     m._registers['eax']=(m._registers['eax']&0xffff0000)|0xee00;state['sent_clobbers']+=1;state['armed']=False
  m.io_tap=io;m.site_tap=m.listen_tap=Tap()
 if listener:
  def listen(a,n,v):
   pc=m.pc();log.append(('w',a,n,v,pc))
   for site in WRITE_SITES:
    if pc==m.lin(site):state['writes'][site]=state['writes'].get(site,0)+1
   if failure=='write' or any(failure=='write:'+site and pc==m.lin(site) for site in WRITE_SITES):raise ValueError('sprite write refused')
   if mutations:
    if pc==m.lin('0791:85AB'):
     put(ds+0x640,0,2);state['sentinel_mutations']+=1
     put(rec,0x267f if case%2 else 0xda80,2);put(rec+4,1,2);state['record_mutations']+=1
     for p,ps in [(0x7c16,0x5010),(0x7c1e,0x6010)]:put(ds+p,0xfff3,2);put(ds+p+2,ps,2)
     state['pointer_mutations']+=1
    if pc==m.lin('0791:8660'):
     put(ds+0x82f7,0xda);state['clamp_mutations']+=1
  m.on_write(0,0x10ffff,listen)
 for site in SITES:
  def handler(replay,site=site):
   visits.append((site,replay));log.append(('state',site,hashlib.sha256(m._memory).hexdigest(),dict(m._registers)))
   log.append(('waiting',site,[(f.entry.address,f.waiting.target,tuple(f.waiting.args),f.waiting.ret_to,f.waiting.far,f.waiting.caller_pops) for f in m.frames if f.waiting is not None]))
   if failure==site:raise ValueError('sprite site refused')
   if mutations and site=='0791:8610':
    m._registers['ds']=0x7777;state['ds_mutations']+=1
   if mutations and site in RETURNS:
    ss=m.reg('ss')*16;at=ss+((sp+4)&65535);put(at,0x100,2);put(at+2,0x7000,2);state['args_mutations']+=1
    m._registers['ebp']=(m._registers['ebp']&0xffff0000)|0xbeef;state['bp_mutations']+=1
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

class PlayerSpriteTests(unittest.TestCase):
 def test_native_caller(self):
  p,_=exercise(Oracle,1);r,n=exercise(PortMachine,1);self.assertIsNone(p['error']);self.assertEqual(p,r);self.assertEqual(n.get(ROOT),1)
 def test_positive_paths_and_mutations(self):
  visited=set();writes=set();targets=set()
  for case in range(180):
   for tapped in [False,True]:
    opts=dict(tapped=tapped,pause=SITES[case%len(SITES)],direct=case%3==0,mutations=case%7==0,clobber_sent=case%5==0)
    with self.subTest(case=case,**opts):
     p,_=exercise(Oracle,case,**opts);r,_=exercise(PortMachine,case,**opts);self.assertIsNone(p['error']);self.assertEqual(p,r);visited.update(s for s,_ in p['visits']);writes.update(p['state']['writes']);targets.update(p['calls'])
  self.assertTrue(set(RETURNS)<=visited);self.assertTrue(set(WRITE_SITES)<=writes,(set(WRITE_SITES)-writes));self.assertTrue(set(TARGETS)<=targets)
 def test_errors_and_variants(self):
  for failure in ['write',*SITES]+['callee:'+ad for ad in TARGETS]:
   for case in [1,2,3,4,7,11,19]:
    with self.subTest(case=case,failure=failure):self.assertEqual(exercise(Oracle,case,failure=failure)[0],exercise(PortMachine,case,failure=failure)[0])
  for variant in ['no-draw','nondefault-identity']:
   p,_=exercise(Oracle,3,variant=variant);r,n=exercise(PortMachine,3,variant=variant);self.assertEqual(p,r);self.assertNotIn(ROOT,n)
if __name__=='__main__':unittest.main()
