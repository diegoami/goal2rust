"""Close accepted T28 and preserve its actual runtime before any new build."""
import hashlib,json,subprocess
from pathlib import Path
B=Path(__file__).resolve().parents[2];O=B/'out/T29';D=B/'.cache/T29-baseline'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads((B/p).read_text())
accepted=load('out/T28/validation-final-v1.json')
assert accepted['pass_all'] and len(accepted['source_sha256'])==3061 and len(accepted['evidence_sha256'])==338
for p,h in accepted['source_sha256'].items():assert sha(B/p)==h,p
for p,h in accepted['evidence_sha256'].items():assert sha(B/'out/T28'/p)==h,p
for p,h in accepted['supplemental_source_sha256'].items():assert sha(B/p)==h,p
audit=load('.cache/T28-merged-binding-audit-v1.json')
assert audit['pass_all'] and audit['identical_tree'] and audit['groups_stopped']==131 and audit['controller_stopped']
revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=B,text=True).strip()
assert audit['merged_sha']==revision=='8b261736722c30e9efea5f52429c7f85066ea757'
assert not D.exists() and not (O/'baseline-snapshot-v1.json').exists()
files=[B/p for p in subprocess.check_output(['git','ls-files','engine'],cwd=B,text=True).splitlines()]
files+=sorted((B/'engine/python/goal2rust_engine').glob('*.so'))+[B/'bindings/goal2rust_overrides.py']
site=B/'.venv-pypy/lib/pypy3.11/site-packages'
pypy=[p for name in ['goal2rust','goal2rust_engine','goal2rust_engine-0.1.0.dist-info'] for p in sorted((site/name).rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
assert len(list((B/'engine/python/goal2rust_engine').glob('*.so')))==len(list((site/'goal2rust_engine').glob('*.so')))==1
mapping={}
for source in files+pypy:
 relative=Path('pypy')/source.relative_to(site) if source in pypy else source.relative_to(B)
 target=D/relative;target.parent.mkdir(parents=True,exist_ok=True)
 with target.open('xb') as f:f.write(source.read_bytes())
 assert sha(source)==sha(target)
 mapping[str(source.relative_to(B))]=str(target.relative_to(B))
assert len(mapping)==84
report=dict(oracle=accepted['oracle'],revision=revision,preserved_before_build=True,accepted_primary=3061,accepted_evidence=338,accepted_merged_audit_sha256=sha(B/'.cache/T28-merged-binding-audit-v1.json'),source_map=mapping,source_and_binary_sha256={p:sha(B/p) for p in sorted(mapping.values())},script_sha256=sha(Path(__file__)))
with (O/'baseline-snapshot-v1.json').open('x') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
print('Accepted3061/338/merged audit verified;84 actual T28 files preserved before builds')
