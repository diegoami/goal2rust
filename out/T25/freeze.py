"""Seal explicit final producer inputs/sources;no generated reports as sources."""
import ast,hashlib,json,sys
from pathlib import Path
import evidence as e
B=e.BASE;O=B/'out/T25';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
e.verify();assert not (O/'freeze-v1.json').exists() and not (O/'source-inputs-v1.json').exists()
assert json.loads((O/'artifact-archive-v1.json').read_text())['both_full_public_preflights_before_archive']
for name in ['cpython','pypy']:
 text=(O/f'public-{name}-preflight-v1.log').read_text();assert 'Ran 94 tests' in text and text.rstrip().endswith('OK')
sources=sorted(p.name for p in O.glob('*.py'))
for name in sources:ast.parse((O/name).read_text())
manifest=dict(proof_sources=sources,proof_source_sha256={name:sha(O/name) for name in sources},generated_reports_excluded=True)
with (O/'source-inputs-v1.json').open('x') as f:json.dump(manifest,f,indent=2,sort_keys=True);f.write('\n')
before=e.hashes();assert all(p.exists() for p in [B/s for s in before])
inv=json.loads((O/'inventory-v2.json').read_text());plan=json.loads((O/'proof-plan-v1.json').read_text());assert len(inv['bodies'])==6 and len(inv['owned_symbols'])==14 and len(inv['guest_sites'])==8
assert plan['error_execution_rows']==plan['distinct_error_selectors']==171 and plan['error_comparisons']==27360
assert plan['test_source_sha256']==sha(B/'engine/tests/test_text.py') and plan['inventory_sha256']==sha(O/'inventory-v2.json')
r=dict(oracle=e.PIN,revision=e.git('rev-parse','HEAD'),source_sha256=before,source_count=len(before),explicit_proof_sources=len(sources),same_combined_artifact=True,baseline_snapshot='out/T25/baseline-snapshot-v1.json',artifact_archive='out/T25/artifact-archive-v1.json',proof_pool_limit=3,M2_stages=87,canonical_groups=92,guest_sites=8,error_execution_rows=171,distinct_error_selectors=171,body_controls=list(range(198,204)),output_controls=list(range(204,246)),return_controls=list(range(246,254)))
with (O/'freeze-v1.json').open('x') as f:json.dump(r,f,indent=2,sort_keys=True);f.write('\n')
assert e.hashes()==before;print('Frozen',len(before),'concrete bindings/',len(sources),'explicit sources;87 M2/92 canonical groups')
