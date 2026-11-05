"""Proof-only positive default source branches, excluding variant-only edges."""
import ast,inspect
from original_match.port import load
from pathlib import Path
import json
BASE=Path(__file__).resolve().parents[2]
ADDRESSES=set(json.loads((BASE/'out/T18/inventory-v2.json').read_text())['bodies'])
ENTRIES={a:e for r,v in load(['all']) for a,e in r.entries.items() if a in ADDRESSES}
class Probe:
 def __init__(self):
  self.conditions={};self.pending={};self.counts={}
  for ad,e in ENTRIES.items():
   tree=ast.parse(inspect.getsource(inspect.getmodule(e.fn)));fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==e.fn.__name__);rows={}
   for n in ast.walk(fn):
    if not isinstance(n,ast.If) or any(isinstance(v,ast.Name) and v.id=='variant' for v in ast.walk(n.test)):continue
    name=ad+':'+str(n.lineno)+':'+ast.unparse(n.test);rows[n.lineno]=(name,n.body[0].lineno)
    self.counts[name+':true']=self.counts[name+':false']=0
   self.conditions[e.fn.__code__]=rows
 def trace(self,f,event,arg):
  if f.f_code not in self.conditions:return None
  if event=='line':
   old=self.pending.pop(id(f),None)
   if old:
    name,line=old;self.counts[name+(':true' if f.f_lineno==line else ':false')]+=1
   new=self.conditions[f.f_code].get(f.f_lineno)
   if new:self.pending[id(f)]=new
  return self.trace
