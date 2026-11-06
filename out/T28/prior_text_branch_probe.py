"""Positive source branches for both shared text helpers and all real returns."""
import ast,inspect
from original_match.port import display
class Probe:
 def __init__(self):
  self.conditions={};self.pending={};self.counts={};self.sites={}
  for fn in [display._text_cells,display._string_cells]:
   base=inspect.getsourcelines(fn)[1]-1;conditions={}
   for n in ast.walk(ast.parse(inspect.getsource(fn))):
    if isinstance(n,(ast.If,ast.While)):
     label=fn.__name__+':'+str(n.lineno+base)+':'+type(n).__name__+':'+ast.unparse(n.test);conditions[n.lineno+base]=(label,n.body[0].lineno+base)
     self.counts[label+':true']=self.counts[label+':false']=0
   self.conditions[fn.__code__]=conditions
  assert len(self.counts)==10
 def trace(self,f,event,arg):
  if f.f_code not in self.conditions:return None
  if event=='line':
   previous=self.pending.pop(id(f),None)
   if previous:
    label,line=previous;self.counts[label+(':true' if f.f_lineno==line else ':false')]+=1
   row=self.conditions[f.f_code].get(f.f_lineno)
   if row:self.pending[id(f)]=row
  if event=='return':self.pending.pop(id(f),None)
  return self.trace
 def observe(self,root,p,controlled=False):
  returns={'214B:01BE','214B:01FF','214B:0220','214B:0267','214B:0288','214B:02C2','214B:02E3','214B:0323'}
  for site,_ in p['visits']:
   if site in returns:self.sites[site]=self.sites.get(site,0)+1
  if not controlled:
   reverse=root in ('214B:0123','214B:01A3','214B:0205')
   assert bool(p['regs']['eflags']&0x400)==reverse,(root,'source DF')
