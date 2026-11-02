"""T18 registry-resolved closed-tree inventory; no native/game execution."""
import ast,hashlib,inspect,json,sys
from pathlib import Path
BASE=Path(__file__).resolve().parents[2];ORACLE=BASE/'.cache/goal2-archaeology';sys.path[:0]=[str(ORACLE/'runtime')]
from original_match.port import load
ROOT='0791:4B64';PROFILE=BASE/'out/T17/profile-after-v1.json';NATIVE=set(json.loads(PROFILE.read_text())['native_calls'])
ENTRIES={a:e for r,v in load(['all']) for a,e in r.entries.items()}
def literals(n,assign):
 if isinstance(n,ast.Constant):return [n.value]
 if isinstance(n,ast.IfExp):return literals(n.body,assign)+literals(n.orelse,assign)
 if isinstance(n,ast.Name) and n.id in assign:return literals(assign[n.id],assign)
 raise ValueError('Unsealed finite expression '+ast.unparse(n))
def body(address):
 e=ENTRIES[address];path=Path(inspect.getsourcefile(e.fn));tree=ast.parse(path.read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==e.fn.__name__)
 assign={n.targets[0].id:n.value for n in ast.walk(fn) if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)}
 sites=[];inline=[]
 for n in ast.walk(fn):
  if not isinstance(n,ast.Call) or not isinstance(n.func,ast.Name):continue
  kind=n.func.id
  if kind=='invoke':inline.append(dict(line=n.lineno,cs=ast.unparse(n.args[2]),return_ip=ast.unparse(n.args[3]),core=ast.unparse(n.args[4])));continue
  if kind not in {'near','same','far','call'}:continue
  i=0 if kind=='call' else 1;target=literals(n.args[i],assign);assert len(target)==1
  target=target[0];target=('0791:'+target) if kind in {'near','same'} else target
  kw={k.arg:k.value for k in n.keywords};rets=literals(kw['ret_to' if kind=='call' else 'at'],assign)
  far=kind!='near'
  if 'far' in kw:far=ast.literal_eval(kw['far'])
  for ret in rets:sites.append(dict(caller=address,target=target,ret_to=ret if ':' in ret else '0791:'+ret,far=far,line=n.lineno,expression=ast.unparse(n)))
 helpers=[];todo=[e.fn];seen=set()
 while todo:
  helper=todo.pop();key=helper.__module__+'.'+helper.__name__
  if key in seen:continue
  seen.add(key);hp=Path(inspect.getsourcefile(helper));ht=ast.parse(hp.read_text());hf=next((n for n in ht.body if isinstance(n,ast.FunctionDef) and n.name==helper.__name__),None)
  if hf is None:continue
  helpers.append(dict(symbol=key,path=str(hp.relative_to(BASE)),line=hf.lineno))
  for ref in ast.walk(hf):
   if isinstance(ref,ast.Name):
    v=helper.__globals__.get(ref.id)
    if inspect.isfunction(v) and v.__module__.startswith('original_match.port') and ref.id not in {'call'}:todo.append(v)
 return dict(address=address,module=e.fn.__module__,name=e.fn.__name__,ret=e.ret,pop=e.pop,long=e.long,return_stack_delta=e.return_stack_delta,path=str(path.relative_to(BASE)),line=fn.lineno,end_line=fn.end_lineno,sites=sorted(sites,key=lambda r:(r['line'],r['ret_to'])),inline_invokes=inline,helper_symbols=sorted(helpers,key=lambda r:r['symbol']))
def inventory():
 bodies={};bound=set();todo=[ROOT]
 while todo:
  address=todo.pop()
  if address in bodies:continue
  if address in NATIVE:bound.add(address);continue
  b=body(address);bodies[address]=b;todo.extend(s['target'] for s in b['sites'])
 assert len(bodies)==15
 profile=json.loads(PROFILE.read_text());new_entries=sum(profile['routines'][a]['guest_entries'] for a in bodies)
 paths={b['path'] for b in bodies.values()}|{h['path'] for b in bodies.values() for h in b['helper_symbols']}
 paths|={str(p.relative_to(BASE)) for p in (ORACLE/'runtime/original_match/port').glob('*.py') if p.name in ['runtime.py','mem.py','guest.py','engine.py']}
 sites=[s for b in bodies.values() for s in b['sites']];assert len({s['ret_to'] for s in sites})==len(sites)
 return dict(oracle='2cbeb36fdd3feb369324aaa88e6e4d2aa3b3d99c',root=ROOT,bodies=dict(sorted(bodies.items())),boundaries=sorted(bound),guest_sites=sites,site_count=len(sites),prediction=dict(new_native_bodies=15,new_native_entries=new_entries,native_bodies=43,native_entries=2129564+new_entries,python_entries=974121-new_entries,total=3103685,scope='unchanged fixture entry prediction only; no speed forecast'),profile_sha256=hashlib.sha256(PROFILE.read_bytes()).hexdigest(),source_sha256={p:hashlib.sha256((BASE/p).read_bytes()).hexdigest() for p in sorted(paths)})
if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);a=ap.parse_args();r=inventory()
 with Path(a.out).open('x') as f:json.dump(r,f,indent=2,sort_keys=True);f.write('\n')
 print('Closed',len(r['bodies']),'bodies;',r['site_count'],'sites;',r['prediction'])
