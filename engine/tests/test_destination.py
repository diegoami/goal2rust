"""T18 complete destination closure; authored state, no private original data."""
import hashlib,json,random,sys,unittest
from pathlib import Path
from original_match.port import Entry,load
from original_match.port.runtime import args
from original_match.port.engine import PortMachine as Oracle
from original_match.port.guest import PortFrame
from original_match.port import positioning,geometry,entrypoints,runtime,ball,pilot
from goal2rust.machine import PortMachine,BridgeRunner
ROOT='0791:4B64'
NEW=('0791:261A','0791:2B7B','0791:2C86','0791:2D10','0791:2D6D','0791:2E36','0791:40BC','0791:42CB','0791:4354','0791:4A28',ROOT,'214B:0D1C','214B:0D56','214B:2031','23E4:08DF')
CALLERS=('0791:40BC','0791:42CB','0791:4354','0791:4A28',ROOT)
LEAVES=tuple(a for a in NEW if a not in CALLERS)
ENTRIES={a:e for reg,_ in load(['all']) for a,e in reg.entries.items()}
TARGETS=('0791:045D','0791:26D7','0791:2996','0791:2B51','0791:2BE5','0791:2C54','0791:47C5','214B:06B1','1771:3216','0791:278A','1771:3A06')
RETURNS=tuple('0791:'+x for x in ['2635','263D']) # real guest returns are appended below
# All41 finite guest return sites, including conditional source expressions.
RETURNS=tuple('0791:'+x for x in ['40E1','40E8','4311','431E','43A7','4392','43BC','442B','4A4F','4A5C','4A77','4A84','4A90','4A9D','4AB5','4AC6','4ACD','4AE1','4AFF','4B1A','4B27','4B74','4B88','4BB2','4BCC','4BF1','4C14','4BF6','4C33','4C59','4C6D','4CCA','4C7B','4C94','4CA8','4CB5','4CD8','4CEB','4D2A','4D30','4D39'])
SITES=NEW+TARGETS+RETURNS
OWNED={getattr(m,n).__code__ for m,names in [(positioning,'update_player_destination update_marking_destination set_destination_from_post position_group argptr rec player r8 r16 w8 w16 guest near same far push_word pop_ax drop_words'),(geometry,'draw_table_byte energy_gate_chance mirror_to_team_frame ball_ahead_of_by ahead_of_ball_by in_own_goal_area direction_in_dx c2be5 c2974 player_byte rec8 rec16 cbw cwd mul imul neg_if_negative sx8'),(entrypoints,'membership test_flags'),(runtime,'min_longint max_longint clamp_byte draw_is_one rng_0688'),(ball,'holder_in_advanced_central_strip local8 mul cbw'),(pilot,'rand')] for n in names.split()}

def exercise(cls,case,*,root=ROOT,tapped=True,listener=True,pause=None,failure=None,variant=None,mutant=0,direct=False,snapshot=None,controlled=False,mutations=False,profile=False):
 rng=random.Random(case);m=cls(bytes(0x110000),0x823,mutant=mutant) if cls is PortMachine else cls(bytes(0x110000),0x823)
 mem=m.port_memory();ds=m.DS*16;log=[];calls={};visits=[];done=[];scope=dict(active=False,owned={},outside=0);state=dict(writes={},mutations=0);mode=case%16
 def put(a,v,n=1):m._memory[a:a+n]=(v&((1<<(8*n))-1)).to_bytes(n,'little')
 selected=set(NEW)|set(json.loads((Path(__file__).resolve().parents[2]/'out/T17/profile-after-v1.json').read_text())['native_calls'])
 for ad in selected:
  original=ENTRIES[ad];entry=original;v=variant if ad==root else None
  if controlled and ad!=root:
   def abi(mem,v,ad=ad,original=original):
    packet=args(mem,original.pop//2);ret=m.frames[-1].waiting.ret_to;log.append(('abi',ad,packet,ret))
    value=0x9800|int(mode%3!=0)
    if ad=='0791:045D':value=0xa700|int((case//8)%3==0)
    if ad=='0791:2B51':value=0xa800|int((case//4)%2!=0)
    if ad=='0791:2B7B':value=0xa900|int((case//8)%2!=0)
    if ad in ('0791:2D10','0791:2E36'):value=0xaa00|int((case//16)%2!=0)
    if ad=='0791:2D6D':value=0xab00|int((case//8)%2!=0)
    if ad=='0791:2BE5':value=0xb800|([255,1,0,128][case%4])
    if ad=='0791:42CB':value=case%5
    if ad=='0791:261A':value=[0,1,127,128,255,65535][case%6]
    if ad=='214B:06B1':value=0 if ret=='0791:4AFF' else [0,1,6,127,128,255,65535][case%7]
    if ad=='0791:26D7':value=0xc900|int((case//2)%2!=0) if ret=='0791:4AC6' else 0xc900|int((case+packet[-1])%3!=0)
    if ad=='0791:47C5':
     parent=packet[0];ss=m._registers['ss']*16;put(ss+((parent-4)&65535),m._memory[ds+0x830b] if case%3==0 else 3,2);put(ss+((parent-2)&65535),0x0102,2)
    for reg,x in [('ax',value),('dx',value^0x1234),('es',0x6000)]:mem.set_reg(reg,x)
    if ad=='23E4:08DF':mem.set_reg('eflags',(m._registers['eflags']&~0x40)|(0x40 if (case//8)%2 else 0))
   entry=Entry(ad,original.ret,abi,'controlled '+ad,original.long,original.stub,original.return_stack_delta);v='T18-controlled'
  if cls is Oracle:
   def runner(machine,entry=entry,v=v):calls[entry.address]=calls.get(entry.address,0)+1;PortFrame(machine,mem,entry,v).start()
  else:runner=BridgeRunner(entry,v,mem,calls)
  m.port(ad,runner)
 seg=0x4000;off=[0x100,0xfff0,0xffff,rng.randrange(65536)][case%4];rec=seg*16+off;sp=[0x100,0,2,8,16,0xffe0,0xfffe][case%7];ss=0x20000
 if snapshot is None:
  for reg in ['eax','ebx','ecx','edx','esi','edi','ebp','eflags']:m.set_reg(reg,rng.randrange(1<<32))
  for k,v,n in [(0xa917,0x100,2),(0xa919,0x6000,2),(0xa91b,0xfff0 if case%3==0 else 0x100,2),(0xa91d,0x7000,2),(0x9b34,0,2),(0x9b36,1,2),(0x668,0,1),(0x669,11,1),(0x8325,mode%2,1),(0x830b,[0,11,12,255][case%4],1),(0x8319,[0,1,127,128,255][case%5],1),(0x831b,[0,1,127,32768,65535][(case//5)%5],2),(0x7920,255,1),(0x7921,1,1),(0x82f7,[0,1,33,35,127,128,255][case%7],1),(0x8437,[0,1,254,255,256,65535][case%6],2)]:put(ds+k,v,n)
  m._memory[ds+0x8337:ds+0x8437]=bytes(range(256))
  for k in range(0x7ba,0x840):put(ds+k,case%5)
  poff=int.from_bytes(m._memory[ds+0xa91b:ds+0xa91d],'little')
  for player in range(64):
   p=0x70000+((poff+20*player)&65535)
   for k,v in [(6,[0,1,2,4,5,11,12,13,255][case%9]),(7,2),(8,10),(9,60),(10,30),(14,[0,1,32,33,127,128,255][case%7]),(15,0)]:put(p+k,v)
  for side in (0,1):
   for slot in range(2,12):put(0x60000+0x100+side*0xbf+(slot-1)*2,slot+side*16,2)
  for slot in range(1,24):
   p=ds+0x80e8+0x16*slot
   for k,v,n in [(0,0,2),(6,slot,1),(13,slot if slot<12 else slot+5,2),(18,9,1)]:put(p+k,v,n)
  pos=[0,0x0101,0x21ff,0xdf01,0x7f80,0x807f,0xffff,0x2304][(case//4)%8]
  for k,v,n in [(0,pos,2),(6,[1,2,3,12,13,22][case%6],1),(9,pos,2),(10,[0,1,127,128,255][case%5],1),(12,[0,1,2,127,128,255][case%6],1),(13,3,2),(18,[9,11,0,1][case%4],1)]:put(rec+k,v,n)
  put(ds+0xa978,[0x100,0xfffe,0xffff,0x200][case%4],2);put(ds+0xa97a,0x8000,2);seedoff=int.from_bytes(m._memory[ds+0xa978:ds+0xa97a],'little');put(0x80000+seedoff,[0,1,65535,0x1234][case%4],2)
  m._memory[m.lin('0791:4B44'):m.lin('0791:4B44')+32]=bytes([255 if mode%2 else 0])*32
  for k in (0x82e3,0x82e9):put(ds+k,[0,1,127,128,255][case%5])
  word=[0,1,127,128,255,32767,32768,65535][case%8]
  words=[seg,off]
  if root in ('0791:2C86','0791:2E36'):words=[pos,seg,off]
  if root in ('0791:2D10','0791:2D6D'):words=[word,seg,off]
  if root=='23E4:08DF':words=[word,seg,off];put(seg*16+((off+(word&255)//8)&65535),255 if mode%2 else 0)
  if root in ('214B:0D1C','214B:0D56'):
   vals=[0,1,65535,32768,32767,rng.randrange(65536)];ahi=vals[case%6];alo=vals[(case//6)%6];bhi=ahi if mode%2 else vals[(case//2)%6];blo=alo if mode%3 else vals[(case//3)%6];words=[ahi,alo,bhi,blo]
  if root=='214B:2031':words=[seg,off,[0,1,127,128,255,0xff80][case%6],[0,1,127,128,255,0x1280][(case//6)%6]];put(rec,word&255)
  if not ENTRIES[root].far:
   put(ss+sp,0x300,2);m.set_reg('ss',0x2000);m.set_reg('sp',sp);m.set_reg('cs',m.seg(0x791));m.set_reg('eip',int(root[5:],16));end=m.lin('0791:0300')
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
   if kind=='g' and failure=='reg:'+str(x):raise ValueError('destination register refused')
  m.io_tap=io;m.site_tap=m.listen_tap=Tap()
 if listener:
  def listen(a,n,v):
   pc=m.pc();state['writes'][pc]=state['writes'].get(pc,0)+1;log.append(('w',a,n,v,pc))
   if failure=='write' or (isinstance(failure,str) and failure.startswith('write:') and pc==m.lin(failure[6:])):raise ValueError('destination write refused')
   if mutations and pc==m.lin('214B:069F'):
    put(ds+0xa978,0xffff,2);put(ds+0xa97a,0x8100,2);m._registers['eflags']^=0x400;state['mutations']+=1
  m.on_write(0,0x10ffff,listen)
 for site in SITES:
  def handler(replay,site=site):
   if site==root:scope['active']=True
   visits.append((site,replay));log.append(('state',site,hashlib.sha256(m._memory).hexdigest(),dict(m._registers)))
   log.append(('waiting',site,[(f.entry.address,f.waiting.target,tuple(f.waiting.args),f.waiting.ret_to) for f in m.frames if f.waiting is not None]))
   if failure==site:raise ValueError('destination site refused')
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

class DestinationTests(unittest.TestCase):
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
   p,_,_=exercise(Oracle,1,root=root);r,_,_=exercise(PortMachine,1,root=root,mutant=49+NEW.index(root));self.assertNotEqual(p,r)
   p,_,_=exercise(Oracle,1,root=root,variant='identity');r,n,scope=exercise(PortMachine,1,root=root,variant='identity',profile=True)
   self.assertEqual(p,r);self.assertNotIn(root,n);self.assertTrue(scope['owned'])
  for i,root in enumerate(LEAVES):
   p,_,_=exercise(Oracle,1,root=root);r,_,_=exercise(PortMachine,1,root=root,mutant=64+i);self.assertNotEqual(p,r)
 def test_individual_guest_return_controls(self):
  inventory=json.loads((Path(__file__).resolve().parents[2]/'out/T18/inventory-v2.json').read_text())
  for i,site in enumerate(inventory['guest_sites']):
   root=site['caller'];ret=site['ret_to'];reached=False
   for case in range(160):
    p,_,_=exercise(Oracle,case,root=root,controlled=True)
    self.assertIsNone(p['error'],(root,ret,case,p['error']))
    if ret not in {s for s,_ in p['visits']}:continue
    r,_,_=exercise(PortMachine,case,root=root,controlled=True,mutant=74+i)
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
