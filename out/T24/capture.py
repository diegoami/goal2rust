"""Eight actual keyboard entries per body across genuine source match drives."""
import argparse,hashlib,json,pickle,sys
import evidence as e
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);a=ap.parse_args();path=e.BASE/'.cache/T24-raw/captures-v1.pkl';assert not path.exists() and not e.Path(a.out).exists()
 e.verify();before=e.hashes();e.deny_original();sys.path.insert(0,str(e.BASE/'engine/tests'))
 from test_keyboard import NEW,ENTRIES
 from original_match import Match,Fixture
 captures={r:[] for r in NEW};originals={r:ENTRIES[r].fn for r in NEW};drives=[]
 for root,fn in originals.items():
  def capture(mem,v,root=root,fn=fn):
   if len(captures[root])<8:captures[root].append((bytes(mem.m._memory),dict(mem.m._registers),mem._entries[-1]))
   return fn(mem,v)
  ENTRIES[root].fn=capture
 try:
  for run in range(8):
   match=Match(e.image(),Fixture(7,19,index=9,kind=200),managed=7,substitutions=None,engine='port',record_draws=True)
   last=-1
   for i,event in enumerate(match.events()):
    last=i
    if event.kind=='decision':match.answer(quick=True) if event.data['context']=='half_time' else match.answer()
    if all(len(c)==8 for c in captures.values()):break
    assert i<831
   drives.append(dict(drive=run+1,last_event=last,captures={r:len(c) for r,c in captures.items()}));print(drives[-1],flush=True)
   if all(len(c)==8 for c in captures.values()):break
 finally:
  for r,fn in originals.items():ENTRIES[r].fn=fn
 assert all(len(c)==8 for c in captures.values())
 path.parent.mkdir(exist_ok=True)
 with path.open('xb') as f:pickle.dump(captures,f,protocol=4)
 e.write(a.out,dict(captures={r:len(c) for r,c in captures.items()},actual_drives=drives,private_file=str(path.relative_to(e.BASE)),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),original_bytes_committed=False),before)
if __name__=='__main__':main()
