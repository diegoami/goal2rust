"""T12 full sweep caller with registered, explicitly controlled external ABI boundaries."""
import hashlib,random,unittest
from original_match.port import Entry,load
from original_match.port.frame import SITES as ALL_SITES
from original_match.port.runtime import args
from original_match.port.engine import PortMachine as Oracle
from original_match.port.guest import PortFrame
from goal2rust.machine import PortMachine,BridgeRunner
ROOT='0791:9564';CALLS={s:v for s,v in ALL_SITES.items() if 0x9592<=s<=0x96e7};TARGETS=tuple(sorted({x[0] for x in CALLS.values()}));RETURNS=tuple(x[2] for x in CALLS.values());SITES=(ROOT,)+TARGETS+RETURNS
ENTRIES={a:e for reg,_ in load(['all']) for a,e in reg.entries.items() if a in (ROOT,)+TARGETS};assert len(CALLS)==17 and len(ENTRIES)==15
WRITE_SITES=tuple('0791:'+s for s in ['9564','956A','9571','9581','95EE','9620','9623','9670','9677','96AF','96B2','9703'])

def exercise(cls,case,*,tapped=True,listener=True,pause=None,failure=None,variant=None,mutant=0,direct=False,snapshot=None,mutations=False,return_mutations=False):
 rng=random.Random(case);m=cls(bytes(range(256))*(0x110000//256),0x823,mutant=mutant) if cls is PortMachine else cls(bytes(range(256))*(0x110000//256),0x823)
 mem=m.port_memory();ds=m.DS*16;log=[];calls={};visits=[];done=[];state=dict(writes={},keys=0,inner=0,bp_mutations=0,rec_mutations=0,slot_mutations=0,play_mutations=0,return_mutations=0)
 limit=None if case%50==0 or case==499 else 1+case%3
 def put(a,v,n=1):m._memory[a:a+n]=(v&((1<<(8*n))-1)).to_bytes(n,'little')
 for ad,original in ENTRIES.items():
  if ad==ROOT:entry=original;v=variant
  else:
   def boundary(mem,v,ad=ad,original=original):
    packet=args(mem,original.pop//2);ret=m.frames[-1].waiting.ret_to
    log.append(('call',ad,packet,ret))
    if failure=='callee:'+ad:raise ValueError('sweep boundary refused')
    value=(case*37+int(ad[-4:],16))&65535;low=value&255;flags=(case*0x1234567)&0xffffffff
    if ad=='23E4:08DF':
     zf=bool(case&2) if ret=='0791:9597' else case%4==0;flags=(flags&~0x40)|(0x40 if zf else 0)
    elif ad=='0791:2BE5':low=[1,255][case%2]
    elif ad=='0791:2996':low=case%2
    elif ad=='0791:2CEC':low=0 if case%4 in [1,2] else 1
    elif ad=='0791:2E36':low=int(case%5!=2)
    elif ad=='0791:59B3':low=0 if case%7==0 or case==499 else 1
    elif ad=='0791:6188':state['inner']+=1
    elif ad=='0791:2956':low=case%2
    elif ad=='0791:9372':
     state['keys']+=1
     if limit is not None and state['keys']>=limit and not (mutations and case%13==0):mem.wds8(0x9a3e,1,'0791:9356')
    value=(value&0xff00)|low
    for reg,x in [('ax',value),('dx',value^0x1234),('di',value^0xdead),('es',0x5000),('eflags',flags)]:mem.set_reg(reg,x)
   entry=Entry(ad,original.ret,boundary,'controlled '+ad,original.long,original.stub,original.return_stack_delta);v='T12-controlled-boundary'
  if cls is Oracle:
   def runner(machine,e=entry,v=v):calls[e.address]=calls.get(e.address,0)+1;PortFrame(machine,mem,e,v).start()
  else:runner=BridgeRunner(entry,v,mem,calls)
  m.port(ad,runner)
 if snapshot is None:
  put(ds+0x8302,int(case%3!=0));put(ds+0x8303,(case//3)%2);put(ds+0x8327,case%256);put(ds+0x8300,0 if case%11==0 else 255,2)
  put(ds+0x82f6,case%5);put(ds+0x82f7,[0,1,255,128][case%4]);put(ds+0x7920,1);put(ds+0x7921,255)
  put(ds+0x668,0);put(ds+0x669,11);put(ds+0x830b,1+case%22);put(ds+0x9a3e,0);put(ds+0x832a,[1,0,2,3,65535][case%5],2)
  for slot in range(1,23):
   put(ds+0x883+slot,slot);put(ds+0x899+slot,255 if case%11==0 else 0);put(ds+0x899+22+slot,255 if case%11==0 else 0)
   put(ds+0x80e8+slot*22,case%5 if case%9 else (case+1)%5)
  for reg in ['eax','ebx','ecx','edx','esi','edi','ebp','eflags']:m.set_reg(reg,rng.randrange(1<<32))
  sp=[0,2,8,16,0x100,0xfffa,0xfffe][case%7]
  for reg,x in [('ss',0x3000),('sp',sp),('cs',m.seg(0x791)),('eip',0x9564)]:m.set_reg(reg,x)
  put(0x30000+sp,0x200,2);end=m.lin('0791:0200')
 else:
  memory,regs,ent=snapshot;m._memory[:]=memory;m._registers.clear();m._registers.update(regs);sp,far=ent;assert not far
  ss=(regs['ss']&65535)*16;end=(regs['cs']&65535)*16+int.from_bytes(memory[ss+sp:ss+sp+2],'little')
  # Keep real memory/register input; constrain only controlled external key return policy.
  limit=1+case%3
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
   if mutations:
    if pc==m.lin('0791:956A'):m.set_reg('bp',m.reg('bp')^0x4567);state['bp_mutations']+=1
    if pc in [m.lin('0791:9623'),m.lin('0791:96B2')]:
     put(m.reg('ss')*16+((bp-8)&65535),0xcafe,2);state['rec_mutations']+=1
    if pc==m.lin('0791:9677') and case%5==0:put(ds+0x8302,1-(int.from_bytes(m._memory[ds+0x8302:ds+0x8303],'little')!=0));state['play_mutations']+=1
   if failure=='write' or any(failure=='write:'+site and pc==m.lin(site) for site in WRITE_SITES):raise ValueError('sweep write refused')
  m.on_write(0,0x10ffff,write)
 for site in SITES:
  def handler(replay,site=site):
   visits.append((site,replay));log.append(('state',site,hashlib.sha256(m._memory).hexdigest(),dict(m._registers)))
   log.append(('waiting',site,[(f.entry.address,f.waiting.target,tuple(f.waiting.args),f.waiting.ret_to,f.waiting.far,f.waiting.caller_pops) for f in m.frames if f.waiting is not None]))
   if failure==site:raise ValueError('sweep site refused')
   if mutations and site=='0791:96EA' and case%13==0:put(m.reg('ss')*16+((bp-2)&65535),22,2);state['slot_mutations']+=1
   if return_mutations and site in ['0791:95C9','0791:9601','0791:963F','0791:966C','0791:96BE']:
    m.set_reg('ax',0xaa00|([0,1,255][case%3]));state['return_mutations']+=1
   if return_mutations and site in ['0791:9597','0791:9634']:m.set_reg('eflags',m.reg('eflags')^0x40);state['return_mutations']+=1
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

class WatchedSweepTests(unittest.TestCase):
 def test_native_caller(self):
  p,_=exercise(Oracle,1);r,n=exercise(PortMachine,1);self.assertIsNone(p['error']);self.assertEqual(p,r);self.assertEqual(n.get(ROOT),1)
 def test_positive_loop_and_branch_coverage(self):
  visits=set();writes=set();targets=set();outer=False;inner=False
  for case in range(60):
   opts=dict(pause=SITES[case%len(SITES)],direct=case%7==0,mutations=case%5==0,return_mutations=case%4==0,tapped=case%2==0)
   with self.subTest(case=case):
    p,_=exercise(Oracle,case,**opts);r,_=exercise(PortMachine,case,**opts);self.assertIsNone(p['error']);self.assertEqual(p,r)
    visits.update(s for s,_ in p['visits']);writes.update(p['state']['writes']);targets.update(p['calls']);outer|=p['state']['keys']==22;inner|=p['state']['inner']>=22
  self.assertTrue(set(RETURNS)<=visits,set(RETURNS)-visits);self.assertTrue(set(WRITE_SITES)<=writes,set(WRITE_SITES)-writes);self.assertTrue(set(TARGETS)<=targets,set(TARGETS)-targets);self.assertTrue(outer and inner)
 def test_errors_and_variants(self):
  for failure in ['write',ROOT,'0791:9597','0791:96EA','callee:0791:8AE9']:
   for case in [1,2,5,7]:
    with self.subTest(case=case,failure=failure):self.assertEqual(exercise(Oracle,case,failure=failure)[0],exercise(PortMachine,case,failure=failure)[0])
  p,_=exercise(Oracle,5,variant='possession-swapped');r,n=exercise(PortMachine,5,variant='possession-swapped');self.assertEqual(p,r);self.assertNotIn(ROOT,n)
if __name__=='__main__':unittest.main()
