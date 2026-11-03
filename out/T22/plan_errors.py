import json,sys
from pathlib import Path
sys.path[:0]=['engine/tests','engine/python','.cache/goal2-archaeology/runtime']
from test_offside import *
errors={};observed={}
for root in NEW:
 selectors=set();maxreads=maxwrites=0;witness={}
 for case in range(160):
  p,_,_=exercise(Oracle,case,root=root)
  assert p['error'] is None
  reads=0
  for event in p['log']:
   if event[0]=='io' and event[1]=='g':selectors.add('reg:'+str(event[2]))
   if event[0]=='io' and event[1]=='r':reads+=1
  maxreads=max(maxreads,reads);maxwrites=max(maxwrites,p['state']['write_index'])
  for pc in p['state']['writes']:
   # All own writes are at known exact source PCs; stack flush uses214B:0000.
   sites=['0791:8CF5','0791:8D1F','0791:8DA9','0791:8DC3','0791:8E24','0791:8EAC','0791:8EBA','0791:8EE5','0791:90C5','0791:90CE','0791:90F6','0791:9100','214B:0000']
   for site in sites:
    seg,ip=(int(x,16) for x in site.split(':'))
    if ((seg+0x823)&65535)*16+ip==pc:selectors.add('write:'+site)
 selectors|={root,'write'}
 selectors|={'read-index:'+str(i) for i in range(1,maxreads+1)}
 selectors|={'write-index:'+str(i) for i in range(1,maxwrites+1)}
 errors[root]=[dict(selector=s,controlled=False) for s in sorted(selectors)]
 observed[root]=dict(reads=maxreads,writes=maxwrites)
rows=sum(map(len,errors.values()));plan=dict(real_captures_per_body=8,authored_per_body=500,observer_modes=4,normal_comparisons=10288,body_control_comparisons=6288,output_control_comparisons=4192,return_control_comparisons=640,branch_comparisons=800,cases_per_error_selector=160,error_execution_rows=rows,distinct_error_selectors=len({r+'/'+v['selector'] for r,vs in errors.items() for v in vs}),error_comparisons=rows*160,errors=errors,variants={ROOT:['offside-max']},observed_maxima=observed)
assert plan['distinct_error_selectors']==rows
with open('out/T22/proof-plan-v1.json','x') as f:json.dump(plan,f,indent=2);f.write('\n')
print('SEALED',rows,'unique selectors',rows*160,'error comparisons',observed)
