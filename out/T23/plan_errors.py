"""Seal positively reachable program-site and representative ordinal errors."""
import json,sys
from pathlib import Path
sys.path[:0]=['engine/tests','engine/python','.cache/goal2-archaeology/runtime']
from test_pascal import *
errors={};observed={}
for root in NEW:
 selectors={root,'write'};reads=set();ordinals=set();maxwrite=0
 for case in range(160):
  p,_,_=exercise(Oracle,case,root=root);assert p['error'] is None
  for event in p['log']:
   if event[0]=='io' and event[1]=='g':selectors.add('reg:'+str(event[2]))
  maxwrite=max(maxwrite,p['state']['write_index']);reads.update(range(1,p['state']['read_index']+1));ordinals.update(range(1,p['state']['write_index']+1))
  for pc in p['state']['writes']:
   for site in ['23E4:0638','23E4:063D','23E4:065C','23E4:0661','23E4:06CA','23E4:06CF','23E4:06DC']:
    seg,ip=(int(x,16) for x in site.split(':'))
    if ((seg+0x823)&65535)*16+ip==pc:selectors.add('write:'+site)
 selectors|={'read-index:'+str(i) for i in reads}
 selected_ordinals=ordinals&{1,2,3,8,9,10,16,17,65,128,255,256}
 selectors|={'write-index:'+str(i) for i in selected_ordinals}
 errors[root]=[dict(selector=s,controlled=False) for s in sorted(selectors)];observed[root]=dict(max_writes=maxwrite,selected_write_ordinals=sorted(selected_ordinals))
rows=sum(map(len,errors.values()));plan=dict(real_captures_per_body=8,authored_per_body=500,observer_modes=4,normal_comparisons=6288,body_control_comparisons=6288,output_control_comparisons=25152,guest_sites=0,branch_comparisons=480,cases_per_error_selector=160,error_execution_rows=rows,distinct_error_selectors=len({r+'/'+v['selector'] for r,vs in errors.items() for v in vs}),error_comparisons=rows*160,errors=errors,variants={},observed_maxima=observed)
assert plan['distinct_error_selectors']==rows
with open('out/T23/proof-plan-v1.json','x') as f:json.dump(plan,f,indent=2);f.write('\n')
print('SEALED',rows,'unique selectors',rows*160,'error pairs',observed)
