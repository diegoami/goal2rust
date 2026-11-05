"""Supplementary T19 captured/live alias probes, fixed1280 source/native pairs."""
import argparse,hashlib,json,os,sys,time
from pathlib import Path
import evidence as e
sys.path.insert(0,str(e.BASE/'engine/tests'))
from test_depth import *
SCENARIOS=('attack-stack','defend-stack','parent-captured','root-live','result-local-ss','slot-captured','coin-seed-df','t6-sent')
OLD_AT={c:c.at for c in (Oracle,PortMachine)};OLD_WRITE={c:c.on_write for c in (Oracle,PortMachine)};ctx={}
def put(m,a,v,n=1):m._memory[a:a+n]=(v&((1<<(n*8))-1)).to_bytes(n,'little')
def word(m,a):return int.from_bytes(m._memory[a:a+2],'little')
def hit(name):ctx['hits'][name]=ctx['hits'].get(name,0)+1
def at(m,site,fn):
 def wrapped(replay):
  fn(replay)
  if not ctx['enabled']:return
  r=m._registers;ss=r['ss']*16;sp=r['esp']&65535
  if site==ctx['root']:
   near=site in ('0791:4532','0791:4649');base=ss+((sp+(2 if near else 4))&65535)
   ctx.update(sp=sp,ss=ss,bp=(sp-2)&65535,argbase=base)
   if near:
    parent=word(m,base);ctx['parent']=parent;ctx['record']=word(m,ss+((parent+8)&65535))*16+word(m,ss+((parent+6)&65535))
   elif site!='214B:06FA':ctx['record']=word(m,base+2)*16+word(m,base)
  scenario=ctx['scenario']
  if scenario=='attack-stack' and site=='0791:455B':
   put(m,ss+sp,0x1234,2);hit('popped-group-live')
  if scenario=='defend-stack' and site=='0791:4689':
   put(m,ss+sp,0x8888,2);put(m,ss+((sp+2)&65535),0x1234,2);hit('popped-group-and-dead-t6')
  if scenario=='parent-captured' and site in ('0791:4549','0791:4660'):
   p=ctx['parent'];put(m,ss+((p+6)&65535),0x900,2);put(m,ss+((p+8)&65535),0x9200,2);hit('captured-parent-pointer')
  if scenario=='root-live' and site in ('0791:478D','0791:479A'):
   put(m,ctx['record']+12,0x7f);hit('live-depth-after-step')
 return OLD_AT[type(m)](m,site,wrapped)
def on_write(m,lo,hi,fn):
 old_io=m.io_tap
 def io(kind,name,value):
  if old_io:old_io(kind,name,value)
  if not ctx['enabled']:return
  r=m._registers
  if ctx.get('restore_ss') and kind=='s' and name=='sp' and value==((ctx['sp']+ENTRIES[ctx['root']].return_stack_delta)&65535):
   r['ss']=ctx['ss']//16;ctx['restore_ss']=False;hit('restore-ss')
  if ctx['scenario']=='t6-sent' and (r['eip']&65535) in (0x4672,0x4689):
   if kind=='g' and name=='ax':ctx['sent_armed']=True
   elif kind=='s' and name=='sp' and ctx.get('sent_armed'):
    r['eax']=(r['eax']&0xffff0000)|0xeeff;ctx['sent_armed']=False;hit('captured-sent-live-ax')
 m.io_tap=io
 def wrapped(a,n,v):
  fn(a,n,v)
  if not ctx['enabled']:return
  r=m._registers;ss=r['ss']*16;ds=m.DS*16;site=m.pc();scenario=ctx['scenario']
  if scenario=='result-local-ss' and n==1 and a==ss+((ctx['bp']-1)&65535) and not ctx.get('restore_ss') and site in [m.lin('0791:'+x) for x in ('45CA','4603','463D','46D4','46EE','4741')]:
   fresh=0xa0000;m._memory[fresh:fresh+65538]=bytes(m._memory[ss:ss+65538]);put(m,fresh+((ctx['bp']-1)&65535),0x5a);r['ss']=0xa000;ctx['restore_ss']=True;hit('fresh-ss-live-local')
  if scenario=='slot-captured' and site==m.lin('214B:0000'):
   base=ctx['argbase'];put(m,base,0x900,2);put(m,base+2,0x9200,2);r['eax']=(r['eax']&0xffff00ff)|0xa500;hit('captured-slot-live-ah')
  if scenario=='coin-seed-df' and site==m.lin('214B:069F'):
   put(m,ds+0xa978,0xffff,2);put(m,ds+0xa97a,0x9200,2);r['eflags']^=0x400;hit('captured-seed-live-df')
 return OLD_WRITE[type(m)](m,lo,hi,wrapped)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);a=ap.parse_args();assert not Path(a.out).exists();e.verify();e.deny_original();before=e.hashes();rows={};start=time.monotonic()
 for cls in (Oracle,PortMachine):cls.at=at;cls.on_write=on_write
 try:
  for scenario in SCENARIOS:
   root={'attack-stack':'0791:4532','defend-stack':'0791:4649','parent-captured':'0791:4532','root-live':ROOT,'result-local-ss':'0791:4649','slot-captured':'0791:2BB1','coin-seed-df':'214B:06FA','t6-sent':'0791:4649'}[scenario]
   row=rows[scenario]=dict(comparisons=0,hits={},effect_witnesses=0)
   for case in range(160):
    if scenario in ('parent-captured','result-local-ss'):root='0791:4532' if case%2 else '0791:4649'
    opts=dict(root=root,controlled=root in CALLERS)
    ctx.clear();ctx.update(enabled=True,scenario=scenario,root=root,hits={});p,_,_=exercise(Oracle,case,**opts);ph=dict(ctx['hits'])
    ctx.clear();ctx.update(enabled=True,scenario=scenario,root=root,hits={});r,_,_=exercise(PortMachine,case,**opts);rh=dict(ctx['hits'])
    assert p['error'] is None and p==r and ph==rh,(scenario,case,p['error'],r['error'],[k for k in p if p[k]!=r[k]],ph,rh)
    ctx['enabled']=False;base,_,_=exercise(Oracle,case,**opts);row['comparisons']+=1;row['effect_witnesses']+=p!=base
    for k,v in ph.items():row['hits'][k]=row['hits'].get(k,0)+v
   assert row['hits'] and all(row['hits'].values()) and row['effect_witnesses']>0,(scenario,row)
   print(scenario,row,flush=True)
 finally:
  for cls in (Oracle,PortMachine):cls.at=OLD_AT[cls];cls.on_write=OLD_WRITE[cls]
 report=dict(pass_all=True,comparisons=1280,scenarios=rows,pid=os.getpid(),pgid=os.getpgrp(),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),wall_s=time.monotonic()-start)
 e.write(a.out,report,before)
if __name__=='__main__':main()
