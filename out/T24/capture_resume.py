"""Quiet-gated genuine source entries,append-only private shards,resumable drives."""
import argparse,hashlib,json,os,pickle,sys,time,traceback
from pathlib import Path
import evidence as e
OUT=e.BASE/'out/T24';RAW=e.BASE/'.cache/T24-raw';SHARDS=RAW/'capture-shards-v2';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',default='out/T24/captures-v2.json');a=ap.parse_args();assert not Path(a.out).exists()
 e.verify();manifest=json.loads((OUT/'capture-inputs-v2.json').read_text());manifest_sha=sha(OUT/'capture-inputs-v2.json')
 def verify():
  e.verify();assert sha(OUT/'capture-inputs-v2.json')==manifest_sha
  for p,h in manifest['source_sha256'].items():assert sha(e.BASE/p)==h,p
 verify();e.deny_original()
 from original_match.port import load
 from original_match import Match,Fixture
 inv=json.loads((OUT/'inventory-v1.json').read_text());roots=tuple(inv['roots']);entries={a:x for reg,_ in load(['all']) for a,x in reg.entries.items()}
 RAW.mkdir(exist_ok=True);SHARDS.mkdir(exist_ok=True);captures={r:[] for r in roots}
 for p in sorted(SHARDS.glob('*.pkl')):
  row=pickle.loads(p.read_bytes());assert row['oracle']==e.PIN and row['source_manifest_sha256']==manifest_sha and row['root'] in roots
  captures[row['root']].append(row['state'])
 assert all(len(v)<=8 for v in captures.values())
 journal=OUT/'capture-drives-v2.jsonl';prior=[json.loads(x) for x in journal.read_text().splitlines()] if journal.exists() else [];next_drive=1+max([x['drive'] for x in prior]+[0]);current={}
 originals={r:entries[r].fn for r in roots}
 for root,fn in originals.items():
  def capture(mem,v,root=root,fn=fn):
   if len(captures[root])<8:
    state=(bytes(mem.m._memory),dict(mem.m._registers),mem._entries[-1]);index=len(captures[root]);path=SHARDS/(root.replace(':','_')+f'-{index:02}.pkl')
    with path.open('xb') as f:pickle.dump(dict(root=root,drive=current['drive'],state=state,oracle=e.PIN,source_manifest_sha256=manifest_sha),f,protocol=4)
    captures[root].append(state);print('CAPTURE',root,len(captures[root]),'drive',current['drive'],flush=True)
   return fn(mem,v)
  entries[root].fn=capture
 try:
  for drive in range(next_drive,next_drive+16):
   if all(len(v)==8 for v in captures.values()):break
   quiet=0
   while quiet<3:
    loads=os.getloadavg();quiet=quiet+1 if max(loads[:2])<4 else 0;print('WAIT CAPTURE QUIET',loads,quiet,'/3',flush=True)
    if quiet<3:time.sleep(10)
   verify();current['drive']=drive;row=dict(drive=drive,started=time.time(),before={r:len(v) for r,v in captures.items()},guard_unchanged=True);last=-1
   try:
    match=Match(e.image(),Fixture(7,19,index=9,kind=200),managed=7,substitutions=None,engine='port',record_draws=True)
    for i,event in enumerate(match.events()):
     last=i
     if event.kind=='decision':match.answer(quick=True) if event.data['context']=='half_time' else match.answer()
     if all(len(v)==8 for v in captures.values()):break
     assert i<831
    row['exit']='complete-or-capture-prefix'
   except Exception as exc:
    row['exit']='rejected-drive';row['error']=(type(exc).__name__,str(exc));traceback.print_exc()
   row.update(finished=time.time(),last_event=last,after={r:len(v) for r,v in captures.items()},source_unchanged=True);verify()
   with journal.open('a') as f:f.write(json.dumps(row)+'\n')
   print('DRIVE',row,flush=True)
  assert all(len(v)==8 for v in captures.values()),'genuine-source capture budget exhausted;preserve shards/resume after audit'
 finally:
  for r,fn in originals.items():entries[r].fn=fn
 verify();bundle=RAW/'captures-v2.pkl';assert not bundle.exists()
 with bundle.open('xb') as f:pickle.dump(captures,f,protocol=4)
 report=dict(captures={r:len(v) for r,v in captures.items()},private_file=str(bundle.relative_to(e.BASE)),sha256=sha(bundle),oracle=e.PIN,source_sha256=manifest['source_sha256'],source_unchanged=True,source_manifest_sha256=manifest_sha,actual_drive_journal='out/T24/capture-drives-v2.jsonl',private_shards={str(p.relative_to(e.BASE)):sha(p) for p in sorted(SHARDS.glob('*.pkl'))},original_bytes_committed=False,pid=os.getpid())
 with Path(a.out).open('x') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
 print('All4 bodies have8 genuine source-entry captures',flush=True)
if __name__=='__main__':main()
