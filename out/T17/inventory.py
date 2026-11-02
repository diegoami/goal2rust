"""Reproduce T17's source inventory without loading the game or native extension."""
import ast, hashlib, json
from pathlib import Path
BASE=Path(__file__).resolve().parents[2]
PORT=BASE/'.cache/goal2-archaeology/runtime/original_match/port'
ROOTS={'0791:47C5','0791:4438','0791:2996','0791:2C54','214B:06B1'}
BOUNDARY={'1771:3216','0791:278A','1771:3A06','0791:2BE5'}
def inventory():
 bodies={}; inbound=[];sites=[]
 for file in sorted(PORT.glob('*.py')):
  for fn in ast.parse(file.read_text()).body:
   if not isinstance(fn,(ast.FunctionDef,ast.AsyncFunctionDef)):continue
   address=None;abi=None
   for d in fn.decorator_list:
    if isinstance(d,ast.Call) and isinstance(d.func,ast.Attribute) and d.func.attr=='port' and d.args and isinstance(d.args[0],ast.Constant):
     address=d.args[0].value;abi=next((k.value.value for k in d.keywords if k.arg=='ret'),None)
   if not address:continue
   if address in ROOTS:bodies[address]=dict(module=file.stem,name=fn.name,ret=abi,line=fn.lineno,guest_sites=[])
   for call in ast.walk(fn):
    if not isinstance(call,ast.Call) or not isinstance(call.func,ast.Name):continue
    kind=call.func.id
    if kind not in {'near','same','far','guest','call'}:continue
    at=0 if kind=='call' else 1
    if len(call.args)<=at or not isinstance(call.args[at],ast.Constant) or not isinstance(call.args[at].value,str):continue
    target=call.args[at].value
    if kind in {'near','same'}:target='0791:'+target
    kw={k.arg:k.value for k in call.keywords}
    ret=kw.get('ret_to',kw.get('at'));ret=ret.value if isinstance(ret,ast.Constant) else None
    if ret and ':' not in ret:ret='0791:'+ret
    far=kind!='near'
    if 'far' in kw and isinstance(kw['far'],ast.Constant):far=kw['far'].value
    row=dict(caller=address,target=target,ret_to=ret,far=far,module=file.stem,line=call.lineno)
    if target in ROOTS:inbound.append(row)
    if address in ROOTS:sites.append(row)
 for s in sites:bodies[s['caller']]['guest_sites'].append(s)
 assert set(bodies)==ROOTS
 assert len(sites)==13 and all(s['target'] in ROOTS|BOUNDARY for s in sites)
 files=['positioning.py','geometry.py','entrypoints.py','runtime.py','mem.py','guest.py','engine.py']
 return dict(oracle='2cbeb36fdd3feb369324aaa88e6e4d2aa3b3d99c',bodies=bodies,guest_sites=sites,literal_registered_inbound_sites=inbound,inbound_note='Static literal sites only; registry dispatch can also invoke each registered body directly. Inline runtime.invoke calls remain inline.',source_sha256={str((PORT/f).relative_to(BASE)):hashlib.sha256((PORT/f).read_bytes()).hexdigest() for f in files})
if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);a=ap.parse_args()
 with Path(a.out).open('x') as f:json.dump(inventory(),f,indent=2,sort_keys=True);f.write('\n')
