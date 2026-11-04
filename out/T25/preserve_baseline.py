"""Preserve accepted T24 before any runtime edit/build; exclusive snapshot."""
import hashlib,json,shutil,subprocess
from pathlib import Path
B=Path(__file__).resolve().parents[2];O=B/'out/T25';D=B/'.cache/T25-baseline'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads((B/p).read_text())
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=B,text=True).strip()=='d51430b6ae9f3dfdd8fa39e9e7bdd02c1c6da62e'
assert not D.exists() and not (O/'baseline-snapshot-v1.json').exists()
old=load('out/T24/validation-final-v1.json');assert old['pass_all'] and len(old['source_sha256'])==852 and len(old['evidence_sha256'])==281
for p,h in old['source_sha256'].items():assert sha(B/p)==h,p
for p,h in old['evidence_sha256'].items():assert sha(B/'out/T24'/p)==h,p
sup=load('out/T24/supplemental-source-inputs-v1.json')
for key in ['source_sha256','input_sha256']:
 for p,h in sup[key].items():assert sha(B/p)==h,p
audit=load('out/T24/profile-reference-audit-v1.json');assert audit['pass_all'] and audit['source_manifest_sha256']==sha(B/'out/T24/supplemental-source-inputs-v1.json')
paths=sorted((B/'engine/src').glob('*.rs'))+sorted((B/'engine/python').rglob('*.py'))+sorted((B/'engine/python').rglob('*.so'))+sorted((B/'engine/tests').glob('*.py'))
paths += [B/'engine'/n for n in ['Cargo.toml','Cargo.lock','pyproject.toml','README.md']]
paths += [B/'bindings/goal2rust_overrides.py']
D.mkdir();saved={}
for p in paths:
 q=D/p.relative_to(B);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);assert sha(p)==sha(q);saved[str(q.relative_to(B))]=sha(q)
site=B/'.venv-pypy/lib/pypy3.11/site-packages'
for name in ['goal2rust','goal2rust_engine','goal2rust_engine-0.1.0.dist-info']:
 for p in sorted((site/name).rglob('*')):
  if p.is_file() and '__pycache__' not in p.parts:
   q=D/'pypy'/p.relative_to(site);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);assert sha(p)==sha(q);saved[str(q.relative_to(B))]=sha(q)
r=dict(revision='d51430b6ae9f3dfdd8fa39e9e7bdd02c1c6da62e',oracle='2cbeb36fdd3feb369324aaa88e6e4d2aa3b3d99c',preserved_before_build=True,accepted_primary=852,accepted_evidence=281,accepted_supplemental_sources=1,accepted_supplemental_inputs=4,source_and_binary_sha256=saved)
with (O/'baseline-snapshot-v1.json').open('x') as f:json.dump(r,f,indent=2,sort_keys=True);f.write('\n')
print('Accepted852 primary/281 evidence/1source/4input verified; baseline preserved',len(saved),flush=True)
