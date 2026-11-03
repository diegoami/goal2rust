"""Supplementary T18 captured/live alias probes, fixed1280 source/native pairs."""
import argparse,hashlib,json,os,sys,time
from pathlib import Path
import evidence as e
sys.path.insert(0,str(e.BASE/'engine/tests'))
from test_destination import *
SCENARIOS=('group-captured','post-live','mirror-captured','clamp-captured','extreme-captured','root-stack','advanced-live-local','mark-captured')
OLD_AT={c:c.at for c in (Oracle,PortMachine)};OLD_WRITE={c:c.on_write for c in (Oracle,PortMachine)};ctx={}
def put(m,a,v,n=1):m._memory[a:a+n]=(v&((1<<(n*8))-1)).to_bytes(n,'little')
def word(m,a):return int.from_bytes(m._memory[a:a+2],'little')
def hit(name):ctx['hits'][name]=ctx['hits'].get(name,0)+1
def pc(m):r=m._registers;return (r['cs']&65535)*16+(r['eip']&65535)
def at(m,site,fn):
 def wrapped(replay):
  fn(replay)
  if not ctx['enabled']:return
  r=m._registers;ss=r['ss']*16;sp=r['esp']&65535
  if site==ctx['root']:
   ctx.update(sp=sp,ss=ss,bp=(sp-2)&65535)
   base=ss+((sp+4)&65535);ctx['argbase']=base
   if ctx['root'].startswith('0791:4') and ctx['root']!='0791:40BC':ctx['record']=word(m,ss+((sp+6)&65535))*16+word(m,ss+((sp+4)&65535))
   elif ctx['root']=='0791:2C86':ctx['record']=word(m,base+2)*16+word(m,base)
  if ctx['scenario']=='root-stack':
   if site in ('0791:4C7B','0791:4CEB'):
    a=ss+sp;put(m,a,word(m,a)^0x8080,2)
    if site=='0791:4CEB':put(m,a+2,0x1234,2)
    hit('live-stack')
   if site=='0791:4D2A':
    for k in (0,2,4):put(m,ss+((sp+k)&65535),0x9999,2)
    hit('prepush-overwrite')
  if ctx['scenario']=='group-captured' and site in ('0791:4311','0791:431E'):
   p=ctx['record'];id=word(m,p+13);off=word(m,m.DS*16+0xa91b);seg=word(m,m.DS*16+0xa91d);put(m,seg*16+((off+id*20)&65535)+6,255);hit('captured-position')
  if ctx['scenario']=='mark-captured' and site=='0791:4AE1':
   bp=r['ebp']&65535;put(m,ss+((bp-2)&65535),0xff01,2);hit('live-parent-locals')
 return OLD_AT[type(m)](m,site,wrapped)
def on_write(m,lo,hi,fn):
 old_io=m.io_tap
 def io(kind,name,value):
  old_io(kind,name,value)
  if not ctx['enabled']:return
  r=m._registers
  if ctx.get('restore_ss') and kind=='s' and name=='sp' and value==ctx['sp']:
   r['ss']=ctx['ss']//16;ctx['restore_ss']=False;hit('restore-ss')
  if ctx['scenario']=='root-stack' and (r['eip']&65535) in (0x4cd8,0x4ceb,0x4bf1):
   if kind=='g' and name=='ax':ctx['sent_armed']=True
   elif kind=='s' and name=='sp' and ctx.get('sent_armed'):
    r['eax']=(r['eax']&0xffff0000)|0xee00;ctx['sent_armed']=False;hit('captured-sent')
    if (r['eip']&65535)==0x4bf1:r['eflags']^=0x40;hit('live-zf')
 m.io_tap=io
 def wrapped(a,n,v):
  fn(a,n,v);writer=m.pc()
  if not ctx['enabled']:return
  r=m._registers;ds=m.DS*16;ss=r['ss']*16;scenario=ctx['scenario'];bp=ctx.get('bp',0)
  if scenario=='group-captured' and writer in (m.lin('0791:42F3'),m.lin('0791:4348')):
   fresh=0xa0000;m._memory[fresh:fresh+65538]=bytes(m._memory[ss:ss+65538]);put(m,fresh+((bp-2)&65535),0x7777,2);r['ss']=0xa000;ctx['restore_ss']=True;hit('captured-group-return')
  if scenario=='post-live':
   if writer in [m.lin('0791:'+x) for x in ('43AD','4398','43C2','4374')]:
    p=ctx['record'];put(m,p+9,0x0101,2);put(m,p+10,127);put(m,p+12,1);hit('post-live-record')
   if writer==m.lin('0791:43FC'):
    p=ctx['record'];put(m,p+9,255);put(m,p+11,7);hit('post-late-x')
  if scenario=='mirror-captured' and writer==m.lin('0791:2C9E'):
   put(m,ctx['argbase']+4,128);put(m,ds+0x8319,128);put(m,ds+0x831b,0,2);hit('captured-word-live-direction')
  if scenario=='clamp-captured' and writer in (m.lin('214B:2045'),m.lin('214B:2059')):
   base=ctx['argbase'];put(m,base,0,2);put(m,base+2,255,2);r['eax']=(r['eax']&0xffff00ff)|0x5a00;hit('captured-bounds-live-ah')
  if scenario=='extreme-captured' and writer==m.lin('214B:0000'):
   for k in range(0,8,2):put(m,ctx['argbase']+k,0x8888,2)
   r['eflags']^=0x400;hit('captured-long-flags')
  if scenario=='advanced-live-local' and writer==m.lin('214B:0000') and (r['eip']&65535) in (0x40e1,0x40e8):
   fresh=0xa0000;m._memory[fresh:fresh+65538]=bytes(m._memory[ss:ss+65538]);bp=r['ebp']&65535;put(m,fresh+((bp-1)&65535),1);r['ss']=0xa000;ctx['restore_ss']=True;hit('flushed-live-local')
  if scenario=='mark-captured' and writer==m.lin('0791:4A40'):
   put(m,ds+0xa91b,0x100,2);put(m,ds+0xa91d,0x9200,2);hit('captured-player-record')
 return OLD_WRITE[type(m)](m,lo,hi,wrapped)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);a=ap.parse_args();assert not Path(a.out).exists();e.verify();e.deny_original();before=e.hashes();rows={};start=time.monotonic()
 for cls in (Oracle,PortMachine):cls.at=at;cls.on_write=on_write
 try:
  for scenario in SCENARIOS:
   root={'group-captured':'0791:42CB','post-live':'0791:4354','mirror-captured':'0791:2C86','clamp-captured':'214B:2031','extreme-captured':'214B:0D1C','root-stack':ROOT,'advanced-live-local':'0791:40BC','mark-captured':'0791:4A28'}[scenario]
   row=rows[scenario]=dict(comparisons=0,hits={},effect_witnesses=0)
   for case in range(160):
    if scenario=='extreme-captured':root='214B:0D1C' if case%2 else '214B:0D56'
    opts=dict(root=root,controlled=root in CALLERS and scenario not in ('advanced-live-local',))
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
