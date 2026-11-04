"""Seal all final proof sources/inputs after both complete public preflights."""
import ast
import hashlib
import json
import os
from pathlib import Path
import types
import evidence as e

B = e.BASE
O = B/'out/T26'
sha = lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
e.verify()
assert not (O/'freeze-v1.json').exists() and not (O/'source-inputs-v1.json').exists()
archive = json.loads((O/'artifact-archive-v1.json').read_text())
assert archive['both_full_public_preflights_before_archive']
for name in ['cpython', 'pypy']:
    text = (O/f'public-{name}-preflight-v1.log').read_text()
    assert 'Ran 98 tests' in text and text.rstrip().endswith('OK')
inventory = json.loads((O/'inventory-v1.json').read_text())
plan = json.loads((O/'proof-plan-v1.json').read_text())
assert len(inventory['bodies']) == 10 and len(inventory['owned_code_objects']) == 31 and inventory['site_count'] == 25
assert plan['error_execution_rows'] == plan['distinct_error_selectors'] == 921 and plan['error_comparisons'] == 147360
assert len(plan['branch_outcomes']) == 65
assert plan['test_source_sha256'] == sha(B/'engine/tests/test_commentary.py')
assert plan['inventory_sha256'] == sha(O/'inventory-v1.json') and plan['branch_probe_sha256'] == sha(O/'branch_probe.py')
sources = sorted(p.name for p in O.glob('*.py'))
for name in sources:ast.parse((O/name).read_text(), filename=name)
controller = (O/'supervise.py').read_text()
queued = []
def start(name, *args, **kw):queued.append(name)
program = controller[controller.index("start('public-cpython-v1'"):controller.index('drain(3)')]
exec(program, dict(start=start, producer=start, wait=lambda *x:None, PY='python', e=e, os=os))
assert len(queued) == len(set(queued)) == 92
assert {'commentary-normal-v1', 'commentary-body-v1', 'commentary-output-v1', 'commentary-returns-v1',
        'prior-text-live-observers-v1', 'live-observers-v1', 'scoped-write-errors-v1'} <= set(queued)
manifest = dict(proof_sources=sources, proof_source_sha256={name:sha(O/name) for name in sources},
                generated_reports_excluded=True)
with (O/'source-inputs-v1.json').open('x') as stream:
    json.dump(manifest, stream, indent=2, sort_keys=True)
    stream.write('\n')
before = e.hashes()
report = dict(oracle=e.PIN, revision=e.git('rev-parse', 'HEAD'), source_sha256=before,
              source_count=len(before), explicit_proof_sources=len(sources), same_combined_artifact=True,
              M2_stages=92, canonical_groups=97, guest_sites=25, error_execution_rows=921,
              distinct_error_selectors=921, body_controls=list(range(254,264)),
              output_controls=list(range(264,334)), return_controls=list(range(334,359)),
              baseline_snapshot='out/T26/baseline-snapshot-v1.json',
              artifact_archive='out/T26/artifact-archive-v1.json', proof_pool_limit=3)
with (O/'freeze-v1.json').open('x') as stream:
    json.dump(report, stream, indent=2, sort_keys=True)
    stream.write('\n')
assert e.hashes() == before
print('Frozen', len(before), 'concrete bindings/', len(sources), 'explicit sources;92 M2/97 canonical groups')
