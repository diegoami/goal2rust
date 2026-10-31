"""Authored-memory bridge microbenchmark; diagnostic, not whole-drive speed proof."""
import argparse,hashlib,json,os,platform,statistics,sys,time
from pathlib import Path
BASE=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(BASE/'engine/python'),str(BASE/'.cache/goal2-archaeology/runtime')]
from original_match.port.engine import PortMachine as Oracle
from goal2rust.machine import PortMachine
from goal2rust_engine import GuestMemory

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);ap.add_argument('--iterations',type=int,default=500000);a=ap.parse_args()
 assert not Path(a.out).exists() and os.environ.get('PYTHONHASHSEED')=='0'
 machines={'plain':Oracle(bytes(0x110000),0x823),'rust':PortMachine(bytes(0x110000),0x823)}
 tests={}
 for name,m in machines.items():
  mem=m.port_memory();m._memory[32:34]=b'\x34\x12'
  tests[name+':word-read']=lambda mem=mem:mem.u16(32)
  tests[name+':byte-read']=lambda mem=mem:mem.u8(32)
  tests[name+':register-read']=lambda mem=mem:mem.reg('ax')
  tests[name+':register-write']=lambda mem=mem:mem.set_reg('ax',0x1234)
  tests[name+':word-write']=lambda m=m:m.write_as(32,2,0x1234,0x100)
 view=GuestMemory(machines['rust']._memory)
 tests['direct-existing-view:word-read']=lambda:view.u16(32)
 tests['direct-existing-core:register-read']=lambda:machines['rust']._core.reg(machines['rust'],'ax')
 tests['direct-existing-core:register-write']=lambda:machines['rust']._core.set_reg(machines['rust'],'ax',0x1234)
 samples={k:[] for k in tests}
 for repeat in range(5):
  order=list(tests);order=order[repeat:]+order[:repeat]
  for name in order:
   fn=tests[name];start=time.process_time()
   for _ in range(a.iterations):fn()
   samples[name].append((time.process_time()-start)/a.iterations)
 report=dict(node=platform.node(),python=sys.version,iterations=a.iterations,repeats=5,
             samples_cpu_s_per_op=samples,median_cpu_s_per_op={k:statistics.median(v) for k,v in samples.items()},
             source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),load=os.getloadavg(),
             limitations='One authored-memory microbenchmark. Call-loop/profile overhead included; no whole-drive or PyPy-win claim.')
 with Path(a.out).open('x') as f:json.dump(report,f,indent=2)
 print(json.dumps(report['median_cpu_s_per_op'],indent=2))
if __name__=='__main__':main()
