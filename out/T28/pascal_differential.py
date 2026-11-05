"""Fixed combined-artifact T23 per-body/integrated/errors/control proof."""
import argparse,hashlib,json,pickle,sys,time
import evidence as e
sys.path.insert(0,str(e.BASE/'engine/tests'))
from test_pascal import *
# The shared outside-scope probe must itself be tracked. This strengthens the
# inside-scope assertion and preserves its explicit outside-scope witness.
OWNED.add(positioning.pitch.__code__)
from prior_pascal_branch_probe import Probe
INV=json.loads((e.BASE/'out/T23/inventory-v1.json').read_text())

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);ap.add_argument('--suite',required=True,choices=['normal','body','output','returns']);a=ap.parse_args()
 assert not e.Path(a.out).exists();e.verify();before=e.hashes();e.deny_original();start=time.monotonic()
 meta=json.loads((e.BASE/'out/T23/captures-v1.json').read_text());file=e.BASE/meta['private_file'];assert hashlib.sha256(file.read_bytes()).hexdigest()==meta['sha256'];captures=pickle.loads(file.read_bytes())
 plan=json.loads((e.BASE/'out/T23/proof-plan-v1.json').read_text());assert all(len(captures[r])==8 for r in NEW)
 owned_calls={};comparisons={};differences=[];closure={};errors={};error_comparisons=0;return_controls={};variants=0;branches=None;writes={r:set() for r in NEW};seen={r:set() for r in NEW}
 def pair(root,case,kind,mutant=0,**opts):
  p,_,ps=exercise(Oracle,case,root=root,**opts);r,n,rs=exercise(PortMachine,case,root=root,mutant=mutant,**opts)
  assert p['error'] is None,(root,kind,case,p['error'])
  row=comparisons.setdefault(root+'/'+kind+('/control'+str(mutant) if a.suite=='output' else ''),dict(total=0,equal=0));row['total']+=1;row['equal']+=p==r
  assert (p==r)==(mutant==0),(root,kind,case,[k for k in p if p[k]!=r[k]])
  if p!=r and len(differences)<15:differences.append(dict(root=root,kind=kind,case=case,python=e.digest(p),rust=e.digest(r),fields=[k for k in p if p[k]!=r[k]]))
  if not mutant:
   assert n.get(root)==1
   if opts.get('profile'):
    assert ps['owned'] and not rs['owned'] and rs['outside']>0;closure[root]=closure.get(root,0)+1
    for name,count in ps['owned'].items():owned_calls[name]=owned_calls.get(name,0)+count
  writes[root].update(p['state']['writes']);seen[root].update(s for s,_ in p['visits'])
 if a.suite=='returns':
  for i,site in enumerate(INV['guest_sites']):
   root=site['caller'];ret=site['ret_to'];row=return_controls[ret]=dict(total=160,reached=0,detected=0)
   for case in range(160):
    p,_,_=exercise(Oracle,case,root=root,controlled=True);r,_,_=exercise(PortMachine,case,root=root,controlled=True,mutant=185+i)
    assert p['error'] is None;hit=ret in {s for s,_ in p['visits']};row['reached']+=hit;row['detected']+=p!=r;assert (p!=r)==hit,(ret,case)
   assert row['reached']>0;print('RETURN CONTROL',ret,row,flush=True)
 else:
  jobs=list(OUTPUTS) if a.suite=='output' else [(root,170+NEW.index(root) if a.suite=='body' else 0) for root in NEW]
  for root,mutant in jobs:
   for case,snapshot in enumerate(captures[root]):
    for tapped in (False,True):
     for listener in (False,True):
      for schedule in range(3):pair(root,case,'real',mutant=mutant,snapshot=snapshot,tapped=tapped,listener=listener,pause=root if schedule==1 else None,direct=schedule==2,profile=not mutant)
   for case in range(500):
    for tapped in (False,True):
     for listener in (False,True):pair(root,case,'authored-integrated',mutant=mutant,tapped=tapped,listener=listener,pause=SITES[case%len(SITES)],direct=case%3==0,mutations=case%5==0,profile=not mutant)
    if case%100==99:print(a.suite,root,case+1,flush=True)
  if a.suite=='normal':
   for root in CALLERS:
    for case in range(500):
     for tapped in (False,True):
      for listener in (False,True):pair(root,case,'controlled-ABI',controlled=True,tapped=tapped,listener=listener,pause=SITES[case%len(SITES)],direct=case%3==0)
   probe=Probe()
   for root in NEW:
    for controlled in ((False,True) if root in CALLERS else (False,)):
     for case in range(160):
      sys.settrace(probe.trace)
      try:p,_,_=exercise(Oracle,case,root=root,controlled=controlled)
      finally:sys.settrace(None)
      r,_,_=exercise(PortMachine,case,root=root,controlled=controlled);assert p['error'] is None and p==r,('branch',root,case)
   branches=probe.counts;assert all(branches.values()),[k for k,v in branches.items() if not v]
   for root in NEW:
    for row in plan['errors'][root]:
     selector=row['selector'];key=root+'/'+selector;errors[key]=0
     for case in range(160):
      opts=dict(root=root,controlled=row['controlled'],failure=selector);p,_,_=exercise(Oracle,case,**opts);r,_,_=exercise(PortMachine,case,**opts);assert p==r,('error',root,selector,case,[k for k in p if p[k]!=r[k]])
      errors[key]+=p['error'] is not None;error_comparisons+=1
     assert errors[key]>0,('unreached selector',key);print('ERROR',key,errors[key],flush=True)
    for variant in ['identity']+list(plan['variants'].get(root,[])):
     for case in range(16):
      p,_,_=exercise(Oracle,case,root=root,variant=variant);r,n,scope=exercise(PortMachine,case,root=root,variant=variant,profile=True);assert p['error'] is None and p==r and root not in n and scope['owned'];variants+=1
   assert all(closure[r]==2096 for r in NEW)
   for root in CALLERS:assert {s['ret_to'] for s in INV['bodies'][root]['sites']}<=seen[root]
 total=sum(r['total'] for r in comparisons.values());expected={'normal':6288,'body':6288,'output':25152,'returns':0}[a.suite];assert total==expected
 report=dict(all_inventory_helper_scope=True,source_owned_calls=owned_calls,owned_symbols=sorted({h['symbol'] for b in INV['bodies'].values() for h in b['helper_symbols']}),suite=a.suite,comparisons=comparisons,captures={r:8 for r in NEW},all_equal=all(r['equal']==r['total'] for r in comparisons.values()),differences=differences,closure_checks=closure,branches=branches,branch_comparisons=480 if branches else 0,error_comparisons=error_comparisons,errors_seen=errors,variants=variants,return_controls=return_controls,sites_seen={r:sorted(s) for r,s in seen.items()},writes_seen={r:sorted(s) for r,s in writes.items()},control_scope_verified=True,wall_s=time.monotonic()-start)
 if a.suite in ('body','output'):assert not report['all_equal'] and all(r['equal']==0 for r in comparisons.values())
 if a.suite=='normal':assert {h['symbol'].rsplit('.',1)[1] for b in INV['bodies'].values() for h in b['helper_symbols']}<=set(owned_calls) and all(owned_calls.values()) and report['all_equal'] and error_comparisons==plan['error_comparisons'] and len(errors)==plan['distinct_error_selectors']==plan['error_execution_rows']
 e.write(a.out,report,before);print(a.suite,'COMPLETE',flush=True)
if __name__=='__main__':main()
