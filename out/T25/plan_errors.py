"""Seal observed reachable sites/registers and bounded early/mid/last ordinals."""
import hashlib,json,sys
from pathlib import Path
sys.path[:0]=['engine/tests','engine/python','.cache/goal2-archaeology/runtime']
from test_text import *
errors={};observed={};programs=['214B:0000','214B:0119','214B:013D','214B:0223','214B:02E6','23E4:065C','23E4:0661']+list(RETURNS)
for root in NEW:
 selectors={root};maxr=maxw=0;write_sites=set()
 for case in range(160):
  p,_,_=exercise(Oracle,case,root=root);assert p['error'] is None,(root,case,p['error'])
  selectors.update('reg:'+str(ev[2]) for ev in p['log'] if ev[0]=='io' and ev[1]=='g')
  selectors.update(site for site,_ in p['visits']);maxr=max(maxr,p['state']['read_index']);maxw=max(maxw,p['state']['write_index'])
  for pc in p['state']['writes']:
   matches=[site for site in programs if ((int(site[:4],16)+0x823)&65535)*16+int(site[5:],16)==pc];assert len(matches)==1,(root,pc);write_sites.update(matches)
 selectors.update('write:'+site for site in write_sites)
 selectors.update('read-index:'+str(i) for i in range(1,maxr+1))
 ordinal=sorted({i for i in [1,2,3,4,8,9,maxw//2,maxw] if 1<=i<=maxw})
 selectors.update('write-index:'+str(i) for i in ordinal)
 if maxw:selectors.add('write')
 errors[root]=[dict(selector=s,controlled=False) for s in sorted(selectors)]
 observed[root]=dict(max_reads=maxr,max_writes=maxw,selected_write_ordinals=ordinal,program_write_sites=sorted(write_sites))
 print('OBSERVED',root,len(selectors),observed[root],flush=True)
rows=sum(map(len,errors.values()));distinct=len({root+'/'+r['selector'] for root,vs in errors.items() for r in vs});assert rows==distinct
plan=dict(real_captures_per_body=8,authored_per_body=500,observer_modes=4,normal_comparisons=20576,body_control_comparisons=12576,output_control_comparisons=88032,return_control_comparisons=1280,branch_comparisons=1600,cases_per_error_selector=160,error_execution_rows=rows,distinct_error_selectors=distinct,error_comparisons=rows*160,errors=errors,variants={r:['omit-'+r.lower().replace(':','-')] for r in NEW},observed_maxima=observed,ordinal_scope='Observed early/mid/last write ordinals, not exhaustive global fault coverage',test_source_sha256=hashlib.sha256(Path('engine/tests/test_text.py').read_bytes()).hexdigest(),inventory_sha256=hashlib.sha256(Path('out/T25/inventory-v2.json').read_bytes()).hexdigest())
with Path('out/T25/proof-plan-v1.json').open('x') as f:json.dump(plan,f,indent=2,sort_keys=True);f.write('\n')
print('SEALED',rows,'rows',distinct,'distinct selectors',rows*160,'error pairs',flush=True)
