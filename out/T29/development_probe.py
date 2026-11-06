"""Archived development proof;does not replace final artifact-bound campaign."""
import hashlib,json,os,pickle,sys,time
from pathlib import Path
import capture_support as pure
sys.path[:0]=[str(pure.BASE/'engine/tests'),str(pure.BASE/'engine/python')]
from test_near_zone import *
from host_gate import wait_idle

def main():
 pure.verify();wait_idle();O=pure.BASE/'out/T29';dest=O/'development-probe-v1.json';assert not dest.exists()
 import goal2rust_engine
 sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 files=sorted((pure.BASE/'engine/src').glob('*.rs'))+[Path(__file__),pure.BASE/'engine/tests/test_near_zone.py']+sorted(Path(goal2rust_engine.__file__).parent.glob('*.so'))
 before={str(p.relative_to(pure.BASE)):sha(p) for p in files};archive=pure.BASE/'.cache/T29-development-sources';archive.mkdir(exist_ok=True);saved={}
 for p in files:
  target=archive/sha(p)
  if not target.exists():
   with target.open('xb') as f:f.write(p.read_bytes())
  assert sha(target)==sha(p);saved[str(p.relative_to(pure.BASE))]=str(target.relative_to(pure.BASE))
 counts=dict(authored=0,real=0,abi=0);source=set();start=time.monotonic()
 def pair(case,kind,**kw):
  p,_,ps=exercise(Oracle,case,profile=True,**kw);r,n,rs=exercise(PortMachine,case,profile=True,**kw)
  assert p['error'] is None and p==r,(case,kind,p['error'],r['error'],[k for k in p if p[k]!=r[k]])
  assert n.get('0791:44C1')==1 and not rs['owned'],(case,rs)
  source.update(ps['owned']);counts[kind]+=1
 for case in range(500):
  for tapped,listener in [(False,False),(True,False),(False,True),(True,True)]:pair(case,'authored',tapped=tapped,listener=listener)
 receipt=json.loads((O/'captures-v1.json').read_text());assert sha(pure.BASE/receipt['private_file'])==receipt['sha256']
 captures=pickle.loads((pure.BASE/receipt['private_file']).read_bytes())['0791:44C1'];assert len(captures)==8
 for i,state in enumerate(captures):
  for tapped,listener in [(False,False),(True,False),(False,True),(True,True)]:
   for kw in [dict(),dict(direct=True),dict(pause='0791:44C1'),dict(pause='0791:2BE5'),dict(pause='0791:4500')]:pair(i,'real',snapshot=state,tapped=tapped,listener=listener,**kw)
 for case in range(64):
  for kw in [dict(),dict(direct=True),dict(pause='0791:2BE5'),dict(pause='0791:4500')]:pair(case,'abi',controlled=True,**kw)
 assert source==set(INV['owned_code_objects'])
 assert before=={str(p.relative_to(pure.BASE)):sha(p) for p in files}
 report=dict(pass_all=True,development_only=True,accepted_canonical_evidence=False,comparisons=counts,all_six_source_codes=sorted(source),zero_owned_default_python_in_native=True,executed_source_sha256=before,preserved_source_map=saved,capture_receipt_sha256=sha(O/'captures-v1.json'),pid=os.getpid(),wall_s=time.monotonic()-start)
 with dest.open('x') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
 print('Development source/native proof passes',counts,'all six owned functions')
if __name__=='__main__':main()
