"""Seven-body quick strength closure;resolve _call,gcall and set-test helpers."""
import ast
import hashlib
import importlib.util
import inspect
import json
from pathlib import Path

B = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('t26_inventory', B/'out/T26/inventory.py')
old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)
ROOT = '1771:0BC4'
EXPECTED = {'1771:0AA7','1771:0BC4','1771:3041','1771:3088','1771:3179','1771:377E','214B:0C57'}


def sites(fn):
    path = Path(inspect.getsourcefile(fn))
    tree = ast.parse(path.read_text())
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == fn.__name__)
    result = []
    for call in ast.walk(node):
        if not isinstance(call, ast.Call) or not isinstance(call.func, ast.Name):
            continue
        name = call.func.id
        keywords = {k.arg:k.value for k in call.keywords}
        if name == '_call':
            assert fn.__globals__[name].__module__ == 'original_match.port.quick'
            target, count, ret, far = [ast.literal_eval(x) for x in call.args[2:6]]
            assert old.ENTRIES[target].pop == count*2
            resolution = dict(kind='quick._call', consumed_words=count, argument_order='pop then reverse and re-push')
            line = call.lineno
        elif name == 'gcall':
            assert fn.__globals__[name].__module__ == 'original_match.port.attributes'
            target = ast.literal_eval(call.args[3])
            ret = ast.literal_eval(keywords['ret_to'])
            far = ast.literal_eval(keywords['far']) if 'far' in keywords else True
            resolution = dict(kind='attributes.gcall', consumes_sent_AX=True, live_DX_after_sent=True)
            line = call.lineno
        elif name == 'set_test':
            helper = fn.__globals__[name]
            if helper.__module__ != 'original_match.port.attributes':
                continue
            assert helper.__name__ == 'set_test'
            helper_path = Path(inspect.getsourcefile(helper))
            helper_tree = ast.parse(helper_path.read_text())
            helper_node = next(n for n in helper_tree.body if isinstance(n,ast.FunctionDef) and n.name == 'set_test')
            guest = next(n for n in ast.walk(helper_node) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id == 'gcall')
            target = ast.literal_eval(guest.args[3])
            assert target == '23E4:08DF' and keywords == {}
            ret = ast.literal_eval(call.args[5])
            far = True
            resolution = dict(kind='attributes.set_test', helper_line=guest.lineno,
                              helper_path=str(helper_path.relative_to(B)), binds_ret_to_argument=5)
            line = call.lineno
        else:
            # All other owned helpers are arithmetic/read/write/record methods.
            assert name not in {'call','guest','go','near','far','same','invoke','_g'}, (fn.__name__,ast.unparse(call))
            continue
        result.append(dict(target=target,ret_to=ret,far=far,line=line,
                           path=str(path.relative_to(B)),resolution=resolution))
    return node, sorted(result,key=lambda row:(row['line'],row['ret_to']))


def inventory():
    profile_path = B/'out/T26/profile-after-v1.json'
    profile = json.loads(profile_path.read_text())
    native = set(profile['native_calls'])
    bodies,boundaries,todo = {},set(),[ROOT]
    from original_match.port.attributes import Rec
    for address in iter(lambda:todo.pop() if todo else None,None):
        if address in native:
            boundaries.add(address)
            continue
        if address in bodies:
            continue
        entry = old.ENTRIES[address]
        node,calls = sites(entry.fn)
        scope = old.owned(entry.fn)
        if 'Rec' in entry.fn.__code__.co_names:
            # Rec is an owned attribute helper,not the generic memory/Frame API.
            for method in [Rec.__init__,Rec.u8,Rec.lin]:
                code = method.__code__
                name = method.__module__+'.'+code.co_qualname+':'+str(code.co_firstlineno)
                scope[name] = dict(symbol=method.__module__+'.'+code.co_qualname,
                                   line=code.co_firstlineno,path=str(Path(code.co_filename).relative_to(B)))
        bodies[address] = dict(address=address,module=entry.fn.__module__,name=entry.fn.__name__,
                               path=str(Path(inspect.getsourcefile(entry.fn)).relative_to(B)),
                               line=node.lineno,end_line=node.end_lineno,ret=entry.ret,pop=entry.pop,
                               long=entry.long,return_stack_delta=entry.return_stack_delta,
                               sites=[dict(caller=address,**row) for row in calls],owned=scope)
        todo.extend(row['target'] for row in calls)
    assert set(bodies) == EXPECTED
    calls = [row for body in bodies.values() for row in body['sites']]
    assert len(calls) == len({row['ret_to'] for row in calls}) == 12
    scope = {name:row for body in bodies.values() for name,row in body['owned'].items()}
    assert len([key for key in scope if '.Rec.' in key]) == 3
    paths = {row['path'] for row in scope.values()}
    paths.update(str(p.relative_to(B)) for p in (old.ORACLE/'runtime/original_match/port').glob('*.py')
                 if p.name in {'runtime.py','mem.py','guest.py','engine.py'})
    moved = sum(profile['routines'][address]['guest_entries'] for address in bodies)
    assert moved == 18250 and boundaries == {'1771:3216','23E4:08DF'}
    return dict(oracle=old.PIN,root=ROOT,roots=[ROOT],bodies=dict(sorted(bodies.items())),
                boundaries=sorted(boundaries),guest_sites=calls,site_count=12,
                owned_code_objects=dict(sorted(scope.items())),
                class_method_ownership=['attributes.Rec.__init__','attributes.Rec.lin','attributes.Rec.u8'],
                prediction=dict(new_native_bodies=7,new_native_entries=moved,native_bodies=86,
                                native_entries=2744673+moved,python_entries=359012-moved,total=3103685,
                                scope='Fixed-fixture entry prediction,not speed or source/test coverage'),
                profile_sha256=hashlib.sha256(profile_path.read_bytes()).hexdigest(),
                inventory_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                source_sha256={p:hashlib.sha256((B/p).read_bytes()).hexdigest() for p in sorted(paths)})


if __name__ == '__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',required=True)
    args=parser.parse_args()
    report=inventory()
    with Path(args.out).open('x') as stream:
        json.dump(report,stream,indent=2,sort_keys=True)
        stream.write('\n')
    print('Seven bodies/12 returns/',len(report['owned_code_objects']),'owned code objects',report['prediction'])
