"""Four distinct post-return own-write failures at shared guest return PCs."""
import hashlib,json,os,sys,time
from pathlib import Path
import evidence as e
sys.path.insert(0,str(e.BASE/'engine/tests'))
from test_depth import Oracle,PortMachine,exercise
OUT=e.BASE/'out/T21';ctx={};OLD_AT={c:c.at for c in (Oracle,PortMachine)};OLD_WRITE={c:c.on_write for c in (Oracle,PortMachine)}
def at(m,site,fn):
 def wrapped(replay):
  fn(replay)
  if site==ctx['root']:
   ctx['sp']=m._registers['esp']&65535;ctx['ss']=m._registers['ss']*16
  if site==ctx['site']:ctx['returned']=True
 return OLD_AT[type(m)](m,site,wrapped)
def on_write(m,lo,hi,fn):
 def wrapped(a,n,v):
  fn(a,n,v)
  if ctx['enabled'] and ctx['returned'] and m.pc()==m.lin(ctx['site']) and n==ctx['size']:
   expected=ctx['ss']+((ctx['sp']-ctx['delta'])&65535)
   assert a==expected,(a,expected)
   ctx['hits'].append(dict(address=a,size=n,after_return=True))
   raise ValueError('depth write refused')
 return OLD_WRITE[type(m)](m,lo,hi,wrapped)
def run(cls,case,row,enabled=True,legacy=False):
 ctx.clear();ctx.update(root=row['root'],site=row['site'],size=row['size'],delta=row['frame_delta'],returned=False,hits=[],enabled=enabled)
 result=exercise(cls,case,root=row['root'],controlled=True,failure=('write:'+row['site']) if legacy else row['selector'])
 return result[0],list(ctx['hits']),ctx['returned']
def main():
 e.verify();before=e.hashes();assert before==json.loads((OUT/'freeze-v1.json').read_text())['source_sha256'];e.deny_original()
 plan=json.loads((e.BASE/'out/T19/proof-plan-v2.json').read_text());manifest=json.loads((e.BASE/'out/T19/supplemental-source-inputs-v2.json').read_text())
 for p,h in manifest['source_sha256'].items():assert hashlib.sha256((e.BASE/p).read_bytes()).hexdigest()==h
 assert hashlib.sha256((e.BASE/'out/T19/proof-plan-v1.json').read_bytes()).hexdigest()==plan['preserved_plan_sha256']
 rows={};start=time.monotonic()
 for cls in (Oracle,PortMachine):cls.at=at;cls.on_write=on_write
 try:
  for item in plan['additional_selectors']:
   row=rows[item['selector']]=dict(total=0,reached=0,equal=0,legacy_pre_return_witnesses=0)
   for case in range(plan['cases_per_selector']):
    p,ph,returned=run(Oracle,case,item);r,rh,_=run(PortMachine,case,item)
    assert p==r and ph==rh,(item,case,[k for k in p if p[k]!=r[k]],ph,rh)
    assert (p['error'] is not None)==bool(ph)
    if ph:
     assert p['error']==('ValueError','depth write refused') and returned
     base,_,_=run(Oracle,case,item,enabled=False);assert base['error'] is None and p!=base
     old,old_hits,old_returned=run(Oracle,case,item,enabled=False,legacy=True)
     assert old['error'] is not None and not old_returned and not old_hits
     row['legacy_pre_return_witnesses']+=1
    row['total']+=1;row['reached']+=bool(ph);row['equal']+=p==r
   assert row['reached']>0 and row['equal']==row['total']==160 and row['legacy_pre_return_witnesses']==row['reached']
   print(item['selector'],row,flush=True)
 finally:
  for cls in (Oracle,PortMachine):cls.at=OLD_AT[cls];cls.on_write=OLD_WRITE[cls]
 assert len(rows)==4 and sum(r['total'] for r in rows.values())==640
 report=dict(pass_all=True,comparisons=640,selectors=rows,script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),supplemental_source_sha256=manifest['source_sha256'],runtime_unchanged=True,pid=os.getpid(),pgid=os.getpgrp(),wall_s=time.monotonic()-start)
 e.write(OUT/'scoped-write-errors-v1.json',report,before)
if __name__=='__main__':main()
