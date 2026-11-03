"""Diagnostic full authored/real input sweep before final proof-source freeze."""
import json,pickle,sys
from pathlib import Path
sys.path[:0]=['engine/tests','engine/python','.cache/goal2-archaeology/runtime']
from test_text import *
meta=json.loads(Path('out/T25/captures-v1.json').read_text());captures=pickle.loads(Path(meta['private_file']).read_bytes())
for root in NEW:
 for case in range(500):
  opts=dict(root=root,profile=True,mutations=case%5==0,pause=SITES[case%len(SITES)],direct=case%3==0)
  p,_,ps=exercise(Oracle,case,**opts);r,n,rs=exercise(PortMachine,case,**opts)
  assert p['error'] is None,(root,case,p['error'])
  assert p==r,(root,case,[k for k in p if p[k]!=r[k]])
  assert n.get(root)==1 and ps['owned'] and not rs['owned'] and rs['outside']>0
  if case%100==99:print('AUTHORED',root,case+1,flush=True)
 for case,snapshot in enumerate(captures[root]):
  for tapped in (False,True):
   for listener in (False,True):
    for schedule in range(3):
     opts=dict(root=root,snapshot=snapshot,tapped=tapped,listener=listener,direct=schedule==2,pause=root if schedule==1 else None,profile=True)
     p,_,ps=exercise(Oracle,case,**opts);r,n,rs=exercise(PortMachine,case,**opts)
     assert p['error'] is None and p==r,(root,'real',case,schedule,p['error'],r['error'],[k for k in p if p[k]!=r[k]])
     assert n.get(root)==1 and ps['owned'] and not rs['owned']
 print('REAL',root,96,flush=True)
print('All six500 authored plus576 real schedules pass;diagnostic only,canonical gates remain',flush=True)
