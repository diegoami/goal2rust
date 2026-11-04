"""Eight source-specific callback witnesses;semantic effects,not log-only deltas."""
import argparse,hashlib,json,os,sys,time
from pathlib import Path
import capture_support as pure
sys.path[:0]=[str(pure.BASE/'engine/tests'),str(pure.BASE/'engine/python')]
from test_strength import *

SCENARIOS=('bit-cached-arguments-live-flags','manager-live-SS-argument',
 'two-foot-captured-pointer-live-bytes','foot-cached-id-live-table',
 'gcall-sent-AX-live-DX-CS','strength-captured-v-after-place',
 'quick-live-record-locals','quick-pop-captures-segment-before-flush')
ROOTS=['214B:0C57','1771:0AA7','1771:3041','1771:3088','1771:3179','1771:377E','1771:0BC4','1771:0BC4']
OLD_AT={c:c.at for c in (Oracle,PortMachine)};OLD_WRITE={c:c.on_write for c in (Oracle,PortMachine)};ctx={}
def put(m,a,v,n=1):m._memory[a:a+n]=(v&((1<<(8*n))-1)).to_bytes(n,'little')
def hit(key):ctx['hits'][key]=ctx['hits'].get(key,0)+1
def at(m,site,fn):
 def wrapped(replay):
  fn(replay);r=m._registers;scenario=ctx['scenario'];ds=m.DS*16
  if site==ctx['root'] and not replay:
   ss=r['ss']*16;old=r['esp']&65535;sp=0xe000
   for i in range(2):
    a=ss+((old+2*i)&65535);put(m,ss+sp+2*i,int.from_bytes(m._memory[a:a+2],'little'),2)
   r['esp']=(r['esp']&0xffff0000)|sp;ctx.update(ss=ss,sp=sp,bp=sp-2)
   packet=[0x8001,33] if scenario==SCENARIOS[0] else [0] if scenario==SCENARIOS[1] else [0,0,0] if scenario in SCENARIOS[6:] else [1]
   for i,v in enumerate(packet):put(m,ss+sp+4+2*i,v,2)
   if scenario==SCENARIOS[1]:
    put(m,0x50100+0x2e,0);put(m,0x50100+191+0x2e,1)
    put(m,0x70101,0);put(m,0x70104,255)
   if scenario==SCENARIOS[2]:put(m,0x60214+5,15);put(m,0x60214+2,14)
   if scenario==SCENARIOS[3]:
    put(m,0x60214+7,3);put(m,ds+0xe7d,0);put(m,ds+0xe60+3,1);put(m,ds+0xe60+31,9)
   if scenario==SCENARIOS[5]:
    for off,v in [(4,128),(14,64),(12,0),(16,0)]:put(m,0x60214+off,v)
   if scenario in SCENARIOS[6:]:
    for slot in range(1,12):put(m,0x50100+2*(slot-1),1 if scenario==SCENARIOS[6] and slot==1 else 0,2)
    put(m,0x60214+6,0);put(m,0x60228+6,3);put(m,ds+0xd4e,0);put(m,ds+0xd51,4)
  if scenario==SCENARIOS[4]:
   if site=='1771:319A':
    r['eax']=(r['eax']&0xffff0000)|1;ctx['foot_returned']=True
   if site=='1771:31A4':
    r['eax']&=0xffffff00
    if ctx['mutate']:r['cs']=0x4000;hit('live-CS-after-second-guest')
  if scenario==SCENARIOS[5]:
   if site=='1771:379F':r['eax']&=0xffffff00
   if site=='1771:3808':
    r['eax']=(r['eax']&0xffff0000)|1;r['edx']=(r['edx']&0xffff0000)|7
    if ctx['mutate']:
     put(m,0x60214+4,255);put(m,0x60214+14,127);put(m,0x60214+12,125);hit('captured-v-survives-live-record-change')
  if scenario==SCENARIOS[6]:
   if site=='1771:0BE5':r['eax']=(r['eax']&0xffff0000)|16
   if site=='1771:0C5C':
    r['eax']=(r['eax']&0xffff0000)|128
    if ctx['mutate']:
     put(m,ctx['ss']+ctx['bp']-17,0x228,2);put(m,ctx['ss']+ctx['bp']-15,0x6000,2);hit('live-record-locals-after-strength')
 return OLD_AT[type(m)](m,site,wrapped)
def on_write(m,lo,hi,fn):
 oldio=m.io_tap
 def io(kind,a,v):
  oldio(kind,a,v)
  if ctx['scenario']==SCENARIOS[4] and ctx['mutate'] and ctx.get('foot_returned') and not ctx.get('sent_changed') and kind=='g' and a=='ax':
   m._registers['eax']&=0xffffff00;m._registers['edx']=(m._registers['edx']&0xffff0000)|0xbeef;ctx['sent_changed']=True;hit('captured-sent-versus-new-live-AX-DX')
 m.io_tap=io
 def wrapped(a,n,v):
  fn(a,n,v);pc=m.pc()
  if not ctx['mutate']:return
  scenario=ctx['scenario'];r=m._registers;ds=m.DS*16
  if scenario==SCENARIOS[0] and pc==m.lin('214B:0000'):
   r['eax']^=0xff00;r['ecx']^=0x1234;r['eflags']^=0x800;hit('cached-arguments-preserved-other-flags-live')
  elif scenario==SCENARIOS[1]:
   if pc==m.lin('1771:0AA7'):
    alt=0x90000;m._memory[alt:alt+65536]=m._memory[ctx['ss']:ctx['ss']+65536];put(m,alt+(a-ctx['ss']),v,n);put(m,alt+ctx['sp']+4,1,2);r['ss']=0x9000;hit('argument-live-SS-after-enter')
   elif pc==m.lin('1771:0AE4'):r['ss']=ctx['ss']//16;hit('restore-SS-after-manager-local')
  elif scenario==SCENARIOS[2] and pc==m.lin('1771:3055'):
   put(m,ds+0xa91b,0x100,2);put(m,ds+0xa91d,0x7000,2);put(m,0x60214+5,29);put(m,0x60214+2,1);hit('captured-pointer-live-two-bytes')
  elif scenario==SCENARIOS[3] and pc==m.lin('1771:3088'):
   put(m,ctx['ss']+ctx['sp']+4,2,2);put(m,ds+0xe7d,2);hit('cached-player-id-live-row-table')
  elif scenario==SCENARIOS[7] and pc==m.lin('214B:0000') and a==ctx['ss']+ctx['bp']-20:
   alt=0x90000;m._memory[alt:alt+65536]=m._memory[ctx['ss']:ctx['ss']+65536];put(m,alt+(a-ctx['ss']),1,2);r['ss']=0x9000;hit('pop-segment-captured-before-pending-flush')
 return OLD_WRITE[type(m)](m,lo,hi,wrapped)
def run(cls,case,scenario,mutate):
 ctx.clear();ctx.update(root=ROOTS[SCENARIOS.index(scenario)],scenario=scenario,mutate=mutate,hits={})
 result,_,_=exercise(cls,case,root=ctx['root'],controlled=scenario in SCENARIOS[4:])
 assert result['error'] is None,(scenario,case,cls.__name__,result['error'])
 if mutate:
  assert ctx['hits'],(scenario,case)
  if scenario==SCENARIOS[0]:assert result['regs']['eax']&65535==1 and result['regs']['edx']&65535==32 and result['regs']['ecx']&65535==32
  if scenario==SCENARIOS[1]:assert result['regs']['eax']&65535==47
  if scenario==SCENARIOS[2]:assert result['regs']['eax']&255==1
  if scenario==SCENARIOS[3]:assert result['regs']['eax']&255==9
  if scenario==SCENARIOS[4]:
   foot=[v for v in result['log'] if v[0]=='w' and v[4]==((0x1771+0x823)*16+0x319a)];assert foot and foot[0][3]==1
   packets=[v[2] for v in result['log'] if v[0]=='abi' and v[1]=='23E4:08DF'];assert packets and packets[0][1]==0x4000
  if scenario==SCENARIOS[5]:assert result['regs']['eax']&65535==65
  if scenario==SCENARIOS[7]:
   packets=[v[2] for v in result['log'] if v[0]=='abi' and v[1]=='1771:0AA7'];assert packets==[(0,)]
 return result,dict(ctx['hits'])
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);parser.add_argument('--development',action='store_true');a=parser.parse_args()
 pure.verify();assert not Path(a.out).exists();import goal2rust_engine
 files=sorted((pure.BASE/'engine/src').glob('*.rs'))+[Path(__file__),pure.BASE/'engine/tests/test_strength.py']+sorted(Path(goal2rust_engine.__file__).parent.glob('*.so'))
 sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 if a.development:before={str(p.relative_to(pure.BASE)):sha(p) for p in files}
 else:
  import evidence as e
  before=e.hashes()
 archived={}
 if a.development:
  folder=pure.BASE/'.cache/T27-development-sources';folder.mkdir(exist_ok=True)
  for p in files:
   target=folder/sha(p)
   if not target.exists():
    with target.open('xb') as f:f.write(p.read_bytes())
   archived[str(p.relative_to(pure.BASE))]=str(target.relative_to(pure.BASE))
 start=time.monotonic();rows={}
 for cls in (Oracle,PortMachine):cls.at=at;cls.on_write=on_write
 try:
  for scenario in SCENARIOS:
   row=rows[scenario]=dict(comparisons=0,effect_witnesses=0,hits={})
   for case in range(160):
    p,ph=run(Oracle,case,scenario,True);r,rh=run(PortMachine,case,scenario,True);assert p==r and ph==rh,(scenario,case,[k for k in p if p[k]!=r[k]])
    baseline,_=run(Oracle,case,scenario,False);row['comparisons']+=1;row['effect_witnesses']+=any(p[k]!=baseline[k] for k in ['memory','regs','calls'])
    for key,value in ph.items():row['hits'][key]=row['hits'].get(key,0)+value
   assert row['effect_witnesses']>0 and all(row['hits'].values()),(scenario,row)
   print(scenario,row,flush=True)
 finally:
  for cls in (Oracle,PortMachine):cls.at=OLD_AT[cls];cls.on_write=OLD_WRITE[cls]
 report=dict(pass_all=True,comparisons=1280,scenarios=rows,pid=os.getpid(),pgid=os.getpgrp(),script_sha256=sha(Path(__file__)),wall_s=time.monotonic()-start)
 if a.development:
  assert before=={str(p.relative_to(pure.BASE)):sha(p) for p in files};report.update(development_only=True,accepted_canonical_evidence=False,executed_source_sha256=before,preserved_source_map=archived)
  with Path(a.out).open('x') as f:json.dump(report,f,indent=2,sort_keys=True)
 else:e.write(a.out,report,before)
if __name__=='__main__':main()
