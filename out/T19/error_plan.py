"""Declared source error sites; regimes exercise real registers and isolated calls."""
import ast,inspect,json
from pathlib import Path
from original_match.port import load
BASE=Path(__file__).resolve().parents[2]
INVENTORY=json.loads((BASE/'out/T19/inventory-v1.json').read_text())
ENTRIES={a:e for r,v in load(['all']) for a,e in r.entries.items()}
def strings(n,assign):
 if isinstance(n,ast.Constant):return [n.value] if isinstance(n.value,str) else []
 if isinstance(n,ast.IfExp):return strings(n.body,assign)+strings(n.orelse,assign)
 if isinstance(n,ast.Name) and n.id in assign:return strings(assign[n.id],assign)
 return []
def own_writes(root):
 fn=ENTRIES[root].fn;tree=ast.parse(inspect.getsource(inspect.getmodule(fn)));node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==fn.__name__)
 assign={n.targets[0].id:n.value for n in ast.walk(node) if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)};sites=set()
 for n in ast.walk(node):
  if not isinstance(n,ast.Call):continue
  if isinstance(n.func,ast.Name) and n.func.id in ('w8','w16','push_word'):sites.update('0791:'+s for s in strings(n.args[-1],assign))
  if isinstance(n.func,ast.Attribute) and n.func.attr in ('w8','w16','wds8','wds16','enter') and n.args:sites.update(strings(n.args[-1],assign))
 if root!='23E4:08DF' and not root.startswith('0791:4') :sites.add('214B:0000')
 if root=='0791:40BC':sites.add('214B:0000')
 if root=='214B:06FA':sites.add('214B:069F')
 return sorted(sites)
def selectors(root,read_names):
 b=INVENTORY['bodies'][root];caller=bool(b['sites']);rows=[dict(selector=root,controlled=False)]
 rows += [dict(selector='reg:'+name,controlled=False) for name in sorted(read_names)]
 if own_writes(root):rows.append(dict(selector='write',controlled=caller))
 rows += [dict(selector='write:'+s,controlled=caller) for s in own_writes(root)]
 rows += [dict(selector=s['target'],controlled=True) for s in {r['target']:r for r in b['sites']}.values()]
 for s in b['sites']:rows.extend([dict(selector=s['ret_to'],controlled=True),dict(selector='write:'+s['ret_to'],controlled=True)])
 return rows
