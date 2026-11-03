"""T25 complete text-cell tree; authored state and artifact-bound real captures."""
import hashlib,json,random,sys,unittest
from pathlib import Path
from original_match.port import Entry,load
from original_match.port.runtime import args
from original_match.port.engine import PortMachine as Oracle
from original_match.port.guest import PortFrame
from original_match.port import positioning,geometry,entrypoints,runtime,contests,motion,display,restarts
from goal2rust.machine import PortMachine,BridgeRunner
ROOT='214B:02C8'
NEW=('214B:00FF','214B:0123','214B:01A3','214B:0205','214B:026D',ROOT)
CALLERS=NEW[2:]
LEAVES=NEW[:2]
OUTPUTS=tuple((root,204+7*i+j) for i,root in enumerate(NEW) for j in range(7))
ENTRIES={a:e for reg,_ in load(['all']) for a,e in reg.entries.items()}
TARGETS=('23E4:0644',)
RETURNS=('214B:01BE','214B:01FF','214B:0220','214B:0267','214B:0288','214B:02C2','214B:02E3','214B:0323')
SITES=NEW+TARGETS+RETURNS
OWNED=set()
import importlib
for body in json.loads((Path(__file__).resolve().parents[2]/'out/T25/inventory-v2.json').read_text())['bodies'].values():
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
    if ad=='23E4:0644':
     maximum,off,seg,_,_=packet;length=[0,1,9,255][case%4]
     for k,value in enumerate([length]+[(case+i*7)&255 for i in range(length)]):mem.w8(seg*16+((off+k)&65535),value,'23E4:0644')
    value=[0,1,65535,32768,32767,0x1234][case%6]
    for reg,x in [('ax',value),('dx',value^0x8000),('bx',0x4321),('cx',0x7654),('si',0x1111),('di',0x2222)]:mem.set_reg(reg,x)
   entry=Entry(ad,original.ret,abi,'controlled '+ad,original.long,original.stub,original.return_stack_delta);v='T25-controlled'
  if cls is Oracle:
   def runner(machine,entry=entry,v=v):calls[entry.address]=calls.get(entry.address,0)+1;PortFrame(machine,mem,entry,v).start()
  else:runner=BridgeRunner(entry,v,mem,calls)
  m.port(ad,runner)
 ss=0x20000;sp=[0x100,0,2,8,16,0xffe0,0xfffe,0xfffb,0xfffd,0xffff][case%10]
 if snapshot is None:
  for reg in ['eax','ebx','ecx','edx','esi','edi','ebp','eflags']:m.set_reg(reg,rng.randrange(1<<32))
  sg=0x4000;dg=0x5000;so=[0x100,0xffff,0xfffe,0,0xfff0,0x101,rng.randrange(65536)][case%7];do=[0x800,0xffff,0xfffe,0,0xfff0,0x801,rng.randrange(65536)][(case//7)%7]
  if mode in (0,1,2,3):dg=sg;do=(so+[0,1,-1,2][mode])&65535
  elif mode==4:dg=sg+1;do=(so-16)&65535
  length=[0,1,2,7,8,9,31,255][(case//16)%8]
  if case==499 and root in LEAVES:length=65535
  for k in range(512):put(sg*16+((so+k)&65535),(case+k*17)&255)
  colour=(case*277+0xab00)&65535
  if root in LEAVES:packet=[length,colour,so,sg,do,dg]
  else:
   put(sg*16+so,length);row=[0,1,2,255,256,0x1234,65535][(case//3)%7];col=[0,1,2,255,256,0xabcd,65535][(case//11)%7]
   table_seg=0x6000;table_off=[0x100,0xffff,0xfffe,0xfffd][case%4];put(table_seg*16+table_off,do,2);put(table_seg*16+table_off+2,dg,2)
   packet=[table_off,table_seg,col,row,so,sg]+([colour] if root in ('214B:0205','214B:02C8') else [])
  put(ds+0xaab2,[0,1,128,255][case%4])
  if ENTRIES[root].far:end=m.far_call(root,list(reversed(packet)),'000E:0300',0x2000,sp)
  else:
   put(ss+sp,0x300,2)
   for i,value in enumerate(packet):put(ss+((sp+2+2*i)&65535),value,2)
   for reg,value in [('ss',0x2000),('sp',sp),('ds',m.DS),('es',m.DS),('cs',m.seg(0x214b)),('eip',int(root[5:],16))]:m.set_reg(reg,value)
   end=m.lin('214B:0300')

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
   if mutations and root in LEAVES and pc in (m.lin('214B:0119'),m.lin('214B:013D')) and snapshot is None:
    step=-1 if root=='214B:0123' else 1;k=state['writes'][pc];put(sg*16+((so+step*k)&65535),(case+k*29)&255)
    m._registers['eax']^=0x8100;m._registers['esi']^=0x1234;m._registers['edi']^=0x4321;m._registers['eflags']^=0x800;state['mutations']+=1
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

class TextTests(unittest.TestCase):
 def pair(self,root,case,**opts):
  p,_,ps=exercise(Oracle,case,root=root,**opts);r,n,rs=exercise(PortMachine,case,root=root,**opts)
  self.assertIsNone(p['error'],(root,case,p['error']));self.assertEqual(p,r);return n,ps,rs
 def test_native_leaves(self):
  for root in LEAVES:
   for case in range(48):
    n,ps,rs=self.pair(root,case,mutations=case%5==0,pause=root if case%7==0 else None,direct=case%3==0,profile=True)
    self.assertEqual(n.get(root),1);self.assertTrue(ps['owned']);self.assertFalse(rs['owned']);self.assertGreater(rs['outside'],0)
 def test_native_callers(self):
  for root in CALLERS:
   for case in range(32):
    n,ps,rs=self.pair(root,case,profile=True,pause=RETURNS[(2*CALLERS.index(root)+case%2)],direct=case%3==0)
    self.assertEqual(n.get(root),1);self.assertEqual(n.get('23E4:0644'),1);self.assertFalse(rs['owned']);self.assertTrue(ps['owned'])
 def test_controlled_ABI(self):
  for root in CALLERS:
   for case in range(16):self.pair(root,case,controlled=True,pause=RETURNS[2*CALLERS.index(root)+case%2])
 def test_body_and_outputs(self):
  for root in NEW:
   p,_,_=exercise(Oracle,3,root=root);r,_,_=exercise(PortMachine,3,root=root,mutant=198+NEW.index(root));self.assertIsNone(p['error']);self.assertNotEqual(p,r)
  for root,control in OUTPUTS:
   p,_,_=exercise(Oracle,3,root=root);r,_,_=exercise(PortMachine,3,root=root,mutant=control);self.assertNotEqual(p,r)
 def test_return_controls(self):
  for i,site in enumerate(RETURNS):
   root=CALLERS[i//2];p,_,_=exercise(Oracle,1,root=root,controlled=True);r,_,_=exercise(PortMachine,1,root=root,controlled=True,mutant=246+i);self.assertIsNone(p['error']);self.assertNotEqual(p,r)
 def test_failures_and_variants(self):
  for root in NEW:
   for failure in (root,'reg:ss','write'):
    p,_,_=exercise(Oracle,1,root=root,failure=failure);r,_,_=exercise(PortMachine,1,root=root,failure=failure);self.assertIsNotNone(p['error']);self.assertEqual(p,r)
   for variant in ['identity','omit-'+root.lower().replace(':','-')]:
    n,ps,rs=self.pair(root,1,variant=variant,profile=True);self.assertNotIn(root,n);self.assertTrue(rs['owned'])
if __name__=='__main__':unittest.main()
