"""Resolve the complete offside/commentary tree, including site tables and loops."""
import ast
import hashlib
import inspect
import json
import sys
import types
from pathlib import Path

B = Path.cwd()
ORACLE = B / '.cache/goal2-archaeology'
sys.path.insert(0, str(ORACLE / 'runtime'))
from original_match.port import load

PIN = '2cbeb36fdd3feb369324aaa88e6e4d2aa3b3d99c'
ROOT = '0791:56D9'
ENTRIES = {a: e for registry, _ in load(['all']) for a, e in registry.entries.items()}
DISPATCH = {'guest', 'call', 'go', 'near', 'same', 'far', '_g'}


def value(node, env):
    if isinstance(node, ast.Name) and node.id in env:
        return env[node.id]
    return ast.literal_eval(node)


def bind(node, item, env):
    if isinstance(node, ast.Name):
        env[node.id] = item
    else:
        assert isinstance(node, (ast.Tuple, ast.List)) and len(node.elts) == len(item)
        for target, val in zip(node.elts, item):
            bind(target, val, env)


def sites(fn):
    path = Path(inspect.getsourcefile(fn))
    tree = ast.parse(path.read_text())
    root = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == fn.__name__)
    rows = []

    def walk(node, env):
        if isinstance(node, ast.For):
            try:
                items = value(node.iter, env)
            except (ValueError, TypeError):
                items = [None]
            for item in items:
                nested = dict(env)
                if item is not None:
                    bind(node.target, item, nested)
                for child in node.body:
                    walk(child, nested)
            for child in node.orelse:
                walk(child, env)
            return
        if isinstance(node, (ast.FunctionDef, ast.Lambda)):
            return
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            kind = node.func.id
            if kind in DISPATCH:
                keywords = {k.arg: k.value for k in node.keywords}
                if kind == 'go':
                    site = value(node.args[0], env)
                    target, far, ret, nargs = fn.__globals__['go'].__globals__['SITES'][site]
                    assert len(node.args) - 1 == nargs
                    resolution = dict(kind='SITES', site=f'0791:{site:04X}', nargs=nargs)
                else:
                    index = 0 if kind == 'call' else 2 if kind in {'guest', '_g'} else 1
                    target = value(node.args[index], env)
                    prefix = '214B:' if kind == '_g' else '0791:'
                    if ':' not in target:
                        target = prefix + target
                    key = 'ret_to' if kind == 'call' else 'ret' if kind in {'guest', '_g'} else 'at'
                    ret = value(keywords[key], env)
                    if ':' not in ret:
                        ret = prefix + ret
                    far = value(keywords['far'], env) if 'far' in keywords else kind != 'near'
                    resolution = dict(kind=kind, loop_bindings=env)
                rows.append(dict(target=target, ret_to=ret, far=far, line=node.lineno,
                                 path=str(path.relative_to(B)), resolution=resolution))
        for child in ast.iter_child_nodes(node):
            walk(child, env)

    for node in root.body:
        walk(node, {})
    unique = {}
    for row in rows:
        key = (row['target'], row['ret_to'], row['far'])
        if key not in unique:
            unique[key] = row
    return root, sorted(unique.values(), key=lambda r: (r['line'], r['ret_to']))


def owned(fn):
    todo, seen, rows = [fn], set(), {}
    while todo:
        helper = todo.pop()
        if helper in seen:
            continue
        seen.add(helper)
        codes = [helper.__code__]
        while codes:
            code = codes.pop()
            symbol = helper.__module__ + '.' + code.co_qualname
            key = symbol + ':' + str(code.co_firstlineno)
            rows[key] = dict(symbol=symbol, line=code.co_firstlineno,
                             path=str(Path(code.co_filename).relative_to(B)))
            codes.extend(c for c in code.co_consts if isinstance(c, types.CodeType))
            for name in code.co_names:
                ref = helper.__globals__.get(name)
                if inspect.isfunction(ref) and ref.__module__.startswith('original_match.port') and name != 'call':
                    todo.append(ref)
    return dict(sorted(rows.items()))


def inventory():
    profile_path = B / 'out/T25/profile-after-v1.json'
    profile = json.loads(profile_path.read_text())
    native = set(profile['native_calls'])
    bodies, boundaries, todo = {}, set(), [ROOT]
    while todo:
        address = todo.pop()
        if address in bodies:
            continue
        if address in native:
            boundaries.add(address)
            continue
        entry = ENTRIES[address]
        fn, calls = sites(entry.fn)
        bodies[address] = dict(address=address, module=entry.fn.__module__, name=entry.fn.__name__,
                               path=str(Path(inspect.getsourcefile(entry.fn)).relative_to(B)),
                               line=fn.lineno, end_line=fn.end_lineno, ret=entry.ret, pop=entry.pop,
                               long=entry.long, return_stack_delta=entry.return_stack_delta,
                               sites=[dict(caller=address, **r) for r in calls], owned=owned(entry.fn))
        todo.extend(r['target'] for r in calls)
    assert set(bodies) == {'0791:56D9', '0791:26A0', '0791:2B0F', '0791:1EB5',
                           '0791:1E53', '0791:1D4A', '0791:1C78', '0791:1829',
                           '214B:0018', '214B:1C86'}
    calls = [s for b in bodies.values() for s in b['sites']]
    assert len(calls) == len({r['ret_to'] for r in calls}) == 25
    scope = {k: v for b in bodies.values() for k, v in b['owned'].items()}
    assert sum('.<locals>.word' in key for key in scope) == 2
    paths = {r['path'] for r in scope.values()}
    paths |= {str(p.relative_to(B)) for p in (ORACLE / 'runtime/original_match/port').glob('*.py')
              if p.name in {'runtime.py', 'mem.py', 'guest.py', 'engine.py'}}
    moved = sum(profile['routines'][a]['guest_entries'] for a in bodies)
    assert moved == 45569
    return dict(oracle=PIN, root=ROOT, roots=[ROOT], bodies=dict(sorted(bodies.items())),
                boundaries=sorted(boundaries), guest_sites=calls, site_count=len(calls),
                owned_code_objects=dict(sorted(scope.items())),
                prediction=dict(new_native_bodies=10, new_native_entries=moved, native_bodies=79,
                                native_entries=2699104 + moved, python_entries=404581 - moved,
                                total=3103685, scope='One fixed fixture entry prediction; no speed or coverage claim'),
                profile_sha256=hashlib.sha256(profile_path.read_bytes()).hexdigest(),
                inventory_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                source_sha256={p: hashlib.sha256((B / p).read_bytes()).hexdigest() for p in sorted(paths)})


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    report = inventory()
    with Path(args.out).open('x') as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print('Ten-body closure,25 sites,', len(report['owned_code_objects']), 'owned code objects', report['prediction'])
