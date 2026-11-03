"""Authored cyclic-lifetime check for bound bridge callables and registered ports."""
import gc,sys,weakref,json,hashlib
from pathlib import Path
import evidence as e
e.verify();before=e.hashes()
sys.path[:0]=['engine/python','.cache/goal2-archaeology/runtime']
from goal2rust.machine import PortMachine,BridgeRunner
from original_match.port import Entry
rows=[]
for fast in [False,True]:
 for i in range(10):
  m=PortMachine(bytes(0x110000),0x823,fast=fast);mem=m.port_memory()
  def leaf(mem,v):return None
  m.port('0791:0100',BridgeRunner(Entry('0791:0100','ret',leaf,'gc-leaf'),None,mem,{}))
  r=weakref.ref(m);s=weakref.ref(mem);del m,mem;gc.collect()
  assert r() is None and s() is None
  rows.append(dict(fast=fast,collected=True))
e.write('out/T24/gc-parity-v1.json',dict(pass_all=True,cases=rows,script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),before)
print('20 registered-port/callable cycles collected')
