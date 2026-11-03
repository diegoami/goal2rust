"""Capture source-entry states to ignored storage; commit hashes/counts only."""
import argparse,hashlib,json,pickle,sys
import evidence as e

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);a=ap.parse_args()
 path=e.BASE/'.cache/T21-raw/captures-v1.pkl';assert not path.exists() and not e.Path(a.out).exists()
 e.verify();before=e.hashes();e.deny_original()
 sys.path.insert(0,str(e.BASE/'engine/tests'))
 from test_travel import NEW,ENTRIES
 from original_match import Match,Fixture
 captures={root:[] for root in NEW};originals={root:ENTRIES[root].fn for root in NEW}
 for root,original in originals.items():
  def capture(mem,v,root=root,original=original):
   if len(captures[root])<8:captures[root].append((bytes(mem.m._memory),dict(mem.m._registers),mem._entries[-1]))
   return original(mem,v)
  ENTRIES[root].fn=capture
 try:
  match=Match(e.image(),Fixture(7,19,index=9,kind=200),managed=7,substitutions=None,engine='port',record_draws=True)
  for i,event in enumerate(match.events()):
   if event.kind=='decision':match.answer(quick=True) if event.data['context']=='half_time' else match.answer()
   if all(len(c)==8 for c in captures.values()):break
   assert i<831,'actual entry capture budget exhausted'
 finally:
  for root,original in originals.items():ENTRIES[root].fn=original
 assert all(len(c)==8 for c in captures.values())
 path.parent.mkdir(exist_ok=True)
 with path.open('xb') as f:pickle.dump(captures,f,protocol=4)
 e.write(a.out,dict(captures={r:len(c) for r,c in captures.items()},private_file=str(path.relative_to(e.BASE)),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),original_bytes_committed=False),before)
 print('Captured eight actual source entries per body',flush=True)
if __name__=='__main__':main()
