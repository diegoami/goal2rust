"""Positive source flags/sign/wrap and independent modulo32 arithmetic witnesses."""
import ast,inspect
from original_match.port import runtime,motion
class Probe:
 def __init__(self):
  self.pending={};self.conditions={};self.counts={}
  fn=runtime.add_flags;node=ast.parse(inspect.getsource(fn)).body[0];base=fn.__code__.co_firstlineno-1
  for n in ast.walk(node):
   if isinstance(n,ast.If):
    label='add-flags:'+ast.unparse(n.test);self.conditions[n.lineno+base]=(label,n.body[0].lineno+base)
    self.counts[label+':true']=self.counts[label+':false']=0
  for label in ['abs:negative','abs:nonnegative','abs:minword','sum:wrap','sum:no-wrap','sum:negative','sum:nonnegative','mul:zero','mul:nonzero','mul:overflow32','mul:no-overflow32','mul:lhs-negative','mul:lhs-nonnegative','mul:rhs-negative','mul:rhs-nonnegative','mul:modulo32']:self.counts[label]=0
 def trace(self,f,event,arg):
  if f.f_code is runtime.add_flags.__code__:
   if event=='line':
    old=self.pending.pop(id(f),None)
    if old:
     label,line=old;self.counts[label+(':true' if f.f_lineno==line else ':false')]+=1
    row=self.conditions.get(f.f_lineno)
    if row:self.pending[id(f)]=row
   return self.trace
  if f.f_code is motion.absw.__code__:
   if event=='call':
    value=f.f_locals['ax']&65535;self.counts['abs:negative' if value&32768 else 'abs:nonnegative']+=1;self.counts['abs:minword']+=value==32768
   return None
  if f.f_code is motion.ball_travel.__code__:
   if event=='return' and 's' in f.f_locals:
    d=f.f_locals;self.counts['sum:wrap' if d['a']+d['b']>65535 else 'sum:no-wrap']+=1;self.counts['sum:negative' if d['s']&32768 else 'sum:nonnegative']+=1
   return self.trace
  if f.f_code is runtime.sys_long_mul.__code__:
   if event=='return':
    d=f.f_locals;lhs=(d['dx']<<16)|d['ax'];rhs=(d['bx']<<16)|d['cx'];product=lhs*rhs;words=d['R']._v
    assert (words['dx']<<16)|words['ax']==product&0xffffffff
    self.counts['mul:modulo32']+=1;self.counts['mul:zero' if (product&0xffffffff)==0 else 'mul:nonzero']+=1
    self.counts['mul:overflow32' if product>0xffffffff else 'mul:no-overflow32']+=1
    self.counts['mul:lhs-negative' if lhs&0x80000000 else 'mul:lhs-nonnegative']+=1
    self.counts['mul:rhs-negative' if rhs&0x80000000 else 'mul:rhs-nonnegative']+=1
   return self.trace
  return None
