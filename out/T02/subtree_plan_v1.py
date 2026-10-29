"""Summarise T01's existing drive profile and literal guest-call edges; no game data."""
import ast
import inspect
import json
import pstats
import re
import sys
import textwrap
from pathlib import Path

G2R=Path(__file__).resolve().parents[2]
ROOT=G2R/'.cache/goal2-archaeology'
sys.path.insert(0,str(ROOT/'runtime'))
from original_match.port import load
import goal2rust_engine

stats=pstats.Stats(str(G2R/'out/T01/profile-d3cf46a3-v1.prof')).stats
dispatch_counts={ad:int(n) for ad,n in re.findall(r'^  ([0-9A-F]{4}:[0-9A-F]{4}) (\d+)$',(G2R/'out/T01/profile-d3cf46a3-v1.txt').read_text(),re.M)}
routines={}
seen=set()
modules={}
for registry,_ in load(['all']):
    for address,entry in registry.entries.items():
        if entry.stub is not None: continue
        code=entry.fn.__code__
        key=(code.co_filename,code.co_firstlineno,code.co_name)
        cc,nc,tt,ct,callers=stats.get(key,(0,0,0,0,{}))
        tree=ast.parse(textwrap.dedent(inspect.getsource(entry.fn)))
        edges=[]
        dynamic=0
        for node in ast.walk(tree):
            if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='call':
                if node.args and isinstance(node.args[0],ast.Constant) and isinstance(node.args[0].value,str): edges.append(node.args[0].value)
                else: dynamic+=1
        item=dict(module=registry.name,function=code.co_name,dispatch_calls=dispatch_counts.get(address),python_calls_or_resumes=nc,body_self_s=tt,
                  cumulative_s=ct,native_T02=address in goal2rust_engine.PORTS,
                  literal_guest_callees=sorted(set(edges)),dynamic_guest_calls=dynamic)
        routines[address]=item
        group=modules.setdefault(registry.name,dict(body_self_s=0,python_calls_or_resumes=0))
        if key not in seen:
            group['body_self_s']+=tt
            group['python_calls_or_resumes']+=nc
            seen.add(key)
report=dict(profile='out/T01/profile-d3cf46a3-v1.prof',oracle='d3cf46a3',
            note='Measured in the T01 Python baseline under cProfile. Generator function counts include resumes; only dispatch_calls comes from the recorded port-call table (top 40 only; null means unrecorded). Self times add; cumulative times overlap. Shared Python code is counted once per module and stubs excluded. Literal edges omit dynamic targets and inline helpers.',
            modules=modules,routines=routines)
with Path(sys.argv[1]).open('x') as f: json.dump(report,f,indent=2,sort_keys=True)
print('module unique body self seconds / Python calls or generator resumes')
for n,s in sorted(modules.items(),key=lambda x:-x[1]['body_self_s']): print(n,round(s['body_self_s'],3),s['python_calls_or_resumes'])
print('next hot entries')
for ad,s in sorted(routines.items(),key=lambda x:-(x[1]['dispatch_calls'] or 0))[:35]:
 print(ad,s['module'],s['function'],s['dispatch_calls'],'native' if s['native_T02'] else 'bridge',s['literal_guest_callees'])
