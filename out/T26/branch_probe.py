"""Observe actual source outcomes without re-evaluating callback-bearing tests."""
import ast
import inspect
from original_match.port import contests, geometry, frame, display, runtime


class Probe:
    def __init__(self):
        self.conditions, self.pending, self.counts, self.exclusions = {}, {}, {}, {}
        functions = [contests.offside_call, geometry.set_message_word,
                     frame.commentary_record_is_new, frame.apply_perf_delta,
                     frame.write_commentary_line, frame.emit_commentary,
                     display.commentary_line_memory, runtime.fill_bytes, runtime.wrap_add]
        for fn in functions:
            base = inspect.getsourcelines(fn)[1]-1
            tree = ast.parse(inspect.getsource(fn))
            positive = next((n for n in ast.walk(tree) if isinstance(n, ast.If)
                             and ast.unparse(n.test) == 's16(delta) > 0'), None)
            inside_positive = {id(n) for child in positive.body for n in ast.walk(child)} if positive else set()
            conditions = {}
            for node in ast.walk(tree):
                if not isinstance(node, (ast.If, ast.While)):
                    continue
                test = ast.unparse(node.test)
                label = fn.__name__+':'+str(base+node.lineno)+':'+type(node).__name__+':'+test
                if 'variant' in test:
                    self.exclusions[label] = 'Variant-only choice; checked by explicit nondefault fallback proofs'
                    continue
                impossible = fn is runtime.wrap_add and (
                    (test == 's16(0) > s16(t_hi)' and id(node) in inside_positive)
                    or (test == 's16(0) < s16(t_hi)' and id(node) not in inside_positive))
                if impossible:
                    self.exclusions[label+':true'] = 'u16 v plus signed16 delta: positive sum cannot have negative high word; nonpositive sum cannot have positive high word'
                constant_loop = isinstance(node, ast.While) and isinstance(node.test, ast.Constant) and node.test.value is True
                if constant_loop:
                    self.exclusions[label+':false'] = 'Unconditional while True exits through its separately observed break condition'
                contexts = [1, 2] if test == 'mem.u8(mem.ss_lin(line + r.di)) == marker' else [None]
                for context in contexts:
                    prefix = label+(':marker='+str(context) if context else '')
                    for outcome in ['false'] if impossible else ['true'] if constant_loop else ['true', 'false']:
                        self.counts[prefix+':'+outcome] = 0
                conditions[base+node.lineno] = dict(label=label, body=base+node.body[0].lineno,
                                                  context=contexts != [None], impossible=impossible,
                                                  constant_loop=constant_loop)
            self.conditions[fn.__code__] = conditions
        self.side_code = frame.commentary_record_is_new.__code__
        self.side_line = next(n.lineno+inspect.getsourcelines(frame.commentary_record_is_new)[1]-1
                              for n in ast.walk(ast.parse(inspect.getsource(frame.commentary_record_is_new)))
                              if isinstance(n, ast.Assign) and isinstance(n.value, ast.IfExp))
        for outcome in ['true', 'false']:
            self.counts['commentary_record_is_new:equal-fields-side-test:'+outcome] = 0

    def trace(self, current, event, arg):
        if current.f_code not in self.conditions:
            return None
        if event == 'line':
            old = self.pending.pop(id(current), None)
            if old:
                if old.get('side'):
                    key = 'commentary_record_is_new:equal-fields-side-test:' + ('true' if current.f_locals['differ'] == 0 else 'false')
                else:
                    outcome = current.f_lineno == old['body']
                    assert not (old['impossible'] and outcome), ('Typed wrap bound falsified', old)
                    assert not (old['constant_loop'] and not outcome), ('Unconditional loop reported false', old)
                    key = old['label']+(':true' if outcome else ':false')
                self.counts[key] += 1
            if current.f_code is self.side_code and current.f_lineno == self.side_line:
                self.pending[id(current)] = dict(side=True)
            else:
                row = self.conditions[current.f_code].get(current.f_lineno)
                if row:
                    row = dict(row)
                    if row['context']:
                        row['label'] += ':marker='+str(current.f_locals['marker'])
                    self.pending[id(current)] = row
        elif event == 'return':
            self.pending.pop(id(current), None)
        return self.trace
