"""Post-canonical all-inventory closure, including shared mem.s8/mem.s16."""
import hashlib,importlib,json,os,pickle,sys,time
from collections import Counter
from pathlib import Path
import evidence as e
OUT=e.BASE/'out/T22';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def bound():
 manifest=json.loads((OUT/'supplemental-source-inputs-v1.json').read_text())
 assert sha(OUT/'freeze-v1.json')==manifest['base_freeze_sha256']
 for p,h in manifest['source_sha256'].items():assert sha(e.BASE/p)==h,p
 return manifest['source_sha256'],sha(OUT/'supplemental-source-inputs-v1.json')
def main():
 if os.getpgrp()!=os.getpid():os.setsid()
 e.verify();assert not e.BASELINE;before=e.hashes();assert before==json.loads((OUT/'freeze-v1.json').read_text())['source_sha256']
 assert json.loads((OUT/'process-closure-v1.json').read_text())['pass_all'];extra,manifest_sha=bound()
 path=OUT/'shared-helper-closure-v1.json';assert not path.exists();start=time.monotonic();e.deny_original()
 sys.path.insert(0,str(e.BASE/'engine/tests'));import test_offside as t
 inv=json.loads((OUT/'inventory-v1.json').read_text());codes={}
 for body in inv['bodies'].values():
  for row in body['helper_symbols']:
   module,name=row['symbol'].rsplit('.',1);fn=getattr(importlib.import_module(module),name);codes[row['symbol']]=fn.__code__
 t.OWNED.clear();t.OWNED.update(codes.values());assert len(codes)==len(set(codes.values()))
 meta=json.loads((OUT/'captures-v1.json').read_text());raw=e.BASE/meta['private_file'];assert sha(raw)==meta['sha256'];captures=pickle.loads(raw.read_bytes())
 source=Counter();rows={root:dict(total=0,real=0,authored=0,outside_positive=0) for root in t.NEW};variants=0
 def pair(root,case,kind,**opts):
  p,_,ps=t.exercise(t.Oracle,case,root=root,profile=True,**opts);r,n,rs=t.exercise(t.PortMachine,case,root=root,profile=True,**opts)
  assert p['error'] is None and p==r,(root,case,kind,p['error'],r['error'])
  assert n.get(root)==1 and ps['owned'] and not rs['owned'] and rs['outside']>0,(root,case,rs)
  source.update(ps['owned']);row=rows[root];row['total']+=1;row[kind]+=1;row['outside_positive']+=rs['outside']>0
 for root in t.NEW:
  for case,snapshot in enumerate(captures[root]):
   for tapped in (False,True):
    for listener in (False,True):
     for schedule in range(3):pair(root,case,'real',snapshot=snapshot,tapped=tapped,listener=listener,pause=root if schedule==1 else None,direct=schedule==2)
  for case in range(500):
   for tapped in (False,True):
    for listener in (False,True):pair(root,case,'authored',tapped=tapped,listener=listener,pause=t.SITES[case%len(t.SITES)],direct=case%3==0,mutations=case%5==0)
  assert rows[root]==dict(total=2096,real=96,authored=2000,outside_positive=2096)
  print(root,rows[root],flush=True)
  for variant in ['identity']+(['offside-max'] if root==t.ROOT else []):
   for case in range(16):
    p,_,ps=t.exercise(t.Oracle,case,root=root,variant=variant,profile=True);r,n,rs=t.exercise(t.PortMachine,case,root=root,variant=variant,profile=True)
    assert p['error'] is None and p==r and root not in n and ps['owned'] and rs['owned'];variants+=1
 assert source['s8']>0 and source['s16']>0 and variants==64
 assert bound()==(extra,manifest_sha)
 report=dict(pass_all=True,comparisons=6288,variants=variants,rows=rows,owned_symbols=sorted(codes),source_owned_calls=dict(source),native_owned_calls={},shared_source_calls={k:source[k] for k in ['s8','s16']},all_native_lifetimes_zero_owned_python=True,supplemental_source_sha256=extra,source_manifest_sha256=manifest_sha,supplemental_source_unchanged=True,pid=os.getpid(),pgid=os.getpgrp(),wall_s=time.monotonic()-start)
 e.write(path,report,before);print('All inventoried helpers:6288 scoped pairs and64 variant probes pass',flush=True)
if __name__=='__main__':main()
