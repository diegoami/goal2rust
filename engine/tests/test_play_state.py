"""T13 complete play-state caller; controlled registered external ABI boundaries."""
import hashlib,random,unittest
from original_match.port import Entry,load
from original_match.port.runtime import args
from original_match.port.engine import PortMachine as Oracle
from original_match.port.guest import PortFrame
from goal2rust.machine import PortMachine,BridgeRunner
ROOT='0791:57AC';PROBES=tuple('0791:'+x for x in ['56D9','5049','533B','5565'])
TARGETS=PROBES+tuple('0791:'+x for x in ['045D','4B64','2BB1','2B51','5729','2974','44C1','4A28','474D','6188'])
RETURNS=tuple('0791:'+x for x in ['57B6','57BE','57C6','57CE','57DE','57F2','582A','5857','585F','586C','5885','58A9','58C2','58CB','58DB'])
SITES=(ROOT,)+TARGETS+RETURNS;WRITE_SITES=('0791:5809','0791:58B3')
ENTRIES={a:e for reg,_ in load(['all']) for a,e in reg.entries.items() if a in (ROOT,)+TARGETS};assert len(ENTRIES)==15

def exercise(cls,case,*,tapped=True,listener=True,pause=None,failure=None,variant=None,mutant=0,direct=False,snapshot=None,mutations=False,return_mutations=False):
 rng=random.Random(case);m=cls(bytes(range(256))*(0x110000//256),0x823,mutant=mutant) if cls is PortMachine else cls(bytes(range(256))*(0x110000//256),0x823)
 mem=m.port_memory();ds=m.DS*16;log=[];calls={};visits=[];done=[];scenario=(case//8)%10;stop=case%8;state=dict(writes={},bp_args_mutations=0,arg_mutations=0,table_mutations=0,play_mutations=0,return_mutations=0,point_mutations=0)
 def put(a,v,n=1):m._memory[a:a+n]=(v&((1<<(8*n))-1)).to_bytes(n,'little')
 for ad,original in ENTRIES.items():
  if ad==ROOT:e=original;v=variant
  else:
   def boundary(mem,v,ad=ad,original=original):
    packet=args(mem,original.pop//2);ret=m.frames[-1].waiting.ret_to;log.append(('call',ad,packet,ret))
    if failure=='callee:'+ad:raise ValueError('play-state callee refused')
    value=(case*37+int(ad[-4:],16))&65535;low=value&255
    if ad in PROBES:low=int(stop<4 and PROBES.index(ad)==stop)
    elif ad=='0791:045D':low=int(scenario==0 and stop==4)
    elif ad=='0791:2BB1':low=1 if scenario in [3,4] else 2
    elif ad=='0791:2B51':low=int(scenario==4)
    elif ad=='0791:5729':low=int(scenario==2)
    elif ad=='0791:2974':low=[0,1,255][case%3]
    elif ad=='0791:44C1':low=int(scenario==7)
    for reg,x in [('ax',(value&0xff00)|low),('dx',value^0x1234),('di',value^0xdead),('es',0x5000),('eflags',(case*0x1234567)&0xffffffff)]:mem.set_reg(reg,x)
   e=Entry(ad,original.ret,boundary,'controlled '+ad,original.long,original.stub,original.return_stack_delta);v='T13-controlled-boundary'
  if cls is Oracle:
   def runner(machine,e=e,v=v):calls[e.address]=calls.get(e.address,0)+1;PortFrame(machine,mem,e,v).start()
  else:runner=BridgeRunner(e,v,mem,calls)
  m.port(ad,runner)
 if snapshot is None:
  seg=0x4000;off=[0,0xfff0,0xffff,rng.randrange(65536)][case%4];slot=3
  for rs,ro,idx in [(seg,off,[0,1,32767,65535][case%4]),(0x6000,0x100,1)]:
   put(rs*16+((ro+6)&65535),slot);put(rs*16+((ro+7)&65535),0xbeef,2);put(rs*16+((ro+13)&65535),idx,2)
   at=0x50000+((0x100+idx*20+6)&65535);put(at,0 if scenario==3 else 1)
  put(ds+0xa91b,0x100,2);put(ds+0xa91d,0x5000,2);put(ds+0x830b,1)
  put(ds+0x8302,int(scenario in [2,6,9]));put(ds+0x8327,5 if scenario==1 else 3);put(ds+0x8300,1,2)
  put(ds+0x8325,int(scenario>=2));put(ds+0x830c,int(scenario in [2,3,4,9]));put(ds+0x82f6,0x2468,2)
  for table in [0x8311,0x830f]:
   match=(scenario==5 and table==0x8311) or(scenario==6 and table==0x830f)
   for index in [-1,0,1]:put(ds+((table+index)&65535),slot if match else slot+1)
  for reg in ['eax','ebx','ecx','edx','esi','edi','ebp','eflags']:m.set_reg(reg,rng.randrange(1<<32))
  sp=[0,2,8,16,0x100,0xfffa,0xfffe][case%7];end=m.far_call(ROOT,[seg,off],'000E:0300',0x3000,sp)
 else:
  memory,regs,ent=snapshot;m._memory[:]=memory;m._registers.clear();m._registers.update(regs);sp,far=ent;assert far
  ss=(regs['ss']&65535)*16;ip=int.from_bytes(memory[ss+sp:ss+sp+2],'little');cs=int.from_bytes(memory[ss+((sp+2)&65535):ss+((sp+2)&65535)+2],'little');end=cs*16+ip
 bp=(sp-2)&65535
 class Tap:
  def site_enter(self,*x,**kw):log.append(('se',x,kw))
  def site_leave(self,*x,**kw):log.append(('sl',x,kw))
  def listen_enter(self,*x):log.append(('le',x));return len(log)
  def listen_leave(self,x):log.append(('ll',x))
 if tapped:m.io_tap=lambda *x:log.append(('io',x));m.site_tap=m.listen_tap=Tap()
 if listener:
  def write(a,n,v):
   pc=m.pc();log.append(('w',a,n,v,pc))
   for site in WRITE_SITES:
    if pc==m.lin(site):state['writes'][site]=state['writes'].get(site,0)+1
   if mutations and pc in [m.lin(x) for x in WRITE_SITES]:put(ds+0x82f6,0xface,2);m._registers['eax']^=0x3456;state['point_mutations']+=1
   if failure=='write' or any(failure=='write:'+site and pc==m.lin(site) for site in WRITE_SITES):raise ValueError('play-state write refused')
  m.on_write(0,0x10ffff,write)
 for site in SITES:
  def handler(replay,site=site):
   visits.append((site,replay));log.append(('state',site,hashlib.sha256(m._memory).hexdigest(),dict(m._registers)))
   log.append(('waiting',site,[(f.entry.address,f.waiting.target,tuple(f.waiting.args),f.waiting.ret_to,f.waiting.far,f.waiting.caller_pops) for f in m.frames if f.waiting is not None]))
   if failure==site:raise ValueError('play-state site refused')
   if mutations and site=='0791:57B6':
    ss=m.reg('ss')*16;other=(bp+0x20)&65535;put(ss+other,0x1234,2);put(ss+((other+6)&65535),0x100,2);put(ss+((other+8)&65535),0x6000,2);m.set_reg('bp',other);state['bp_args_mutations']+=1
   if mutations and site in ['0791:57DE','0791:582A']:
    ss=m.reg('ss')*16;live=m.reg('bp');put(ss+((live+6)&65535),0x100,2);put(ss+((live+8)&65535),0x6000,2);state['arg_mutations']+=1
   if mutations and site=='0791:586C':
    for idx in [-1,0,1]:put(ds+((0x830f+idx)&65535),3)
    state['table_mutations']+=1
   if mutations and site=='0791:58CB':put(ds+0x8302,1);state['play_mutations']+=1
   if return_mutations and site in ['0791:57DE','0791:582A','0791:585F','0791:586C','0791:5885']:
    low=2 if site=='0791:582A' else (1 if site=='0791:585F' else 255 if site in ['0791:586C','0791:5885'] else 0);m.set_reg('ax',0xaa00|low);state['return_mutations']+=1
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

class PlayStateTests(unittest.TestCase):
 def test_native_caller(self):
  p,_=exercise(Oracle,5);r,n=exercise(PortMachine,5);self.assertIsNone(p['error']);self.assertEqual(p,r);self.assertEqual(n.get(ROOT),1)
 def test_positive_all_branches(self):
  visits=set();called=set();writes=set()
  for case in range(160):
   opts=dict(tapped=case%2==0,pause=SITES[case%len(SITES)],mutations=case%5==0,return_mutations=case%7==0,direct=case%11==0)
   with self.subTest(case=case):
    p,_=exercise(Oracle,case,**opts);r,_=exercise(PortMachine,case,**opts);self.assertIsNone(p['error']);self.assertEqual(p,r);visits.update(s for s,_ in p['visits']);called.update(p['calls']);writes.update(p['state']['writes'])
  self.assertTrue(set(RETURNS)<=visits,set(RETURNS)-visits);self.assertTrue(set(TARGETS)<=called,set(TARGETS)-called);self.assertTrue(set(WRITE_SITES)<=writes,set(WRITE_SITES)-writes)
 def test_errors_and_variants(self):
  for failure in ['write',ROOT,'0791:57B6','0791:58CB','callee:0791:4A28']:
   for case in [4,5,12,44,60]:
    with self.subTest(case=case,failure=failure):self.assertEqual(exercise(Oracle,case,failure=failure)[0],exercise(PortMachine,case,failure=failure)[0])
  for variant in ['nearest-not-chasing','nondefault-identity']:
   p,_=exercise(Oracle,44,variant=variant);r,n=exercise(PortMachine,44,variant=variant);self.assertEqual(p,r);self.assertNotIn(ROOT,n)
if __name__=='__main__':unittest.main()
