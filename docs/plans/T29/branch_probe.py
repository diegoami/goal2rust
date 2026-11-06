"""Prepared T29 source branch observer; no extra memory or register reads.

Install into out/T29 only after the development controller exits. This module
has not yet been exercised against the candidate artifact.
"""
import ast,inspect
from original_match.port.positioning import near_player_zone,r8
class Probe:
 def __init__(self):
  self.root=near_player_zone.__code__;self.read=r8.__code__;self.frames={}
  source,base=inspect.getsourcelines(near_player_zone);tree=ast.parse(''.join(source))
  fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef))
  outer=next(n for n in fn.body if isinstance(n,ast.If));inner=next(n for n in outer.body if isinstance(n,ast.If))
  self.guard=base+outer.lineno-1;self.xcheck=base+inner.lineno-1
  self.yassign=base+inner.body[-1].lineno-1
  self.local=base+fn.body[-2].lineno-1
  self.counts={key:0 for key in ['state13:yes','state13:no','holder-equal:yes','holder-equal:no','x-near:yes','x-near:no','y-near:yes','y-near:no']}
  self.exclusions={}
 def trace(self,f,event,arg):
  if f.f_code is self.root:
   row=self.frames.setdefault(id(f),{})
   if event=='line':
    line=f.f_lineno
    if line==self.guard:row['guard_pending']=True;row.pop('slot_read',None)
    elif row.pop('guard_pending',False):
     state13=row.pop('state13');self.counts['state13:'+('yes' if state13 else 'no')]+=1
     if not state13:
      assert row.get('slot_read'),'second operand was not reached'
      self.counts['holder-equal:'+('yes' if line==self.local else 'no')]+=1
    if line==self.xcheck:self.counts['x-near:'+('yes' if f.f_locals['close'] else 'no')]+=1
    if line==self.yassign:row['y_pending']=True
    if line==self.local and row.pop('y_pending',False):self.counts['y-near:'+('yes' if f.f_locals['close'] else 'no')]+=1
   # A generator also returns a yielded Call; keep its pending state until the
   # actual final return rather than treating suspension as an epilogue.
   if event=='return' and isinstance(arg,int):self.frames.pop(id(f),None)
   return self.trace
  if f.f_code is self.read and event=='return' and f.f_back is not None and f.f_back.f_code is self.root:
   row=self.frames.setdefault(id(f.f_back),{});field=f.f_locals['k']
   if field==0x12:row['state13']=arg==13
   if field==6:row['slot_read']=True
  return self.trace
