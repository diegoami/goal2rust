"""Prepared five-scenario T29 live-callback matrix; not yet executed.

Install into out/T29 after the development controller has exited. Keep every
failed epoch before retrying; no source or artifact may change while running.
"""
import argparse,hashlib,json,os,sys,time
from pathlib import Path
import capture_support as pure
sys.path[:0]=[str(pure.BASE/'engine/tests'),str(pure.BASE/'engine/python')]
from test_near_zone import *
from host_gate import wait_idle
SCENARIOS=('cached-physical-pointer-versus-later-argument-rereads',
 'cached-point-and-pointer-versus-live-y-after-guest',
 'sent-direction-versus-live-AX-after-resume-capture',
 'local-byte-read-uses-live-SS-after-write-listener',
 'AX-high-captured-before-local-SS-read')
OLD_AT={c:c.at for c in (Oracle,PortMachine)}
OLD_WRITE={c:c.on_write for c in (Oracle,PortMachine)}
ctx={}
def put(m,a,v,n=1):m._memory[a:a+n]=(v&((1<<(8*n))-1)).to_bytes(n,'little')
def hit(key):ctx['hits'][key]=ctx['hits'].get(key,0)+1
def argument(m,index,value):put(m,ctx['ss']+((ctx['sp']+4+index*2)&65535),value,2)
def at(m,site,fn):
 def wrapped(replay):
  fn(replay)
  if site=='0791:44C1' and not replay:
   regs=m._registers;ss=(regs['ss']&65535)*16;sp=regs['esp']&65535
   ctx.update(ss=ss,sp=sp,bp=(sp-2)&65535,p=0x60100,ds=m.DS*16,ss_reads=0)
   for seg,off in [(0x6000,0x100),(0x7000,0x300)]:
    p=seg*16+off;put(m,p,10);put(m,p+1,10 if seg==0x6000 else 99);put(m,p+6,2);put(m,p+0x12,0)
   argument(m,0,0x100);argument(m,1,0x6000);argument(m,2,0x0a0a)
   put(m,ctx['ds']+0x830b,1)
  if site=='0791:4500':
   # The actual return hook supplies a stable low direction value in every
   # scenario; the subsequent resume must capture it through the real API.
   m._registers['eax']=(m._registers['eax']&0xffff0000)|0xab01
   ctx['returned']=True
   if ctx['mutate'] and ctx['scenario']==SCENARIOS[1]:
    argument(m,0,0x300);argument(m,1,0x7000);argument(m,2,0x280a)
    put(m,ctx['p']+1,40);put(m,0x70301,40);hit('cached-inputs-with-live-old-record-Y')
 return OLD_AT[type(m)](m,site,wrapped)
def on_write(m,lo,hi,fn):
 original_io=m.io_tap
 def io(kind,a,value):
  original_io(kind,a,value)
  if not ctx['mutate'] or kind!='g' or 'ss' not in ctx:return
  scenario=ctx['scenario']
  if scenario==SCENARIOS[0] and a=='ss' and not ctx.get('returned'):
   ctx['ss_reads']+=1
   # PortFrame constructor reads SS once, then argptr reads arg1,arg0,arg1,
   # arg0. At the second arg1 read the physical p is already cached.
   if ctx['ss_reads']==4:
    argument(m,0,0x300);argument(m,1,0x7000);hit('later-seg-off-rereads')
  if scenario==SCENARIOS[2] and a=='ax' and ctx.get('returned') and not ctx.get('changed'):
   ctx['changed']=True;m._registers['eax']=(m._registers['eax']&0xffff0000)|0xcdff
   hit('AX-mutated-after-captured-SENT')
  if scenario==SCENARIOS[4] and a=='ss' and ctx.get('local_written') and not ctx.get('changed'):
   ctx['changed']=True;m._registers['eax']=(m._registers['eax']&0xffff0000)|0xcd00
   put(m,ctx['ss']+((ctx['bp']-1)&65535),0xa5);hit('captured-high-then-live-local-byte')
 m.io_tap=io
 def wrapped(a,n,value):
  fn(a,n,value)
  if not ctx['mutate'] or 'ss' not in ctx:return
  if m.pc()!=m.lin('0791:4526'):return
  expected=ctx['ss']+((ctx['bp']-1)&65535);assert a==expected and n==1
  if ctx['scenario']==SCENARIOS[3]:
   alt=0x90000;m._memory[alt:alt+65536]=m._memory[ctx['ss']:ctx['ss']+65536]
   put(m,alt+((ctx['bp']-1)&65535),0xa5);m._registers['ss']=0x9000
   hit('read-local-in-new-SS-after-original-write')
  if ctx['scenario']==SCENARIOS[4]:ctx['local_written']=True
 return OLD_WRITE[type(m)](m,lo,hi,wrapped)
def run(cls,case,scenario,mutate):
 ctx.clear();ctx.update(scenario=scenario,mutate=mutate,hits={})
 result,_,_=exercise(cls,case,controlled=True)
 assert result['error'] is None,(cls.__module__,case,scenario,result['error'])
 if mutate:
  assert ctx['hits'],(case,scenario)
  # ABI fixture records stack order (off,seg), the reverse of Call args.
  packets=[row[2] for row in result['log'] if row[0]=='abi' and row[1]=='0791:2BE5']
  assert packets==([(0x300,0x7000)] if scenario==SCENARIOS[0] else [(0x100,0x6000)]),(scenario,packets)
  value=result['regs']['eax']&65535
  if scenario==SCENARIOS[0]:assert value==0xab01
  if scenario==SCENARIOS[1]:assert value==0xab00
  if scenario==SCENARIOS[2]:assert value==0xcd01
  if scenario==SCENARIOS[3]:assert value==0xaba5 and result['regs']['ss']==0x9000
  if scenario==SCENARIOS[4]:assert value==0xaba5
 return result,dict(ctx['hits'])
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);parser.add_argument('--development',action='store_true');args=parser.parse_args()
 pure.verify();wait_idle();dest=Path(args.out);assert not dest.exists();import goal2rust_engine
 sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 files=sorted((pure.BASE/'engine/src').glob('*.rs'))+[Path(__file__),pure.BASE/'engine/tests/test_near_zone.py']+sorted(Path(goal2rust_engine.__file__).parent.glob('*.so'))
 saved={}
 if args.development:
  before={str(p.relative_to(pure.BASE)):sha(p) for p in files};folder=pure.BASE/'.cache/T29-development-sources';folder.mkdir(exist_ok=True)
  for p in files:
   target=folder/sha(p)
   if not target.exists():
    with target.open('xb') as f:f.write(p.read_bytes())
   assert sha(target)==sha(p);saved[str(p.relative_to(pure.BASE))]=str(target.relative_to(pure.BASE))
 else:
  import evidence as e
  before=e.hashes()
 started=time.monotonic();rows={}
 for cls in (Oracle,PortMachine):cls.at=at;cls.on_write=on_write
 try:
  for scenario in SCENARIOS:
   row=rows[scenario]=dict(comparisons=0,effect_witnesses=0,hits={})
   for case in range(160):
    p,ph=run(Oracle,case,scenario,True);r,rh=run(PortMachine,case,scenario,True)
    assert p==r and ph==rh,(case,scenario,[key for key in p if p[key]!=r[key]])
    baseline,_=run(Oracle,case,scenario,False)
    row['comparisons']+=1;row['effect_witnesses']+=any(p[key]!=baseline[key] for key in ['memory','regs','calls'])
    for key,value in ph.items():row['hits'][key]=row['hits'].get(key,0)+value
   assert row['comparisons']==row['effect_witnesses']==160 and all(row['hits'].values()),row
   print(scenario,row,flush=True)
 finally:
  for cls in (Oracle,PortMachine):cls.at=OLD_AT[cls];cls.on_write=OLD_WRITE[cls]
 report=dict(pass_all=True,comparisons=800,scenarios=rows,pid=os.getpid(),pgid=os.getpgrp(),script_sha256=sha(Path(__file__)),wall_s=time.monotonic()-started)
 if args.development:
  assert before=={str(p.relative_to(pure.BASE)):sha(p) for p in files}
  report.update(development_only=True,accepted_canonical_evidence=False,executed_source_sha256=before,preserved_source_map=saved)
  with dest.open('x') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
 else:e.write(dest,report,before)
if __name__=='__main__':main()
