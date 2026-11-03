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
 def observe(self,root,p):
  def add(k):self.counts[k]=self.counts.get(k,0)+1
  writes=[x for x in p['log'] if x[0]=='w'];pc=lambda off:((0x214b+0x823)&65535)*16+off
  if root=='214B:0723':
   truth=[x[1] for x in p['log'] if x[0]=='provider-truth'];assert len(truth)==1 and not writes
   add('poll:truth-true' if truth[0] else 'poll:truth-false');add('poll:no-BIOS-frame')
  if root=='214B:08DD':
   if p['state'].get('keys'):
    assert all(x[4]!=pc(0) for x in writes);add('read:kit-no-frame')
   else:
    assert writes[0][4]==pc(0x8ea) and writes[1][4]==pc(0x97c) and writes[2][4]==pc(0)
    add('read:pushed-frame-after-immediate-writes')
  if root=='214B:0993':
   assert writes[0][4]==pc(0x996) and writes[1][4]==pc(0) and writes[2][4]==pc(0x99e)
   add('push:flag-before-frame-flush-before-key')
  if root=='214B:0983':
   assert any(x[4]==pc(0x98a) and x[3]==0 for x in writes);add('wait:real-return-key-clear')
