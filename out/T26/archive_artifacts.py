"""Archive both final binaries only after both complete public preflights pass."""
import hashlib,json,shutil,subprocess
from pathlib import Path
B=Path(__file__).resolve().parents[2];O=B/'out/T26';D=B/'.cache/T26-artifacts';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not D.exists() and not (O/'artifact-archive-v1.json').exists()
logs={}
for name in ['cpython','pypy']:
 p=O/f'public-{name}-preflight-v1.log';text=p.read_text();assert 'Ran 98 tests' in text and text.rstrip().endswith('OK');logs[name]=sha(p)
artifacts=[]
for name,interpreter in [('cpython','.venv/bin/python'),('pypy','.venv-pypy/bin/python')]:
 code="import json,goal2rust_engine;from pathlib import Path;print(json.dumps([str(p.resolve()) for p in Path(goal2rust_engine.__file__).parent.glob('*.so')]))"
 paths=json.loads(subprocess.check_output([str(B/interpreter),'-B','-c',code],cwd=B,text=True));assert len(paths)==1
 p=Path(paths[0]);q=D/name/p.name;q.parent.mkdir(parents=True);shutil.copy2(p,q);assert sha(p)==sha(q)
 artifacts.append(dict(interpreter=name,original=str(p.relative_to(B)),archive=str(q.relative_to(B)),sha256=sha(q),public_preflight_sha256=logs[name]))
with (O/'artifact-archive-v1.json').open('x') as f:json.dump(dict(both_full_public_preflights_before_archive=True,artifacts=artifacts,script_sha256=sha(Path(__file__))),f,indent=2,sort_keys=True);f.write('\n')
print('Both final artifacts archived after both98-test preflights passed')
