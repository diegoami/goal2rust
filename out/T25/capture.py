"""Pure-oracle genuine prefix captures; immutable inputs and exclusive shards."""
import fcntl,hashlib,json,os,pickle,subprocess,sys,time,traceback
from pathlib import Path
B=Path(__file__).resolve().parents[2];O=B/'out/T25';RAW=B/'.cache/T25-raw';SHARDS=RAW/'capture-shards-v1'
sys.path.insert(0,str(B/'out/T24'));import evidence as e
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert not (O/'captures-v1.json').exists()
 lock=(B/'.cache/T25-capture.lock').open('a+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);lock.seek(0);lock.truncate();lock.write(str(os.getpid()));lock.flush()
 manifest_path=O/'capture-inputs-v1.json';manifest=json.loads(manifest_path.read_text());mh=sha(manifest_path)
 def verify():
  e.verify();assert sha(manifest_path)==mh
  for p,h in manifest['source_sha256'].items():assert sha(B/p)==h,p
 verify();e.deny_original()
 from original_match.port import load
 from original_match import Match,Fixture
 roots=tuple(json.loads((O/'inventory-v2.json').read_text())['roots']);entries={a:x for reg,_ in load(['all']) for a,x in reg.entries.items()};captures={r:[] for r in roots}
 SHARDS.mkdir(parents=True,exist_ok=True)
 for p in sorted(SHARDS.glob('*.pkl')):
  r=pickle.loads(p.read_bytes());assert r['oracle']==e.PIN and r['source_manifest_sha256']==mh;captures[r['root']].append(r['state'])
 assert all(len(v)<=8 for v in captures.values())
 journal=O/'capture-drives-v1.jsonl';prior=[json.loads(x) for x in journal.read_text().splitlines()] if journal.exists() else [];first=1+max([r['drive'] for r in prior]+[0]);current={};originals={r:entries[r].fn for r in roots}
 for root,fn in originals.items():
  def capture(mem,v,root=root,fn=fn):
   if len(captures[root])<8:
    state=(bytes(mem.m._memory),dict(mem.m._registers),mem._entries[-1]);p=SHARDS/(root.replace(':','_')+f'-{len(captures[root]):02}.pkl')
    with p.open('xb') as f:pickle.dump(dict(root=root,drive=current['drive'],state=state,oracle=e.PIN,source_manifest_sha256=mh),f,protocol=4)
    captures[root].append(state);print('CAPTURE',root,len(captures[root]),'drive',current['drive'],flush=True)
   return fn(mem,v)
  entries[root].fn=capture
 try:
  for drive in range(first,first+16):
   if all(len(v)==8 for v in captures.values()):break
   quiet=0
   while quiet<3:
    try:
     runners=json.loads(subprocess.check_output(['gh','api','repos/diegoami/goal2/actions/runners'],text=True))['runners'];busy=any(r['busy'] for r in runners if 'it13' in r['name'].lower())
    except Exception:busy=True
    loads=os.getloadavg();quiet=quiet+1 if not busy and max(loads[:2])<4 else 0;print('WAIT CAPTURE QUIET',loads,'IT13 runners busy',busy,quiet,'/3',flush=True)
    if quiet<3:time.sleep(10)
   verify();current['drive']=drive;row=dict(drive=drive,started=time.time(),before={r:len(v) for r,v in captures.items()},guard_unchanged=True,runner_idle=True);needed=[r for r in roots if row['before'][r]<8];last=-1
   try:
    match=Match(e.image(),Fixture(7,19,index=9,kind=200),managed=7,substitutions=None,engine='port',record_draws=True)
    for i,event in enumerate(match.events()):
     last=i
     if event.kind=='decision':match.answer(quick=True) if event.data['context']=='half_time' else match.answer()
     if all(len(v)==8 for v in captures.values()) or all(len(captures[r])>row['before'][r] for r in needed):break
     assert i<831
    row['exit']='genuine-prefix-after-needed-entries'
   except Exception as exc:
    row['exit']='rejected-drive';row['error']=(type(exc).__name__,str(exc));traceback.print_exc()
   verify();row.update(finished=time.time(),last_event=last,after={r:len(v) for r,v in captures.items()},source_unchanged=True)
   with journal.open('a') as f:f.write(json.dumps(row)+'\n')
   print('DRIVE',row,flush=True)
  assert all(len(v)==8 for v in captures.values()),'capture budget exhausted;preserve shards before resume'
 finally:
  for r,fn in originals.items():entries[r].fn=fn
 verify();bundle=RAW/'captures-v1.pkl'
 with bundle.open('xb') as f:pickle.dump(captures,f,protocol=4)
 report=dict(oracle=e.PIN,pid=os.getpid(),captures={r:len(v) for r,v in captures.items()},private_file=str(bundle.relative_to(B)),sha256=sha(bundle),source_sha256=manifest['source_sha256'],source_unchanged=True,source_manifest_sha256=mh,actual_drive_journal='out/T25/capture-drives-v1.jsonl',private_shards={str(p.relative_to(B)):sha(p) for p in sorted(SHARDS.glob('*.pkl'))},original_bytes_committed=False)
 with (O/'captures-v1.json').open('x') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
 print('All six bodies have eight genuine entries',flush=True)
if __name__=='__main__':main()
