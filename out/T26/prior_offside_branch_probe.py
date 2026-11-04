"""Source branch/loop and signed arithmetic witnesses, independent of native code."""
import ast,inspect
from original_match.port import motion
class Probe:
 def __init__(self):
  self.conditions={};self.pending={};self.counts={}
  for fn in [motion.track_offside_line,motion.move_sprite,motion.place_marker]:
   node=ast.parse(inspect.getsource(fn));base=inspect.getsourcelines(fn)[1]-1
   for n in ast.walk(node):
    if isinstance(n,ast.If):
     if 'variant' in ast.unparse(n.test):continue
     label=fn.__name__+':'+str(n.lineno+base)+':'+ast.unparse(n.test)
     self.conditions[(fn.__code__,n.lineno+base)]=(label,n.body[0].lineno+base)
     self.counts[label+':true']=self.counts[label+':false']=0
  for label in ['cell:negative-row','cell:nonnegative-row','cell:negative-column','cell:nonnegative-column','cell:offset-wrap','loop:ten-players','loop:first-high','loop:first-low','marker:signed-add-wrap']:self.counts[label]=0
 def trace(self,f,event,arg):
  if f.f_code is motion.cell.__code__:
   if event=='return':
    d=f.f_locals;row=d['row'];col=d['col'];self.counts['cell:negative-row' if row&128 else 'cell:nonnegative-row']+=1;self.counts['cell:negative-column' if col&128 else 'cell:nonnegative-column']+=1
    self.counts['cell:offset-wrap']+=d['boff']+motion.mul(motion.cbw(row),160)[0]+((motion.cbw(col)<<1)&65535)>65535
   return self.trace
  if f.f_code not in {c for c,_ in self.conditions}:return None
  if event=='line':
   old=self.pending.pop(id(f),None)
   if old:
    label,line=old;self.counts[label+(':true' if f.f_lineno==line else ':false')]+=1
   row=self.conditions.get((f.f_code,f.f_lineno))
   if row:self.pending[id(f)]=row
   if f.f_code is motion.track_offside_line.__code__ and f.f_lineno==417:
    d=f.f_locals
    assert d['k']==d['first']+11
    self.counts['loop:ten-players']+=1;self.counts['loop:first-high' if d['first']>244 else 'loop:first-low']+=1
  if event=='return':self.pending.pop(id(f),None)
  if event=='line' and f.f_code is motion.place_marker.__code__ and f.f_lineno==465:
   self.counts['marker:signed-add-wrap']+=f.f_locals['ax']>255
  return self.trace
