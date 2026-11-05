"""Proof-only source branch observations; no instrumentation in timing arms."""
import ast,inspect,sys
from original_match.port import positioning,geometry,entrypoints
FUNCS=(positioning.choose_marking_target,positioning.near_post_zone)
class Probe:
 def __init__(self):
  self.conditions={};self.pending={};self.counts={};self.slots=set();self.draws=set();self.products=set();self.holders=set();self.zone=set()
  for fn in FUNCS:
   tree=ast.parse(inspect.getsource(inspect.getmodule(fn)))
   node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==fn.__name__)
   rows={}
   for n in ast.walk(node):
    if isinstance(n,ast.If):
     name=f'{fn.__name__}:{n.lineno}:{ast.unparse(n.test)}';rows[n.lineno]=(name,n.body[0].lineno)
     self.counts[name+':true']=self.counts[name+':false']=0
   self.conditions[fn.__code__]=rows
 def trace(self,frame,event,arg):
  code=frame.f_code
  if code not in self.conditions and code not in {geometry.c2996.__code__,geometry.c2c54.__code__,entrypoints.rng_core.__code__}:return None
  ident=id(frame)
  if code in self.conditions and event=='line':
   old=self.pending.pop(ident,None)
   if old:
    name,first=old;self.counts[name+(':true' if frame.f_lineno==first else ':false')]+=1
   cond=self.conditions[code].get(frame.f_lineno)
   if cond:self.pending[ident]=cond
   if code is positioning.choose_marking_target.__code__ and 'slot' in frame.f_locals:self.slots.add(frame.f_locals['slot'])
  if event=='return':
   loc=frame.f_locals
   if code is geometry.c2996.__code__ and 'R' in loc:self.holders.add(loc['R']._v.get('ax',0)&255)
   if code is geometry.c2c54.__code__ and 'R' in loc:self.products.add(loc['R']._v.get('ax',0)&255)
   if code is entrypoints.rng_core.__code__ and 'new' in loc:
    self.draws.add((loc['n'],bool(loc['high']),loc['step']))
   if code is positioning.near_post_zone.__code__ and 'close' in loc:self.zone.add(bool(loc['close']))
  return self.trace
 def report(self):return dict(conditions=self.counts,slots=sorted(self.slots),holder_results=sorted(self.holders),half_results=sorted(self.products),zone_results=sorted(self.zone),rng_cases=sorted(self.draws))
