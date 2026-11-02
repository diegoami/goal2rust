"""T20 closed depth tree; authored state and artifact-bound real captures."""
import hashlib,json,random,sys,unittest
from pathlib import Path
from original_match.port import Entry,load
from original_match.port.runtime import args
from original_match.port.engine import PortMachine as Oracle
from original_match.port.guest import PortFrame
from original_match.port import positioning,geometry,entrypoints,runtime,contests
from goal2rust.machine import PortMachine,BridgeRunner
ROOT='0791:5729'
NEW=('0791:2EB8','0791:2EF0',ROOT)
CALLERS=(ROOT,)
LEAVES=('0791:2EB8','0791:2EF0')
ENTRIES={a:e for reg,_ in load(['all']) for a,e in reg.entries.items()}
TARGETS=('0791:045D', '0791:26D7', '0791:2B51')
RETURNS=('0791:5740', '0791:5751', '0791:5766', '0791:5781', '0791:5796')
SITES=NEW+TARGETS+RETURNS
OWNED=set()
for body in json.loads((Path(__file__).resolve().parents[2]/'out/T20/inventory-v1.json').read_text())['bodies'].values():
 for helper in body['helper_symbols']:
  module,name=helper['symbol'].rsplit('.',1)
  if module.rsplit('.',1)[-1] not in ('positioning','geometry','contests'):continue
  obj=getattr(sys.modules[module],name)
  OWNED.add(obj.__code__)
OWNED.add(positioning.pitch.__code__)

def exercise(cls,case,*,root=ROOT,tapped=True,listener=True,pause=None,failure=None,variant=None,mutant=0,direct=False,snapshot=None,controlled=False,mutations=False,profile=False):
 rng=random.Random(case);m=cls(bytes(0x110000),0x823,mutant=mutant) if cls is PortMachine else cls(bytes(0x110000),0x823)
 mem=m.port_memory();ds=m.DS*16;log=[];calls={};visits=[];done=[];scope=dict(active=False,owned={},outside=0);state=dict(writes={},mutations=0,read_index=0,write_index=0);mode=case%16
 def put(a,v,n=1):m._memory[a:a+n]=(v&((1<<(8*n))-1)).to_bytes(n,'little')
 selected=set(NEW)|set(json.loads((Path(__file__).resolve().parents[2]/'out/T19/profile-after-v1.json').read_text())['native_calls'])
 for ad in selected:
  original=ENTRIES[ad];entry=original;v=variant if ad==root else None
  if controlled and ad!=root:
   def abi(mem,v,ad=ad,original=original):
    packet=args(mem,original.pop//2);ret=m.frames[-1].waiting.ret_to;log.append(('abi',ad,packet,ret))
    value=0
    if ad=='0791:045D':value=0xa700|(case%2)
    if ad=='0791:2B51':value=0xa800|int((case//2)%2!=0)
    if ad=='0791:2EB8':value=0xa900|int((case//4)%2!=0)
    if ad=='0791:2EF0':value=0xaa00|int((case//8)%2!=0)
    if ad=='0791:26D7':value=0xab00|[0,1,128,255][(case//16)%4]
    for reg,x in [('ax',value),('dx',value^0x1234),('es',0x6000)]:mem.set_reg(reg,x)
   entry=Entry(ad,original.ret,abi,'controlled '+ad,original.long,original.stub,original.return_stack_delta);v='T20-controlled'
  if cls is Oracle:
   def runner(machine,entry=entry,v=v):calls[entry.address]=calls.get(entry.address,0)+1;PortFrame(machine,mem,entry,v).start()
  else:runner=BridgeRunner(entry,v,mem,calls)
  m.port(ad,runner)
 seg=0x4000;off=[0x100,0xfff0,0xffff,rng.randrange(65536)][case%4];rec=seg*16+off;sp=[0x100,0,2,8,16,0xffe0,0xfffe][case%7];ss=0x20000
 if snapshot is None:
  for reg in ['eax','ebx','ecx','edx','esi','edi','ebp','eflags']:m.set_reg(reg,rng.randrange(1<<32))
  for k,v,n in [(0xa91b,0xfff0 if case%3==0 else 0x100,2),(0xa91d,0x7000,2),(0x830b,[0,11,12,255][case%4],1),(0x8319,[0,1,127,128,255][case%5],1),(0x831b,[0,1,127,32768,65535][case%5],2),(0x7920,255,1),(0x7921,1,1)]:put(ds+k,v,n)
  for k in range(0x7ba,0x840):put(ds+k,case%5 if k<0x7be else (case//5)%4)
  poff=int.from_bytes(m._memory[ds+0xa91b:ds+0xa91d],'little')
  for player in range(64):
   p=0x70000+((poff+20*player)&65535)
   for k,v in [(6,[0,1,2,4,5,11,12,13,255][case%9]),(7,2),(8,10),(9,60),(10,30),(14,[0,1,32,33,127,128,255][case%7]),(15,0)]:put(p+k,v)
  for k,v,n in [(0,[0,0x101,0x7f80,0x807f,65535][case%5],2),(6,[1,2,3,11,12,13,22,255][case%8],1),(9,[0,1,127,128,255][case%5],1),(12,[0,1,2,127,128,255][(case//3)%6],1),(13,3,2)]:put(rec+k,v,n)
  points=[0,0x1800,0x1900,0x1a05,0x1906,0x1eff,0xe700,0xe6fb,0xe706,0x7f80,0x807f,0xffff]
  point=points[(case//4)%len(points)];put(ds+0x82f6,point,2)
  put(rec,[0x1900,0xe700,0x1a05,0xe6fb,0x7f05,0x8005,0][(case//7)%7],2)
  parent=0x3000;put(ss+parent+6,off,2);put(ss+parent+8,seg,2)
  words=[parent] if root==ROOT else [point,seg,off]
  if not ENTRIES[root].far:
   put(ss+sp,0x300,2);put(ss+((sp+2)&65535),parent,2);m.set_reg('ss',0x2000);m.set_reg('sp',sp);m.set_reg('cs',m.seg(0x791));m.set_reg('eip',int(root[5:],16));end=m.lin('0791:0300')
  else:
   end=m.far_call(root,words,'000E:0300',0x2000,sp)
   if root in LEAVES:
    base=ss+((sp+4)&65535)
    for i,x in enumerate(reversed(words)):put(base+2*i,x,2)

 else:
  memory,regs,ent=snapshot;m._memory[:]=memory;m._registers.clear();m._registers.update(regs);sp,far=ent;ss=regs['ss']*16;ip=int.from_bytes(memory[ss+sp:ss+sp+2],'little');cs=int.from_bytes(memory[ss+((sp+2)&65535):ss+((sp+2)&65535)+2],'little') if far else regs['cs']&65535;end=cs*16+ip
 class Tap:
  def site_enter(self,*x,**kw):log.append(('se',x,kw))
  def site_leave(self,*x,**kw):log.append(('sl',x,kw))
  def listen_enter(self,*x):log.append(('le',x));return len(log)
  def listen_leave(self,x):log.append(('ll',x))
 if tapped:
  def io(kind,x,v):
   log.append(('io',kind,x,bytes(v) if isinstance(v,(bytes,bytearray)) else v))
   if kind=='r':
    state['read_index']+=1
    if failure=='read-index:'+str(state['read_index']):raise ValueError('chase read refused')
   if kind=='g' and failure=='reg:'+str(x):raise ValueError('depth register refused')
  m.io_tap=io;m.site_tap=m.listen_tap=Tap()
 if listener:
  def listen(a,n,v):
   state['write_index']+=1
   if failure=='write-index:'+str(state['write_index']):
    log.append(('ordinal-write-refused',a,n,v,m.pc()));raise ValueError('chase ordinal write refused')
   pc=m.pc();state['writes'][pc]=state['writes'].get(pc,0)+1;log.append(('w',a,n,v,pc))
   if failure=='write' or (isinstance(failure,str) and failure.startswith('write:') and pc==m.lin(failure[6:])):raise ValueError('depth write refused')
   if mutations and pc==m.lin('214B:0000'):
    put(ds+0x8319,m._memory[ds+0x8319]^128);m._registers['eflags']^=0x400;state['mutations']+=1
  m.on_write(0,0x10ffff,listen)
 for site in SITES:
  def handler(replay,site=site):
   if site==root:scope['active']=True
   visits.append((site,replay));log.append(('state',site,hashlib.sha256(m._memory).hexdigest(),dict(m._registers)))
   log.append(('waiting',site,[(f.entry.address,f.waiting.target,tuple(f.waiting.args),f.waiting.ret_to) for f in m.frames if f.waiting is not None]))
   if failure==site:raise ValueError('depth site refused')
   if pause==site and sum(s==site for s,_ in visits)==1:m.stop('pause')
  m.at(site,handler)
 def profiler(frame,event,arg):
  if event=='call' and frame.f_code in OWNED:
   if scope['active']:scope['owned'][frame.f_code.co_name]=scope['owned'].get(frame.f_code.co_name,0)+1
   else:scope['outside']+=1
 def finish(f):scope['active']=False;done.append((f.entry.address,f.value))
 oldprofile=sys.getprofile();error=suspended=None
 try:
  if profile:sys.setprofile(profiler)
  if direct:
   scope['active']=True
   if cls is Oracle:calls[root]=1;PortFrame(m,mem,ENTRIES[root],variant,finish).start()
   else:BridgeRunner(ENTRIES[root],variant,mem,calls)(m,finish)
  reason=m.run(end,fresh=True)
  if reason=='pause':
   suspended=[(f.entry.address,f.ss,f.sp,f.bp,f.ret_lin,f.expect_sp,f.after_sp,None if f.waiting is None else (f.waiting.target,f.waiting.args,f.waiting.ret_to)) for f in m.frames];m.run(end)
 except Exception as exc:error=(type(exc).__name__,str(exc))
 finally:
  scope['active']=False
  if profile:positioning.pitch(mem,0)
  sys.setprofile(oldprofile)
 m.io_tap=None
 return dict(memory=hashlib.sha256(m._memory).hexdigest(),regs=dict(m._registers),log=log,calls=calls,visits=visits,done=done,error=error,suspended=suspended,state=state,entries=list(mem._entries),frames=[f.describe() for f in m.frames],running=m.running,no_replay_at=m.no_replay_at),getattr(getattr(m,'_core',None),'native_calls',{}),scope

class ChaseTests(unittest.TestCase):
 def test_native_callers(self):
  for root in CALLERS:
   for case in range(64):
    with self.subTest(root=root,case=case):
     opts=dict(root=root,pause=SITES[case%len(SITES)],direct=case%3==0,mutations=case%5==0,profile=True)
     p,_,ps=exercise(Oracle,case,**opts);r,n,rs=exercise(PortMachine,case,**opts)
     self.assertIsNone(p['error'],p['error']);self.assertEqual(p,r);self.assertEqual(n.get(root),1);self.assertTrue(ps['owned']);self.assertFalse(rs['owned'],rs)
 def test_controlled_callers(self):
  for root in CALLERS:
   for case in range(64):
    with self.subTest(root=root,case=case):
     opts=dict(root=root,controlled=True,pause=SITES[case%len(SITES)],direct=case%3==0)
     p,_,_=exercise(Oracle,case,**opts);r,_,_=exercise(PortMachine,case,**opts)
     self.assertIsNone(p['error'],p['error']);self.assertEqual(p,r)
 def test_errors_variants_controls(self):
  for root in NEW:
   for failure in (root,'reg:ss')+(() if root=='23E4:08DF' else ('write',)):
    with self.subTest(root=root,failure=failure):
     p,_,_=exercise(Oracle,1,root=root,failure=failure);r,_,_=exercise(PortMachine,1,root=root,failure=failure)
     self.assertIsNotNone(p['error']);self.assertEqual(p,r)
   p,_,_=exercise(Oracle,1,root=root);r,_,_=exercise(PortMachine,1,root=root,mutant=145+NEW.index(root));self.assertNotEqual(p,r)
   p,_,_=exercise(Oracle,1,root=root,variant='identity');r,n,scope=exercise(PortMachine,1,root=root,variant='identity',profile=True)
   self.assertEqual(p,r);self.assertNotIn(root,n);self.assertTrue(scope['owned'])
  for i,root in enumerate(LEAVES):
   p,_,_=exercise(Oracle,1,root=root);r,_,_=exercise(PortMachine,1,root=root,mutant=148+i);self.assertNotEqual(p,r)
 def test_individual_guest_return_controls(self):
  inventory=json.loads((Path(__file__).resolve().parents[2]/'out/T20/inventory-v1.json').read_text())
  for i,site in enumerate(inventory['guest_sites']):
   root=site['caller'];ret=site['ret_to'];reached=False
   for case in range(160):
    p,_,_=exercise(Oracle,case,root=root,controlled=True)
    self.assertIsNone(p['error'],(root,ret,case,p['error']))
    if ret not in {s for s,_ in p['visits']}:continue
    r,_,_=exercise(PortMachine,case,root=root,controlled=True,mutant=150+i)
    self.assertNotEqual(p,r,(root,ret,case));reached=True;break
   self.assertTrue(reached,(root,ret))
 def test_native_leaves(self):
  for root in LEAVES:
   for case in range(40):
    with self.subTest(root=root,case=case):
     opts=dict(root=root,mutations=case%5==0,direct=case%3==0,pause=root if case%7==0 else None,profile=True)
     p,_,ps=exercise(Oracle,case,**opts);r,n,rs=exercise(PortMachine,case,**opts)
     self.assertIsNone(p['error']);self.assertEqual(p,r);self.assertEqual(n.get(root),1);self.assertTrue(ps['owned']);self.assertFalse(rs['owned'])
if __name__=='__main__':unittest.main()
