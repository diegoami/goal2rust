"""Observe all selected source branches/errors, then seal one explicit proof plan."""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
import capture_support as e
e.verify()
e.deny_original()
sys.path[:0] = [str(e.BASE/'engine/tests'), str(e.BASE/'engine/python')]
from test_commentary import *
from branch_probe import Probe

parser = argparse.ArgumentParser()
parser.add_argument('--out', required=True)
a = parser.parse_args()
assert not Path(a.out).exists()
probe = Probe()
errors, maxima = {}, {}
for root in NEW:
    selectors, max_reads, max_writes = {root}, 0, 0
    write_sites = set()
    for controlled in [False, True] if INV['bodies'][root]['sites'] else [False]:
        for case in range(160):
            sys.settrace(probe.trace)
            try:
                p, _, _ = exercise(Oracle, case, root=root, controlled=controlled)
            finally:
                sys.settrace(None)
            assert p['error'] is None, (root, controlled, case, p['error'])
            r, _, _ = exercise(PortMachine, case, root=root, controlled=controlled)
            assert p == r, (root, controlled, case, [k for k in p if p[k] != r[k]])
            if not controlled:
                selectors.update(site for site, _ in p['visits'])
                selectors.update('reg:'+str(row[2]) for row in p['log'] if row[0] == 'io' and row[1] == 'g')
                write_sites.update(p['state']['writes'])
                max_reads = max(max_reads, p['state']['read_index'])
                max_writes = max(max_writes, p['state']['write_index'])
    selectors.update('write:'+str(pc) for pc in write_sites)
    selectors.update('read-index:'+str(i) for i in range(1, max_reads+1))
    ordinals = sorted({i for i in [1, 2, 3, 4, 8, 9, max_writes//2, max_writes] if 1 <= i <= max_writes})
    selectors.update('write-index:'+str(i) for i in ordinals)
    if max_writes:
        selectors.add('write')
    errors[root] = [dict(selector=selector, controlled=False) for selector in sorted(selectors)]
    maxima[root] = dict(max_reads=max_reads, max_writes=max_writes, selected_write_ordinals=ordinals,
                        observed_write_pcs=sorted(write_sites))
    print('OBSERVED', root, len(selectors), 'error selectors', flush=True)
missing = [label for label, count in probe.counts.items() if not count]
print('UNWITNESSED BRANCH OUTCOMES', missing, flush=True)
assert not missing, missing
source = (e.BASE/'engine/src/commentary.rs').read_text()
returns = json.loads('['+re.search(r'pub const RETURNS:.*?= \[(.*?)\];', source, re.S).group(1)+']')
assert returns == list(RETURNS)
rows = sum(len(v) for v in errors.values())
distinct = len({root+'/'+row['selector'] for root, items in errors.items() for row in items})
assert rows == distinct
plan = dict(real_captures_per_body=8, authored_per_body=500, observer_modes=4,
            normal_comparisons=30960, body_control_comparisons=20960, output_control_comparisons=146720,
            return_control_comparisons=4000, branch_cases_per_mode=160,
            cases_per_error_selector=160, error_execution_rows=rows, distinct_error_selectors=distinct,
            error_comparisons=rows*160, errors=errors, observed_maxima=maxima,
            branch_outcomes=sorted(probe.counts), branch_exclusions=probe.exclusions,
            body_controls={root:254+i for i, root in enumerate(NEW)},
            output_controls=[dict(root=root, control=control) for root, control in OUTPUTS],
            return_controls=[dict(**site, control=334+i) for i, site in enumerate(INV['guest_sites'])],
            variants={'0791:1829':['omit-0791-1829'], '0791:1D4A':['ring-players-swapped'],
                      '0791:1E53':['rating-sign'], '214B:1C86':['wrap-high-inclusive']},
            ordinal_scope='Bounded observed early/middle/last writes; no exhaustive global fault coverage claim',
            test_source_sha256=hashlib.sha256((e.BASE/'engine/tests/test_commentary.py').read_bytes()).hexdigest(),
            inventory_sha256=hashlib.sha256((e.BASE/'out/T26/inventory-v1.json').read_bytes()).hexdigest(),
            branch_probe_sha256=hashlib.sha256((e.BASE/'out/T26/branch_probe.py').read_bytes()).hexdigest())
with Path(a.out).open('x') as stream:
    json.dump(plan, stream, indent=2, sort_keys=True)
    stream.write('\n')
print('SEALED', rows, 'rows/', distinct, 'distinct error selectors;', len(probe.counts), 'positive source outcomes', flush=True)
