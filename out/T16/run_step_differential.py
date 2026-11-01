"""T16 complete plain run-step/inline movement proof; actual RAM stays private."""
import argparse,json,sys,time
import evidence as e

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);ap.add_argument('--mutant',type=int,choices=[0,24,25],default=0);a=ap.parse_args()
 assert not e.Path(a.out).exists();e.verify();before=e.hashes();e.deny_original()
 from original_match import Match,Fixture
 sys.path.insert(0,str(e.BASE/'engine/tests'))
 from test_run_step import ROOT,WRITE_SITES,ENTRY,Oracle,PortMachine,exercise
 m=Match(e.image(),Fixture(7,19,index=9,kind=200),managed=7,substitutions=None,engine='port',record_draws=True);captures=[];original=ENTRY.fn
 def capture(mem,v):
  if len(captures)<8:captures.append((bytes(mem.m._memory),dict(mem.m._registers),mem._entries[-1]))
  return original(mem,v)
 ENTRY.fn=capture
 try:
  for i,ev in enumerate(m.events()):
   if ev.kind=='decision':m.answer(quick=True) if ev.data['context']=='half_time' else m.answer()
   if len(captures)==8:break
   assert i<150,'real capture budget exhausted'
 finally:ENTRY.fn=original
 assert len(captures)==8
 counts={};differences=[];writes=set();mutations={};paths=dict(offside=0,target=0,coin_draw=0,retry=0,no_retry=0,axis_x_coin=0,axis_y_coin=0,axis_y_other=0,axis_x_other=0,step_left=0,step_right=0,step_up=0,step_down=0);start=time.monotonic()
 def compare(kind,case,**opts):
  p,_=exercise(Oracle,case,**opts);r,n=exercise(PortMachine,case,mutant=a.mutant,**opts);assert p['error'] is None,(kind,case,p['error'])
  row=counts.setdefault(kind,dict(total=0,equal=0));row['total']+=1;row['equal']+=p==r;w=p['state']['writes'];writes.update(w)
  for k,v in p['state'].items():
   if k!='writes':mutations[k]=mutations.get(k,0)+v
  mapping=dict(offside='0791:89E1',target='0791:8A26',coin_draw='214B:069F',retry='0791:8ADD',axis_x_coin='0791:8A5B',axis_y_coin='0791:8A79',axis_y_other='0791:8AA5',axis_x_other='0791:8AC1',step_left='0791:8711',step_right='0791:8725',step_up='0791:8739',step_down='0791:874E')
  for k,s in mapping.items():paths[k]+=s in w
  paths['no_retry']+='0791:8ADD' not in w
  assert p['calls']=={ROOT:1},p['calls']
  assert all(f is None for _,f in p['done']),p['done']
  if p!=r and len(differences)<12:differences.append(dict(kind=kind,case=case,fields=[k for k in p if p[k]!=r[k]],python=e.digest(p),rust=e.digest(r)))
  assert (p==r)==(a.mutant==0),(kind,case,[k for k in p if p[k]!=r[k]])
  assert n.get(ROOT)==1,n
 for case,snapshot in enumerate(captures):
  for tapped in [False,True]:
   for listener in [False,True]:
    for mode in range(3):compare('real',case,snapshot=snapshot,tapped=tapped,listener=listener,pause=ROOT if mode==1 else None,direct=mode==2)
 print('Real entry cases complete',counts,flush=True)
 for case in range(500):
  for tapped in [False,True]:
   for listener in [False,True]:compare('random-edge',case,tapped=tapped,listener=listener,pause=ROOT if case%7==0 else None,mutations=case%5==0,direct=case%3==0)
  if case%100==99:print('Authored inputs complete',case+1,flush=True)
 assert set(WRITE_SITES)<=writes and all(paths.values()) and all(mutations.values()),(set(WRITE_SITES)-writes,paths,mutations)
 branch_coverage={};branch_comparisons=0
 if a.mutant==0:
  import inspect
  from original_match.port import pilot
  source=inspect.getsource(pilot).splitlines();line_labels={};return_labels={}
  conditions={"if ball > own:":'skip_ball',"if slot == mem.ds8(0x830B) or slot == mem.ds8(0x830C)":'skip_holder',"if a != c:":'skip_direction',"if abs(s8(mem.u8(rec + 8))) < line:":'line_inside',"elif not in_set(mem, mem.addr(mem.seg(0x791), CS_STATES)":'state_excluded',"elif is_keeper_slot(mem.u8(rec + 6))":'keeper'}
  returns={"if mem.u8(rec + 0xF) == 5:":'stationary',"if not on_pitch(mem.u16(rec), variant)":'off_pitch',"if mem.ds8(0x8325) == 0:":'no_play',"if slot == mem.ds8(0x830C) or slot == mem.ds8(0x830B)":'holder',"if mem.u8(mem.addr(pseg, poff + ((player * 0x14) & 0xFFFF)) + 6) == 0":'position_code',"if mem.u8(mem.addr(bseg, cell + 0x90F)) == 0x0D":'picture_attribute'}
  for i,line in enumerate(source,1):
   for snippet,label in conditions.items():
    if snippet in line:line_labels[i+1]=label
   for snippet,label in returns.items():
    if snippet in line:return_labels[i+1]=label
   if 'mem.w8(rec + 8, s8(mem.ds8(0x82E3' in line:line_labels[i]='line_clamped'
   if 'return not in_set(mem, mem.DS * 16 + 0x648' in line:picture_return=i
  required=set(line_labels.values())|set(return_labels.values())|{'holder_b','holder_c','picture_free','picture_blocked'}
  branch_coverage={k:0 for k in required}
  def trace(frame,event,arg):
   if frame.f_code is pilot.player_run_step.__code__ and event=='line' and frame.f_lineno in line_labels:branch_coverage[line_labels[frame.f_lineno]]+=1
   if frame.f_code is pilot.can_move.__code__ and event=='return':
    label=return_labels.get(frame.f_lineno)
    if label:
     branch_coverage[label]+=1
     if label=='holder':
      mem=frame.f_locals['mem'];slot=frame.f_locals['slot'];held_c=mem.m._memory[mem.DS*16+0x830c];branch_coverage['holder_c' if slot==held_c else 'holder_b']+=1
    elif frame.f_lineno==picture_return:branch_coverage['picture_free' if arg else 'picture_blocked']+=1
   return trace
  for case in range(160):
   sys.settrace(trace)
   try:p,_=exercise(Oracle,case)
   finally:sys.settrace(None)
   r,n=exercise(PortMachine,case);assert p['error'] is None and p==r and n.get(ROOT)==1,('branch trace',case)
   branch_comparisons+=1
  assert all(branch_coverage.values()),branch_coverage
 errors_seen={};error_comparisons=0
 if a.mutant==0:
  for failure in ['write',ROOT,'reg:ss']+['write:'+s for s in WRITE_SITES]:
   errors_seen[failure]=0
   for case in range(160):
    p,_=exercise(Oracle,case,failure=failure);r,_=exercise(PortMachine,case,failure=failure);assert p==r,('error',failure,case,[k for k in p if p[k]!=r[k]])
    errors_seen[failure]+=p['error'] is not None;error_comparisons+=1
  assert all(errors_seen.values()),errors_seen
 report=dict(branch_coverage=branch_coverage,branch_comparisons=branch_comparisons,mutant=a.mutant,captures=8,comparisons=counts,paths=paths,observer_mutations=mutations,write_sites_seen=sorted(writes&set(WRITE_SITES)),guest_calls=0,error_comparisons=error_comparisons,errors_seen=errors_seen,differences=differences,all_equal=all(v['total']==v['equal'] for v in counts.values()),control_scope_verified=True,control_kind={0:'normal',24:'dead-stack-body',25:'final-position'}[a.mutant],wall_s=time.monotonic()-start)
 e.write(a.out,report,before);assert report['all_equal']==(a.mutant==0)
 print(json.dumps({k:report[k] for k in ['mutant','comparisons','paths','observer_mutations','error_comparisons','all_equal','source_unchanged']}),flush=True)
if __name__=='__main__':main()
