"""Positive source branch and copy-mode witnesses, never inferred from native code."""
import ast,inspect
from original_match.port import runtime
class Probe:
 def __init__(self):
  self.pending={};self.conditions={};self.counts={};self.functions={runtime._copy_forward.__code__,runtime.sys_str_store_max.__code__,runtime.str_concat.__code__}
  for fn in [runtime._copy_forward,runtime.sys_str_store_max,runtime.str_concat]:
   tree=ast.parse(inspect.getsource(fn));base=inspect.getsourcelines(fn)[1]-1
   for n in ast.walk(tree):
    if isinstance(n,ast.If):
     label=fn.__name__+':'+ast.unparse(n.test);self.conditions[(fn.__code__,n.lineno+base)]=(label,n.body[0].lineno+base);self.counts[label+':true']=self.counts[label+':false']=0
  for key in ['copy:empty','copy:eight','copy:nine','copy:overlap-forward','copy:overlap-backward','copy:wrap-source','copy:wrap-destination','copy:unmasked65536','max:high-byte-ignored','concat:exact255','concat:overflow','concat:empty-source']:self.counts[key]=0
 def trace(self,f,event,arg):
  if f.f_code not in self.functions:return None
  if event=='call':
   d=f.f_locals
   if f.f_code is runtime._copy_forward.__code__:
    n=d['n'];so=d['soff'];do=d['doff'];sl=d['sseg']*16+(so&65535);dl=d['dseg']*16+(do&65535)
    for key,hit in [('empty',n==0),('eight',n==8),('nine',n==9),('overlap-forward',sl<dl<sl+n),('overlap-backward',dl<sl<dl+n),('wrap-source',so+n>65536),('wrap-destination',do+n>65536),('unmasked65536',so==65536 or do==65536)]:self.counts['copy:'+key]+=hit
  if event=='line':
   old=self.pending.pop(id(f),None)
   if old:
    label,line=old;self.counts[label+(':true' if f.f_lineno==line else ':false')]+=1
   row=self.conditions.get((f.f_code,f.f_lineno))
   if row:self.pending[id(f)]=row
  if event=='return':
   self.pending.pop(id(f),None);d=f.f_locals
   if f.f_code is runtime.sys_str_store_max.__code__:self.counts['max:high-byte-ignored']+=d['mx']>255
   if f.f_code is runtime.str_concat.__code__:
    self.counts['concat:exact255']+=d['total']==255;self.counts['concat:overflow']+=d['total']>255;self.counts['concat:empty-source']+=d['total']==d['cl']
  return self.trace
