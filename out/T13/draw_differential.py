"""T13 actual-callee full caller proof; private RAM captures never written."""
import argparse,json,sys,time
import evidence as e

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);ap.add_argument('--mutant',type=int,choices=[0,12,13],default=0);a=ap.parse_args()
 assert not e.Path(a.out).exists();e.verify();before=e.hashes();e.deny_original()
 from original_match import Match,Fixture
 sys.path.insert(0,str(e.BASE/'engine/tests'))
 from test_ball_draw_state import ROOT,MEMBER,TRAVEL,TARGETS,RETURNS,SITES,WRITE_SITES,ENTRIES,Oracle,PortMachine,exercise
 m=Match(e.image(),Fixture(7,19,index=9,kind=200),managed=7,substitutions=None,engine='port',record_draws=True)
 captures=[];original=ENTRIES[ROOT].fn
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
 counts={};differences=[];visited=set();writes=set();called=set();mutations={};paths=dict(member_true=0,member_false=0,travel=0,no_travel=0,no_guest_calls=0,glyph_low=0,glyph_high=0);start=time.monotonic()
 def compare(kind,case,**opts):
  p,_=exercise(Oracle,case,**opts);r,n=exercise(PortMachine,case,mutant=a.mutant,**opts)
  assert p['error'] is None,(kind,case,p['error'])
  has_guest=bool(p['calls'].get(MEMBER,0) or p['calls'].get(TRAVEL,0));expected=a.mutant==12 or (a.mutant==13 and has_guest)
  row=counts.setdefault(kind,dict(total=0,equal=0,expected_different=0));row['total']+=1;row['equal']+=p==r;row['expected_different']+=expected
  visited.update(s for s,_ in p['visits']);called.update(p['calls']);writes.update(p['state']['writes'])
  for k,v in p['state'].items():
   if k!='writes':mutations[k]=mutations.get(k,0)+v
  if p['calls'].get(MEMBER,0):paths['member_true' if p['state']['writes'].get('0791:8FAF',0) else 'member_false']+=1
  paths['travel' if p['calls'].get(TRAVEL,0) else 'no_travel']+=1;paths['no_guest_calls']+=not has_guest
  if kind=='random-edge':
   for event in p['log']:
    if event[0]=='w' and event[4]==(0x823+0x791)*16+0x8fe9:
     if event[3]==0x2a:paths['glyph_low']+=1
     if event[3]==0x2b:paths['glyph_high']+=1
  if p!=r and len(differences)<12:differences.append(dict(kind=kind,case=case,python=e.digest(p),rust=e.digest(r),fields=[k for k in p if p[k]!=r[k]]))
  assert (p!=r)==expected,(kind,case,expected,[k for k in p if p[k]!=r[k]])
  assert n.get(ROOT)==1,n
 for case,snapshot in enumerate(captures):
  for tapped in [False,True]:
   for listener in [False,True]:
    for pause in [None,MEMBER,RETURNS[0]]:compare('real',case,snapshot=snapshot,tapped=tapped,listener=listener,pause=pause)
 print('Real capture comparisons complete',counts,flush=True)
 for case in range(500):
  for tapped in [False,True]:
   for listener in [False,True]:compare('random-edge',case,tapped=tapped,listener=listener,pause=SITES[case%len(SITES)],mutations=case%3==0,return_mutations=case%5==0,direct=case%7==0)
  if case%100==99:print('Authored inputs complete',case+1,flush=True)
 assert set(RETURNS)<=visited and set(WRITE_SITES)<=writes and set(TARGETS)<=called
 assert all(paths.values()),paths
 assert all(v>0 for v in mutations.values()),mutations
 errors_seen={};error_comparisons=0
 if a.mutant==0:
  for failure in ['write',*SITES]+['callee:'+ad for ad in TARGETS]:
   errors_seen[failure]=0
   for case in range(32):
    p,_=exercise(Oracle,case,failure=failure,mutations=True);r,_=exercise(PortMachine,case,failure=failure,mutations=True);assert p==r,('error',failure,case,[k for k in p if p[k]!=r[k]])
    error_comparisons+=1;errors_seen[failure]+=p['error'] is not None
  assert all(errors_seen.values()),errors_seen
 report=dict(mutant=a.mutant,captures=8,comparisons=counts,paths=paths,observer_mutations=mutations,error_comparisons=error_comparisons,errors_seen=errors_seen,differences=differences,all_equal=all(v['equal']==v['total'] for v in counts.values()),control_scope_verified=True,return_sites_seen=sorted(set(RETURNS)&visited),write_sites_seen=sorted(set(WRITE_SITES)&writes),delegated_targets_seen=sorted(set(TARGETS)&called),delegates='actual registered source bodies, including nested long multiplication',wall_s=time.monotonic()-start)
 e.write(a.out,report,before);assert report['all_equal']==(a.mutant==0)
 print(json.dumps({k:report[k] for k in ['mutant','comparisons','paths','observer_mutations','error_comparisons','all_equal','source_unchanged']}),flush=True)
if __name__=='__main__':main()
