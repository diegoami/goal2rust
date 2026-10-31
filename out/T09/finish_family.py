"""Exact F40 source-line selection and unchanged strict ALL/F40 comparators."""
import hashlib,json,subprocess,sys
import evidence as e
e.verify();out=e.BASE/'out/T09';path=out/'family-ALL-rust-v1.jsonl'
lines=path.read_bytes().splitlines(keepends=True);rows=[json.loads(x) for x in lines]
assert len(rows)==len({r['id'] for r in rows})==75
assert all(not r['error'] and r['stopped_at_board'] for r in rows)
selected=[(i,line) for i,(line,r) in enumerate(zip(lines,rows),1) if r['family']=='F40'];assert len(selected)==40
f40=out/'family-F40-rust-v1.jsonl'
with f40.open('xb') as f:
    for _,line in selected:f.write(line)
with (out/'F40-selection-v1.json').open('x') as f:
    json.dump(dict(source=path.name,source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),lines=[dict(line=i,sha256=hashlib.sha256(line).hexdigest()) for i,line in selected]),f,indent=2)
for family,candidate in [('ALL',path),('F40',f40)]:
    command=[sys.executable,'-B','experiments/E036-match-port/compare.py','--family',family,'--no-screen','--candidate',str(candidate)]
    with (out/f'compare-{family}-v1.log').open('x') as f:code=subprocess.call(command,cwd=e.ORACLE,stdout=f,stderr=subprocess.STDOUT)
    with (out/f'compare-{family}-v1.status.json').open('x') as f:json.dump(dict(command=command,exit_code=code),f,indent=2)
    assert code==0,family
