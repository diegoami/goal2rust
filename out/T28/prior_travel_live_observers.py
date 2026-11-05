"""T21 captured/register/stack/flag live-alias matrix;1280 comparisons."""
import argparse,hashlib,json,os,sys,time
from pathlib import Path
import evidence as e
sys.path.insert(0,str(e.BASE/'engine/tests'))
from test_travel import *
SCENARIOS=('cached-sum-live-scale','captured-SENT-live-DX','live-record-SS','callee-registers','captured-multiply-inputs','live-final-flags','cached-stack-SS','captured-record-live-scale')
OLD_AT={c:c.at for c in (Oracle,PortMachine)};OLD_WRITE={c:c.on_write for c in (Oracle,PortMachine)};ctx={}
def put(m,a,v,n=1):m._memory[a:a+n]=(v&((1<<(8*n))-1)).to_bytes(n,'little')
def word(m,a):return int.from_bytes(m._memory[a:a+2],'little')
def hit(name):ctx['hits'][name]=ctx['hits'].get(name,0)+1
def at(m,site,fn):
 def wrapped(replay):
  fn(replay)
  if not ctx['enabled']:return
  r=m._registers;ss=r['ss']*16;sp=r['esp']&65535
  if site==ctx['root']:
   ctx.update(ss=ss,sp=sp)
   if site==ROOT:
    base=ss+((sp+4)&65535);ctx['argbase']=base;ctx['record']=word(m,base+2)*16+word(m,base)
  if ctx['scenario']=='captured-SENT-live-DX' and site=='0791:8396':ctx['returned']=True
  if ctx['scenario']=='callee-registers' and site=='23E4:0279':
   values=[(65535,65535,65535,65535),(32768,32768,1,1),(1,32767,1,1),(0x1234,0x5678,0xabcd,0xef01)][ctx['case']%4]
   for reg,value in zip(['eax','edx','ebx','ecx'],values):r[reg]=(r[reg]&0xffff0000)|value
   hit('live-register-arguments')
 return OLD_AT[type(m)](m,site,wrapped)
def on_write(m,lo,hi,fn):
 old_io=m.io_tap
 def io(kind,name,value):
  if old_io:old_io(kind,name,value)
  if not ctx['enabled']:return
  r=m._registers;scenario=ctx['scenario']
  if ctx.get('restore_ss'):
   if scenario=='live-record-SS' and kind=='s' and name=='dx' and (r['eip']&65535)==0x835f:
    r['ss']=ctx['ss']//16;ctx['restore_ss']=False;hit('restore-SS-before-guest')
   elif scenario=='cached-stack-SS' and kind=='s' and name=='sp' and value==((ctx['sp']+ENTRIES[ctx['root']].return_stack_delta)&65535):
    r['ss']=ctx['ss']//16;ctx['restore_ss']=False;hit('restore-SS-before-return')
  if scenario=='cached-sum-live-scale' and kind=='s' and name=='bx' and not ctx.get('changed'):
   p=ctx['record'];put(m,p+6,0,2);put(m,p+8,0,2);put(m,p+10,3,2);r['ecx']=(r['ecx']&0xffff0000)|0x8001;ctx['changed']=True;hit('cached-sum-live-CX-and-scale')
  if scenario=='captured-record-live-scale' and kind=='s' and name=='cx' and not ctx.get('changed'):
   base=ctx['argbase'];put(m,base,0x900,2);put(m,base+2,0x9300,2);put(m,0x93000+0x90a,0x7777,2);put(m,ctx['record']+10,9,2);ctx['changed']=True;hit('captured-record-live-scale')
  if scenario=='captured-SENT-live-DX' and ctx.get('returned') and not ctx.get('changed'):
   if kind=='g' and name=='ax':ctx['armed']=True
   elif kind=='s' and name=='sp' and ctx.get('armed'):
    r['eax']=(r['eax']&0xffff0000)|0xee00;r['edx']=(r['edx']&0xffff0000)|0x5a5a;ctx['changed']=True;hit('captured-SENT-versus-live-AX-DX')
  if scenario=='live-final-flags' and kind=='s' and name=='di' and not ctx.get('changed'):
   r['eflags']^=0xcd5;ctx['changed']=True;hit('live-flags-after-scratch-before-flags-store')
 m.io_tap=io
 def wrapped(a,n,v):
  fn(a,n,v)
  if not ctx['enabled']:return
  r=m._registers;scenario=ctx['scenario']
  if scenario=='live-record-SS' and m.pc()==m.lin('0791:835F') and not ctx.get('changed'):
   newss=0xa0000;m._memory[newss:newss+65538]=bytes(m._memory[ctx['ss']:ctx['ss']+65538]);base=newss+((ctx['sp']+4)&65535);put(m,base,0x900,2);put(m,base+2,0x9200,2)
   for k,value in [(6,65535),(8,1),(10,19)]:put(m,0x92000+0x900+k,value,2)
   r['ss']=0xa000;ctx['restore_ss']=True;ctx['changed']=True;hit('live-SS-after-prologue-before-record')
  if scenario=='captured-multiply-inputs' and m.pc()==m.lin('214B:0000'):
   for reg in ['eax','edx','ebx','ecx']:r[reg]=(r[reg]&0xffff0000)|0x8888
   r['eflags']^=0x400;hit('captured-four-inputs-before-stack-flush')
  if scenario=='cached-stack-SS' and m.pc()==m.lin('214B:0000'):
   assert ctx['ss']<=a<a+n<=ctx['ss']+65538
   if not ctx.get('changed'):
    newss=0xa0000;m._memory[newss:newss+65538]=bytes(m._memory[ctx['ss']:ctx['ss']+65538]);r['ss']=0xa000;ctx['restore_ss']=True;ctx['changed']=True;hit('cached-stack-SS-at-first-flush')
   else:hit('later-write-retains-cached-SS')
 return OLD_WRITE[type(m)](m,lo,hi,wrapped)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);a=ap.parse_args();assert not Path(a.out).exists();e.verify();before=e.hashes();e.deny_original();rows={};start=time.monotonic()
 for cls in (Oracle,PortMachine):cls.at=at;cls.on_write=on_write
 try:
  for scenario in SCENARIOS:
   row=rows[scenario]=dict(comparisons=0,hits={},effect_witnesses=0)
   root='23E4:0279' if scenario in ('captured-multiply-inputs','live-final-flags','cached-stack-SS') else ROOT
   for case in range(160):
    opts=dict(root=root)
    ctx.clear();ctx.update(enabled=True,scenario=scenario,root=root,case=case,hits={});p,_,_=exercise(Oracle,case,**opts);ph=dict(ctx['hits'])
    ctx.clear();ctx.update(enabled=True,scenario=scenario,root=root,case=case,hits={});r,_,_=exercise(PortMachine,case,**opts);rh=dict(ctx['hits'])
    assert p['error'] is None and p==r and ph==rh,(scenario,case,p['error'],r['error'],[k for k in p if p[k]!=r[k]],ph,rh)
    ctx['enabled']=False;base,_,_=exercise(Oracle,case,**opts);row['comparisons']+=1;row['effect_witnesses']+=p!=base
    if scenario=='captured-multiply-inputs':assert all(p['regs'][reg]==base['regs'][reg] for reg in ['eax','edx','ebx','ecx','esi','edi'])
    if scenario=='live-final-flags':assert (p['regs']['eflags']&0x8d5)==(base['regs']['eflags']&0x8d5)
    for k,v in ph.items():row['hits'][k]=row['hits'].get(k,0)+v
   assert row['hits'] and all(row['hits'].values()) and row['effect_witnesses']>0,(scenario,row)
   print(scenario,row,flush=True)
 finally:
  for cls in (Oracle,PortMachine):cls.at=OLD_AT[cls];cls.on_write=OLD_WRITE[cls]
 e.write(a.out,dict(pass_all=True,comparisons=1280,scenarios=rows,pid=os.getpid(),pgid=os.getpgrp(),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),wall_s=time.monotonic()-start),before)
if __name__=='__main__':main()
