"""Combined-artifact five-body/integrated proof; exclusive immutable receipts."""
import argparse,json,pickle,sys,time
import evidence as e
sys.path.insert(0,str(e.BASE/'engine/tests'))
from test_marking import *
from marking_branch_probe import Probe

def selectors(root):
 sites={ROOT:('47C5','47E2','47E5','47E8','47EF','4836','483F','489A','489D','48AB','49D3','48FB','4914','4937','494D','4980','49A7','49B2','49C7','49CB','4A1B'),ZONE:('4438','4445','4470','44B5')}.get(root,())
 returns=RETURNS[:12] if root==ROOT else (RETURNS[-1:] if root==ZONE else ())
 targets={ROOT:(HOLDER,'1771:3216',ZONE,HALF,'0791:278A',RANDOM,'0791:2BE5'),ZONE:('0791:2BE5',)}.get(root,())
 result=[root,'write','reg:ss']+(['reg:ax'] if root!=RANDOM else ['reg:eflags'])+list(returns)+['callee:'+s for s in targets]+['write:0791:'+s for s in sites]
 if root in (HOLDER,HALF,RANDOM):result+=['write:214B:0000']
 if root==RANDOM:result+=['write:214B:069F']
 return result

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);ap.add_argument('--suite',choices=['normal','body','output','returns'],required=True);a=ap.parse_args()
 assert not e.Path(a.out).exists();e.verify();before=e.hashes();e.deny_original()
 meta=json.loads((e.BASE/'out/T17/captures-v1.json').read_text());file=e.BASE/meta['private_file'];assert hashlib.sha256(file.read_bytes()).hexdigest()==meta['sha256']
 captures=pickle.loads(file.read_bytes());assert set(captures)==set(NEW) and all(len(c)==8 for c in captures.values())
 counts={};errors_seen={};error_comparisons=0;branches=None;controls={};closures={};writes=set();seen=set();variants=0;start=time.monotonic();mutations={};differences=[]
 def compare(root,case,kind,mutant=0,expect_different=False,**opts):
  p,_,ps=exercise(Oracle,case,root=root,**opts);r,n,rs=exercise(PortMachine,case,root=root,mutant=mutant,**opts)
  assert p['error'] is None,(root,kind,case,p['error'])
  row=counts.setdefault(root+'/'+kind,dict(total=0,equal=0,expected_different=0));row['total']+=1;row['equal']+=p==r;row['expected_different']+=expect_different
  assert (p!=r)==expect_different,(a.suite,root,kind,case,[k for k in p if p[k]!=r[k]])
  if p!=r and len(differences)<16:differences.append(dict(root=root,kind=kind,case=case,python=e.digest(p),rust=e.digest(r),fields=[k for k in p if p[k]!=r[k]]))
  if not mutant:
   assert n.get(root)==1,(root,n)
   if opts.get('profile'):
    assert ps['owned'] and not rs['owned'] and rs['outside']>0,(root,ps,rs)
    closures[root]=closures.get(root,0)+1
  for k,v in p['state'].items():
   if k not in ('writes','armed'):mutations[k]=mutations.get(k,0)+v
  writes.update(p['state']['writes']);seen.update(s for s,_ in p['visits'])
  return p
 if a.suite=='returns':
  for i,site in enumerate(RETURNS):
   root=ZONE if site==RETURNS[-1] else ROOT;controls[site]=dict(reached=0,detected=0,total=160)
   for case in range(160):
    p,_,_=exercise(Oracle,case,root=root,controlled=True)
    assert p['error'] is None,(site,case,p['error'])
    r,_,_=exercise(PortMachine,case,root=root,controlled=True,mutant=36+i)
    reached=site in {s for s,_ in p['visits']};controls[site]['reached']+=reached;controls[site]['detected']+=p!=r
    assert (p!=r)==reached,(site,case,reached)
   assert controls[site]['reached']>0
 else:
  roots=NEW if a.suite!='output' else (HOLDER,HALF,RANDOM)
  for root in roots:
   mutant=BODY_MUTANTS[root] if a.suite=='body' else ({HOLDER:31,HALF:33,RANDOM:35}[root] if a.suite=='output' else 0)
   for case,snapshot in enumerate(captures[root]):
    for tapped in (False,True):
     for listener in (False,True):
      for schedule in range(3):compare(root,case,'real',mutant=mutant,expect_different=bool(mutant),snapshot=snapshot,tapped=tapped,listener=listener,pause=root if schedule==1 else None,direct=schedule==2,profile=not mutant)
   for case in range(500):
    for tapped in (False,True):
     for listener in (False,True):compare(root,case,'authored-integrated' if root==ROOT else 'authored',mutant=mutant,expect_different=bool(mutant),tapped=tapped,listener=listener,pause=SITES[case%len(SITES)],direct=case%3==0,mutations=case%5==0,clobber_sent=case%7==0,profile=not mutant)
    if case%100==99:print(a.suite,root,case+1,flush=True)
  if a.suite=='normal':
   for root in (ROOT,ZONE):
    for case in range(500):
     for tapped in (False,True):
      for listener in (False,True):compare(root,case,'controlled-ABI',controlled=True,tapped=tapped,listener=listener,pause=SITES[case%len(SITES)],direct=case%3==0,mutations=case%5==0,clobber_sent=case%7==0)
   probe=Probe()
   for root in NEW:
    for controlled in ((False,True) if root in (ROOT,ZONE) else (False,)):
     for case in range(160):
      sys.settrace(probe.trace)
      try:p,_,_=exercise(Oracle,case,root=root,controlled=controlled)
      finally:sys.settrace(None)
      r,_,_=exercise(PortMachine,case,root=root,controlled=controlled)
      assert p['error'] is None and p==r,('branch',root,controlled,case,p['error'])
   branches=probe.report();assert all(branches['conditions'].values()),branches
   assert branches['slots']==list(range(2,12)) and branches['half_results']==branches['holder_results']==[0,1] and branches['zone_results']==[False,True]
   assert set(RETURNS)<=seen and set(WRITE_SITES)<=writes,(set(RETURNS)-seen,set(WRITE_SITES)-writes)
   for root in NEW:
    for failure in selectors(root):
     key=root+'/'+failure;errors_seen[key]=0
     for case in range(160):
      opts=dict(root=root,controlled=root in (ROOT,ZONE),failure=failure)
      p,_,_=exercise(Oracle,case,**opts);r,_,_=exercise(PortMachine,case,**opts)
      assert p==r,('error',root,failure,case,[k for k in p if p[k]!=r[k]])
      errors_seen[key]+=p['error'] is not None;error_comparisons+=1
     assert errors_seen[key]>0,('unreached error',key)
     print('ERROR',key,errors_seen[key],flush=True)
    for variant in ('identity','own-half-zero'):
     for case in range(16):
      p,_,_=exercise(Oracle,case,root=root,variant=variant);r,n,scope=exercise(PortMachine,case,root=root,variant=variant,profile=True)
      assert p['error'] is None and p==r and root not in n and scope['owned'] and scope['outside']>0,(root,variant,case)
      variants+=1
 report=dict(suite=a.suite,captures={r:len(c) for r,c in captures.items()},comparisons=counts,error_comparisons=error_comparisons,errors_seen=errors_seen,branches=branches,branch_comparisons=1120 if branches else 0,return_controls=controls,closure_checks=closures,observer_mutations=mutations,variants=variants,return_sites_seen=sorted(set(RETURNS)&seen),write_sites_seen=sorted(set(WRITE_SITES)&writes),all_equal=all(r['equal']==r['total'] for r in counts.values()),control_scope_verified=True,differences=differences,wall_s=time.monotonic()-start)
 if a.suite in ('body','output'):assert not report['all_equal']
 if a.suite=='normal':assert report['all_equal'] and all(closures[r]==2096 for r in NEW) and all(mutations.values())
 e.write(a.out,report,before);print(a.suite,'COMPLETE',flush=True)
if __name__=='__main__':main()
