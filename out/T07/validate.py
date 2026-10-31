"""Exclusive post-writer state-v2 compatibility ledger."""
import hashlib,json,os,sys
import evidence as e
e.verify();out=e.BASE/'out/T07';load=lambda n:json.loads((out/(n+'.json')).read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
names=['legacy-v1','legacy-body-v1','check-v1','taps-python-v1','taps-rust-v1','profile-after-v1','cpu-python-v1','cpu-pypy-v1','cpu-rust-v1','attest-family-ALL-v1-invocation']
for suite in ['availability','ball','skill']:
    names.extend(suite+'-'+kind+'-v1' for kind in ['differential','body','return'])
for name in names:
    r=load(name);assert r['source_unchanged'],name
    for p,h in r['source_sha256'].items():assert sha(e.BASE/p)==h,(name,p)
legacy=load('legacy-v1');assert legacy['all_equal'] and len(legacy['routines'])==7
assert sum(r['equal'] for r in legacy['routines'].values())==28448
assert all(n==8 for n in legacy['captured_counts'].values())
assert not load('legacy-body-v1')['all_equal'] and load('legacy-body-v1')['exit_code']==1
for suite in ['availability','ball','skill']:
    assert load(suite+'-differential-v1')['all_equal']
    for kind in ['body','return']:assert not load(suite+'-'+kind+'-v1')['all_equal'] and load(suite+'-'+kind+'-v1')['differences']
check=load('check-v1');assert check['state'] and check['exit_code']==0 and set(check['checks'])=={'engine','interactive','goals','knockout'}
assert all(r['pass'] for r in check['checks'].values())
comparisons=[]
for group in [['taps-python-v1','taps-rust-v1'],['cpu-python-v1','cpu-pypy-v1','cpu-rust-v1']]:
    rows=[load(n) for n in group]
    for field in ['oracle','input_state_sha256','events','events_sha256','result_sha256','records_sha256','memory_sha256','stretches','taps']:
        assert all(r[field]==rows[0][field] for r in rows),(group,field)
    comparisons.append(dict(files=group,equal=True))
for name in ['taps-rust-v1','cpu-rust-v1']:
    r=load(name);assert len(r['native_calls'])==12 and sum(r['native_calls'].values())==1350794
    assert r['native_calls']['0791:278A']==r['native_calls']['1771:3A06']==23342
for name in ['taps-python-v1','cpu-python-v1','cpu-pypy-v1']:assert load(name)['native_calls']=={}
p=load('profile-after-v1');assert p['equal_to_fresh_state_v2'] and p['total_guest_entries']==3103685 and p['python_guest_entries']==1752891
old=json.loads((e.BASE/'out/T06/cpu-rust-v1.json').read_text());new=load('cpu-rust-v1')
for field in ['events','events_sha256','result_sha256','stretches']:assert old[field]==new[field],field
# Full memory/record/tap values are compared only between equivalent fresh state-v2 machines.
lines=(out/'family-ALL-rust-v1.jsonl').read_bytes().splitlines(keepends=True);rows=[json.loads(x) for x in lines]
assert len(rows)==len({r['id'] for r in rows})==75 and all(not r['error'] and r['stopped_at_board'] for r in rows)
selection=load('F40-selection-v1');assert selection['source_sha256']==sha(out/'family-ALL-rust-v1.jsonl')
f40=[lines[r['line']-1] for r in selection['lines']];assert len(f40)==40
assert all(hashlib.sha256(line).hexdigest()==r['sha256'] for line,r in zip(f40,selection['lines']))
assert b''.join(f40)==(out/'family-F40-rust-v1.jsonl').read_bytes()
for family in ['ALL','F40']:assert load('compare-'+family+'-v1.status')['exit_code']==0
attest={}
for label,count in [('check',11),('family-ALL',75)]:
    ar=[json.loads(p.read_text()) for p in (out/f'attest-{label}-v1').glob('*.json')]
    assert sum(r['machines'] for r in ar)==count
    assert all(r['oracle']==e.PIN and r['backend']=='rust' for r in ar)
    counts={ad:sum(r['native_calls'].get(ad,0) for r in ar) for ad in ['0791:278A','1771:3A06','0791:2FB1']};assert all(counts.values())
    attest[label]=dict(machines=count,native_calls=counts)
jobs=[json.loads(x) for x in (out/'jobs-v1.jsonl').read_text().splitlines()];starts=[r for r in jobs if r['event']=='start'];exits=[r for r in jobs if r['event']=='exit']
assert len(starts)==len(exits)==19 and all(r['code']==0 for r in exits)
assert {r['pid'] for r in starts}=={r['pid'] for r in exits}
for r in starts:
    try:os.killpg(r['pid'],0)
    except ProcessLookupError:pass
    else:raise AssertionError(('live producer group',r))
times=[r['time'] for r in starts if r['name'].startswith('cpu-')];assert max(times)-min(times)<5
quiet=[json.loads(x) for x in (out/'quiet-v1.jsonl').read_text().splitlines()];assert len(quiet)>=3 and all(max(r['load'][:2])<4 for r in quiet[-3:])
r=dict(pass_all=True,all_writers_finished=True,comparisons=comparisons,attestation=attest,state_schema='original_match.state/2',native_bodies=12,
       evidence_sha256={str(p.relative_to(out)):sha(p) for p in sorted(out.rglob('*')) if p.is_file() and p.suffix in ['.json','.jsonl','.log','.prof','.txt'] and not p.name.startswith('validation-')})
e.write(sys.argv[1],r,e.hashes());print('T07 all compatibility gates pass; post-writer hashes sealed')
