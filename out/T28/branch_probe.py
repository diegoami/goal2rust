"""Source branches and short-circuit operands observed without extra memory reads."""
import ast,inspect
from original_match.port.contests import pass_receiver_destination
class Probe:
 def __init__(self):
  self.root=pass_receiver_destination.__code__;self.pending={};self.conditions={};self.counts={}
  base=inspect.getsourcelines(pass_receiver_destination)[1]-1
  for node in ast.walk(ast.parse(inspect.getsource(pass_receiver_destination))):
   if not isinstance(node,ast.If):continue
   label='receiver-match' if not isinstance(node.test,ast.BoolOp) else 'keeper-or-countdown'
   self.conditions[base+node.lineno]=(label,base+node.body[0].lineno)
   for outcome in ['true','false']:self.counts[label+':'+outcome]=0
  for name in ['keeper-short-circuit:yes','keeper-short-circuit:no','nonkeeper-countdown:below10','nonkeeper-countdown:at-least10']:self.counts[name]=0
  self.exclusions={'variant-only':'receiver-to-target is positively exercised by explicit nondefault fallback proofs','nested-loop-positive':'Default533B calls nested with levels=1;no positive iteration of range(levels-1) is in this root contract'}
 def trace(self,f,event,arg):
  if f.f_code is not self.root:return None
  if event=='line':
   prior=self.pending.pop(id(f),None)
   if prior:
    label,body=prior;yes=f.f_lineno==body;self.counts[label+(':true' if yes else ':false')]+=1
    if label=='keeper-or-countdown':
     # r.al was cached by the already executed condition. Inspect only that
     # local cache, never call a getter or re-read guest memory.
     keeper=bool(f.f_locals['r']._v['ax']&255)
     self.counts['keeper-short-circuit:'+('yes' if keeper else 'no')]+=1
     if not keeper:self.counts['nonkeeper-countdown:'+('below10' if yes else 'at-least10')]+=1
   row=self.conditions.get(f.f_lineno)
   if row:self.pending[id(f)]=row
  if event=='return':self.pending.pop(id(f),None)
  return self.trace
