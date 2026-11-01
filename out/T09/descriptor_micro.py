"""Authored Regs property microbenchmark/parity; no whole-drive speed claim."""
import argparse,hashlib,json,os,statistics,sys,time
from pathlib import Path
BASE=Path(__file__).resolve().parents[2];sys.path[:0]=[str(BASE/'engine/python'),str(BASE/'.cache/goal2-archaeology/runtime')]
from original_match.port.runtime import Regs
from goal2rust.register_cache import FastRegs,counts
from goal2rust.machine import PortMachine

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);a=ap.parse_args();assert not Path(a.out).exists()
 m=PortMachine(bytes(0x110000),0x823);mem=m.port_memory();mem._entries.append((0x100,True))
 samples={};outcomes={}
 for cls in [Regs,FastRegs]:
  r=cls(mem);r.ax=0x1234
  tests={'get':lambda:r.ax,'set':lambda:setattr(r,'ax',0x4321),'halves':lambda:setattr(r,'al',0x81)}
  for name,fn in tests.items():
   values=[]
   for repeat in range(5):
    start=time.process_time()
    for _ in range(1000000):fn()
    values.append((time.process_time()-start)/1000000)
   samples[cls.__name__+':'+name]=values
  outcomes[cls.__name__]=dict(values=r._v,dirty=sorted(r._dirty),sp=r.sp)
 assert outcomes['Regs']==outcomes['FastRegs']
 report=dict(samples=samples,medians={k:statistics.median(v) for k,v in samples.items()},same_state=True,descriptor_counts=counts(),source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),limitations='Authored single-object property microbenchmark; no whole-drive performance claim')
 with Path(a.out).open('x') as f:json.dump(report,f,indent=2)
 print(json.dumps(report['medians'],indent=2))
if __name__=='__main__':main()
