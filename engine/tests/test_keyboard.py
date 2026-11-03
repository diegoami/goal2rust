"""T24 closed depth tree; authored state and artifact-bound real captures."""
import hashlib,json,random,sys,unittest
from pathlib import Path
from original_match.port import Entry,load
from original_match.port.runtime import args
from original_match.port.engine import PortMachine as Oracle
from original_match.port.guest import PortFrame
from original_match.port import positioning,geometry,entrypoints,runtime,contests,motion,menus,restarts
from goal2rust.machine import PortMachine,BridgeRunner
ROOT='214B:0983'
NEW=('214B:0723','214B:08DD',ROOT,'214B:0993')
CALLERS=(ROOT,)
LEAVES=('214B:0723','214B:08DD','214B:0993')
OUTPUTS=tuple((r,189+i) for i,r in enumerate(NEW))+tuple((r,193+i) for i,r in enumerate(NEW))
ENTRIES={a:e for reg,_ in load(['all']) for a,e in reg.entries.items()}
TARGETS=()
RETURNS=('214B:098A',)
SITES=NEW+RETURNS
OWNED=set()
import importlib
for body in json.loads((Path(__file__).resolve().parents[2]/'out/T24/inventory-v1.json').read_text())['bodies'].values():
 for helper in body['helper_symbols']:
  module,name=helper['symbol'].rsplit('.',1)
  OWNED.add(getattr(importlib.import_module(module),name).__code__)

def exercise(cls,case,*,root=ROOT,tapped=True,listener=True,pause=None,failure=None,variant=None,mutant=0,direct=False,snapshot=None,controlled=False,mutations=False,profile=False):
 rng=random.Random(case);m=cls(bytes(0x110000),0x823,mutant=mutant) if cls is PortMachine else cls(bytes(0x110000),0x823)
 mem=m.port_memory();ds=m.DS*16;log=[];calls={};visits=[];done=[];scope=dict(active=False,owned={},outside=0);state=dict(writes={},mutations=0,read_index=0,write_index=0);mode=case%16
 def put(a,v,n=1):m._memory[a:a+n]=(v&((1<<(8*n))-1)).to_bytes(n,'little')
 selected=set(NEW)|set(TARGETS)
 for ad in selected:
  original=ENTRIES[ad];entry=original;v=variant if ad==root else None
  if controlled and ad!=root:
   def abi(mem,v,ad=ad,original=original):
    packet=args(mem,original.pop//2);ret=m.frames[-1].waiting.ret_to;log.append(('abi',ad,packet,ret))
    value=[0,1,65535,32768,32767,0x1234][case%6]
    for reg,x in [('ax',value),('dx',value^0x8000),('bx',0x4321),('cx',0x7654),('si',0x1111),('di',0x2222)]:mem.set_reg(reg,x)
   entry=Entry(ad,original.ret,abi,'controlled '+ad,original.long,original.stub,original.return_stack_delta);v='T24-controlled'
  if cls is Oracle:
   def runner(machine,entry=entry,v=v):calls[entry.address]=calls.get(entry.address,0)+1;PortFrame(machine,mem,entry,v).start()
  else:runner=BridgeRunner(entry,v,mem,calls)
  m.port(ad,runner)
 ss=0x20000;sp=[0x100,0,2,8,16,0xffe0,0xfffe,0xfffb,0xfffd,0xffff][case%10]
 if snapshot is None:
  for reg in ['eax','ebx','ecx','edx','esi','edi','ebp','eflags']:m.set_reg(reg,rng.randrange(1<<32))
  put(ds+0x79ae,[0,1,255][case%3]);put(ds+0xa976,[0,13,27,65,128,255][case%6]);put(ds+0xa977,rng.randrange(256))
  packet=[(case*277+0xab00)&65535] if root=='214B:0993' else []
  end=m.far_call(root,list(reversed(packet)),'000E:0300',0x2000,sp)
  if packet:put(ss+((sp+4)&65535),packet[0],2)

 else:
  memory,regs,ent=snapshot;m._memory[:]=memory;m._registers.clear();m._registers.update(regs);sp,far=ent;ss=regs['ss']*16;ip=int.from_bytes(memory[ss+sp:ss+sp+2],'little');cs=int.from_bytes(memory[ss+((sp+2)&65535):ss+((sp+2)&65535)+2],'little') if far else regs['cs']&65535;end=cs*16+ip
 class Truth:
  def __bool__(self):
   log.append(('provider-truth',case%2))
   if failure=='truth':raise ValueError('keyboard truth refused')
   return bool(case%2)
 class Keys:
  def keypressed(self,site):
   state['polls']=state.get('polls',0)+1;log.append(('kit-poll',site))
   if failure=='poll':raise ValueError('keyboard poll refused')
   if mutations:m.set_reg('ax',0xbac0);state['mutations']+=1
   return Truth()
  def key(self,site):
   state['keys']=state.get('keys',0)+1;log.append(('kit-key',site))
   if failure=='key':raise ValueError('keyboard read refused')
   key=[0,13,27,65,128,255][case%6]
   mem.wds8(0xa976,key,'214B:08DD');mem.wds8(0xa977,key^255,'214B:08DD');mem.set_reg('ax',0xa500|key)
   if failure=='decision-stop':m.stop('decision')
   if failure=='events-stop':m.stop('events')
   return key^0x40
 mem.keys=None if failure=='missing-kit' else Keys()
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
    if failure=='read-index:'+str(state['read_index']):raise ValueError('travel read refused')
   if kind=='g' and failure=='reg:'+str(x):raise ValueError('travel register refused')
  m.io_tap=io;m.site_tap=m.listen_tap=Tap()
 if listener:
  def listen(a,n,v):
   state['write_index']+=1
   if failure=='write-index:'+str(state['write_index']):
    log.append(('ordinal-write-refused',a,n,v,m.pc()));raise ValueError('travel ordinal write refused')
   pc=m.pc();state['writes'][pc]=state['writes'].get(pc,0)+1;log.append(('w',a,n,v,pc))
   if failure=='write' or (isinstance(failure,str) and failure.startswith('write:') and pc==m.lin(failure[6:])):raise ValueError('travel write refused')
   if mutations and pc==m.lin('214B:0000'):
    m._registers['eflags']^=0x400;state['mutations']+=1
  m.on_write(0,0x10ffff,listen)
 for site in SITES:
  def handler(replay,site=site):
   if site==root:scope['active']=True
   visits.append((site,replay));log.append(('state',site,hashlib.sha256(m._memory).hexdigest(),dict(m._registers)))
   log.append(('waiting',site,[(f.entry.address,f.waiting.target,tuple(f.waiting.args),f.waiting.ret_to) for f in m.frames if f.waiting is not None]))
   if failure==site:raise ValueError('travel site refused')
   if pause==site and sum(s==site for s,_ in visits)==1:m.stop('pause')
  m.at(site,handler)
 def profiler(frame,event,arg):
  if event=='call' and frame.f_code in OWNED:
   if scope['active']:scope['owned'][frame.f_code.co_name]=scope['owned'].get(frame.f_code.co_name,0)+1
   else:scope['outside']+=1
 def finish(f):scope['active']=False;done.append((f.entry.address,f.value))
 class Outside:
  def leave(self):pass
  def store(self):pass
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
  if profile:restarts._end(Outside())
  sys.setprofile(oldprofile)
 m.io_tap=None
 return dict(memory=hashlib.sha256(m._memory).hexdigest(),regs=dict(m._registers),log=log,calls=calls,visits=visits,done=done,error=error,suspended=suspended,state=state,entries=list(mem._entries),frames=[f.describe() for f in m.frames],running=m.running,no_replay_at=m.no_replay_at),getattr(getattr(m,'_core',None),'native_calls',{}),scope

class KeyboardTests(unittest.TestCase):
 def test_wait_actual_and_controlled(self):
  for controlled in (False,True):
   for case in range(64):
    opts=dict(root=ROOT,controlled=controlled,pause='214B:098A' if case%2 else ROOT,direct=case%3==0,profile=not controlled)
    p,_,ps=exercise(Oracle,case,**opts);r,n,rs=exercise(PortMachine,case,**opts)
    self.assertIsNone(p['error'],p['error']);self.assertEqual(p,r);self.assertEqual(n.get(ROOT),1)
    if not controlled:self.assertFalse(rs['owned']);self.assertTrue(ps['owned'])
 def test_kit_failures_and_stop_rules(self):
  for root in ['214B:0723','214B:08DD']:
   failures=['missing-kit','poll','truth'] if root=='214B:0723' else ['missing-kit','key','decision-stop']
   for failure in failures:
    p,_,_=exercise(Oracle,0,root=root,failure=failure);r,_,_=exercise(PortMachine,0,root=root,failure=failure)
    self.assertIsNotNone(p['error'],(root,failure));self.assertEqual(p,r)
  p,_,_=exercise(Oracle,0,root='214B:08DD',failure='events-stop');r,_,_=exercise(PortMachine,0,root='214B:08DD',failure='events-stop');self.assertIsNone(p['error']);self.assertEqual(p,r)
 def test_wait_return_control(self):
  for case in range(16):
   p,_,_=exercise(Oracle,case,root=ROOT);r,_,_=exercise(PortMachine,case,root=ROOT,mutant=197);self.assertIsNone(p['error']);self.assertNotEqual(p,r)
 def test_errors_variants_controls(self):
  for root in NEW:
   for failure in (root,'reg:ss')+(() if root=='214B:0723' else ('write',)):
    with self.subTest(root=root,failure=failure):
     p,_,_=exercise(Oracle,1,root=root,failure=failure);r,_,_=exercise(PortMachine,1,root=root,failure=failure)
     self.assertIsNotNone(p['error']);self.assertEqual(p,r)
   p,_,_=exercise(Oracle,1,root=root);r,_,_=exercise(PortMachine,1,root=root,mutant=185+NEW.index(root));self.assertNotEqual(p,r)
   p,_,_=exercise(Oracle,1,root=root,variant='identity');r,n,scope=exercise(PortMachine,1,root=root,variant='identity',profile=True)
   self.assertEqual(p,r);self.assertNotIn(root,n);self.assertTrue(scope['owned'])
  for root,control in OUTPUTS:
   p,_,_=exercise(Oracle,1,root=root);r,_,_=exercise(PortMachine,1,root=root,mutant=control);self.assertNotEqual(p,r)
 def test_native_leaves(self):
  for root in LEAVES:
   for case in range(96):
    with self.subTest(root=root,case=case):
     opts=dict(root=root,mutations=case%5==0,direct=case%3==0,pause=root if case%7==0 else None,profile=True)
     p,_,ps=exercise(Oracle,case,**opts);r,n,rs=exercise(PortMachine,case,**opts)
     self.assertIsNone(p['error']);self.assertEqual(p,r);self.assertEqual(n.get(root),1);self.assertTrue(ps['owned']);self.assertFalse(rs['owned'])
if __name__=='__main__':unittest.main()
