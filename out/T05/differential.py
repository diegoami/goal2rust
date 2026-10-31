"""T05 real captured root frames plus 500 authored random/edge states.

Full state at every guest boundary and final completion; only hashes/counts persist.
"""
import argparse
import json
import sys
import time
import evidence as e


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);ap.add_argument('--mutant',type=int,default=0)
    a=ap.parse_args();assert not e.Path(a.out).exists();e.verify();before=e.hashes();e.deny_original()
    from original_match import Match, Fixture
    sys.path.insert(0,str(e.BASE/'engine/tests'))
    from test_nearest_ball import Oracle,PortMachine,ROOT,ENTRIES,SITES,exercise
    m=Match(e.image(),Fixture(7,19,index=9,kind=200),managed=7,substitutions=None,engine='port',record_draws=True)
    captured=[];original=ENTRIES[ROOT].fn
    def capture(mem,variant):
        if len(captured)<8:captured.append((bytes(mem.m._memory),dict(mem.m._registers),mem._entries[-1]))
        return original(mem,variant)
    ENTRIES[ROOT].fn=capture
    try:
        for i,ev in enumerate(m.events()):
            if ev.kind=='decision':m.answer(quick=True) if ev.data['context']=='half_time' else m.answer()
            if i>=60:break
    finally:ENTRIES[ROOT].fn=original
    assert len(captured)==8
    counts={};differences=[]
    def compare(kind,case,**opts):
        left,_=exercise(Oracle,case,**opts)
        right,_=exercise(PortMachine,case,mutant=a.mutant,**opts)
        row=counts.setdefault(kind,dict(total=0,equal=0));row['total']+=1;row['equal']+=left==right
        if left!=right and len(differences)<10:
            differences.append(dict(kind=kind,case=case,python=e.digest(left),rust=e.digest(right),
                                    differing_fields=[k for k in left if left[k]!=right[k]]))
    start=time.monotonic()
    for case,snapshot in enumerate(captured):
        for tapped in (False,True):
            for listener in (False,True):
                for pause in (None,'0791:3013','0791:3090','0791:30A3'):
                    compare('real',case,snapshot=snapshot,tapped=tapped,listener=listener,pause=pause)
    print('Real capture comparisons complete',counts,flush=True)
    for case in range(500):
        for tapped in (False,True):
            for listener in (False,True):
                compare('random-edge',case,tapped=tapped,listener=listener,pause=SITES[case%len(SITES)])
        if case%100==99:print('Synthetic cases complete',case+1,flush=True)
    report=dict(mutant=a.mutant,real_captures=len(captured),comparisons=counts,differences=differences,
                all_equal=all(r['total']==r['equal'] for r in counts.values()),wall_s=time.monotonic()-start)
    e.write(a.out,report,before)
    print(json.dumps({k:report[k] for k in ['mutant','comparisons','all_equal','source_unchanged']}),flush=True)
    assert report['all_equal']==(a.mutant==0)


if __name__=='__main__':main()
