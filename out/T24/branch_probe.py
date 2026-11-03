"""Reachable source service/frame branches and semantic callback witnesses."""
import ast,inspect
from original_match.port import menus
class Probe:
 def __init__(self):
  self.pending={};self.counts={};self.conditions={}
  fn=menus.read_key;tree=ast.parse(inspect.getsource(fn));base=inspect.getsourcelines(fn)[1]-1
  for n in ast.walk(tree):
   if isinstance(n,ast.If):
    label='read_key:'+ast.unparse(n.test);self.conditions[n.lineno+base]=(label,n.body[0].lineno+base);self.counts[label+':true']=self.counts[label+':false']=0
  self.sites={};self.source_ret_sites=0
 def trace(self,f,event,arg):
  if f.f_code is menus._ret_site.__code__:
   if event=='return' and isinstance(arg,str):self.source_ret_sites+=1;self.sites[arg]=self.sites.get(arg,0)+1
   return self.trace
  if f.f_code is not menus.read_key.__code__:return None
  if event=='line':
   old=self.pending.pop(id(f),None)
   if old:
    label,line=old;self.counts[label+(':true' if f.f_lineno==line else ':false')]+=1
   row=self.conditions.get(f.f_lineno)
   if row:self.pending[id(f)]=row
  if event=='return':self.pending.pop(id(f),None)
  return self.trace
