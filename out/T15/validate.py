"""Closed evidence/performance acceptance. No threshold weakening or dropped rounds."""
import hashlib,json,os,statistics,sys
import evidence as e
e.verify();assert not e.BASELINE;out=e.BASE/'out/T15';load=lambda n:json.loads((out/(n+'.json')).read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
names=['legacy-v1','legacy-body-v1','check-v1','taps-python-v1','taps-rust-v1','profile-after-v1','attest-family-ALL-v1-invocation']
for suite in ['availability','ball','skill']:names.extend(suite+'-'+k+'-v1' for k in ['differential','body','return'])
names.extend('speaker-'+k+'-v1' for k in ['differential','body','root-return','seed-return'])
names.extend('keys-'+k+'-v1' for k in ['differential','body','return'])
names.extend('draw-'+k+'-v1' for k in ['differential','body','return'])
names.extend('sweep-'+k+'-v1' for k in ['differential','body','return'])
names.extend('play-'+k+'-v1' for k in ['differential','body','return'])
names.extend(suite+'-'+k+'-v1' for suite in ['update','sprite'] for k in ['differential','body','return'])
for rnd in range(1,4):names.extend(f'cpu-{arm}-r{rnd}-v1' for arm in ['baseline','candidate','python','pypy'])
for name in names:
 r=load(name);assert r['source_unchanged'],name
 for path,h in r['source_sha256'].items():assert sha(e.BASE/path)==h,(name,path)
legacy=load('legacy-v1');assert legacy['all_equal'] and sum(v['equal'] for v in legacy['routines'].values())==28448
assert all(v==8 for v in legacy['captured_counts'].values())
assert not load('legacy-body-v1')['all_equal']
for suite,count in [('availability',3224),('ball',2128),('skill',6224)]:
 r=load(suite+'-differential-v1');assert r['all_equal'] and sum(v['equal'] for v in r['comparisons'].values())==count
 for kind in ['body','return']:assert not load(suite+'-'+kind+'-v1')['all_equal'] and load(suite+'-'+kind+'-v1')['differences']
for label in ['differential','body','root-return','seed-return']:
 r=load('speaker-'+label+'-v1');assert r['control_scope_verified'] and sum(v['total'] for v in r['comparisons'].values())==12448
 assert all(v==8 for v in r['captures'].values()) and r['all_equal']==(label=='differential')
for label in ['differential','body','return']:
 r=load('keys-'+label+'-v1');assert r['control_scope_verified'] and r['captures']==8 and sum(v['total'] for v in r['comparisons'].values())==2096
 assert len(r['visited_return_sites'])==15 and len(r['delegated_targets_seen'])==12
 assert r['all_equal']==(label=='differential')
 if label=='differential':assert r['error_comparisons']==1066 and all(r['errors_seen'].values())
 else:assert all(v['equal']==0 for v in r['comparisons'].values())
for label in ['differential','body','return']:
 r=load('draw-'+label+'-v1');assert r['control_scope_verified'] and r['captures']==8 and sum(v['total'] for v in r['comparisons'].values())==2096
 assert len(r['return_sites_seen'])==2 and len(r['write_sites_seen'])==4 and len(r['delegated_targets_seen'])==3
 assert r['all_equal']==(label=='differential')
 assert all(v['equal']==v['total']-v['expected_different'] for v in r['comparisons'].values())
 if label=='differential':assert r['error_comparisons']==352 and all(r['errors_seen'].values())
for label in ['differential','body','return']:
 r=load('sweep-'+label+'-v1');assert r['source_unchanged'] and r['captures']==8 and sum(v['total'] for v in r['comparisons'].values())==2096
 assert len(r['return_sites_seen'])==17 and len(r['write_sites_seen'])==12 and len(r['delegated_targets_seen'])==14
 assert r['all_equal']==(label=='differential')
 if label=='differential':assert r['error_comparisons']==1888 and all(r['errors_seen'].values())
 else:assert all(v['equal']==0 for v in r['comparisons'].values())
for label in ['differential','body','return']:
 r=load('play-'+label+'-v1');assert r['source_unchanged'] and r['captures']==8 and sum(v['total'] for v in r['comparisons'].values())==2096
 assert len(r['return_sites_seen'])==15 and len(r['write_sites_seen'])==2 and len(r['delegated_targets_seen'])==14
 assert r['all_equal']==(label=='differential')
 if label=='differential':assert r['error_comparisons']==3760 and all(r['errors_seen'].values())
 else:assert all(v['equal']==0 for v in r['comparisons'].values())
for label in ['differential','body','return']:
 r=load('update-'+label+'-v1');assert r['source_unchanged'] and r['captures']==8 and sum(v['total'] for v in r['comparisons'].values())==2096
 assert len(r['return_sites_seen'])==16 and len(r['write_sites_seen'])==6 and len(r['delegated_targets_seen'])==16
 assert r['all_equal']==(label=='differential')
 if label=='differential':assert r['error_comparisons']==6720 and all(r['errors_seen'].values())
 else:assert all(v['equal']==0 for v in r['comparisons'].values())
for label in ['differential','body','return']:
 r=load('sprite-'+label+'-v1');assert r['source_unchanged'] and r['captures']==8 and sum(v['total'] for v in r['comparisons'].values())==2096
 assert len(r['return_sites_seen'])==5 and len(r['write_sites_seen'])==10 and len(r['delegated_targets_seen'])==5
 assert r['all_equal']==(label=='differential') and all(r['paths'].values()) and all(r['observer_mutations'].values())
 if label=='differential':assert r['error_comparisons']==3240 and all(r['errors_seen'].values())
 else:assert all(v['equal']==0 for v in r['comparisons'].values())
check=load('check-v1');assert check['state'] and check['exit_code']==0 and set(check['checks'])=={'engine','interactive','goals','knockout'} and all(r['pass'] for r in check['checks'].values())
comparisons=[]
for group in [['taps-python-v1','taps-rust-v1']]+[[f'cpu-{a}-r{r}-v1' for a in ['baseline','candidate','python','pypy']] for r in range(1,4)]:
 rows=[load(n) for n in group]
 for key in ['oracle','input_state_sha256','events','events_sha256','result_sha256','records_sha256','memory_sha256','stretches']:
  assert all(row[key]==rows[0][key] for row in rows),(group,key)
 comparisons.append(dict(files=group,equal=True))
assert load('taps-python-v1')['taps']==load('taps-rust-v1')['taps']
for name in ['taps-rust-v1']+[f'cpu-{a}-r{r}-v1' for r in range(1,4) for a in ['baseline','candidate']]:
 assert len(load(name)['native_calls'])==(21 if 'baseline' in name else 22) and sum(load(name)['native_calls'].values())==(1828188 if 'baseline' in name else 1904131)
for name in ['taps-rust-v1']+[f'cpu-candidate-r{r}-v1' for r in range(1,4)]:assert all(v>0 for v in load(name)['bridge_fast_calls'].values())
for rnd in range(1,4):
 base=load(f'cpu-baseline-r{rnd}-v1');assert base['bridge_fast_calls'] and all(base['bridge_fast_calls'].values()) and base['arm']=='baseline'
 so=[p for p in base['source_sha256'] if p.endswith('.so')];assert len(so)==1 and so[0].startswith('.cache/T15-baseline/engine/')
perf=load('performance-v1');assert perf['outputs_equal'] and perf['measurement_complete'] and perf['incremental_port_no_magnitude_minimum']
ratios=[]
for rnd in range(1,4):
 ratio=load(f'cpu-candidate-r{rnd}-v1')['drive_cpu_s']/load(f'cpu-baseline-r{rnd}-v1')['drive_cpu_s'];ratios.append(ratio)
 starts=[r for r in perf['starts'] if r['round']==rnd];assert len(starts)==4 and max(r['time'] for r in starts)-min(r['time'] for r in starts)<5 and len({r['cpu'] for r in starts})==4
 quiet=[r for r in perf['quiet_observations'] if r['round']==rnd];assert len(quiet)>=3 and all(max(r['load'][:2])<4 for r in quiet[-3:])
assert statistics.median(ratios)==perf['median_ratio']
assert len(perf['exits'])==12 and all(r['code']==0 for r in perf['exits'])
for r in perf['starts']:
 try:os.killpg(r['pid'],0)
 except ProcessLookupError:pass
 else:raise AssertionError(('performance child group still alive',r))
lines=(out/'family-ALL-rust-v1.jsonl').read_bytes().splitlines(keepends=True);rows=[json.loads(x) for x in lines];assert len(rows)==len({r['id'] for r in rows})==75 and all(not r['error'] and r['stopped_at_board'] for r in rows)
selection=load('F40-selection-v1');assert selection['source_sha256']==sha(out/'family-ALL-rust-v1.jsonl')
f40=[lines[r['line']-1] for r in selection['lines']];assert len(f40)==40 and b''.join(f40)==(out/'family-F40-rust-v1.jsonl').read_bytes()
assert all(hashlib.sha256(line).hexdigest()==r['sha256'] for line,r in zip(f40,selection['lines']))
for fam in ['ALL','F40']:assert load('compare-'+fam+'-v1.status')['exit_code']==0
attest={}
for label,count in [('check',11),('family-ALL',75)]:
 ar=[json.loads(p.read_text()) for p in (out/f'attest-{label}-v1').glob('*.json')];assert sum(r['machines'] for r in ar)==count
 assert all(r['oracle']==e.PIN and r['backend']=='rust' for r in ar)
 counts={k:sum(r['bridge_fast_calls'].get(k,0) for r in ar) for k in ['u8','u16','write']};assert all(counts.values())
 attest[label]=dict(machines=count,bridge_fast_calls=counts)
p=load('profile-after-v1');assert p['equal_to_fresh_state_v2'] and p['total_guest_entries']==3103685 and p['python_guest_entries']==1199554
for path,h in load('baseline-snapshot-v1')['source_and_binary_sha256'].items():assert sha(e.BASE/path)==h,path
jobs=[json.loads(x) for x in (out/'jobs-v1.jsonl').read_text().splitlines()];starts=[r for r in jobs if r['event']=='start'];exits=[r for r in jobs if r['event']=='exit']
assert len(starts)==len(exits)==39 and all(r['code']==0 for r in exits) and {r['pid'] for r in starts}=={r['pid'] for r in exits}
for r in starts:
 try:os.killpg(r['pid'],0)
 except ProcessLookupError:pass
 else:raise AssertionError(('canonical producer group still alive',r))
result=dict(pass_all=True,all_writers_finished=True,comparisons=comparisons,attestation=attest,performance_ratios=ratios,median_performance_ratio=statistics.median(ratios),incremental_port_no_magnitude_minimum=True,all_rounds_improve=all(r<1 for r in ratios),
 evidence_sha256={str(p.relative_to(out)):sha(p) for p in sorted(out.rglob('*')) if p.is_file() and p.suffix in ['.json','.jsonl','.log','.txt','.prof'] and not p.name.startswith('validation-')})
e.write(sys.argv[1],result,e.hashes());print('T15 fidelity, complete measurements and closed source/binary/input/evidence gates pass')
