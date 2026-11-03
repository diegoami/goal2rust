"""Seal reachable keyboard/site/provider/ordinal fault selectors;no original data."""
import json,sys
sys.path[:0]=['engine/tests','engine/python','.cache/goal2-archaeology/runtime']
from test_keyboard import *
errors={};observed={}
for root in NEW:
 selectors={root};reads=set();writes=set();maxw=0
 for case in range(160):
  p,_,_=exercise(Oracle,case,root=root);assert p['error'] is None,(root,case,p['error'])
  for ev in p['log']:
   if ev[0]=='io' and ev[1]=='g':selectors.add('reg:'+str(ev[2]))
  reads.update(range(1,p['state']['read_index']+1));writes.update(range(1,p['state']['write_index']+1));maxw=max(maxw,p['state']['write_index'])
  for pc in p['state']['writes']:
   for site in ['214B:0000','214B:08DD','214B:08EA','214B:097C','214B:098A','214B:0996','214B:099E']:
    seg,ip=(int(x,16) for x in site.split(':'))
    if ((seg+0x823)&65535)*16+ip==pc:selectors.add('write:'+site)
 if writes:selectors.add('write')
 selectors|={'read-index:'+str(i) for i in reads}|{'write-index:'+str(i) for i in writes}
 if root=='214B:0723':selectors|={'missing-kit','poll','truth'}
 if root in ['214B:08DD',ROOT]:selectors|={'missing-kit','key','decision-stop'}
 if root==ROOT:selectors|={'214B:08DD','214B:098A'}
 errors[root]=[dict(selector=s,controlled=False) for s in sorted(selectors)];observed[root]=dict(max_reads=max(reads,default=0),max_writes=maxw)
rows=sum(map(len,errors.values()));plan=dict(real_captures_per_body=8,authored_per_body=500,observer_modes=4,normal_comparisons=10384,body_control_comparisons=8384,output_control_comparisons=16768,return_control_comparisons=160,branch_comparisons=800,cases_per_error_selector=160,error_execution_rows=rows,distinct_error_selectors=len({r+'/'+v['selector'] for r,vs in errors.items() for v in vs}),error_comparisons=rows*160,errors=errors,variants={},observed_maxima=observed)
assert plan['distinct_error_selectors']==rows
with open('out/T24/proof-plan-v1.json','x') as f:json.dump(plan,f,indent=2);f.write('\n')
print('SEALED',rows,'distinct reached selectors',rows*160,'error pairs',observed)
