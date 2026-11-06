"""Observe fixed-block edges and semantic choices without re-reading memory."""
import ast,inspect
from original_match.port import attributes,quick

class Probe:
 def __init__(self):
  self.counts={};self.pending={};self.previous={};self.conditions={};self.block_lines={}
  self.exclusions={'variant-only':'Explicit nondefault fallback proofs cover variant-only choices',
                   'pc-dispatch':'Track actual block edges instead of false comparisons in the dispatch ladder',
                   'while-True:false':'Constant loop exits through its source branch/return edges'}
  self.root=quick.listing_1771_0BC4.__code__
  source,base=inspect.getsourcelines(quick.listing_1771_0BC4);base-=1
  tree=ast.parse(''.join(source));loop=next(n for n in tree.body[0].body if isinstance(n,ast.While));branch=loop.body[0]
  while isinstance(branch,ast.If):
   pc=ast.literal_eval(branch.test.comparators[0]);self.block_lines[branch.body[0].lineno+base]=pc
   for statement in branch.body:
    if isinstance(statement,ast.Assign) and isinstance(statement.targets[0],ast.Name) and statement.targets[0].id=='pc':
     value=statement.value
     targets=[value.body,value.orelse] if isinstance(value,ast.IfExp) else [value]
     for target in targets:self.counts[f'quick-edge:{pc:04X}->{ast.literal_eval(target):04X}']=0
   branch=branch.orelse[0]
  for fn in [attributes.player_strength,attributes.out_of_place_flag]:
   base=inspect.getsourcelines(fn)[1]-1;conditions={}
   for node in ast.walk(ast.parse(inspect.getsource(fn))):
    if not isinstance(node,ast.If):continue
    test=ast.unparse(node.test)
    if 'variant' in test:continue
    label=fn.__name__+':'+str(node.lineno+base)+':'+test
    conditions[node.lineno+base]=(label,node.body[0].lineno+base)
    for outcome in ['true','false']:self.counts[label+':'+outcome]=0
   self.conditions[fn.__code__]=conditions
  for fn in ['two-footed','bit-result']:
   for value in [0,1]:self.counts[fn+':'+str(value)]=0
 def trace(self,f,event,arg):
  if f.f_code is self.root:
   if event=='line' and f.f_lineno in self.block_lines:
    pc=self.block_lines[f.f_lineno];previous=self.previous.get(id(f))
    if previous is not None:
     key=f'quick-edge:{previous:04X}->{pc:04X}';assert key in self.counts,key;self.counts[key]+=1
    self.previous[id(f)]=pc
   if event=='return' and arg is None:self.previous.pop(id(f),None)
   return self.trace
  if f.f_code in self.conditions:
   if event=='line':
    previous=self.pending.pop(id(f),None)
    if previous:
     label,line=previous;self.counts[label+(':true' if f.f_lineno==line else ':false')]+=1
    row=self.conditions[f.f_code].get(f.f_lineno)
    if row:self.pending[id(f)]=row
   if event=='return':self.pending.pop(id(f),None)
   return self.trace
  return None
 def observe(self,root,result):
  if root=='1771:3041':self.counts['two-footed:'+str(result['regs']['eax']&1)]+=1
  if root=='214B:0C57':self.counts['bit-result:'+str(result['regs']['eax']&1)]+=1
