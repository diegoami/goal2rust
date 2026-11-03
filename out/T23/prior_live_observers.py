"""Supplementary live-stack/pointer/SS observers on the unchanged T21 artifact.
Counts sealed before running: eight scenarios *160 authored inputs =1280 pairs.
This file is installed into out/T23 only after all canonical writers exit.
"""
import argparse,hashlib,json,os,sys,time
from pathlib import Path
sys.path[:0]=['out/T23','engine/tests']
import evidence as e
from test_marking import ROOT,ZONE,RANDOM,Oracle,PortMachine,exercise
SCENARIOS=('split-frame-ss','captured-country','live-first-skill','live-second-skill','live-draw','zone-record-args','zone-live-local','rng-captured-arg')
OLD_AT={c:c.at for c in (Oracle,PortMachine)};OLD_WRITE={c:c.on_write for c in (Oracle,PortMachine)}
context={}
def regs(m):return m._registers

def put(m,at,value,size=1):m._memory[at:at+size]=(value&((1<<(8*size))-1)).to_bytes(size,'little')
def word(m,at):return int.from_bytes(m._memory[at:at+2],'little')
def hit(name):context['hits'][name]=context['hits'].get(name,0)+1

def at(m,site,fn):
 def wrapped(replay):
  fn(replay)
  if not context['enabled']:return
  r=regs(m);ss=(r['ss']&65535)*16;sp=r['esp']&65535
  if site==context['root']:
   context.update(sp=sp,ss=ss,parent=word(m,ss+((sp+2)&65535)))
   if site==ROOT and context['scenario']=='split-frame-ss' and context['case']%7==0:
    parent=context['parent'];off=word(m,ss+((parent+6)&65535));seg=word(m,ss+((parent+8)&65535))
    parent=0xfff9;put(m,ss+((sp+2)&65535),parent,2);put(m,ss+((parent+6)&65535),off,2);put(m,ss+((parent+8)&65535),seg,2)
    context['parent']=parent;hit('wrapped-parent')
   if site==ZONE:
    off=word(m,ss+((sp+4)&65535));seg=word(m,ss+((sp+6)&65535));context['record']=seg*16+off
  targets={'live-first-skill':'0791:496A','live-second-skill':'0791:499D','live-draw':'0791:49C0'}
  if targets.get(context['scenario'])==site:
   a=ss+sp;put(m,a,word(m,a)^0x8080,2);hit('stack-word')
  if context['scenario']=='zone-live-local' and site=='0791:4493':
   put(m,ss+((context['sp']-4)&65535),127);hit('zone-local')
 return OLD_AT[type(m)](m,site,wrapped)

def on_write(m,begin,end,fn):
 original_io=m.io_tap
 def io(kind,name,value):
  original_io(kind,name,value)
  if not context['enabled'] or context['scenario']!='split-frame-ss' or 'sp' not in context:return
  if kind=='s' and name=='sp' and value==((context['sp']-14)&65535) and not context.get('prologue'):
   context['prologue']=True;context['ss_reads']=0
  if kind=='g' and name=='ss' and context.get('prologue'):
   context['ss_reads']+=1
   if context['ss_reads']==2:
    old=context['ss'];fresh=0xa0000;m._memory[fresh:fresh+65538]=bytes(m._memory[old:old+65538])
    put(m,fresh+((context['parent']+6)&65535),0x200,2);regs(m)['ss']=0xa000;hit('split-begin')
   if context['ss_reads']==3:regs(m)['ss']=context['ss']//16;hit('split-end')
 m.io_tap=io
 def wrapped(a,n,v):
  fn(a,n,v)
  pc=m.pc()
  if not context['enabled']:return
  r=regs(m);scenario=context['scenario'];ds=m.DS*16;ss=(r['ss']&65535)*16
  if scenario=='captured-country' and pc==m.lin('0791:47E2'):
   put(m,ds+0xa917,0x100,2);put(m,ds+0xa919,0x9300,2);hit('country-pointer')
  if scenario=='zone-record-args' and pc==m.lin('0791:4445'):
   rec=context['record'];put(m,rec+9,0x8080,2);put(m,rec+0x12,1)
   put(m,ds+0xa91b,0x100,2);put(m,ds+0xa91d,0x9200,2)
   player=word(m,rec+0xd);put(m,0x92000+((0x100+20*player)&65535)+6,5);put(m,ds+0x7c3,128)
   sp=context['sp'];put(m,ss+((sp+4)&65535),0x200,2);put(m,ss+((sp+6)&65535),0x9400,2);put(m,ss+((sp+8)&65535),0x7f7f,2);hit('zone-record-args')
  if scenario=='rng-captured-arg' and pc==m.lin('214B:069F'):
   put(m,ss+((context['sp']+4)&65535),65535,2);put(m,ds+0xa978,0xffff,2);put(m,ds+0xa97a,0x9100,2);r['eflags']^=0x400;hit('rng-arg-pointer-df')
 return OLD_WRITE[type(m)](m,begin,end,wrapped)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);a=ap.parse_args();assert not Path(a.out).exists()
 e.verify();e.deny_original();before=e.hashes();start=time.monotonic();rows={}
 for cls in (Oracle,PortMachine):cls.at=at;cls.on_write=on_write
 try:
  for scenario in SCENARIOS:
   root=ZONE if scenario.startswith('zone-') else RANDOM if scenario.startswith('rng-') else ROOT
   row=rows[scenario]=dict(comparisons=0,hits={},effect_witnesses=0)
   for case in range(160):
    opts=dict(root=root,controlled=root==ROOT)
    context.clear();context.update(enabled=True,scenario=scenario,root=root,case=case,hits={})
    p,_,_=exercise(Oracle,case,**opts);ph=dict(context['hits'])
    context.clear();context.update(enabled=True,scenario=scenario,root=root,case=case,hits={})
    r,_,_=exercise(PortMachine,case,**opts);rh=dict(context['hits'])
    assert p['error'] is None and p==r and ph==rh,(scenario,case,p['error'],r['error'],[k for k in p if p[k]!=r[k]],ph,rh)
    context['enabled']=False;base,_,_=exercise(Oracle,case,**opts)
    row['comparisons']+=1;row['effect_witnesses']+=p!=base
    for key,count in ph.items():row['hits'][key]=row['hits'].get(key,0)+count
   assert row['hits'] and all(row['hits'].values()) and row['effect_witnesses']>0,(scenario,row)
   print(scenario,row,flush=True)
 finally:
  for cls in (Oracle,PortMachine):cls.at=OLD_AT[cls];cls.on_write=OLD_WRITE[cls]
 report=dict(pass_all=True,pid=os.getpid(),pgid=os.getpgrp(),scenarios=rows,comparisons=sum(r['comparisons'] for r in rows.values()),fixed_production_artifact=True,script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),wall_s=time.monotonic()-start)
 assert report['comparisons']==1280
 e.write(a.out,report,before);print('Supplementary live observer comparisons passed',report['comparisons'],flush=True)
if __name__=='__main__':main()
