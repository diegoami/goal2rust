"""Eight scoped captured/live probes for T20;1280 source/native comparisons."""
import argparse,hashlib,json,os,sys,time
from pathlib import Path
import evidence as e
sys.path.insert(0,str(e.BASE/'engine/tests'))
from test_chase import *
SCENARIOS=('parent-live','actual-bank','root-cached-local-ss','leaf-args-captured','direction-live','flags-live','split-point-pointer','captured-parent-di')
OLD_AT={c:c.at for c in (Oracle,PortMachine)};OLD_WRITE={c:c.on_write for c in (Oracle,PortMachine)};ctx={}
def put(m,a,v,n=1):m._memory[a:a+n]=(v&((1<<(8*n))-1)).to_bytes(n,'little')
def word(m,a):return int.from_bytes(m._memory[a:a+2],'little')
def hit(name):ctx['hits'][name]=ctx['hits'].get(name,0)+1
def fresh_record(m):
 ss=ctx['ss'];parent=ctx['parent'];old=word(m,ss+((parent+8)&65535))*16+word(m,ss+((parent+6)&65535));new=0x92000+0x900
 m._memory[new:new+24]=bytes(m._memory[old:old+24]);put(m,new,0xe700,2);put(m,new+6,2)
 return 0x9200,0x900
def at(m,site,fn):
 def wrapped(replay):
  fn(replay)
  if not ctx['enabled']:return
  r=m._registers;ss=r['ss']*16;sp=r['esp']&65535
  if site==ctx['root']:
   ctx.update(ss=ss,sp=sp,bp=(sp-2)&65535,ss_reads=0)
   if site==ROOT:ctx['parent']=word(m,ss+((sp+2)&65535))
   else:ctx['argbase']=ss+((sp+4)&65535)
  scenario=ctx['scenario']
  if scenario=='parent-live' and site in ('0791:5740','0791:5751'):
   seg,off=fresh_record(m);parent=ctx['parent'];put(m,ss+((parent+6)&65535),off,2);put(m,ss+((parent+8)&65535),seg,2);hit('fresh-parent-far-pointer')
  target={'actual-bank':'0791:5740','split-point-pointer':'0791:5766','captured-parent-di':'0791:5751'}.get(scenario)
  if site==target:ctx['return_seen']=True
 return OLD_AT[type(m)](m,site,wrapped)
def on_write(m,lo,hi,fn):
 old_io=m.io_tap
 def io(kind,name,value):
  if old_io:old_io(kind,name,value)
  if not ctx['enabled']:return
  r=m._registers;scenario=ctx['scenario']
  if ctx.get('restore_ss') and kind=='s' and name=='sp' and value==((ctx['sp']+ENTRIES[ctx['root']].return_stack_delta)&65535):
   r['ss']=ctx['ss']//16;ctx['restore_ss']=False;hit('restored-return-ss')
  if ctx.get('return_seen') and not ctx.get('resumed'):
   if kind=='g' and name=='ax':ctx['armed']=True
   elif kind=='s' and name=='sp' and ctx.get('armed'):
    ctx['resumed']=True;ctx['ss_reads']=0
    if scenario=='actual-bank':r['eax']=(r['eax']&0xffff0000)|((r['eax']^1)&65535);hit('actual-AX-after-captured-SENT')
  if ctx.get('resumed') and kind=='g' and name=='ss':
   ctx['ss_reads']+=1
   if scenario=='split-point-pointer' and ctx['ss_reads']==4:
    seg,off=fresh_record(m);parent=ctx['parent'];put(m,ctx['ss']+((parent+6)&65535),off,2);put(m,ctx['ss']+((parent+8)&65535),seg,2);hit('captured-point-new-far-pointer')
   if scenario=='captured-parent-di' and ctx['ss_reads']==3:
    seg,off=fresh_record(m);put(m,ctx['ss']+0x3106,off,2);put(m,ctx['ss']+0x3108,seg,2);put(m,ctx['ss']+((ctx['bp']+4)&65535),0x3100,2);hit('captured-parent-DI-during-offset-read')
  if scenario=='direction-live' and kind=='g' and name=='ss':
   ctx['ss_reads']+=1
   if ctx['ss_reads']==4:
    put(m,m.DS*16+0x8319,128);put(m,m.DS*16+0x831b,0x7fff,2);put(m,m.DS*16+0x7920,1);put(m,m.DS*16+0x7921,255);hit('live-direction-after-args')
 m.io_tap=io
 def wrapped(a,n,v):
  fn(a,n,v)
  if not ctx['enabled']:return
  r=m._registers;scenario=ctx['scenario'];ss=r['ss']*16
  if scenario=='root-cached-local-ss' and m.pc()==m.lin('214B:0000') and n==1 and a==ctx['ss']+((ctx['bp']-1)&65535) and not ctx.get('restore_ss'):
   newss=0xa0000;m._memory[newss:newss+65538]=bytes(m._memory[ss:ss+65538]);put(m,newss+((ctx['bp']-1)&65535),0x5a);r['ss']=0xa000;ctx['restore_ss']=True;hit('captured-AL-cached-stack-SS')
  if scenario=='leaf-args-captured' and m.pc()==m.lin('214B:0000'):
   for k in (0,2,4):put(m,ctx['argbase']+k,0x8888,2)
   hit('captured-word-and-far-pointer')
  if scenario=='flags-live' and m.pc()==m.lin('214B:0000'):
   r['eflags']^=0x440;hit('preserved-live-flags')
 return OLD_WRITE[type(m)](m,lo,hi,wrapped)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);a=ap.parse_args();assert not Path(a.out).exists();e.verify();before=e.hashes();e.deny_original();start=time.monotonic();rows={}
 for cls in (Oracle,PortMachine):cls.at=at;cls.on_write=on_write
 try:
  for scenario in SCENARIOS:
   row=rows[scenario]=dict(comparisons=0,hits={},effect_witnesses=0)
   for case in range(160):
    root=LEAVES[case%2] if scenario in ('leaf-args-captured','direction-live','flags-live') else ROOT
    opts=dict(root=root,controlled=root==ROOT)
    ctx.clear();ctx.update(enabled=True,scenario=scenario,root=root,hits={});p,_,_=exercise(Oracle,case,**opts);ph=dict(ctx['hits'])
    ctx.clear();ctx.update(enabled=True,scenario=scenario,root=root,hits={});r,_,_=exercise(PortMachine,case,**opts);rh=dict(ctx['hits'])
    assert p['error'] is None and p==r and ph==rh,(scenario,case,p['error'],r['error'],[k for k in p if p[k]!=r[k]],ph,rh)
    ctx['enabled']=False;base,_,_=exercise(Oracle,case,**opts);row['comparisons']+=1;row['effect_witnesses']+=p!=base
    for k,v in ph.items():row['hits'][k]=row['hits'].get(k,0)+v
   assert row['hits'] and all(row['hits'].values()) and row['effect_witnesses']>0,(scenario,row)
   print(scenario,row,flush=True)
 finally:
  for cls in (Oracle,PortMachine):cls.at=OLD_AT[cls];cls.on_write=OLD_WRITE[cls]
 e.write(a.out,dict(pass_all=True,comparisons=1280,scenarios=rows,pid=os.getpid(),pgid=os.getpgrp(),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),wall_s=time.monotonic()-start),before)
if __name__=='__main__':main()
