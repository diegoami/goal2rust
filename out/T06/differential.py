"""T06 body/frame/continuation differential; private captures stay in RAM."""
import argparse,json,sys,time
import evidence as e

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);ap.add_argument('--mutant',type=int,default=0)
    a=ap.parse_args();assert not e.Path(a.out).exists();e.verify();before=e.hashes();e.deny_original()
    from original_match import Match,Fixture
    sys.path.insert(0,str(e.BASE/'engine/tests'))
    from test_effective_skill import ROOT,LEAF,RETURN,ENTRIES,SITES,Oracle,PortMachine,exercise
    m=Match(e.image(),Fixture(7,19,index=9,kind=200),managed=7,substitutions=None,engine='port',record_draws=True)
    captures={ad:[] for ad in ENTRIES};originals={ad:en.fn for ad,en in ENTRIES.items()}
    for ad,en in ENTRIES.items():
        def capture(mem,variant,ad=ad):
            if len(captures[ad])<8:captures[ad].append((bytes(mem.m._memory),dict(mem.m._registers),mem._entries[-1]))
            return originals[ad](mem,variant)
        en.fn=capture
    try:
        for i,ev in enumerate(m.events()):
            if ev.kind=='decision':m.answer(quick=True) if ev.data['context']=='half_time' else m.answer()
            if i>=60:break
    finally:
        for ad,en in ENTRIES.items():en.fn=originals[ad]
    assert all(len(v)==8 for v in captures.values())
    counts={};differences=[];mutations=dict(saved=0,sent=0)
    def compare(kind,case,**opts):
        p,_=exercise(Oracle,case,**opts);r,_=exercise(PortMachine,case,mutant=a.mutant,**opts)
        row=counts.setdefault(kind,dict(total=0,equal=0));row['total']+=1;row['equal']+=p==r
        mutations['saved']+=p['flags']['saved_mutated'];mutations['sent']+=p['flags']['clobbered']
        if p!=r and len(differences)<10:differences.append(dict(kind=kind,case=case,python=e.digest(p),rust=e.digest(r),fields=[k for k in p if p[k]!=r[k]]))
    start=time.monotonic()
    for ad,snaps in captures.items():
        for case,snapshot in enumerate(snaps):
            for tapped in (False,True):
                for listener in (False,True):
                    for pause in (None,LEAF,RETURN):compare('real:'+ad,case,root=ad,snapshot=snapshot,tapped=tapped,listener=listener,pause=pause)
                    if ad==LEAF:compare('real-body:'+ad,case,root=ad,snapshot=snapshot,tapped=tapped,listener=listener,body=True)
    print('Real comparisons complete',counts,flush=True)
    for case in range(500):
        for ad in ENTRIES:
            for tapped in (False,True):
                for listener in (False,True):
                    compare('random-edge:'+ad,case,root=ad,tapped=tapped,listener=listener,pause=SITES[case%3],
                            mutate_saved=ad==ROOT and case%5==0,clobber_sent=ad==ROOT and case%7==0)
                    if ad==LEAF:compare('random-body:'+ad,case,root=ad,tapped=tapped,listener=listener,body=True)
        if case%100==99:print('Synthetic inputs complete',case+1,flush=True)
    report=dict(mutant=a.mutant,captures={ad:len(v) for ad,v in captures.items()},comparisons=counts,
                callback_mutations=mutations,differences=differences,all_equal=all(r['total']==r['equal'] for r in counts.values()),wall_s=time.monotonic()-start)
    e.write(a.out,report,before)
    print(json.dumps({k:report[k] for k in ['mutant','comparisons','callback_mutations','all_equal','source_unchanged']}),flush=True)
    assert report['all_equal']==(a.mutant==0)

if __name__=='__main__':main()
