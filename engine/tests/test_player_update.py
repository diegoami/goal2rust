"""T14 immediate/captured-linear caller, controlled registered ABI callees and SENT AX."""
import hashlib,random,unittest
from original_match.port import Entry,load
from original_match.port.motion import HANDLERS
from original_match.port.runtime import args
from original_match.port.engine import PortMachine as Oracle
from original_match.port.guest import PortFrame
from goal2rust.machine import PortMachine,BridgeRunner
ROOT='0791:8AE9';HANDLER_RET=tuple(v[1] for v in HANDLERS.values());STATES=tuple(HANDLERS)+(0,4,12,255)
TARGETS=tuple(v[0] for v in HANDLERS.values())+('0791:8889','0791:2CEC','0791:2AD4','0791:869F','0791:8537')
RETURNS=HANDLER_RET+('0791:8BB7','0791:8BED','0791:8C1D','0791:8C26','0791:8C35');SITES=(ROOT,)+TARGETS+RETURNS
WRITE_SITES=tuple('0791:'+x for x in ['8AE9','8BCC','8C04','8C29','8C54','8C5D'])
ENTRIES={a:e for reg,_ in load(['all']) for a,e in reg.entries.items() if a in (ROOT,)+TARGETS};assert len(ENTRIES)==17

def exercise(cls,case,*,tapped=True,listener=True,pause=None,failure=None,variant=None,mutant=0,direct=False,snapshot=None,mutations=False,clobber_sent=False):
 rng=random.Random(case);m=cls(bytes(range(256))*(0x110000//256),0x823,mutant=mutant) if cls is PortMachine else cls(bytes(range(256))*(0x110000//256),0x823)
 mem=m.port_memory();ds=m.DS*16;log=[];calls={};visits=[];done=[];mode=(case//len(STATES))%8;state=dict(writes={},arg_code_mutations=0,bp_mutations=0,kept_mutations=0,play_mutations=0,fatigue_mutations=0,state_mutations=0,sent_clobbers=0,armed=False)
 def put(a,v,n=1):m._memory[a:a+n]=(v&((1<<(8*n))-1)).to_bytes(n,'little')
 for ad,original in ENTRIES.items():
  if ad==ROOT:e=original;v=variant
  else:
   def boundary(mem,v,ad=ad,original=original):
    packet=args(mem,original.pop//2);log.append(('call',ad,packet,m.frames[-1].waiting.ret_to))
    if failure=='callee:'+ad:raise ValueError('player-update callee refused')
    value=(case*37+int(ad[-4:],16))&65535
    if ad=='0791:2CEC':value=(value&0xff00)|int(mode!=2)
    if ad=='0791:2AD4':value=0xb301
    if ad=='0791:869F':value=0xc47f
    if ad=='0791:8537':value=0xd500|(case&255)
    for reg,x in [('ax',value),('dx',value^0x1234),('di',value^0xdead),('es',0x5000),('eflags',(case*0x1234567)&0xffffffff)]:mem.set_reg(reg,x)
   e=Entry(ad,original.ret,boundary,'controlled '+ad,original.long,original.stub,original.return_stack_delta);v='T14-controlled-boundary'
  if cls is Oracle:
   def runner(machine,e=e,v=v):calls[e.address]=calls.get(e.address,0)+1;PortFrame(machine,mem,e,v).start()
  else:runner=BridgeRunner(e,v,mem,calls)
  m.port(ad,runner)
 if snapshot is None:
  seg=0x4000;off=[0,0xfff0,0xffff,rng.randrange(65536)][case%4];rec=seg*16+off
  idx=[0,1,32767,65535][case%4];put(rec+13,idx,2);put(rec+0x12,STATES[case%len(STATES)]);put(rec+0xf,[0,4,5,255][case%4]);put(rec+6,3)
  put(rec+0x14,[0,179,180,181,65535][(case//3)%5],2)
  poff=[0,0xfffe,0xffff,rng.randrange(65536)][case%4];pseg=0x5000;put(ds+0xa91b,poff,2);put(ds+0xa91d,pseg,2);code=pseg*16+((poff+((idx*20)&65535))&65535)
  put(code+0xe,[0,1,2,127,128,255][case%6]);put(ds+0x8302,int(mode!=0));put(ds+0x830d,4 if mode==1 else 3);put(ds+0x830b,3 if mode==6 else 2);put(ds+0x8303,int(mode==4));put(ds+0x830c,0);put(ds+0x8325,(case//5)%2)
  for reg in ['eax','ebx','ecx','edx','esi','edi','ebp','eflags']:m.set_reg(reg,rng.randrange(1<<32))
  sp=[0,2,8,16,0x100,0xfffa,0xfffe][case%7];end=m.far_call(ROOT,[seg,off],'000E:0300',0x3000,sp)
  # Source record() uses farptr at one wrapped SS base, second word linear+2.
  at=0x30000+((sp+4)&65535);put(at,off,2);put(at+2,seg,2)
 else:
  memory,regs,ent=snapshot;m._memory[:]=memory;m._registers.clear();m._registers.update(regs);sp,far=ent;assert far
  ss=(regs['ss']&65535)*16;ip=int.from_bytes(memory[ss+sp:ss+sp+2],'little');cs=int.from_bytes(memory[ss+((sp+2)&65535):ss+((sp+2)&65535)+2],'little');end=cs*16+ip
  at=ss+((sp+4)&65535);off=int.from_bytes(memory[at:at+2],'little');seg=int.from_bytes(memory[at+2:at+4],'little');rec=seg*16+off
  idx=int.from_bytes(memory[rec+13:rec+15],'little');poff=int.from_bytes(memory[ds+0xa91b:ds+0xa91d],'little');pseg=int.from_bytes(memory[ds+0xa91d:ds+0xa91f],'little');code=pseg*16+((poff+((idx*20)&65535))&65535)
 class Tap:
  def site_enter(self,*x,**kw):log.append(('se',x,kw))
  def site_leave(self,*x,**kw):log.append(('sl',x,kw))
  def listen_enter(self,*x):log.append(('le',x));return len(log)
  def listen_leave(self,x):log.append(('ll',x))
 if tapped:
  def io(kind,x,v):
   log.append(('io',kind,x,bytes(v) if isinstance(v,(bytes,bytearray)) else v));ip=m._registers['eip']&65535
   if mutations and ip==0x8ae9 and kind=='s' and x=='ax' and not state['state_mutations']:
    put(rec+0x12,12);put(ds+0xa91b,0x1234,2);put(ds+0xa91d,0x6000,2);state['state_mutations']+=1
   if clobber_sent and ip in [0x8bed,0x8c1d,0x8c26]:
    if kind=='g' and x=='ax':state['armed']=True
    elif kind=='s' and x=='sp' and state['armed']:
     m._registers['eax']=(m._registers['eax']&0xffff0000)|0xee00;state['armed']=False;state['sent_clobbers']+=1
  m.io_tap=io;m.site_tap=m.listen_tap=Tap()
 if listener:
  def write(a,n,v):
   pc=m.pc();log.append(('w',a,n,v,pc))
   for site in WRITE_SITES:
    if pc==m.lin(site):state['writes'][site]=state['writes'].get(site,0)+1
   if mutations:
    if pc==m.lin('0791:8C04'):put(ds+0x8303,0 if mode==4 else 255);state['kept_mutations']+=1
    if pc==m.lin('0791:8BCC') and case%2==0:put(ds+0x8302,1);state['play_mutations']+=1
    if pc==m.lin('0791:8C54'):put(rec+0x14,0x7777,2);m._registers['eax']^=0xabcd;state['fatigue_mutations']+=1
   if failure=='write' or any(failure=='write:'+site and pc==m.lin(site) for site in WRITE_SITES):raise ValueError('player-update write refused')
  m.on_write(0,0x10ffff,write)
 for site in SITES:
  def handler(replay,site=site):
   visits.append((site,replay));log.append(('state',site,hashlib.sha256(m._memory).hexdigest(),dict(m._registers)))
   log.append(('waiting',site,[(f.entry.address,f.waiting.target,tuple(f.waiting.args),f.waiting.ret_to,f.waiting.far,f.waiting.caller_pops) for f in m.frames if f.waiting is not None]))
   if failure==site:raise ValueError('player-update site refused')
   if mutations and site in HANDLER_RET+('0791:8BB7',):
    at=(m.reg('ss')*16)+((sp+4)&65535);put(at,0x100,2);put(at+2,0x6000,2);put(ds+0xa91b,0x2345,2);put(ds+0xa91d,0x7000,2);state['arg_code_mutations']+=1
    if site in HANDLER_RET:m.set_reg('bp',0xbeef);state['bp_mutations']+=1
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

class PlayerUpdateTests(unittest.TestCase):
 def test_native_caller(self):
  p,_=exercise(Oracle,1);r,n=exercise(PortMachine,1);self.assertIsNone(p['error']);self.assertEqual(p,r);self.assertEqual(n.get(ROOT),1)
 def test_positive_dispatch_and_observers(self):
  visits=set();writes=set();called=set();values=set()
  for case in range(240):
   opts=dict(tapped=case%2==0,pause=SITES[case%len(SITES)],mutations=case%7==0,clobber_sent=case%5==0,direct=case%3==0)
   with self.subTest(case=case):
    p,_=exercise(Oracle,case,**opts);r,_=exercise(PortMachine,case,**opts);self.assertIsNone(p['error']);self.assertEqual(p,r);visits.update(s for s,_ in p['visits']);writes.update(p['state']['writes']);called.update(p['calls']);values.update(x[1] for x in p['done'])
  self.assertTrue(set(RETURNS)<=visits,set(RETURNS)-visits);self.assertTrue(set(TARGETS)<=called,set(TARGETS)-called);self.assertTrue(set(WRITE_SITES)<=writes,set(WRITE_SITES)-writes);self.assertEqual(values,{None,0})
 def test_errors_and_variants(self):
  for failure in ['write',ROOT,'0791:8BB7','0791:8C26','callee:0791:8537']:
   for case in [1,4,63,83,113]:
    with self.subTest(case=case,failure=failure):self.assertEqual(exercise(Oracle,case,failure=failure)[0],exercise(PortMachine,case,failure=failure)[0])
  for variant in ['no-draw','nondefault-identity']:
   p,_=exercise(Oracle,65,variant=variant);r,n=exercise(PortMachine,65,variant=variant);self.assertEqual(p,r);self.assertNotIn(ROOT,n)
if __name__=='__main__':unittest.main()
