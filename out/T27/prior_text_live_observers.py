"""Eight text-specific live/cached callback witnesses,160 pairs each."""
import argparse,hashlib,json,os,sys,time
from pathlib import Path
import evidence as e
sys.path.insert(0,str(e.BASE/'engine/tests'))
from test_text import *
SCENARIOS=('forward-live-byte','backward-live-byte','cached-attribute-AH','late-DF-live-flags','global-attribute-after-copy','attribute-before-position','live-SS-length-and-source','captured-destination')
OLD_AT={c:c.at for c in (Oracle,PortMachine)};OLD_WRITE={c:c.on_write for c in (Oracle,PortMachine)};ctx={}
def put(m,a,v,n=1):m._memory[a:a+n]=(v&((1<<(n*8))-1)).to_bytes(n,'little')
def hit(s):ctx['hits'][s]=ctx['hits'].get(s,0)+1
def at(m,site,fn):
 def wrapped(replay):
  fn(replay)
  if site==ctx['root'] and not replay:
   r=m._registers;ss=r['ss']*16;sp=r['esp']&65535;ctx.update(ss=ss,sp=sp,entered=True,temporary=(sp-2-0x100)&65535)
   if ctx['root'] in LEAVES:
    reverse=ctx['root']=='214B:0123';so=0 if reverse else 0xffff;sg=0x4000;do=0xfffc;dg=0x5000
    ctx.update(source_seg=sg,source_off=so,step=-1 if reverse else 1)
    for k in range(12):put(m,sg*16+((so+ctx['step']*k)&65535),(ctx['case']+k*7+0x41)&255)
    packet=[9,0x5ad1,so,sg,do,dg];base=4 if ENTRIES[ctx['root']].far else 2
   else:
    put(m,0x40100,9)
    for k in range(1,10):put(m,0x40100+k,(ctx['case']+k*11)&255)
    put(m,0x60100,0x800,2);put(m,0x60102,0x5000,2);put(m,m.DS*16+0xaab2,0x3e)
    packet=[0x100,0x6000,1,1,0x100,0x4000]+([0x5ac4] if ctx['root']=='214B:02C8' else []);base=4
   for i,v in enumerate(packet):put(m,ss+((sp+base+2*i)&65535),v,2)
  if site in ('214B:0288','214B:02E3'):
   ctx['copied']=True
   if ctx['mutate'] and ctx['scenario']=='global-attribute-after-copy':put(m,m.DS*16+0xaab2,0xe7);hit('global-colour-changed-after-copy')
 return OLD_AT[type(m)](m,site,wrapped)
def on_write(m,lo,hi,fn):
 oldio=m.io_tap
 def io(kind,name,value):
  if oldio:oldio(kind,name,value)
  if not ctx['mutate'] or not ctx.get('entered'):return
  r=m._registers;s=ctx['scenario']
  if ctx.get('copied') and kind=='g' and name=='bp' and not ctx.get('body_started'):
   ctx['body_started']=True;ctx['ss_reads']=0
   if s=='live-SS-length-and-source':
    ss=ctx['ss'];newss=0x90000;m._memory[newss:newss+65538]=bytes(m._memory[ss:ss+65538]);put(m,newss+ctx['temporary'],5)
    for k in range(1,6):put(m,newss+((ctx['temporary']+k)&65535),0xd0+k)
    r['ss']=0x9000;ctx['swapped']=True;hit('live-SS-before-length-and-source')
  if ctx.get('body_started') and kind=='g' and name=='ss':
   ctx['ss_reads']=ctx.get('ss_reads',0)+1
   if s=='captured-destination' and ctx['ss_reads']==5:
    put(m,0x60100,0x1234,2);put(m,0x60102,0x7000,2);hit('destination-table-changed-after-capture')
  if ctx.get('swapped') and not ctx.get('restored') and kind=='s':
   r['ss']=ctx['ss']//16;ctx['restored']=True;hit('source-SS-captured-before-restoring-call-stack')
  if s=='late-DF-live-flags' and kind=='s' and name=='eflags':assert value&0x400;hit('STD-stored-late')
 m.io_tap=io
 def wrapped(a,n,v):
  fn(a,n,v)
  if not ctx['mutate']:return
  s=ctx['scenario'];r=m._registers;pc=m.pc()
  if pc in (m.lin('214B:0119'),m.lin('214B:013D')) and ctx['root'] in LEAVES:
   k=ctx.get('word',0);ctx['word']=k+1
   if s in ('forward-live-byte','backward-live-byte'):
    current=ctx['source_seg']*16+((ctx['source_off']+ctx['step']*k)&65535)
    assert v&255==m._memory[current]
    if k:hit('each-byte-read-live-before-its-word-write')
    if k<8:put(m,ctx['source_seg']*16+((ctx['source_off']+ctx['step']*(k+1))&65535),(ctx['case']+k*29+0xa1)&255);hit('future-source-byte-mutated')
   if s=='cached-attribute-AH':
    assert v>>8==0xd1;r['eax']=(r['eax']&0xffff0000)|0xab55
    if k:hit('captured-AH-survives-live-AX-change')
    if not k:r['ebx']^=1
   if s=='late-DF-live-flags' and not k:r['eflags']^=0xc01;hit('DF-and-other-live-flags-mutated-before-store')
  if s=='attribute-before-position' and pc==m.lin('214B:02E6'):
   assert v==0xc4;put(m,ctx['ss']+((ctx['sp']+8)&65535),2+ctx['case']%5,2);hit('attribute-write-precedes-live-column-read')
 return OLD_WRITE[type(m)](m,lo,hi,wrapped)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);a=ap.parse_args();assert not Path(a.out).exists();e.verify();before=e.hashes();e.deny_original();start=time.monotonic();rows={}
 for c in (Oracle,PortMachine):c.at=at;c.on_write=on_write
 try:
  for s in SCENARIOS:
   root='214B:0123' if s in ('backward-live-byte','late-DF-live-flags') else '214B:00FF' if s in ('forward-live-byte','cached-attribute-AH') else '214B:02C8' if s=='attribute-before-position' else '214B:026D'
   row=rows[s]=dict(comparisons=0,hits={},effect_witnesses=0)
   for case in range(160):
    def run(cls,mutate):
     ctx.clear();ctx.update(scenario=s,root=root,case=case,mutate=mutate,hits={});p,_,_=exercise(cls,case,root=root);return p,dict(ctx['hits'])
    p,ph=run(Oracle,True);r,rh=run(PortMachine,True)
    assert p==r and ph==rh,(s,case,p['error'],r['error'],[k for k in p if p[k]!=r[k]],ph,rh)
    assert p['error'] is None,(s,case,p['error']);base,_=run(Oracle,False)
    row['comparisons']+=1;row['effect_witnesses']+=p!=base
    for k,v in ph.items():row['hits'][k]=row['hits'].get(k,0)+v
   assert row['effect_witnesses']>0 and row['hits'] and all(row['hits'].values()),(s,row)
   print(s,row,flush=True)
 finally:
  for c in (Oracle,PortMachine):c.at=OLD_AT[c];c.on_write=OLD_WRITE[c]
 e.write(a.out,dict(pass_all=True,comparisons=1280,scenarios=rows,pid=os.getpid(),pgid=os.getpgrp(),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),wall_s=time.monotonic()-start),before)
if __name__=='__main__':main()
