"""T22 captured/live frame, pointer, row and reply callback matrix;1280 pairs."""
import argparse,hashlib,json,os,sys,time
from pathlib import Path
import evidence as e
sys.path.insert(0,str(e.BASE/'engine/tests'))
from test_offside import *
SCENARIOS=('captured-first-live-rows','captured-SENT-live-DX','marker-live-SS','marker-captured-record-live-column','marker-captured-AX-DX','sprite-live-current-glyph','sprite-captured-row','sprite-live-grid-pointer')
OLD_AT={c:c.at for c in (Oracle,PortMachine)};OLD_WRITE={c:c.on_write for c in (Oracle,PortMachine)};ctx={}
def put(m,a,v,n=1):m._memory[a:a+n]=(v&((1<<(8*n))-1)).to_bytes(n,'little')
def word(m,a):return int.from_bytes(m._memory[a:a+2],'little')
def hit(s):ctx['hits'][s]=ctx['hits'].get(s,0)+1

def at(m,site,fn):
 def wrapped(replay):
  fn(replay)
  if not ctx['enabled']:return
  r=m._registers;ss=r['ss']*16;sp=r['esp']&65535;ds=m.DS*16
  if site==ctx['root']:
   ctx.update(ss=ss,sp=sp)
   if site!=ROOT:
    base=ss+((sp+4)&65535);ctx['argbase']=base;ctx['record']=word(m,base)+word(m,base+2)*16
  if ctx['scenario']=='captured-first-live-rows' and site=='0791:8D42':
   side=ctx.get('side',0);first=m._memory[ds+0x668+side];put(m,ds+0x668+side,100);ctx['side']=side+1
   for k in range(first+2,first+12):put(m,ds+((k*22+0x80e9)&65535),128 if k%2 else 127)
   hit('captured-first-live-row-contents')
  if ctx['scenario']=='captured-SENT-live-DX' and site=='0791:8DD0':ctx['reply']=True;ctx['changed']=False
 return OLD_AT[type(m)](m,site,wrapped)
def on_write(m,lo,hi,fn):
 old_io=m.io_tap
 def io(kind,name,value):
  if old_io:old_io(kind,name,value)
  if not ctx['enabled']:return
  r=m._registers
  if ctx['scenario']=='captured-SENT-live-DX' and ctx.get('reply') and not ctx.get('changed') and kind=='g' and name=='ax':
   r['eax']=(r['eax']&0xffff0000)|0xdead;r['edx']=(r['edx']&0xffff0000)|0x5a80;ctx['changed']=True;hit('SENT-captured-before-live-DX')
  if ctx.get('restore_ss') and kind=='s' and name=='dx':r['ss']=ctx['ss']//16;ctx['restore_ss']=False;hit('restore-SS-before-guest')
 m.io_tap=io
 def wrapped(a,n,v):
  fn(a,n,v)
  if not ctx['enabled']:return
  r=m._registers;scenario=ctx['scenario'];pc=m.pc();ds=m.DS*16
  if scenario=='marker-live-SS' and pc==m.lin('0791:90C5') and not ctx.get('changed'):
   newss=0xa0000;m._memory[newss:newss+65538]=bytes(m._memory[ctx['ss']:ctx['ss']+65538]);base=newss+((ctx['sp']+4)&65535)
   put(m,base,0x900,2);put(m,base+2,0x9200,2);put(m,base+4,0x807f,2);put(m,base+6,0x0eae,2);r['ss']=0xa000;ctx['restore_ss']=True;ctx['changed']=True;hit('live-SS-frame-and-record')
  if scenario=='marker-captured-record-live-column' and pc==m.lin('0791:90F6'):
   base=ctx['argbase'];put(m,base,0x900,2);put(m,base+2,0x9300,2);put(m,base+4,0x7f);hit('captured-record-live-column')
  if scenario=='marker-captured-AX-DX' and pc==m.lin('0791:90F6'):
   r['eax']=(r['eax']&0xffff0000)|0x1234;r['edx']=(r['edx']&0xffff0000)|0x5678;put(m,ds+0x7920,0);put(m,ds+0x7921,0);hit('captured-row-and-direction')
  if scenario=='sprite-live-current-glyph' and pc==m.lin('0791:8EBA'):
   p=ctx['record'];put(m,p,128);put(m,p+1,255);put(m,p+4,0xbeef,2);hit('live-position-and-glyph-after-old-position-write')
  if scenario=='sprite-captured-row' and pc==m.lin('0791:8EE5'):
   put(m,ctx['record'],127);r['edx']=(r['edx']&0xffff0000)|0x7777;hit('captured-row-at-final-draw')
  if scenario=='sprite-live-grid-pointer' and pc==m.lin('0791:8EAC'):
   put(m,ds+0x7c16,0xfff0,2);put(m,ds+0x7c18,0x8000,2);hit('live-picture-pointer-after-background-restore')
 return OLD_WRITE[type(m)](m,lo,hi,wrapped)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);a=ap.parse_args();assert not Path(a.out).exists();e.verify();before=e.hashes();e.deny_original();rows={};start=time.monotonic()
 for cls in (Oracle,PortMachine):cls.at=at;cls.on_write=on_write
 try:
  for scenario in SCENARIOS:
   row=rows[scenario]=dict(comparisons=0,hits={},effect_witnesses=0)
   root=ROOT if scenario.startswith('captured-') else '0791:90C5' if scenario.startswith('marker-') else '0791:8E24'
   for case in range(160):
    opts=dict(root=root)
    ctx.clear();ctx.update(enabled=True,scenario=scenario,root=root,case=case,hits={});p,_,_=exercise(Oracle,case,**opts);ph=dict(ctx['hits'])
    ctx.clear();ctx.update(enabled=True,scenario=scenario,root=root,case=case,hits={});r,_,_=exercise(PortMachine,case,**opts);rh=dict(ctx['hits'])
    assert p['error'] is None and p==r and ph==rh,(scenario,case,p['error'],r['error'],[k for k in p if p[k]!=r[k]],ph,rh)
    ctx['enabled']=False;base,_,_=exercise(Oracle,case,**opts);row['comparisons']+=1;row['effect_witnesses']+=p!=base
    for k,v in ph.items():row['hits'][k]=row['hits'].get(k,0)+v
   assert row['hits'] and all(row['hits'].values()) and row['effect_witnesses']>0,(scenario,row)
   print(scenario,row,flush=True)
 finally:
  for cls in (Oracle,PortMachine):cls.at=OLD_AT[cls];cls.on_write=OLD_WRITE[cls]
 e.write(a.out,dict(pass_all=True,comparisons=1280,scenarios=rows,pid=os.getpid(),pgid=os.getpgrp(),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),wall_s=time.monotonic()-start),before)
if __name__=='__main__':main()
