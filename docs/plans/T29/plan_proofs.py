"""Prepared T29 proof-plan producer; install/run only after development exits.

No selector or branch count is sealed until every row is positively reached.
"""
import argparse,hashlib,json,re,sys
from pathlib import Path
import capture_support as e
e.verify();e.deny_original()
sys.path[:0]=[str(e.BASE/'engine/tests'),str(e.BASE/'engine/python')]
from test_near_zone import *
from branch_probe import Probe
from host_gate import wait_idle
wait_idle()
parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);a=parser.parse_args();assert not Path(a.out).exists()
probe=Probe();errors={};maxima={}
for root in NEW:
 selectors={root};maxr=maxw=0;writes=set()
 for controlled in ([False,True] if INV['bodies'][root]['sites'] else [False]):
  for case in range(160):
   sys.settrace(probe.trace)
   try:p,_,_=exercise(Oracle,case,root=root,controlled=controlled)
   finally:sys.settrace(None)
   assert p['error'] is None,(root,case,p['error'])
   r,_,_=exercise(PortMachine,case,root=root,controlled=controlled);assert p==r,(root,case,controlled,[k for k in p if p[k]!=r[k]])
   if not controlled:
    selectors.update(site for site,_ in p['visits']);selectors.update('reg:'+str(v[2]) for v in p['log'] if v[0]=='io' and v[1]=='g')
    writes.update(p['state']['writes']);maxr=max(maxr,p['state']['read_index']);maxw=max(maxw,p['state']['write_index'])
 def ordinals(n):return sorted({i for i in [1,2,3,4,8,9,n//2,n] if 1<=i<=n})
 reads=ordinals(maxr);stores=ordinals(maxw)
 selectors.update('read-index:'+str(i) for i in reads);selectors.update('write-index:'+str(i) for i in stores);selectors.update('write:'+str(pc) for pc in writes)
 if maxw:selectors.add('write')
 errors[root]=[dict(selector=s,controlled=False) for s in sorted(selectors)]
 maxima[root]=dict(max_reads=maxr,max_writes=maxw,selected_read_ordinals=reads,selected_write_ordinals=stores,observed_write_pcs=sorted(writes))
 print('OBSERVED',root,len(selectors),'selectors',flush=True)
missing=[key for key,value in probe.counts.items() if not value];print('MISSING',missing,flush=True);assert not missing,missing
reached_errors={}
for root,selectors in errors.items():
 for row in selectors:
  key=root+'/'+row['selector']
  for case in range(160):
   opts=dict(root=root,failure=row['selector'],controlled=row['controlled'])
   p,_,_=exercise(Oracle,case,**opts)
   r,_,_=exercise(PortMachine,case,**opts)
   assert p==r,('preseal-error',key,case,[k for k in p if p[k]!=r[k]])
   if p['error'] is not None:
    reached_errors[key]=dict(case=case,error=p['error'])
    break
  else:raise AssertionError(('unreached preseal selector',key))
  print('REACHED',key,'case',case,flush=True)
rows=sum(len(v) for v in errors.values());distinct=len({root+'/'+v['selector'] for root,vs in errors.items() for v in vs});assert rows==distinct
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report=dict(real_captures_per_body=8,authored_per_body=500,observer_modes=4,normal_comparisons=4096,body_control_comparisons=2096,output_control_comparisons=14672,return_control_comparisons=160,branch_comparisons=320,cases_per_error_selector=160,error_execution_rows=rows,distinct_error_selectors=distinct,error_comparisons=rows*160,errors=errors,observed_maxima=maxima,branch_outcomes=sorted(probe.counts),branch_exclusions=probe.exclusions,body_controls={root:436+i for i,root in enumerate(NEW)},output_controls=[dict(root=root,control=c) for root,c in OUTPUTS],return_controls=[dict(**v,control=444+i) for i,v in enumerate(INV['guest_sites'])],variants={'0791:44C1':['depth-plus-one','marking-no-copy','keeper-no-state']},ordinal_scope='Bounded observed early/middle/last read AND write ordinals,plus every observed write PC/register/site;not exhaustive global fault coverage',test_source_sha256=sha(e.BASE/'engine/tests/test_near_zone.py'),inventory_sha256=sha(e.BASE/'out/T29/inventory-v1.json'),branch_probe_sha256=sha(e.BASE/'out/T29/branch_probe.py'))
assert len(reached_errors)==rows
report['preseal_reached_errors']=reached_errors
with Path(a.out).open('x') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
print('SEALED',rows,'distinct selectors,',len(probe.counts),'positive edge/branch outcomes',flush=True)
