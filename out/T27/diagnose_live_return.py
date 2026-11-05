"""Preserved v2 case: distinguish identically named Python/Rust machine classes."""
import hashlib,json,sys
from pathlib import Path
import live_observers as live
from host_gate import idle

def main():
 live.pure.verify();assert idle(), 'IT13 runners must be known idle'
 out=live.pure.BASE/'out/T27/live-return-diagnosis-v1.json';assert not out.exists()
 rejected=json.loads((live.pure.BASE/'out/T27/rejected-preparation-v2.json').read_text())
 for name,digest in rejected['receipts_sha256'].items():
  assert hashlib.sha256((live.pure.BASE/'out/T27'/name).read_bytes()).hexdigest()==digest
 for cls in (live.Oracle,live.PortMachine):cls.at=live.at;cls.on_write=live.on_write
 results=[]
 try:
  for cls in (live.Oracle,live.PortMachine):
   live.ctx.clear();live.ctx.update(root=live.ROOTS[7],scenario=live.SCENARIOS[7],mutate=True,hits={})
   result,_,_=live.exercise(cls,0,root=live.ROOTS[7],controlled=True)
   results.append(result)
  assert results[0]==results[1]
  assert results[0]['error']==('PortError','no registered port/return at 1771:0BE5')
  assert [v[2] for v in results[0]['log'] if v[0]=='abi' and v[1]=='1771:0AA7']==[(0,)]
  report=dict(pass_all=True,backends=[c.__module__+'.'+c.__name__ for c in (live.Oracle,live.PortMachine)],
   equal_full_results=True,error=results[0]['error'],guest_packet=[0],return_ss=results[0]['regs']['ss'],
   explanation='Both frames retain entry SS 0x2000; callback leaves live SS 0x9000 at return. Both reject it.',
   sources={str(p.relative_to(live.pure.BASE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),live.pure.BASE/'out/T27/live_observers.py']})
  with out.open('x') as f:json.dump(report,f,indent=2,sort_keys=True)
  print(json.dumps(report,sort_keys=True))
 finally:
  for cls in (live.Oracle,live.PortMachine):cls.at=live.OLD_AT[cls];cls.on_write=live.OLD_WRITE[cls]
if __name__=='__main__':main()
