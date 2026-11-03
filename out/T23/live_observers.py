"""Eight source-specific string-copy callback matrices,160 pairs each."""
import argparse,hashlib,json,os,sys,time
from pathlib import Path
import evidence as e
sys.path.insert(0,str(e.BASE/'engine/tests'))
from test_pascal import *
SCENARIOS=('bulk-snapshot','overlap-live','wrap-live','eight-nine-threshold','concat-captured-lengths-live-AX','store-captured-length-AX','live-flags-last','live-SS-arguments')
OLD_AT={c:c.at for c in (Oracle,PortMachine)};OLD_WRITE={c:c.on_write for c in (Oracle,PortMachine)};ctx={}
def put(m,a,v,n=1):m._memory[a:a+n]=(v&((1<<(8*n))-1)).to_bytes(n,'little')
def hit(s):ctx['hits'][s]=ctx['hits'].get(s,0)+1
def at(m,site,fn):
 def wrapped(replay):
  fn(replay)
  if site!=ctx['root'] or replay:return
  ss=m._registers['ss']*16;sp=m._registers['esp']&65535;sg=0x4000;so=0x100;dg=0x5000;do=0x800;n=16;destlen=0;mx=255;s=ctx['scenario']
  if s=='overlap-live':dg=sg;do=so-1
  if s=='wrap-live':so=0xfff8
  if s=='eight-nine-threshold':n=8+ctx['case']%2
  if s=='concat-captured-lengths-live-AX':destlen=250
  if s=='store-captured-length-AX':mx=9
  for k in range(1,257):put(m,sg*16+((so+k)&65535),k*7+3)
  for k in range(1,257):put(m,dg*16+((do+k)&65535),0x55)
  put(m,sg*16+so,n);put(m,dg*16+do,destlen)
  packet=[mx,do,dg,so,sg] if site=='23E4:0644' else [so,sg,do,dg]
  base=ss+((sp+4)&65535)
  for i,v in enumerate(packet):put(m,base+2*i,v,2)
  ctx.update(ss=ss,sp=sp,argbase=base,src=sg*16+so,so=so,sg=sg,dst=dg*16+do,dg=dg,do=do,n=n,destlen=destlen,mx=mx,copy_start=dg*16+((do+(destlen if site=='23E4:06B7' else 0)+1)&65535))
 return OLD_AT[type(m)](m,site,wrapped)
def on_write(m,lo,hi,fn):
 old_io=m.io_tap
 def io(kind,name,value):
  if old_io:old_io(kind,name,value)
  if not ctx['mutate']:return
  r=m._registers;s=ctx['scenario']
  if s=='live-flags-last' and kind=='s' and name=='di':r['eflags']^=0xcd5;hit('live-arithmetic-and-DF-before-late-flags-store')
  if s=='live-SS-arguments':
   if kind=='g' and name=='ss' and not ctx.get('changed_ss'):
    newss=0x90000;m._memory[newss:newss+65538]=bytes(m._memory[ctx['ss']:ctx['ss']+65538]);base=newss+((ctx['sp']+4)&65535)
    for k in range(17):put(m,0x60000+0x300+k,16 if k==0 else 0xa0+k)
    packet=[255,ctx['do'],ctx['dg'],0x300,0x6000] if ctx['root']=='23E4:0644' else [0x300,0x6000,ctx['do'],ctx['dg']]
    for i,v in enumerate(packet):put(m,base+2*i,v,2)
    r['ss']=0x9000;ctx['changed_ss']=True;ctx['restore_ss']=True;hit('live-SS-before-captured-argument-block')
   elif kind=='s' and name=='es' and ctx.get('restore_ss'):
    r['ss']=ctx['ss']//16;ctx['restore_ss']=False;hit('restore-SS-before-return')
 m.io_tap=io
 def wrapped(a,n,v):
  fn(a,n,v)
  if not ctx['mutate']:return
  s=ctx['scenario'];r=m._registers;pc=m.pc()
  length_pc='23E4:06CA' if ctx['root']=='23E4:06B7' else '23E4:065C' if ctx['root']=='23E4:0644' else '23E4:0638'
  if pc==m.lin(length_pc) and s in ('concat-captured-lengths-live-AX','store-captured-length-AX'):
   put(m,ctx['src'],0);r['eax']=(r['eax']&0xffff0000)|0xabcd
   if s.startswith('store-'):put(m,ctx['argbase'],255,2)
   hit('captured-lengths-versus-live-or-cached-AX')
  if s in ('bulk-snapshot','overlap-live','wrap-live','eight-nine-threshold') and a==ctx['copy_start'] and not ctx.get('changed'):
   k=9 if s=='wrap-live' else 3;addr=ctx['sg']*16+((ctx['so']+1+k)&65535);put(m,addr,0xe7);ctx.update(changed=True,changed_index=k);hit('future-source-byte-mutated-at-first-copy')
 return OLD_WRITE[type(m)](m,lo,hi,wrapped)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);a=ap.parse_args();assert not Path(a.out).exists();e.verify();before=e.hashes();e.deny_original();start=time.monotonic();rows={}
 for c in (Oracle,PortMachine):c.at=at;c.on_write=on_write
 try:
  for scenario in SCENARIOS:
   row=rows[scenario]=dict(comparisons=0,hits={},effect_witnesses=0,snapshot_witnesses=0,live_read_witnesses=0)
   root='23E4:06B7' if scenario.startswith('concat-') else '23E4:0644' if scenario in ('wrap-live','store-captured-length-AX','live-flags-last','live-SS-arguments') else ROOT
   for case in range(160):
    def run(cls,mutate):
     ctx.clear();ctx.update(root=root,scenario=scenario,case=case,mutate=mutate,hits={});p,_,_=exercise(cls,case,root=root);return p,dict(ctx['hits'])
    p,ph=run(Oracle,True);r,rh=run(PortMachine,True);assert p['error'] is None and p==r and ph==rh,(scenario,case,p['error'],r['error'],[k for k in p if p[k]!=r[k]],ph,rh)
    base,_=run(Oracle,False);row['comparisons']+=1;row['effect_witnesses']+=p!=base
    # The callback's source mutation must affect later copy writes only on the live branch.
    if scenario in ('bulk-snapshot','overlap-live','wrap-live','eight-nine-threshold'):
     def copied(result):return [x for x in result['log'] if x[0]=='w' and x[4] in {((0x23e4+0x823)&65535)*16+v for v in [0x63d,0x661,0x6dc]}]
     same=copied(p)==copied(base);snapshot=scenario=='bulk-snapshot' or scenario=='eight-nine-threshold' and case%2==1
     assert same==snapshot,(scenario,case);row['snapshot_witnesses']+=snapshot;row['live_read_witnesses']+=not snapshot
    for k,v in ph.items():row['hits'][k]=row['hits'].get(k,0)+v
   assert row['effect_witnesses']>0 and row['hits'] and all(row['hits'].values()),(scenario,row)
   print(scenario,row,flush=True)
 finally:
  for c in (Oracle,PortMachine):c.at=OLD_AT[c];c.on_write=OLD_WRITE[c]
 e.write(a.out,dict(pass_all=True,comparisons=1280,scenarios=rows,pid=os.getpid(),pgid=os.getpgrp(),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),wall_s=time.monotonic()-start),before)
if __name__=='__main__':main()
