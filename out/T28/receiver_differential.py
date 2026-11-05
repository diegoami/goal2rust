"""Fresh combined-artifact T28 per-body/control/error/branch/closure proofs."""
import argparse
import hashlib
import json
import pickle
import sys
import time
import evidence as e
sys.path.insert(0, str(e.BASE/'engine/tests'))
from test_receiver import *
from branch_probe import Probe


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    parser.add_argument('--suite', required=True, choices=['normal', 'body', 'output', 'returns'])
    a = parser.parse_args()
    assert not Path(a.out).exists()
    e.verify()
    before = e.hashes()
    e.deny_original()
    O = e.BASE/'out/T28'
    plan = json.loads((O/'proof-plan-v1.json').read_text())
    meta = json.loads((O/'captures-v1.json').read_text())
    raw = e.BASE/meta['private_file']
    assert hashlib.sha256(raw.read_bytes()).hexdigest() == meta['sha256']
    captures = pickle.loads(raw.read_bytes())
    assert all(len(captures[root]) == 8 for root in NEW)
    counts, differences, owned, closure, errors, controls = {}, [], {}, {}, {}, {}
    error_pairs = variants = 0
    outside_owned, variant_owned = {}, {}
    probe = None
    start = time.monotonic()

    def pair(root, case, kind, mutant=0, **options):
        p, _, ps = exercise(Oracle, case, root=root, **options)
        r, native, rs = exercise(PortMachine, case, root=root, mutant=mutant, **options)
        assert p['error'] is None, (root, case, kind, p['error'])
        key = root+'/'+kind+('/control'+str(mutant) if a.suite == 'output' else '')
        row = counts.setdefault(key, dict(total=0, equal=0))
        row['total'] += 1
        row['equal'] += p == r
        assert (p == r) == (mutant == 0), (root, case, kind, mutant, [k for k in p if p[k] != r[k]])
        if p != r and len(differences) < 15:
            differences.append(dict(root=root, case=case, kind=kind,
                                    fields=[k for k in p if p[k] != r[k]],
                                    python=e.digest(p), rust=e.digest(r)))
        if not mutant:
            assert native.get(root) == 1
            if options.get('profile'):
                assert ps['owned'] and not rs['owned'] 
                closure[root] = closure.get(root, 0)+1
                for name, n in ps['owned'].items():owned[name] = owned.get(name, 0)+n

    if a.suite == 'returns':
        for index, site in enumerate(INV['guest_sites']):
            row = controls[site['ret_to']] = dict(total=160, reached=0, detected=0)
            for case in range(160):
                p, _, _ = exercise(Oracle, case, root=site['caller'])
                r, _, _ = exercise(PortMachine, case, root=site['caller'], mutant=435+index)
                assert p['error'] is None
                reached = site['ret_to'] in {s for s, _ in p['visits']}
                row['reached'] += reached
                row['detected'] += p != r
                assert (p != r) == reached, (site['ret_to'], case)
            assert row['reached'] == row['detected'] > 0
            print('RETURN', site['ret_to'], row, flush=True)
    else:
        jobs = list(OUTPUTS) if a.suite == 'output' else [(root, 427+i if a.suite == 'body' else 0) for i, root in enumerate(NEW)]
        for root, mutant in jobs:
            for case, snapshot in enumerate(captures[root]):
                for tapped in (False, True):
                    for listener in (False, True):
                        for schedule in range(3):
                            pair(root, case, 'real', mutant=mutant, snapshot=snapshot,
                                 tapped=tapped, listener=listener, direct=schedule == 2,
                                 pause=root if schedule == 1 else None, profile=not mutant)
            for case in range(500):
                for tapped in (False, True):
                    for listener in (False, True):
                        pair(root, case, 'authored-integrated', mutant=mutant, tapped=tapped,
                             listener=listener, pause=SITES[case % len(SITES)], direct=case % 3 == 0,
                             mutations=case % 7 == 0, profile=not mutant)
                if case % 100 == 99:print(a.suite, root, mutant, case+1, flush=True)
        if a.suite == 'normal':
            for root in NEW:
                if INV['bodies'][root]['sites']:
                    for case in range(500):
                        for tapped in (False, True):
                            for listener in (False, True):
                                pair(root, case, 'controlled-ABI', controlled=True, tapped=tapped,
                                     listener=listener, direct=case % 3 == 0, pause=RETURNS[case % len(RETURNS)])
            probe = Probe()
            for root in NEW:
                for controlled in [False, True] if INV['bodies'][root]['sites'] else [False]:
                    for case in range(160):
                        sys.settrace(probe.trace)
                        try:p, _, _ = exercise(Oracle, case, root=root, controlled=controlled)
                        finally:sys.settrace(None)
                        r, _, _ = exercise(PortMachine, case, root=root, controlled=controlled)
                        assert p['error'] is None and p == r, ('branch', root, case, controlled)
            assert sorted(probe.counts) == plan['branch_outcomes'] and all(probe.counts.values())
            assert probe.exclusions == plan['branch_exclusions']
            for root in NEW:
                for row in plan['errors'][root]:
                    key = root+'/'+row['selector']
                    errors[key] = 0
                    for case in range(160):
                        opts = dict(root=root, failure=row['selector'], controlled=row['controlled'])
                        p, _, _ = exercise(Oracle, case, **opts)
                        r, _, _ = exercise(PortMachine, case, **opts)
                        assert p == r, ('error', key, case, [k for k in p if p[k] != r[k]])
                        errors[key] += p['error'] is not None
                        error_pairs += 1
                    assert errors[key] > 0, ('unreached error', key)
                    print('ERROR', key, errors[key], flush=True)
                for variant in ['identity']+plan['variants'].get(root, []):
                    for case in range(16):
                        p, _, _ = exercise(Oracle, case, root=root, variant=variant)
                        r, native, scope = exercise(PortMachine, case, root=root, variant=variant, profile=True)
                        assert p['error'] is None and p == r and root not in native and scope['owned']
                        for name,n in scope['owned'].items():variant_owned[name]=variant_owned.get(name,0)+n
                        variants += 1
            class OutsideNative(PortMachine):
                def __init__(self,memory,load):super().__init__(memory,load,native=False)
            for case in range(16):
                p,_,_=exercise(Oracle,case)
                r,native,scope=exercise(OutsideNative,case,profile=True)
                assert p==r and not native and scope['owned']
                for name,n in scope['owned'].items():outside_owned[name]=outside_owned.get(name,0)+n
            assert set(outside_owned)==set(variant_owned)==set(INV['owned_code_objects'])
            assert all(closure[root] == 2096 for root in NEW)
            assert set(owned) == set(INV['owned_code_objects']) and all(owned.values())
            assert error_pairs == plan['error_comparisons'] and len(errors) == plan['distinct_error_selectors']
    total = sum(row['total'] for row in counts.values())
    expected = dict(normal=4096, body=2096, output=14672, returns=0)[a.suite]
    assert total == expected
    report = dict(suite=a.suite, captures={root:8 for root in NEW}, comparisons=counts,
                  differences=differences, all_equal=all(row['total'] == row['equal'] for row in counts.values()),
                  control_scope_verified=True, all_inventory_helper_scope=True,
                  owned_code_objects=INV['owned_code_objects'], source_owned_calls=owned,
                  outside_native_owned_calls=outside_owned,nondefault_owned_calls=variant_owned,
                  closure_checks=closure, return_controls=controls, branches=None if probe is None else probe.counts,
                  branch_comparisons=320 if probe else 0, variants=variants,
                  errors_seen=errors, error_comparisons=error_pairs, wall_s=time.monotonic()-start)
    if a.suite in ['body', 'output']:assert not report['all_equal'] and all(row['equal'] == 0 for row in counts.values())
    e.write(a.out, report, before)
    print(a.suite, total, 'comparisons pass', flush=True)


if __name__ == '__main__':main()
