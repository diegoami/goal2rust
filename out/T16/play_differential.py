"""T16 caller proof: RAM captures, positive paths/early exits, real full-drive composition later."""
import argparse,json,sys,time
import evidence as e

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);ap.add_argument('--mutant',type=int,choices=[0,18,19],default=0);a=ap.parse_args()
 assert not e.Path(a.out).exists();e.verify();before=e.hashes();e.deny_original()
 from original_match import Match,Fixture
 sys.path.insert(0,str(e.BASE/'engine/tests'))
 from test_play_state import ROOT,PROBES,TARGETS,RETURNS,SITES,WRITE_SITES,ENTRIES,Oracle,PortMachine,exercise
 m=Match(e.image(),Fixture(7,19,index=9,kind=200),managed=7,substitutions=None,engine='port',record_draws=True);captures=[];original=ENTRIES[ROOT].fn
 def capture(mem,v):
  if len(captures)<8:captures.append((bytes(mem.m._memory),dict(mem.m._registers),mem._entries[-1]))
  return original(mem,v)
 ENTRIES[ROOT].fn=capture
 try:
  for i,ev in enumerate(m.events()):
   if ev.kind=='decision':m.answer(quick=True) if ev.data['context']=='half_time' else m.answer()
   if len(captures)==8:break
   assert i<150,'real capture budget exhausted'
 finally:ENTRIES[ROOT].fn=original
 assert len(captures)==8
 counts={};differences=[];seen=set();writes=set();called=set();mutations={};paths=dict(early_probe=0,early_keeper=0,choice_false=0,choice_true=0,choice_none=0,movement=0,holder=0);start=time.monotonic()
 def compare(kind,case,**opts):
  p,_=exercise(Oracle,case,**opts);r,n=exercise(PortMachine,case,mutant=a.mutant,**opts);assert p['error'] is None,(kind,case,p['error'])
  row=counts.setdefault(kind,dict(total=0,equal=0));row['total']+=1;row['equal']+=p==r;seen.update(s for s,_ in p['visits']);writes.update(p['state']['writes']);called.update(p['calls'])
  for k,v in p['state'].items():
   if k!='writes':mutations[k]=mutations.get(k,0)+v
  c=p['calls'];w=p['state']['writes'];paths['early_probe']+='0791:045D' not in c;paths['early_keeper']+='0791:4B64' in c;paths['choice_false']+=bool(w.get('0791:5809'));paths['choice_true']+=bool(w.get('0791:58B3'));paths['choice_none']+='0791:4A28' in c;paths['movement']+='0791:474D' in c;paths['holder']+='0791:6188' in c
  if p!=r and len(differences)<12:differences.append(dict(kind=kind,case=case,python=e.digest(p),rust=e.digest(r),fields=[k for k in p if p[k]!=r[k]]))
  assert (p==r)==(a.mutant==0),(kind,case,[k for k in p if p[k]!=r[k]])
  assert n.get(ROOT)==1,n
 for case,snapshot in enumerate(captures):
  for tapped in [False,True]:
   for listener in [False,True]:
    for pause in [None,PROBES[0],RETURNS[0]]:compare('real',case,snapshot=snapshot,tapped=tapped,listener=listener,pause=pause)
 print('Real cases complete',counts,flush=True)
 for case in range(500):
  for tapped in [False,True]:
   for listener in [False,True]:compare('random-edge',case,tapped=tapped,listener=listener,pause=SITES[case%len(SITES)],mutations=case%5==0,return_mutations=case%7==0,direct=case%11==0)
  if case%100==99:print('Authored inputs complete',case+1,flush=True)
 assert set(RETURNS)<=seen and set(WRITE_SITES)<=writes and set(TARGETS)<=called,(set(RETURNS)-seen,set(WRITE_SITES)-writes,set(TARGETS)-called)
 assert all(paths.values()) and all(mutations.values()),(paths,mutations)
 errors_seen={};error_comparisons=0
 if a.mutant==0:
  for failure in ['write',*SITES]+['callee:'+ad for ad in TARGETS]+['write:'+s for s in WRITE_SITES]:
   errors_seen[failure]=0
   for case in range(80):
    p,_=exercise(Oracle,case,failure=failure,mutations=False);r,_=exercise(PortMachine,case,failure=failure,mutations=False);assert p==r,('error',failure,case,[k for k in p if p[k]!=r[k]])
    errors_seen[failure]+=p['error'] is not None;error_comparisons+=1
  assert all(errors_seen.values()),errors_seen
 report=dict(mutant=a.mutant,captures=8,comparisons=counts,paths=paths,observer_mutations=mutations,return_sites_seen=sorted(set(RETURNS)&seen),write_sites_seen=sorted(set(WRITE_SITES)&writes),delegated_targets_seen=sorted(set(TARGETS)&called),error_comparisons=error_comparisons,errors_seen=errors_seen,differences=differences,all_equal=all(v['total']==v['equal'] for v in counts.values()),control_scope_verified=True,delegates='controlled registered ABI boundaries; actual admitted drives use actual source bodies',wall_s=time.monotonic()-start)
 e.write(a.out,report,before);assert report['all_equal']==(a.mutant==0)
 print(json.dumps({k:report[k] for k in ['mutant','comparisons','paths','observer_mutations','error_comparisons','all_equal','source_unchanged']}),flush=True)
if __name__=='__main__':main()
