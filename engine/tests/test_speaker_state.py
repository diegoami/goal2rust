"""T09 speaker/RNG data state, exact ABI stub boundaries and callback mutation."""
import hashlib,random,unittest
from original_match.port import load
from original_match.port.engine import PortMachine as Oracle
from original_match.port.guest import PortFrame
from goal2rust.machine import PortMachine,BridgeRunner
ROOT,SEED,RNG,OFF='0791:94E8','0791:94C9','214B:0688','214B:1E8D'
BODIES=(ROOT,SEED,RNG,OFF);STUBS=('214B:1EBC','0791:0425')
SITES=BODIES+STUBS+tuple('0791:'+x for x in ['94F9','94DC','9522','952B','9532','9540'])
ENTRIES={ad:e for reg,_ in load(['all']) for ad,e in reg.entries.items() if ad in BODIES+STUBS}

def exercise(cls,case,*,root=ROOT,tapped=True,listener=True,pause=None,failure=None,variant=None,seed_variant=None,
             mutant=0,body=False,direct=False,snapshot=None,mutations=False):
 rng=random.Random(case)
 m=cls(bytes(range(256))*(0x110000//256),0x823,mutant=mutant) if cls is PortMachine else cls(bytes(range(256))*(0x110000//256),0x823)
 mem=m.port_memory();log=[];calls={};visits=[];done=[];flags=dict(seed_writes=0,stack_mutations=0,pending=False)
 for ad,e in ENTRIES.items():
  v=variant if ad==root else seed_variant if ad==SEED else None
  if cls is Oracle:
   def runner(machine,e=e,v=v):calls[e.address]=calls.get(e.address,0)+1;PortFrame(machine,mem,e,v).start()
  else:runner=BridgeRunner(e,v,mem,calls)
  m.port(ad,runner)
 if snapshot is None:
  ds=m.DS*16;game_off=[0,0xfff0,rng.randrange(65536)][case%3];game_seg=0x4000
  def put(at,v,n=1):m._memory[at:at+n]=v.to_bytes(n,'little')
  put(ds+0xa923,game_off,2);put(ds+0xa925,game_seg,2)
  put(game_seg*16+((game_off+63)&65535),[0,1,5,127,255][case%5])
  put(ds+0x832a,[0,1,49,50,51,300,32767,32768,65535][case%9],2)
  put(ds+0x8336,[0,1,0xffff,0x7fff,rng.randrange(65536)][case%5],2)
  put(ds+0x8338,rng.randrange(65536),2);put(ds+0xa9fc,[0,1,255][case%3])
  off=[0,0xffff,rng.randrange(65536)][case%3];seg=0x5000;n=[0,1,2,50,0xffff,rng.randrange(65536)][case%6]
  put(seg*16+off,rng.randrange(65536),2)
  for reg in ['eax','ebx','ecx','edx','esi','edi','ebp']:m.set_reg(reg,rng.randrange(1<<32))
  m.set_reg('eflags',rng.randrange(1<<32)|(0x400 if case%2 else 0)|2)
  sp=[0,2,8,16,0x100,0xfffa,0xfffe][case%7];args=[] if root in [ROOT,OFF] else [n] if root==SEED else [seg,off,n]
  if ENTRIES[root].far:end=m.far_call(root,args,'000E:0300',0x3000,sp)
  else:
   for reg,v in [('ss',0x3000),('sp',sp),('ds',m.DS),('es',m.DS),('cs',m.seg(0x791)),('eip',int(root[5:],16))]:m.set_reg(reg,v)
   for i,w in enumerate([0x200]+list(reversed(args))):put(0x30000+((sp+2*i)&65535),w,2)
   end=m.lin('0791:0200')
  seed_addr=seg*16+off if root==RNG else ds+0x8336
 else:
  memory,regs,entry=snapshot;m._memory[:]=memory;m._registers.clear();m._registers.update(regs);sp,far=entry;ss=(regs['ss']&65535)*16
  ip=int.from_bytes(memory[ss+sp:ss+sp+2],'little')
  if far:
   p=(sp+2)&65535;cs=int.from_bytes(memory[ss+p:ss+p+2],'little')
  else:cs=regs['cs']&65535
  end=cs*16+ip;seed_addr=m.DS*16+0x8336
 class Tap:
  def site_enter(self,*x,**kw):log.append(('se',x,kw))
  def site_leave(self,*x,**kw):log.append(('sl',x,kw))
  def listen_enter(self,*x):log.append(('le',x));return len(log)
  def listen_leave(self,x):log.append(('ll',x))
 if tapped:m.io_tap=lambda *x:log.append(('io',x));m.site_tap=m.listen_tap=Tap()
 if listener:
  def write(a,n,v):
   pc=m.pc();log.append(('w',a,n,v,pc))
   if mutations and pc==m.lin('214B:069F'):
    m._registers['eflags']^=0x400;flags['seed_writes']+=1;flags['pending']=True
   elif mutations and flags['pending'] and pc==m.lin('214B:0000'):
    m._registers['eflags']^=0x400;m._memory[seed_addr:seed_addr+2]=b'\xcd\xab';flags['pending']=False;flags['stack_mutations']+=1
   if failure=='write':raise ValueError('speaker write refused')
  m.on_write(0,0x10ffff,write)
 for site in SITES:
  def handler(replay,site=site):
   visits.append((site,replay));log.append(('state',site,hashlib.sha256(m._memory).hexdigest(),dict(m._registers)))
   if failure==site:raise ValueError('speaker site refused')
   if pause==site and sum(s==site for s,_ in visits)==1:m.stop('pause')
  m.at(site,handler)
 error,suspended,value=None,None,None
 try:
  if body:
   mem._entries.append((sp,ENTRIES[root].far))
   try:value=m._core.routine(m,mem,root) if cls is PortMachine else ENTRIES[root].fn(mem,variant)
   finally:mem._entries.pop()
   reason=None
  else:
   if direct:
    cb=lambda f:done.append((f.entry.address,f.value))
    if cls is Oracle:calls[root]=1;PortFrame(m,mem,ENTRIES[root],variant,cb).start()
    else:BridgeRunner(ENTRIES[root],variant,mem,calls)(m,cb)
   reason=m.run(end,fresh=True)
  if reason=='pause':
   suspended=[(f.entry.address,f.ss,f.sp,f.bp,f.ret_lin,f.expect_sp,f.after_sp,None if f.waiting is None else (f.waiting.target,f.waiting.args,f.waiting.ret_to)) for f in m.frames]
   m.run(end)
 except Exception as e:error=(type(e).__name__,str(e))
 m.io_tap=None
 return dict(memory=hashlib.sha256(m._memory).hexdigest(),regs=dict(m._registers),log=log,calls=calls,visits=visits,done=done,value=value,error=error,suspended=suspended,flags=flags,entries=list(mem._entries),frames=[f.describe() for f in m.frames],no_replay_at=m.no_replay_at,running=m.running),getattr(getattr(m,'_core',None),'native_calls',{})

class SpeakerStateTests(unittest.TestCase):
 def test_all_bodies_and_continuations(self):
  p,_=exercise(Oracle,2);r,n=exercise(PortMachine,2);self.assertEqual(p,r);self.assertEqual(n.get(ROOT),1)
  for case in range(80):
   for root in BODIES:
    for tapped in [False,True]:
     opts=dict(root=root,tapped=tapped,pause=SITES[case%len(SITES)],mutations=case%3==0)
     with self.subTest(case=case,**opts):
      p,_=exercise(Oracle,case,**opts);r,n=exercise(PortMachine,case,**opts);self.assertEqual(p,r);self.assertEqual(n.get(root),1)
 def test_leaf_bodies_callbacks_and_done(self):
  for case in range(30):
   for opts in [dict(root=RNG,body=True,mutations=True),dict(root=OFF,body=True),dict(root=SEED,direct=True),dict(root=ROOT,direct=True,mutations=True)]:
    with self.subTest(case=case,**opts):self.assertEqual(exercise(Oracle,case,**opts)[0],exercise(PortMachine,case,**opts)[0])
 def test_errors_and_variants(self):
  for opts in [dict(failure=s) for s in ['write',ROOT,SEED,RNG,OFF,'0791:94DC','0791:9540']]+[dict(variant='omit-0791-94e8'),dict(seed_variant='secondary-seed-adjacent')]:
   with self.subTest(**opts):
    p,_=exercise(Oracle,2,**opts);r,n=exercise(PortMachine,2,**opts);self.assertEqual(p,r)
    if opts.get('variant'):self.assertNotIn(ROOT,n)
if __name__=='__main__':unittest.main()
