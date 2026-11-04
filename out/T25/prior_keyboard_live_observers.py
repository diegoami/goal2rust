"""Eight keyboard-specific live callback/frame witnesses,160 comparisons each."""
import argparse,hashlib,json,os,sys,time
from pathlib import Path
import evidence as e
sys.path.insert(0,str(e.BASE/'engine/tests'))
from test_keyboard import *
SCENARIOS=('poll-live-AH-truth','poll-two-live-SS-reads','read-ignore-provider-value','pushed-live-key-AH','push-flag-before-cached-flush-live-SS','push-cached-AH','wait-ignore-SENT','key-stop-refusal')
OLD_MEM={c:c.port_memory for c in (Oracle,PortMachine)};OLD_AT={c:c.at for c in (Oracle,PortMachine)};OLD_WRITE={c:c.on_write for c in (Oracle,PortMachine)};ctx={}
def put(m,a,v,n=1):m._memory[a:a+n]=(v&((1<<(8*n))-1)).to_bytes(n,'little')
def hit(k):ctx['hits'][k]=ctx['hits'].get(k,0)+1
def memory(m,keys=None):
 result=OLD_MEM[type(m)](m,keys);ctx['mem']=result;return result
def at(m,site,fn):
 def wrapped(replay):
  fn(replay)
  r=m._registers;ds=m.DS*16;s=ctx['scenario']
  if site==ctx['root'] and not replay:
   ctx.update(ss=r['ss']*16,sp=r['esp']&65535,root_entered=True)
   put(m,ds+0x79ae,1 if s=='pushed-live-key-AH' else 0)
   if ctx['root']=='214B:0993':put(m,ctx['ss']+((ctx['sp']+4)&65535),0xab7e,2)
   provider=ctx['mem'].keys
   if s in ('poll-live-AH-truth','poll-two-live-SS-reads'):
    original=provider.keypressed
    def poll(where):
     value=original(where)
     if ctx['mutate']:
      if s=='poll-two-live-SS-reads':
       assert where.endswith(':BEEF'),where;r['ss']=ctx['ss']//16;hit('split-return-site-and-restore-SS')
      else:
       class Truth:
        def __bool__(self):r['eax']=(r['eax']&0xffff0000)|0xbe55;hit('AH-read-after-provider-truth');return bool(ctx['case']%2)
       return Truth()
     return value
    provider.keypressed=poll
   if s in ('read-ignore-provider-value','key-stop-refusal'):
    original=provider.key
    def key(where):
     result=original(where)
     if ctx['mutate']:
      if s=='read-ignore-provider-value':r['eax']=(r['eax']&0xffff0000)|0xbeef;hit('live-AX-versus-ignored-provider-return');return 0x12345678
      m.stop('decision');hit('nondeferrable-stop-after-key-effects')
     return result
    provider.key=key
  if site=='214B:098A' and s=='wait-ignore-SENT':ctx['returned']=True
 return OLD_AT[type(m)](m,site,wrapped)
def on_write(m,lo,hi,fn):
 oldio=m.io_tap
 def io(kind,name,value):
  if oldio:oldio(kind,name,value)
  if not ctx['mutate'] or not ctx.get('root_entered'):return
  r=m._registers;s=ctx['scenario']
  if s=='poll-two-live-SS-reads' and kind=='g' and name=='ss':
   ctx['ss_reads']=ctx.get('ss_reads',0)+1
   if ctx['ss_reads']==2:
    newss=0x90000;m._memory[newss:newss+65538]=bytes(m._memory[ctx['ss']:ctx['ss']+65538]);put(m,newss+(ctx['sp']&65535),0xbeef,2);r['ss']=0x9000;hit('SS-changed-after-first-return-word-address')
  if s=='wait-ignore-SENT' and ctx.get('returned') and kind=='g' and name=='ax' and not ctx.get('changed'):
   r['eax']=(r['eax']&0xffff0000)|0xfede;ctx['changed']=True;hit('actual-AX-changed-after-SENT-capture')
 m.io_tap=io
 def wrapped(a,n,v):
  fn(a,n,v)
  if not ctx['mutate']:return
  r=m._registers;ds=m.DS*16;s=ctx['scenario'];pc=m.pc()
  if s=='pushed-live-key-AH' and pc==m.lin('214B:08EA'):
   put(m,ds+0xa976,0xe7);r['eax']=(r['eax']&0xffff0000)|0xab34;hit('pushed-key-and-AH-read-after-flag-clear')
  if s=='push-flag-before-cached-flush-live-SS':
   if pc==m.lin('214B:0996'):
    newss=0x90000;m._memory[newss:newss+65538]=bytes(m._memory[ctx['ss']:ctx['ss']+65538]);put(m,newss+((ctx['sp']+4)&65535),0xee);r['ss']=0x9000;ctx['flag_seen']=True;hit('flag-before-queued-frame-flush')
   elif pc==m.lin('214B:0000'):
    assert ctx.get('flag_seen') and ctx['ss']<=a<ctx['ss']+65536;hit('queued-frame-keeps-cached-SS')
   elif pc==m.lin('214B:099E'):
    assert v==0xee,v;r['ss']=ctx['ss']//16;hit('argument-read-with-live-SS')
  if s=='push-cached-AH':
   if pc==m.lin('214B:0000'):r['eax']=(r['eax']&0xffff0000)|0xab00;hit('AH-live-after-frame-flush')
   elif pc==m.lin('214B:099E'):r['eax']=(r['eax']&0xffff0000)|0xcd00;hit('cached-AX-survives-key-write-callback')
 return OLD_WRITE[type(m)](m,lo,hi,wrapped)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);a=ap.parse_args();assert not Path(a.out).exists();e.verify();before=e.hashes();e.deny_original();start=time.monotonic();rows={}
 for c in (Oracle,PortMachine):c.port_memory=memory;c.at=at;c.on_write=on_write
 try:
  for s in SCENARIOS:
   root='214B:0723' if s.startswith('poll-') else '214B:0993' if s.startswith('push-') else ROOT if s.startswith('wait-') else '214B:08DD'
   row=rows[s]=dict(comparisons=0,hits={},effect_witnesses=0)
   for case in range(160):
    def run(cls,mutate):
     ctx.clear();ctx.update(scenario=s,root=root,case=case,mutate=mutate,hits={});p,_,_=exercise(cls,case,root=root);return p,dict(ctx['hits'])
    p,ph=run(Oracle,True);r,rh=run(PortMachine,True);assert p==r and ph==rh,(s,case,p['error'],r['error'],[k for k in p if p[k]!=r[k]],ph,rh)
    if s=='key-stop-refusal':assert p['error'] and p['error'][0]=='PortError'
    else:assert p['error'] is None,(s,case,p['error'])
    base,_=run(Oracle,False);row['comparisons']+=1;row['effect_witnesses']+=p!=base
    if s=='read-ignore-provider-value':assert p['regs']['eax']&65535==0xbeef
    if s=='wait-ignore-SENT':assert p['regs']['eax']&65535==0xfede
    if s=='push-cached-AH':assert p['regs']['eax']&65535==0xab7e
    for k,v in ph.items():row['hits'][k]=row['hits'].get(k,0)+v
   assert row['effect_witnesses']>0 and row['hits'] and all(row['hits'].values()),(s,row)
   print(s,row,flush=True)
 finally:
  for c in (Oracle,PortMachine):c.port_memory=OLD_MEM[c];c.at=OLD_AT[c];c.on_write=OLD_WRITE[c]
 e.write(a.out,dict(pass_all=True,comparisons=1280,scenarios=rows,pid=os.getpid(),pgid=os.getpgrp(),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),wall_s=time.monotonic()-start),before)
if __name__=='__main__':main()
