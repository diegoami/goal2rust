"""Compile this pinned function's fixed Python blocks into explicit native Rust.

No instruction bytes/runtime Python inspection or general ISA interpreter.
Every expression is lowered in source evaluation order before a helper call.
"""
import ast,hashlib,inspect,json,sys
from pathlib import Path
B=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(B/'.cache/goal2-archaeology/runtime'))
from original_match.port.quick import listing_1771_0BC4

class Generator:
 def __init__(self):self.serial=0;self.lines=[];self.segments={};self.label=None
 def temp(self,expression):
  self.serial+=1;name='t'+str(self.serial);self.lines.append(f'let {name} = {expression};');return name
 def expression(self,n):
  if isinstance(n,ast.Constant):
   if isinstance(n.value,bool):return str(n.value).lower()
   assert isinstance(n.value,int);return str(n.value)+'i64'
  if isinstance(n,ast.Name):
   assert n.id in {'z','unsigned','signed','_v','_a','_b','_off','_seg','_divisor','_q'}
   return 's.'+n.id.lstrip('_')
  if isinstance(n,ast.Attribute):
   assert isinstance(n.value,ast.Name)
   if n.value.id=='mem' and n.attr=='DS':return self.temp('h.ds() as i64')
   assert n.value.id=='r'
   if n.attr=='ss':return self.temp('r.ss(h)? as i64')
   assert n.attr in {'ax','bx','cx','dx','si','di','es','sp','bp'}
   return self.temp('r.get(h, Reg::'+n.attr.title()+')? as i64')
  if isinstance(n,ast.BinOp):
   a=self.expression(n.left);b=self.expression(n.right)
   ops={ast.Add:'+',ast.Sub:'-',ast.Mult:'*',ast.BitAnd:'&',ast.BitOr:'|',ast.BitXor:'^',ast.LShift:'<<',ast.RShift:'>>'}
   if isinstance(n.op,ast.FloorDiv):return self.temp(f'({a}).div_euclid({b})')
   return self.temp(f'({a}) {ops[type(n.op)]} ({b})')
  if isinstance(n,ast.Compare):
   assert len(n.ops)==len(n.comparators)==1
   a=self.expression(n.left);b=self.expression(n.comparators[0]);op={ast.Eq:'==',ast.NotEq:'!=',ast.GtE:'>=',ast.Lt:'<'}[type(n.ops[0])]
   return self.temp(f'({a}) {op} ({b})')
  if isinstance(n,ast.UnaryOp):
   a=self.expression(n.operand)
   return self.temp(('!' if isinstance(n.op,ast.Not) else '-')+'('+a+')')
  if isinstance(n,ast.IfExp):
   test=self.expression(n.test)
   boolean=isinstance(n.test,ast.Compare) or (isinstance(n.test,ast.UnaryOp) and isinstance(n.test.op,ast.Not)) or (isinstance(n.test,ast.Name) and n.test.id=='z') or (isinstance(n.test,ast.Constant) and isinstance(n.test.value,bool))
   if not boolean:test=self.temp('('+test+') != 0')
   saved=self.lines;self.lines=[];a=self.expression(n.body);left=self.lines;self.lines=[];b=self.expression(n.orelse);right=self.lines;self.lines=saved
   return self.temp('if '+test+' { '+' '.join(left)+a+' } else { '+' '.join(right)+b+' }')
  if isinstance(n,ast.Call):
   if isinstance(n.func,ast.Name) and n.func.id in {'abs','s16'}:
    a=self.expression(n.args[0]);return self.temp(f'({a}).abs()' if n.func.id=='abs' else f'({a} as u16 as i16) as i64')
   if isinstance(n.func,ast.Name) and n.func.id=='_read':
    seg,off,width=[self.expression(a) for a in n.args[2:]]
    return self.temp(f'read(h, &mut r, {seg} as u16, {off}, {width} as u8)? as i64')
   if isinstance(n.func,ast.Name) and n.func.id=='_pop':return self.temp('pop(h, &mut r)? as i64')
   if isinstance(n.func,ast.Name) and n.func.id=='bool':return self.temp('('+self.expression(n.args[0])+') != 0')
   if isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Name) and n.func.value.id=='mem':
    if n.func.attr=='reg':
     assert ast.literal_eval(n.args[0])=='eflags';return self.temp('h.reg(Reg::Eflags)? as i64')
    assert n.func.attr=='seg';a=self.expression(n.args[0]);return self.temp(f'h.seg({a} as u16) as i64')
  raise AssertionError(ast.dump(n))
 def assign(self,target,value):
  if isinstance(target,ast.Attribute):
   assert isinstance(target.value,ast.Name) and target.value.id=='r'
   self.lines.append(f'r.set(Reg::{target.attr.title()}, {value} as u32);');return
  assert isinstance(target,ast.Name)
  if target.id=='pc':self.lines.append(f's.qpc = {value} as u16;')
  else:self.lines.append(f's.{target.id.lstrip("_")} = {value};')
 def save_segment(self):
  assert self.label not in self.segments,self.label
  self.segments[self.label]=self.lines;self.lines=[]
 def statement(self,n):
  if isinstance(n,ast.Assign):
   assert len(n.targets)==1
   if isinstance(n.value,ast.YieldFrom):
    call=n.value.value;assert isinstance(call.func,ast.Name) and call.func.id=='_call'
    target,count,ret,far=[ast.literal_eval(a) for a in call.args[2:]]
    resume=int(ret[5:],16)
    self.lines += [f'let mut words = Vec::with_capacity({count});',f'for _ in 0..{count} {{ words.push(pop(h, &mut r)?); }}',
                   'words.reverse();','r.store(h, true)?;',f's.qpc = {resume};',
                   f'return Ok(call(s, Phase::Quick, "{target}", "{ret}", words, {str(far).lower()}));']
    self.save_segment();self.label=resume;return
   if isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name) and n.value.func.id=='divmod':
    a,b=[self.expression(a) for a in n.value.args];q=self.temp(f'({a}).div_euclid({b})');rem=self.temp(f'({a}).rem_euclid({b})')
    assert isinstance(n.targets[0],ast.Tuple)
    for target,value in zip(n.targets[0].elts,[q,rem]):self.assign(target,value)
    return
   self.assign(n.targets[0],self.expression(n.value));return
  if isinstance(n,ast.Expr):
   call=n.value;assert isinstance(call,ast.Call)
   if isinstance(call.func,ast.Name) and call.func.id=='_write':
    seg,off,width,value=[self.expression(a) for a in call.args[2:6]];pc=ast.literal_eval(call.args[6]);assert pc[:5]=='1771:'
    self.lines.append(f'write_regs(h, &mut r, {seg} as u16, {off}, {width} as u8, {value} as u16, 0x{pc[5:]})?;');return
   assert isinstance(call.func,ast.Attribute) and isinstance(call.func.value,ast.Name) and call.func.value.id=='r'
   if call.func.attr=='push':
    value=self.expression(call.args[0]);self.lines.append(f'r.push(h, {value} as u32)?;');return
   assert call.func.attr=='store';assert len(call.keywords)==1 and call.keywords[0].arg=='stack' and ast.literal_eval(call.keywords[0].value) is True
   self.lines.append('r.store(h, true)?;');return
  if isinstance(n,ast.Continue):self.lines.append('continue;');return
  if isinstance(n,ast.Return):
   assert isinstance(n.value,ast.Constant) and n.value.value is None
   self.lines.append('return Ok(Action::Done(None));');return
  raise AssertionError(ast.dump(n))
 def generate(self):
  tree=ast.parse(inspect.getsource(listing_1771_0BC4));fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef));loop=next(n for n in fn.body if isinstance(n,ast.While));branch=loop.body[0]
  while isinstance(branch,ast.If):
   assert ast.unparse(branch.test.left)=='pc'
   self.label=ast.literal_eval(branch.test.comparators[0]);self.lines=[]
   for stmt in branch.body:self.statement(stmt)
   self.save_segment();assert len(branch.orelse)==1;branch=branch.orelse[0]
  assert isinstance(branch,ast.Raise)
  output=['// Generated by out/T28/generate_quick_root.py from the pinned Python function.',
          'fn quick<H: Host>(h: &mut H, resumed: bool, mut s: Saved) -> Result<Action,H::Err> {',
          'let mut r = Regs::new(resumed);','loop { match s.qpc {']
  for label,lines in self.segments.items():output += [f'0x{label:04X} => {{']+lines+['}']
  output += ['_ => unreachable!("invalid sealed quick-strength block"),','} }','}']
  return '\n'.join(output)+'\n'

if __name__=='__main__':
 output=Generator().generate();path=B/'engine/src/strength_quick.inc.rs'
 assert not path.exists()
 with path.open('x') as f:f.write(output)
 print('Generated explicit Rust source blocks;',len(output.splitlines()),'lines')
