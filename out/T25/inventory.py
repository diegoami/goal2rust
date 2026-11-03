"""Registry/helper-resolved six-body text closure; no match/native execution."""
import ast,hashlib,importlib.util,inspect,json
from pathlib import Path
B=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('t24_inventory',B/'out/T24/inventory.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
ROOTS=('214B:00FF','214B:0123','214B:01A3','214B:0205','214B:026D','214B:02C8')
CONFIG={
 '214B:01A3':(True,False,'214B:01BE','214B:01FF',None),
 '214B:0205':(True,True,'214B:0220','214B:0267','214B:0223'),
 '214B:026D':(False,False,'214B:0288','214B:02C2',None),
 '214B:02C8':(False,True,'214B:02E3','214B:0323','214B:02E6'),
}
def inventory():
 p=B/'out/T24/profile-after-v1.json';profile=json.loads(p.read_text());native=set(profile['native_calls']);bodies={}
 for root in ROOTS:
  b=old.body(root);assert not b['sites'] and root not in native
  if root in CONFIG:
   fn=old.ENTRIES[root].fn;tree=ast.parse(inspect.getsource(fn))
   call=next(n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='_string_cells')
   values=tuple(ast.literal_eval(n) for n in call.args[1:]);assert values==CONFIG[root]
   backward,set_attr,copied,written,at=values
   b['specialized_helper']=dict(symbol='original_match.port.display._string_cells',backwards=backward,set_attr=set_attr,copied_ret=copied,written_ret=written,attribute_site=at)
   ht=ast.parse((B/b['path']).read_text());hf=next(n for n in ht.body if isinstance(n,ast.FunctionDef) and n.name=='_string_cells')
   calls=sorted((n for n in ast.walk(hf) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='guest'),key=lambda n:n.lineno);assert len(calls)==2
   assert ast.literal_eval(calls[0].args[2])=='23E4:0644'
   assert ast.unparse(calls[1].args[2])=="'214B:0123' if backwards else '214B:00FF'"
   assert [next(k.value.id for k in c.keywords if k.arg=='ret') for c in calls]==['copied_ret','written_ret']
   b['sites']=[dict(caller=root,target='23E4:0644',ret_to=copied,far=True,helper='display._string_cells',line=calls[0].lineno),dict(caller=root,target='214B:0123' if backward else '214B:00FF',ret_to=written,far=not backward,helper='display._string_cells',line=calls[1].lineno)]
  bodies[root]=b
 sites=[s for b in bodies.values() for s in b['sites']];assert len(sites)==len({s['ret_to'] for s in sites})==8
 assert {s['target'] for s in sites}-set(ROOTS)=={'23E4:0644'} and '23E4:0644' in native
 paths={b['path'] for b in bodies.values()}|{h['path'] for b in bodies.values() for h in b['helper_symbols']}
 paths|={str(p.relative_to(B)) for p in (B/'.cache/goal2-archaeology/runtime/original_match/port').glob('*.py') if p.name in ['runtime.py','mem.py','guest.py','engine.py']}
 moved=sum(profile['routines'][r]['guest_entries'] for r in ROOTS);assert moved==10810
 return dict(oracle=old.inventory()['oracle'],roots=ROOTS,bodies=bodies,boundaries=['23E4:0644'],guest_sites=sites,site_count=8,owned_symbols=sorted({h['symbol'] for b in bodies.values() for h in b['helper_symbols']}),prediction=dict(new_native_bodies=6,new_native_entries=moved,native_bodies=69,native_entries=2688294+moved,python_entries=415391-moved,total=3103685,scope='fixed-fixture entry prediction, not speed/LOC/test coverage'),profile_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),inventory_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),source_sha256={p:hashlib.sha256((B/p).read_bytes()).hexdigest() for p in sorted(paths)})
if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);a=ap.parse_args();r=inventory()
 with Path(a.out).open('x') as f:json.dump(r,f,indent=2,sort_keys=True);f.write('\n')
 print('Closed six bodies/eight sites/',len(r['owned_symbols']),'owned functions;',r['prediction'])
