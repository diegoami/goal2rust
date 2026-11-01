"""T16 complete plain-function run step: inline moves/random draws, no guest calls."""
import hashlib,random,unittest
from original_match.port import load
from original_match.port.engine import PortMachine as Oracle
from original_match.port.guest import PortFrame
from goal2rust.machine import PortMachine,BridgeRunner
ROOT='0791:8889'
WRITE_SITES=tuple('0791:'+x for x in ['89E1','8A26','8A5B','8A79','8AA5','8AC1','86F0','8711','8725','8739','874E','8ADD'])+('214B:069F',)
ENTRY=next(reg.entries[ROOT] for reg,_ in load(['all']) if ROOT in reg.entries)

def exercise(cls,case,*,tapped=True,listener=True,pause=None,failure=None,variant=None,mutant=0,direct=False,snapshot=None,mutations=False):
 rng=random.Random(case);m=cls(bytes(range(256))*(0x110000//256),0x823,mutant=mutant) if cls is PortMachine else cls(bytes(range(256))*(0x110000//256),0x823)
 mem=m.port_memory();ds=m.DS*16;log=[];calls={};visits=[];done=[];state=dict(writes={},seed_mutations=0,arg_mutations=0,delta_mutations=0,direction_mutations=0,retry_mutations=0)
 def put(a,v,n=1):m._memory[a:a+n]=(v&((1<<(8*n))-1)).to_bytes(n,'little')
 if cls is Oracle:
  def runner(machine):calls[ROOT]=calls.get(ROOT,0)+1;PortFrame(machine,mem,ENTRY,variant).start()
 else:runner=BridgeRunner(ENTRY,variant,mem,calls)
 m.port(ROOT,runner)
 if snapshot is None:
  mode=case%16;seg=0x4000;off=[0,0xfff0,0xffff,rng.randrange(65536)][case%4];rec=seg*16+off
  x=[0,1,8,255,248,127,128,7][(case//16)%8];y=[0,1,37,255,219,127,128,36][(case//8)%8]
  ddx,ddy=[(0,0),(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(128,127)][(case//3)%8]
  tx=(x+ddx)&255;ty=(y+ddy)&255
  if mode==0:tx,ty=x,y
  if mode==6:x,y,tx,ty=0,1,2,10
  if mode in [5,14]:x,y=127,128
  for k,v,n in [(0,x|y<<8,2),(2,x|y<<8,2),(6,1 if mode==3 else 3,1),(7,tx,1),(8,ty,1),(13,[0,1,32767,65535][case%4],2),(15,0,1),(18,5,1)]:put(rec+k,v,n)
  put(ds+0x8302,int(mode in [1,2]));put(ds+0x830b,3 if mode==9 else 99);put(ds+0x830c,3 if mode==8 else 98);put(ds+0x8325,int(mode not in [0,7]));put(ds+0x82f7,127 if mode==1 else 128)
  put(ds+0x8319,[128,255,0,1,127][case%5]);put(ds+0x831b,[0,1,127,32768,65535][case%5],2);put(ds+0x7920,255);put(ds+0x7921,1)
  for k in [0x82e3,0x82e9]:put(ds+k,4)
  if mode==6:put(ds+0x8319,0);put(ds+0x831b,0,2)
  m._memory[m.lin('0791:8869'):m.lin('0791:8869')+32]=bytes([0 if mode==4 else 255])*32
  m._memory[ds+0x648:ds+0x668]=bytes([0 if mode==12 else 255])*32
  poff=[0,0xffff,0xfffe,rng.randrange(65536)][case%4];pseg=0x6000;idx=int.from_bytes(m._memory[rec+13:rec+15],'little');put(ds+0xa91b,poff,2);put(ds+0xa91d,pseg,2);put(pseg*16+((poff+idx*20)&65535)+6,int(mode!=10))
  boff=[0,0xffff,0xfffe,rng.randrange(65536)][case%4];bseg=0xa000;put(ds+0x7c16,boff,2);put(ds+0x7c18,bseg,2);m._memory[bseg*16:bseg*16+65536]=bytes([13 if mode==11 else 0x42])*65536
  seedoff=[0,0xffff,0xfffe,rng.randrange(65536)][case%4];seedseg=0x8000;put(ds+0xa978,seedoff,2);put(ds+0xa97a,seedseg,2);put(seedseg*16+seedoff,[0,1,0x1234,32767,65535,rng.randrange(65536)][case%6],2)
  for reg in ['eax','ebx','ecx','edx','esi','edi','ebp','eflags']:m.set_reg(reg,rng.randrange(1<<32))
  sp=[0,2,8,16,0x100,0xffff,0xfffe][case%7];parent=[0,0xfff9,0xfffa,0xfffb,0xffff,0x2000][case%6];ss=0x20000
  occupied=set(range(ss+sp,ss+sp+2))|set(range(ss+((sp+2)&65535),ss+((sp+2)&65535)+2));at=ss+((parent+6)&65535)
  if occupied&set(range(at,at+4)):parent=0x2000;at=ss+parent+6
  put(at,off,2);put(at+2,seg,2);put(ss+sp,0x300,2);put(ss+((sp+2)&65535),parent,2)
  for reg,val in [('ss',0x2000),('sp',sp),('cs',m.seg(0x791)),('eip',0x8889)]:m.set_reg(reg,val)
  end=m.lin('0791:0300')
 else:
  memory,regs,ent=snapshot;m._memory[:]=memory;m._registers.clear();m._registers.update(regs);sp,far=ent;assert not far
  ss=(regs['ss']&65535)*16;ip=int.from_bytes(memory[ss+sp:ss+sp+2],'little');end=(regs['cs']&65535)*16+ip
  parent=int.from_bytes(memory[ss+((sp+2)&65535):ss+((sp+2)&65535)+2],'little');at=ss+((parent+6)&65535);off=int.from_bytes(memory[at:at+2],'little');seg=int.from_bytes(memory[at+2:at+4],'little');rec=seg*16+off
 class Tap:
  def site_enter(self,*x,**kw):log.append(('se',x,kw))
  def site_leave(self,*x,**kw):log.append(('sl',x,kw))
  def listen_enter(self,*x):log.append(('le',x));return len(log)
  def listen_leave(self,x):log.append(('ll',x))
 if tapped:
  def io(kind,x,v):
   log.append(('io',kind,x,bytes(v) if isinstance(v,(bytes,bytearray)) else v))
   if failure=='reg:ss' and kind=='g' and x=='ss':raise ValueError('run-step register refused')
  m.io_tap=io;m.site_tap=m.listen_tap=Tap()
 if listener:
  def listen(a,n,v):
   pc=m.pc();log.append(('w',a,n,v,pc))
   for site in WRITE_SITES:
    if pc==m.lin(site):state['writes'][site]=state['writes'].get(site,0)+1
   if failure=='write' or any(failure=='write:'+s and pc==m.lin(s) for s in WRITE_SITES):raise ValueError('run-step write refused')
   if mutations:
    if pc==m.lin('214B:069F') and state['seed_mutations']==0:
     put(ds+0xa978,0xffff,2);put(ds+0xa97a,0x8100,2);put(0x81000+0xffff,1,2);state['seed_mutations']+=1
     put(rec+7,127);put(rec+8,128);state['delta_mutations']+=1
     put(ss+((sp+2)&65535),0x2222,2);put(ss+((parent+6)&65535),0x100,2);state['arg_mutations']+=1
    if pc in [m.lin(s) for s in ['0791:8711','0791:8725','0791:8739','0791:874E']] and state['direction_mutations']==0 and case%2==0:put(rec+15,5);state['direction_mutations']+=1
    if pc==m.lin('0791:8ADD'):put(rec+2,0,2);state['retry_mutations']+=1
  m.on_write(0,0x10ffff,listen)
 def handler(replay):
  visits.append((ROOT,replay));log.append(('state',ROOT,hashlib.sha256(m._memory).hexdigest(),dict(m._registers)))
  if failure==ROOT:raise ValueError('run-step entry refused')
  if pause==ROOT and len(visits)==1:m.stop('pause')
 m.at(ROOT,handler)
 error=suspended=None
 try:
  if direct:
   cb=lambda f:done.append((f.entry.address,f.value))
   if cls is Oracle:calls[ROOT]=1;PortFrame(m,mem,ENTRY,variant,cb).start()
   else:BridgeRunner(ENTRY,variant,mem,calls)(m,cb)
  reason=m.run(end,fresh=True)
  if reason=='pause':
   suspended=[(f.entry.address,f.ss,f.sp,f.bp,f.waiting) for f in m.frames];m.run(end)
 except Exception as exc:error=(type(exc).__name__,str(exc))
 m.io_tap=None
 return dict(memory=hashlib.sha256(m._memory).hexdigest(),regs=dict(m._registers),log=log,calls=calls,visits=visits,done=done,error=error,suspended=suspended,state=state,entries=list(mem._entries),frames=[f.describe() for f in m.frames],no_replay_at=m.no_replay_at,running=m.running),getattr(getattr(m,'_core',None),'native_calls',{})

class RunStepTests(unittest.TestCase):
 def test_native_body(self):
  p,_=exercise(Oracle,1);r,n=exercise(PortMachine,1);self.assertIsNone(p['error']);self.assertEqual(p,r);self.assertEqual(n.get(ROOT),1)
 def test_positive_paths_and_mutations(self):
  writes=set();mutations={}
  for case in range(240):
   for tapped in [False,True]:
    opts=dict(tapped=tapped,pause=ROOT if case%7==0 else None,direct=case%3==0,mutations=case%5==0)
    with self.subTest(case=case,tapped=tapped):
     p,_=exercise(Oracle,case,**opts);r,_=exercise(PortMachine,case,**opts);self.assertIsNone(p['error']);self.assertEqual(p,r);writes.update(p['state']['writes'])
     for k,v in p['state'].items():
      if k!='writes':mutations[k]=mutations.get(k,0)+v
  self.assertTrue(set(WRITE_SITES)<=writes,set(WRITE_SITES)-writes);self.assertTrue(all(mutations.values()),mutations)
 def test_errors_and_variants(self):
  for failure in ['write',ROOT,'reg:ss']+['write:'+s for s in WRITE_SITES]:
   for case in [1,2,3,4,6,7,11,12,13,14,17,25]:
    with self.subTest(case=case,failure=failure):self.assertEqual(exercise(Oracle,case,failure=failure)[0],exercise(PortMachine,case,failure=failure)[0])
  for variant in ['coin-swapped','bound-36','no-picture','nondefault-identity']:
   p,_=exercise(Oracle,13,variant=variant);r,n=exercise(PortMachine,13,variant=variant);self.assertEqual(p,r);self.assertNotIn(ROOT,n)
if __name__=='__main__':unittest.main()
