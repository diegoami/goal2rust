"""Verify accepted T25 ledgers and exclusively preserve it before any build."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

B = Path(__file__).resolve().parents[2]
O = B / 'out/T26'
DEST = B / '.cache/T26-baseline'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads((B / p).read_text())
accepted = load('out/T25/validation-final-v2.json')
assert accepted['pass_all'] and len(accepted['source_sha256']) == 1083
assert len(accepted['evidence_sha256']) == 277
for p, digest in accepted['source_sha256'].items():
    assert sha(B / p) == digest, p
for p, digest in accepted['evidence_sha256'].items():
    assert sha(B / 'out/T25' / p) == digest, p
resume = load('out/T25/resume-source-inputs-v2.json')
assert len(resume['source_sha256']) == 6 and len(resume['input_sha256']) == 121
for key in ['source_sha256', 'input_sha256']:
    for p, digest in resume[key].items():
        assert sha(B / p) == digest, p
    assert accepted['resume_' + key] == resume[key]
audit = load('.cache/T25-merged-binding-audit-v1.json')
assert audit['pass_all'] and audit['identical_tree'] and audit['groups_stopped'] == 105
assert len(audit['controllers_stopped']) == 3
assert audit['merged_sha'] == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=B, text=True).strip()
assert audit['merged_sha'] == 'd300f988a343124969d870625aaa5c2c0a75e8d0'
assert not DEST.exists() and not (O / 'baseline-snapshot-v1.json').exists()
files = [B / p for p in subprocess.check_output(['git', 'ls-files', 'engine'], cwd=B, text=True).splitlines()]
files += sorted((B / 'engine/python/goal2rust_engine').glob('*.so'))
files += [B / 'bindings/goal2rust_overrides.py']
site = B / '.venv-pypy/lib/pypy3.11/site-packages'
pypy_files = [p for name in ['goal2rust', 'goal2rust_engine', 'goal2rust_engine-0.1.0.dist-info']
              for p in sorted((site / name).rglob('*'))
              if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
assert len(list((B / 'engine/python/goal2rust_engine').glob('*.so'))) == 1
assert len(list((site / 'goal2rust_engine').glob('*.so'))) == 1
source_map = {}
for source in files + pypy_files:
    relative = Path('pypy') / source.relative_to(site) if source in pypy_files else source.relative_to(B)
    target = DEST / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('xb') as stream:
        stream.write(source.read_bytes())
    assert sha(source) == sha(target)
    source_map[str(source.relative_to(B))] = str(target.relative_to(B))
report = dict(oracle=accepted['oracle'], revision=audit['merged_sha'], preserved_before_build=True,
              accepted_primary=1083, accepted_evidence=277, accepted_supplemental_sources=6,
              accepted_supplemental_inputs=121, accepted_merged_audit_sha256=sha(B / '.cache/T25-merged-binding-audit-v1.json'),
              source_map=source_map,
              source_and_binary_sha256={p: sha(B / p) for p in sorted(source_map.values())},
              script_sha256=sha(Path(__file__)))
with (O / 'baseline-snapshot-v1.json').open('x') as stream:
    json.dump(report, stream, indent=2, sort_keys=True)
    stream.write('\n')
print('Accepted1083+277/resume6+121/merged audit verified;', len(source_map), 'T25 baseline files preserved before builds')
