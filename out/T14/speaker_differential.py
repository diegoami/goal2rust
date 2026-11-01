"""T14 four-body proof, eight private RAM captures/body, 500 authored cases/body."""
import argparse,json,sys,time
import evidence as e

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);ap.add_argument('--mutant',type=int,choices=[0,7,8,9],default=0);a=ap.parse_args()
 assert not e.Path(a.out).exists();e.verify();before=e.hashes();e.deny_original()
 from original_match import Match,Fixture
 sys.path.insert(0,str(e.BASE/'engine/tests'))
 from test_speaker_state import ROOT,SEED,RNG,OFF,BODIES,SITES,ENTRIES,Oracle,PortMachine,exercise
 m=Match(e.image(),Fixture(7,19,index=9,kind=200),managed=7,substitutions=None,engine='port',record_draws=True)
 captures={ad:[] for ad in BODIES};originals={ad:ENTRIES[ad].fn for ad in BODIES}
 for ad in BODIES:
  def capture(mem,variant,ad=ad):
   if len(captures[ad])<8:captures[ad].append((bytes(mem.m._memory),dict(mem.m._registers),mem._entries[-1]))
   return originals[ad](mem,variant)
  ENTRIES[ad].fn=capture
 try:
  for i,ev in enumerate(m.events()):
   if ev.kind=='decision':m.answer(quick=True) if ev.data['context']=='half_time' else m.answer()
   if all(len(v)==8 for v in captures.values()):break
   assert i<150,'real capture budget exhausted'
 finally:
  for ad in BODIES:ENTRIES[ad].fn=originals[ad]
 assert all(len(v)==8 for v in captures.values())
 counts={};differences=[];mutations=dict(seed_writes=0,stack_mutations=0);start=time.monotonic()
 def compare(kind,case,**opts):
  p,_=exercise(Oracle,case,**opts);r,n=exercise(PortMachine,case,mutant=a.mutant,**opts)
  row=counts.setdefault(kind,dict(total=0,equal=0,expected_different=0));row['total']+=1;row['equal']+=p==r
  for k in mutations:mutations[k]+=p['flags'][k]
  root=opts['root'];expected=a.mutant==7 or (a.mutant==8 and root==ROOT) or (a.mutant==9 and (root==SEED or (root==ROOT and p['calls'].get(SEED,0)>0)))
  row['expected_different']+=expected
  if p!=r and len(differences)<12:differences.append(dict(kind=kind,case=case,python=e.digest(p),rust=e.digest(r),fields=[k for k in p if p[k]!=r[k]]))
  assert (p!=r)==expected,(kind,case,opts.get('pause'),expected,[k for k in p if p[k]!=r[k]])
  assert n.get(root,0)==(0 if opts.get('body') else 1),(root,n)
 for ad,snaps in captures.items():
  for case,snapshot in enumerate(snaps):
   for tapped in (False,True):
    for listener in (False,True):
     for pause in (None,RNG,'0791:9540'):compare('real:'+ad,case,root=ad,snapshot=snapshot,tapped=tapped,listener=listener,pause=pause)
     if ad in (RNG,OFF):compare('real-body:'+ad,case,root=ad,snapshot=snapshot,tapped=tapped,listener=listener,body=True)
 print('Real comparisons complete',counts,flush=True)
 for case in range(500):
  for ad in BODIES:
   for tapped in (False,True):
    for listener in (False,True):
     opts=dict(root=ad,tapped=tapped,listener=listener,mutations=case%3==0)
     compare('random-edge:'+ad,case,**opts,pause=SITES[case%len(SITES)],direct=case%5==0)
     if ad in (RNG,OFF):compare('random-body:'+ad,case,**opts,body=True)
  if case%100==99:print('Synthetic inputs complete',case+1,flush=True)
 report=dict(mutant=a.mutant,captures={ad:len(v) for ad,v in captures.items()},comparisons=counts,callback_mutations=mutations,differences=differences,all_equal=all(r['total']==r['equal'] for r in counts.values()),control_scope_verified=True,wall_s=time.monotonic()-start)
 e.write(a.out,report,before);assert report['all_equal']==(a.mutant==0)
 print(json.dumps({k:report[k] for k in ['mutant','comparisons','callback_mutations','all_equal','source_unchanged']}),flush=True)
if __name__=='__main__':main()
