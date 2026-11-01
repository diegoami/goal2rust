"""T11 caller plus actual registered membership/travel/long-multiply delegation."""
import hashlib,random,unittest
from original_match.port import Entry,load
from original_match.port.runtime import args
from original_match.port.engine import PortMachine as Oracle
from original_match.port.guest import PortFrame
from goal2rust.machine import PortMachine,BridgeRunner
ROOT='0791:8F10';MEMBER='23E4:08DF';TRAVEL='0791:835F';MUL='23E4:0279'
TARGETS=(MEMBER,TRAVEL,MUL);RETURNS=('0791:8F66','0791:8FD4');SITES=(ROOT,)+TARGETS+RETURNS+('0791:8396',)
WRITE_SITES=('0791:8FAF','0791:8FBD','0791:8FE9','0791:906E')
ENTRIES={ad:e for reg,_ in load(['all']) for ad,e in reg.entries.items() if ad in (ROOT,)+TARGETS}
assert len(ENTRIES)==4

def exercise(cls,case,*,tapped=True,listener=True,pause=None,failure=None,variant=None,mutant=0,direct=False,snapshot=None,mutations=False,return_mutations=False):
 rng=random.Random(case);m=cls(bytes(range(256))*(0x110000//256),0x823,mutant=mutant) if cls is PortMachine else cls(bytes(range(256))*(0x110000//256),0x823)
 mem=m.port_memory();log=[];calls={};visits=[];done=[];state=dict(writes={},arg_mutations=0,pointer_mutations=0,zf_mutations=0,ax_mutations=0,saved_bp_mutations=0);ds=m.DS*16
 def put(a,v,n=1):m._memory[a:a+n]=(v&((1<<(8*n))-1)).to_bytes(n,'little')
 for ad,original in ENTRIES.items():
  if ad==ROOT:entry=original;v=variant
  else:
   def observed(mem,v,ad=ad,original=original):
    packet=args(mem,original.pop//2);log.append(('call',ad,packet,hashlib.sha256(m._memory).hexdigest(),dict(m._registers)))
    if failure=='callee:'+ad:raise ValueError('draw-state callee refused')
    return original.fn(mem,v)
   entry=Entry(ad,original.ret,observed,original.name,original.long,original.stub,original.return_stack_delta);v=None
  if cls is Oracle:
   def runner(machine,e=entry,v=v):calls[e.address]=calls.get(e.address,0)+1;PortFrame(machine,mem,e,v).start()
  else:runner=BridgeRunner(entry,v,mem,calls)
  m.port(ad,runner)
 if snapshot is None:
  seg=0x4000;off=[0,0xfff0,0xffff,rng.randrange(65536)][case%4]
  def rec(k,v,n=1):put(seg*16+((off+k)&65535),v,n)
  current=([0,1,127,128,255][case%5],[255,128,127,1,0][case%5]);old=current if case%4==0 else ([1,255,128,127,0][case%5],[0,1,127,128,255][case%5])
  rec(0,current[0]);rec(1,current[1]);rec(2,old[0]);rec(3,old[1]);rec(4,0x1234,2);rec(0xd,int(case%3!=0))
  for k,v in [(6,[0,1,65535,32768,32767,7][case%6]),(8,[7,32767,32768,65535,1,0][case%6]),(10,[0,1,2,3,65535][case%5])]:rec(k,v,2)
  sentinel=[65535,0,old[0]|old[1]<<8,current[0]|current[1]<<8][case%4];put(ds+0x640,sentinel,2)
  oldoff=[0,0xfff0,0xf800,rng.randrange(65536)][case%4];newoff=[0x400,0xfff0,0,rng.randrange(65536)][case%4];oldseg,newseg=0x5000,0x6000
  if case%7==0:newseg=oldseg;newoff=oldoff
  if case%11==0:
   sx=lambda x:x if x<128 else x-256
   delta=(sx(old[0])*160+sx(old[1])*2)&65535;oldseg=seg;oldoff=(off-0x90e-delta)&65535
  for p,o,s in [(0x7c16,oldoff,oldseg),(0x7c1e,newoff,newseg)]:put(ds+p,o,2);put(ds+p+2,s,2)
  put(ds+0x880,0x2a);put(ds+0x881,0x2b)
  at=m.seg(0x791)*16+0x8ef0;m._memory[at:at+32]=bytes([255 if case%2==0 else 0])*32
  for reg in ['eax','ebx','ecx','edx','esi','edi','ebp','eflags']:m.set_reg(reg,rng.randrange(1<<32))
  sp=[0,2,8,16,0x100,0xfffa,0xfffe][case%7];end=m.far_call(ROOT,[seg,off],'000E:0300',0x3000,sp)
 else:
  memory,regs,entry=snapshot;m._memory[:]=memory;m._registers.clear();m._registers.update(regs);sp,far=entry;assert far
  ss=(regs['ss']&65535)*16;ip=int.from_bytes(memory[ss+sp:ss+sp+2],'little');cs=int.from_bytes(memory[ss+((sp+2)&65535):ss+((sp+2)&65535)+2],'little');end=cs*16+ip
  off=int.from_bytes(memory[ss+((sp+4)&65535):ss+((sp+4)&65535)+2],'little');seg=int.from_bytes(memory[ss+((sp+6)&65535):ss+((sp+6)&65535)+2],'little')
 class Tap:
  def site_enter(self,*x,**kw):log.append(('se',x,kw))
  def site_leave(self,*x,**kw):log.append(('sl',x,kw))
  def listen_enter(self,*x):log.append(('le',x));return len(log)
  def listen_leave(self,x):log.append(('ll',x))
 if tapped:m.io_tap=lambda *x:log.append(('io',x));m.site_tap=m.listen_tap=Tap()
 if listener:
  def write(a,n,v):
   pc=m.pc();log.append(('w',a,n,v,pc))
   for label in WRITE_SITES:
    if pc==m.lin(label):state['writes'][label]=state['writes'].get(label,0)+1
   if mutations and pc==m.lin('0791:8FBD'):
    for p,s in [(0x7c16,0x5010),(0x7c1e,0x6010)]:put(ds+p,0xfff3,2);put(ds+p+2,s,2)
    state['pointer_mutations']+=1;m._registers['eax']^=0x7777
   if mutations and pc==m.lin('0791:8FE9'):put(seg*16+off,[0,1,127,128,255][case%5]);m._registers['ebx']^=0x3456
   if failure=='write':raise ValueError('draw-state write refused')
  m.on_write(0,0x10ffff,write)
 for site in SITES:
  def handler(replay,site=site):
   visits.append((site,replay));log.append(('state',site,hashlib.sha256(m._memory).hexdigest(),dict(m._registers)))
   log.append(('waiting',site,[(f.entry.address,f.waiting.target,tuple(f.waiting.args),f.waiting.ret_to,f.waiting.far,f.waiting.caller_pops) for f in m.frames if f.waiting is not None]))
   if failure==site:raise ValueError('draw-state site refused')
   if mutations and site in RETURNS:
    ss=m.reg('ss')*16;put(ss+((sp+4)&65535),0x100,2);put(ss+((sp+6)&65535),0x7000,2);state['arg_mutations']+=1
    bp=m.reg('bp');saved=int.from_bytes(m._memory[ss+bp:ss+bp+2],'little');put(ss+bp,saved^0x2468,2);state['saved_bp_mutations']+=1
   if return_mutations and site==RETURNS[0]:m.set_reg('eflags',m.reg('eflags')^0x40);state['zf_mutations']+=1
   if return_mutations and site==RETURNS[1]:m.set_reg('ax',[0,2,3,65535][case%4]);state['ax_mutations']+=1
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

class BallDrawStateTests(unittest.TestCase):
 def test_native_caller(self):
  p,_=exercise(Oracle,1);r,n=exercise(PortMachine,1);self.assertIsNone(p['error']);self.assertEqual(p,r);self.assertEqual(n.get(ROOT),1)
 def test_positive_paths_and_mutations(self):
  visits=set();writes=set();calls=set()
  for case in range(100):
   for tapped in [False,True]:
    opts=dict(tapped=tapped,pause=SITES[case%len(SITES)],direct=case%7==0,mutations=case%3==0,return_mutations=case%5==0)
    with self.subTest(case=case,**opts):
     p,_=exercise(Oracle,case,**opts);r,_=exercise(PortMachine,case,**opts);self.assertIsNone(p['error']);self.assertEqual(p,r);visits.update(s for s,_ in p['visits']);writes.update(p['state']['writes']);calls.update(p['calls'])
  self.assertTrue(set(RETURNS)<=visits);self.assertTrue(set(WRITE_SITES)<=writes);self.assertTrue(set(TARGETS)<=calls)
 def test_errors_and_variants(self):
  for failure in ['write',*SITES]+['callee:'+ad for ad in TARGETS]:
   for case in [1,3,4,7,8]:
    with self.subTest(case=case,failure=failure):self.assertEqual(exercise(Oracle,case,failure=failure)[0],exercise(PortMachine,case,failure=failure)[0])
  for variant in ['omit-0791-8f10','nondefault-identity']:
   p,_=exercise(Oracle,3,variant=variant);r,n=exercise(PortMachine,3,variant=variant);self.assertEqual(p,r);self.assertNotIn(ROOT,n)
if __name__=='__main__':unittest.main()
