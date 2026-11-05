"""Receiver callback witnesses with positive state/call effects and exact ABI."""
import hashlib,json,os,sys,time
from pathlib import Path
import capture_support as pure
sys.path[:0]=[str(pure.BASE/'engine/tests'),str(pure.BASE/'engine/python')]
from test_receiver import *
from host_gate import wait_idle
SCENARIOS=('local-flag-read-live-SS-after-flush','cached-target-before-live-parent-reload','parent-ES-before-DI','branch-decided-before-live-slot-reread')
OLD_AT={c:c.at for c in (Oracle,PortMachine)};OLD_WRITE={c:c.on_write for c in (Oracle,PortMachine)};ctx={}
def put(m,a,v,n=1):m._memory[a:a+n]=(v&((1<<(8*n))-1)).to_bytes(n,'little')
def hit(k):ctx['hits'][k]=ctx['hits'].get(k,0)+1
def at(m,site,fn):
 def wrapped(replay):
  fn(replay)
  if site=='0791:533B' and not replay:
   r=m._registers;ss=r['ss']*16;sp=r['esp']&65535;parent=0x5000;ds=m.DS*16
   ctx.update(ss=ss,bp=(sp-2)&65535,parent=parent,ds=ds)
   put(m,ss+((sp+2)&65535),parent,2);put(m,ss+parent+6,0x100,2);put(m,ss+parent+8,0x6000,2)
   for seg,off,slot in [(0x6000,0x100,2),(0x6000,0x300,12),(0x7000,0x300,255)]:put(m,seg*16+off+6,slot)
   receiver=3 if ctx['scenario']==SCENARIOS[0] else 12 if ctx['scenario']==SCENARIOS[2] else 2
   put(m,ds+0x830c,receiver);put(m,ds+0x8300,10,2);put(m,ds+0x8313,0x2468,2);put(m,ds+0x82f6,0x1357,2)
  if site=='0791:5367' and ctx['scenario']==SCENARIOS[1]:
   m._registers['eax']&=0xffffff00;ctx['returned']=True
 return OLD_AT[type(m)](m,site,wrapped)
def on_write(m,lo,hi,fn):
 original_io=m.io_tap
 def io(kind,a,v):
  original_io(kind,a,v)
  if not ctx['mutate'] or kind!='g' or 'ds' not in ctx:return
  ds=ctx['ds'];parent=ctx['ss']+ctx['parent'];scenario=ctx['scenario']
  if scenario==SCENARIOS[1] and a=='bp' and ctx.get('returned') and not ctx.get('changed'):
   ctx['changed']=True;put(m,parent+6,0x300,2);put(m,ds+0x8313,0xdead,2);hit('target-captured-before-parent-and-table-change')
  elif scenario==SCENARIOS[2] and a=='ss':
   ctx['ss_reads']=ctx.get('ss_reads',0)+1
   # Frame entry and Regs.enter read SS first; nested reads parent,ES,DI.
   if ctx['ss_reads']==5:
    put(m,parent+8,0x7000,2);put(m,parent+6,0x300,2);hit('captured-old-ES-new-DI')
 m.io_tap=io
 def wrapped(a,n,v):
  fn(a,n,v)
  if ctx['mutate'] and ctx['scenario']==SCENARIOS[3] and a==ctx['ss']+ctx['bp']-1:
   put(m,0x60106,12);put(m,ctx['ds']+0x830c,3);hit('slot-cached-then-reread-for-keeper')
  if ctx['mutate'] and ctx['scenario']==SCENARIOS[0] and a==ctx['ss']+ctx['bp']-1:
   alt=0x90000;m._memory[alt:alt+65536]=m._memory[ctx['ss']:ctx['ss']+65536]
   put(m,alt+ctx['bp']-1,0xa5);m._registers['ss']=0x9000;hit('local-read-live-SS-after-pending-write')
 return OLD_WRITE[type(m)](m,lo,hi,wrapped)
def run(cls,case,scenario,mutate):
 ctx.clear();ctx.update(scenario=scenario,mutate=mutate,hits={})
 p,_,_=exercise(cls,case,controlled=scenario!=SCENARIOS[0])
 assert p['error'] is None,(cls.__module__,case,scenario,p['error'])
 if mutate:
  assert ctx['hits'],(case,scenario)
  packets=[r[2] for r in p['log'] if r[0]=='abi' and r[1]=='0791:045D']
  if scenario==SCENARIOS[0]:assert p['regs']['eax']&255==0xa5 and p['regs']['ss']==0x9000
  if scenario==SCENARIOS[1]:assert any(r[0]=='w' and r[1]==0x60307 and r[3]==0x2468 for r in p['log'])
  if scenario==SCENARIOS[2]:assert packets==[(255,)]
  if scenario==SCENARIOS[3]:assert packets==[(12,)]
 return p,dict(ctx['hits'])
def main():
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);parser.add_argument('--development',action='store_true');a=parser.parse_args()
 pure.verify();wait_idle();dest=Path(a.out);assert not dest.exists();import goal2rust_engine
 sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 files=sorted((pure.BASE/'engine/src').glob('*.rs'))+[Path(__file__),pure.BASE/'engine/tests/test_receiver.py']+sorted(Path(goal2rust_engine.__file__).parent.glob('*.so'))
 saved={}
 if a.development:
  before={str(p.relative_to(pure.BASE)):sha(p) for p in files};folder=pure.BASE/'.cache/T28-development-sources';folder.mkdir(exist_ok=True)
  for p in files:
   target=folder/sha(p)
   if not target.exists():
    with target.open('xb') as f:f.write(p.read_bytes())
   saved[str(p.relative_to(pure.BASE))]=str(target.relative_to(pure.BASE))
 else:
  import evidence as e
  before=e.hashes()
 start=time.monotonic();rows={}
 for cls in (Oracle,PortMachine):cls.at=at;cls.on_write=on_write
 try:
  for scenario in SCENARIOS:
   row=rows[scenario]=dict(comparisons=0,effect_witnesses=0,hits={})
   for case in range(160):
    p,ph=run(Oracle,case,scenario,True);r,rh=run(PortMachine,case,scenario,True)
    assert p==r and ph==rh,(case,scenario,[k for k in p if p[k]!=r[k]])
    baseline,_=run(Oracle,case,scenario,False);row['comparisons']+=1;row['effect_witnesses']+=any(p[k]!=baseline[k] for k in ['memory','regs','calls'])
    for k,v in ph.items():row['hits'][k]=row['hits'].get(k,0)+v
   assert row['effect_witnesses']==160 and all(row['hits'].values()),row
   print(scenario,row,flush=True)
 finally:
  for cls in (Oracle,PortMachine):cls.at=OLD_AT[cls];cls.on_write=OLD_WRITE[cls]
 report=dict(pass_all=True,comparisons=640,scenarios=rows,pid=os.getpid(),pgid=os.getpgrp(),script_sha256=sha(Path(__file__)),wall_s=time.monotonic()-start)
 if a.development:
  assert before=={str(p.relative_to(pure.BASE)):sha(p) for p in files};report.update(development_only=True,accepted_canonical_evidence=False,executed_source_sha256=before,preserved_source_map=saved)
  with dest.open('x') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
 else:e.write(dest,report,before)
if __name__=='__main__':main()
