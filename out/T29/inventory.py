"""Complete near-player-zone closure; exclude attribute/global name collisions."""
import hashlib,importlib.util,inspect,json
from pathlib import Path
B=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('t26_inventory',B/'out/T26/inventory.py')
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
ROOT='0791:44C1'
def inventory():
 profile_path=B/'out/T28/profile-after-v1.json';profile=json.loads(profile_path.read_text())
 entry=old.ENTRIES[ROOT];node,calls=old.sites(entry.fn);scope=old.owned(entry.fn)
 # f.w8 is a Frame method, not positioning.w8; the latter is never called here.
 excluded={k:scope.pop(k) for k in list(scope) if k.startswith('original_match.port.positioning.w8:')}
 assert len(excluded)==1 and len(scope)==6
 assert {r['symbol'].split('.')[-1] for r in scope.values()}=={'near_player_zone','argptr','r8','s8','same','guest'}
 assert len(calls)==1 and calls[0]['target']=='0791:2BE5' and calls[0]['ret_to']=='0791:4500' and calls[0]['far']
 assert calls[0]['target'] in profile['native_calls'] and ROOT not in profile['native_calls']
 paths={r['path'] for r in scope.values()}
 paths.update(str(p.relative_to(B)) for p in (old.ORACLE/'runtime/original_match/port').glob('*.py') if p.name in {'runtime.py','mem.py','guest.py','engine.py'})
 moved=profile['routines'][ROOT]['python_entries'];assert moved==16064
 body=dict(address=ROOT,module=entry.fn.__module__,name=entry.fn.__name__,path=str(Path(inspect.getsourcefile(entry.fn)).relative_to(B)),line=node.lineno,end_line=node.end_lineno,ret=entry.ret,pop=entry.pop,long=entry.long,return_stack_delta=entry.return_stack_delta,sites=[dict(caller=ROOT,**r) for r in calls],owned=scope)
 return dict(oracle=old.PIN,root=ROOT,roots=[ROOT],bodies={ROOT:body},boundaries=['0791:2BE5'],guest_sites=body['sites'],site_count=1,owned_code_objects=scope,excluded_attribute_collisions={k:dict(**v,reason='f.w8 resolves a Frame method, not this module global; no direct name load in selected body or reached helpers') for k,v in excluded.items()},
 prediction=dict(new_native_bodies=1,new_native_entries=moved,native_bodies=88,native_entries=2798646+moved,python_entries=305039-moved,total=3103685,scope='One fixture entry prediction,not speed/source/test/whole-game coverage'),
 selection=dict(profile_order=5,body_self_s=profile['routines'][ROOT]['body_self_s'],higher_roots=['0791:6188','0791:5049','0791:73BA','0791:5565'],higher_root_limit='Duel/holder/restart/substitution or rare72F2 state/delay/launch closures; do not cut at unported default callees.',complete_default_guest_closure=True),profile_sha256=hashlib.sha256(profile_path.read_bytes()).hexdigest(),inventory_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),source_sha256={p:hashlib.sha256((B/p).read_bytes()).hexdigest() for p in sorted(paths)})
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args()
 with Path(a.out).open('x') as f:json.dump(inventory(),f,indent=2,sort_keys=True);f.write('\n')
