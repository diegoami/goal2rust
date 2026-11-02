"""T17 five-body marking closure: full state, real callees and scoped Python detection."""
import hashlib,random,sys,unittest
from original_match.port import Entry,load
from original_match.port.engine import PortMachine as Oracle
from original_match.port.guest import PortFrame
from original_match.port.runtime import args
from original_match.port import positioning,geometry,entrypoints
from goal2rust.machine import PortMachine,BridgeRunner
ROOT='0791:47C5';ZONE='0791:4438';HOLDER='0791:2996';HALF='0791:2C54';RANDOM='214B:06B1'
NEW=(ROOT,ZONE,HOLDER,HALF,RANDOM)
BOUNDARIES=('1771:3216','0791:278A','1771:3A06','0791:2BE5')
ENTRIES={a:e for reg,_ in load(['all']) for a,e in reg.entries.items() if a in NEW+BOUNDARIES}
RETURNS=('0791:47CE','0791:47EF','0791:485D','0791:4888','0791:48E2','0791:4930','0791:494D','0791:496A','0791:4980','0791:499D','0791:49B2','0791:49C0','0791:4493')
SITES=NEW+BOUNDARIES+RETURNS
WRITE_SITES=tuple('0791:'+s for s in ('47C5','47E2','47E5','47E8','47EF','4836','483F','489A','489D','48AB','49D3','48FB','4914','4937','494D','4980','49A7','49B2','49C7','49CB','4A1B','4438','4445','4470','44B5'))+('214B:069F','214B:0000')
OWNED={getattr(module,name).__code__ for module,names in (
 (positioning,'choose_marking_target near_post_zone rec player country pitch argptr r8 r16 w8 w16 guest near same far local_far push_word pop_dx'),
 (geometry,'ball_holder_is_side0 in_own_half c2996 c2c54 direction_in_dx c2be5 c2974 rec8 cbw cwd imul'),
 (entrypoints,'random_n random_core rng_core')) for name in names.split()}
BODY_MUTANTS={ROOT:26,ZONE:28,HOLDER:30,HALF:32,RANDOM:34}

def exercise(cls,case,*,root=ROOT,tapped=True,listener=True,pause=None,failure=None,variant=None,mutant=0,direct=False,snapshot=None,mutations=False,clobber_sent=False,controlled=False,profile=False):
 rng=random.Random(case);m=cls(bytes(0x110000),0x823,mutant=mutant) if cls is PortMachine else cls(bytes(0x110000),0x823)
 mem=m.port_memory();ds=m.DS*16;log=[];calls={};visits=[];done=[];mode=case%16
 state=dict(writes={},record_mutations=0,seed_mutations=0,frame_mutations=0,sent_clobbers=0,armed=False)
 scope=dict(active=False,owned={},outside=0);captured=[]
 def put(a,v,n=1):m._memory[a:a+n]=(v&((1<<(8*n))-1)).to_bytes(n,'little')
 def finish(f):
  if f.entry.address==root:scope['active']=False
  if direct:done.append((f.entry.address,f.value))
 for ad,original in ENTRIES.items():
  v=variant if ad==root else None;e=original
  if controlled and ad!=root:
   def boundary(mem,v,ad=ad,original=original):
    packet=args(mem,original.pop//2);ret=m.frames[-1].waiting.ret_to;log.append(('call',ad,packet,ret))
    value=0xa700
    if ad==HOLDER:value=0xb800|(case%2)
    if ad=='1771:3216':value=0xc900|int(mode in (2,3) or (mode==4 and (packet[0]%2==0 or ret=='0791:48E2')))
    if ad==ZONE:value=0xda00|int(mode not in (0,5))
    if ad==HALF:value=0xeb00|int(mode==6)
    if ad=='0791:278A':value=(100 if packet[-1]==5 else (200 if mode%2 else 50))
    if ad==RANDOM:value=[0,1,127,128,255,0xffff][case%6]
    if ad=='0791:2BE5':value=0xdc00|([1,255,0,2][case%4])
    mem.set_reg('ax',value);mem.set_reg('dx',value^0x1234)
   e=Entry(ad,original.ret,boundary,'controlled '+ad,original.long,original.stub,original.return_stack_delta);v='T17-controlled'
  if cls is Oracle:
   def runner(machine,e=e,v=v):
    calls[e.address]=calls.get(e.address,0)+1
    if e.address==root:scope['active']=True
    PortFrame(machine,mem,e,v).start()
  else:
   runner=BridgeRunner(e,v,mem,calls)
  m.port(ad,runner)
 seg=0x4000;off=[0x100,0xfff0,0xffff,rng.randrange(65536)][case%4];rec=seg*16+off
 parent=[0x1800,0xfff8,0xfffa,0xfffb,0xffff][case%5];ss=0x20000;stack=[0x100,0,2,8,16,0xffe0,0xfffe][case%7]
 if snapshot is None:
  # All arrays/pointers valid, with unrelated memory initialized deterministically.
  for reg in ['eax','ebx','ecx','edx','esi','edi','ebp','eflags']:m.set_reg(reg,rng.randrange(1<<32))
  put(ds+0xa917,0xff90 if case%3==0 else 0x100,2);put(ds+0xa919,0x6000,2)
  put(ds+0xa91b,0xfff0 if case%3==0 else 0x100,2);put(ds+0xa91d,0x7000,2)
  put(ds+0x9b34,0,2);put(ds+0x9b36,1,2);put(ds+0x668,0);put(ds+0x669,11)
  poff=int.from_bytes(m._memory[ds+0xa91b:ds+0xa91d],'little')
  coff=int.from_bytes(m._memory[ds+0xa917:ds+0xa919],'little')
  for side in (0,1):
   c=0x60000+((coff+0xbf*side)&65535)
   for slot in range(2,12):put(c+(slot-1)*2,slot+side*16,2)
  for player in range(64):
   p=0x70000+((poff+20*player)&65535)
   m._memory[p:p+20]=bytes(20)
   for k,v in [(6,1),(7,2),(8,40 if mode%2 else 10),(9,60),(10,30),(14,10),(15,0)]:put(p+k,v)
  for slot in range(1,24):
   p=ds+0x80e8+0x16*slot
   for k,v,n in [(0,0,2),(6,slot,1),(13,slot if slot<12 else slot+5,2),(18,9,1)]:put(p+k,v,n)
  pos=[0,0x7f80,0x807f,0xff01,0x0100,0x8080,0x7f7f][(case//16)%7]
  for k,v,n in [(0,pos,2),(6,3,1),(9,0,2),(13,3,2),(18,9 if mode%3 else 1,1),(19,0,1)]:put(rec+k,v,n)
  put(ds+0x7bf,[0,1,255,127,128][case%5])
  put(ds+0x830b,[0,11,12,255][case%4]);put(ds+0x8319,[0,1,127,128,255][case%5]);put(ds+0x831b,[0,1,127,32768,65535][(case//5)%5],2)
  put(ds+0x7920,255);put(ds+0x7921,1)
  side=int(m._memory[ds+0x830b]<12);markoff=0x9a3e+(side==0)*0x28+2*((3-m._memory[ds+0x668+(side==0)])&65535)
  mark=0 if mode in (0,1,2,4,5,7,9,11,13,15) else (3+(16 if side else 0) if mode!=8 else 999)
  put(ds+(markoff&65535),mark,2)
  if controlled:
   # Both possible holder flags must select the same planned branch; the ABI
   # double can intentionally disagree with the real DS:830B fixture byte.
   for side_flag in (0,1):
    at=0x9a3e+(side_flag==0)*0x28+2*((3-m._memory[ds+0x668+(side_flag==0)])&65535)
    selected_mark=0 if mode in (0,1,2,4,5,7,9,11,13,15) else (999 if mode==8 else 3+(16 if side_flag else 0))
    put(ds+(at&65535),selected_mark,2)
  # Some opponents are in their own half, others outside; source uses signed coordinates.
  if mode in (6,10):
   for slot in range(1,24):put(ds+0x80e8+0x16*slot+1,255 if slot<12 else 1)
  seedoff=[0x100,0xffff,0xfffe,rng.randrange(65536)][case%4];seedseg=0x8000
  if mode==14 and root==RANDOM:seedoff=(stack-20)&65535;seedseg=0x2000
  put(ds+0xa978,seedoff,2);put(ds+0xa97a,seedseg,2);put(seedseg*16+seedoff,[0,1,65535,rng.randrange(65536)][case%4],2)
  m.set_reg('ss',0x2000);m.set_reg('sp',stack);m.set_reg('cs',m.seg(0x791));m.set_reg('eip',int(root[5:],16))
  if root==ROOT:
   occupied={ss+((stack+i)&65535) for i in range(-128,6)}
   parent_bytes={ss+((parent+i)&65535)+j for i in (-4,-2,6,8) for j in (0,1)}
   if occupied & parent_bytes:parent=0x1800
  if root in (ROOT,HOLDER):
   put(ss+stack,0x300,2);m.set_reg('cs',m.seg(0x791));end=m.lin('0791:0300')
   if root==ROOT:
    put(ss+((stack+2)&65535),parent,2)
    put(ss+((parent+8)&65535),seg,2);put(ss+((parent+6)&65535),off,2)
  else:
   words=[seg,off] if root==HALF else ([pos,seg,off] if root==ZONE else [[0,1,2,5,32767,32768,65535][(case//4)%7]])
   end=m.far_call(root,words,'000E:0300',0x2000,stack)
   # far_call accepts desired entry SP; runtime.args reads one contiguous block.
   actual=list(reversed(words));at=ss+((stack+4)&65535)
   for i,x in enumerate(actual):put(at+2*i,x,2)
 else:
  memory,regs,ent=snapshot;m._memory[:]=memory;m._registers.clear();m._registers.update(regs);stack,far=ent
  ss=(regs['ss']&65535)*16;ip=int.from_bytes(memory[ss+stack:ss+stack+2],'little')
  cs=int.from_bytes(memory[ss+((stack+2)&65535):ss+((stack+2)&65535)+2],'little') if far else regs['cs']&65535
  end=cs*16+ip
 class Tap:
  def site_enter(self,*x,**kw):log.append(('se',x,kw))
  def site_leave(self,*x,**kw):log.append(('sl',x,kw))
  def listen_enter(self,*x):log.append(('le',x));return len(log)
  def listen_leave(self,x):log.append(('ll',x))
 if tapped:
  def io(kind,x,v):
   log.append(('io',kind,x,bytes(v) if isinstance(v,(bytes,bytearray)) else v))
   if failure=='reg:'+str(x) and kind=='g':raise ValueError('marking register refused')
   if clobber_sent and (m._registers['eip']&65535) in [int(s[5:],16) for s in RETURNS]:
    if kind=='g' and x=='ax':state['armed']=True
    elif kind=='s' and x=='sp' and state['armed']:
     m._registers['eax']=(m._registers['eax']&0xffff0000)|0xee00;state['sent_clobbers']+=1;state['armed']=False
  m.io_tap=io;m.site_tap=m.listen_tap=Tap()
 if listener:
  def listen(a,n,v):
   pc=m.pc();log.append(('w',a,n,v,pc))
   for site in WRITE_SITES:
    if pc==m.lin(site):state['writes'][site]=state['writes'].get(site,0)+1
   if failure=='write' or any(failure=='write:'+s and pc==m.lin(s) for s in WRITE_SITES):raise ValueError('marking write refused')
   if mutations and pc==m.lin('214B:069F'):
    put(ds+0xa978,0xffff,2);put(ds+0xa97a,0x8100,2);put(a,0xdead,2);state['seed_mutations']+=1
    m._registers['eflags']^=0x400
   if mutations and pc==m.lin('0791:4445'):
    put(rec+9,0x7f7f,2);state['record_mutations']+=1
  m.on_write(0,0x10ffff,listen)
 for site in SITES:
  def handler(replay,site=site):
   if site==root:scope['active']=True
   visits.append((site,replay));log.append(('state',site,hashlib.sha256(m._memory).hexdigest(),dict(m._registers)))
   log.append(('waiting',site,[(f.entry.address,f.waiting.target,tuple(f.waiting.args),f.waiting.ret_to,f.waiting.far,f.waiting.caller_pops) for f in m.frames if f.waiting is not None]))
   if failure==site or failure=='callee:'+site:raise ValueError('marking site refused')
   if mutations and site in RETURNS and snapshot is None:
    if root==ROOT:put(ss+((parent+8)&65535),0x9000,2)
    elif root==ZONE:put(ss+((stack-4)&65535),127)
    state['frame_mutations']+=1
   if pause==site and sum(s==site for s,_ in visits)==1:m.stop('pause')
  m.at(site,handler)
 def profiler(frame,event,arg):
  if event=='call' and frame.f_code in OWNED:
   if scope['active']:scope['owned'][frame.f_code.co_name]=scope['owned'].get(frame.f_code.co_name,0)+1
   else:scope['outside']+=1
 oldprof=sys.getprofile();error=suspended=None
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
  if profile:
   positioning.pitch(mem,0)  # Same shared helper outside the completed subtree.
  sys.setprofile(oldprof)
 m.io_tap=None
 result=dict(memory=hashlib.sha256(m._memory).hexdigest(),regs=dict(m._registers),log=log,calls=calls,visits=visits,done=done,error=error,suspended=suspended,state=state,entries=list(mem._entries),frames=[f.describe() for f in m.frames],no_replay_at=m.no_replay_at,running=m.running)
 return result,getattr(getattr(m,'_core',None),'native_calls',{}),scope

class MarkingTests(unittest.TestCase):
 def test_individual_and_integrated_default(self):
  for root in NEW:
   for case in range(32):
    with self.subTest(root=root,case=case):
     opts=dict(root=root,pause=SITES[case%len(SITES)],direct=case%3==0,mutations=case%5==0,profile=True)
     p,_,ps=exercise(Oracle,case,**opts);r,n,rs=exercise(PortMachine,case,**opts)
     self.assertIsNone(p['error'],p['error']);self.assertEqual(p,r);self.assertEqual(n.get(root),1)
     self.assertTrue(ps['owned']);self.assertFalse(rs['owned'],rs);self.assertGreater(rs['outside'],0)
 def test_scoped_controls_and_errors(self):
  for root,mutant in [(HOLDER,31),(HALF,33),(RANDOM,35)]:
   p,_,_=exercise(Oracle,1,root=root);r,_,_=exercise(PortMachine,1,root=root,mutant=mutant)
   self.assertNotEqual(p,r)
  for root in NEW:
   for failure in [root,'write','reg:ss']+(['reg:ax'] if root!=RANDOM else ['reg:eflags']):
    p,_,_=exercise(Oracle,1,root=root,failure=failure);r,_,_=exercise(PortMachine,1,root=root,failure=failure)
    self.assertIsNotNone(p['error']);self.assertEqual(p,r)
  for i,site in enumerate(RETURNS):
   root=ZONE if site=='0791:4493' else ROOT;reached=False
   for case in range(16):
    p,_,_=exercise(Oracle,case,root=root,controlled=True)
    if site not in {s for s,_ in p['visits']}:continue
    r,_,_=exercise(PortMachine,case,root=root,controlled=True,mutant=36+i)
    self.assertIsNone(p['error']);self.assertNotEqual(p,r);reached=True;break
   self.assertTrue(reached,site)
 def test_controlled_callers(self):
  for root in (ROOT,ZONE):
   for case in range(32):
    with self.subTest(root=root,case=case):
     opts=dict(root=root,controlled=True,clobber_sent=True,mutations=True,pause=SITES[case%len(SITES)])
     p,_,_=exercise(Oracle,case,**opts);r,_,_=exercise(PortMachine,case,**opts)
     self.assertIsNone(p['error'],p['error']);self.assertEqual(p,r)
 def test_variants_and_body_controls(self):
  for root in NEW:
   for variant in ['identity','own-half-zero']:
    p,_,_=exercise(Oracle,1,root=root,variant=variant);r,n,scope=exercise(PortMachine,1,root=root,variant=variant,profile=True)
    self.assertEqual(p,r);self.assertNotIn(root,n);self.assertTrue(scope['owned'])
   p,_,_=exercise(Oracle,1,root=root);r,_,_=exercise(PortMachine,1,root=root,mutant=BODY_MUTANTS[root]);self.assertNotEqual(p,r)
if __name__=='__main__':unittest.main()
