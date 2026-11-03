"""Closed evidence/performance acceptance. No threshold weakening or dropped rounds."""
import hashlib,json,os,statistics,sys
import evidence as e
e.verify();assert not e.BASELINE;out=e.BASE/'out/T25';load=lambda n:json.loads((out/(n+'.json')).read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
selection=load('performance-selection-v1');assert selection['pass_all'];version=selection['selected_version'];campaigns=selection['campaigns'];perf=load('performance-'+version)
names=['legacy-v1','legacy-body-v1','check-v1','taps-python-v1','taps-rust-v1','profile-after-v1','attest-family-ALL-v1-invocation']
for suite in ['availability','ball','skill']:names.extend(suite+'-'+k+'-v1' for k in ['differential','body','return'])
names.extend('speaker-'+k+'-v1' for k in ['differential','body','root-return','seed-return'])
names.extend('keys-'+k+'-v1' for k in ['differential','body','return'])
names.extend('draw-'+k+'-v1' for k in ['differential','body','return'])
names.extend('sweep-'+k+'-v1' for k in ['differential','body','return'])
names.extend('play-'+k+'-v1' for k in ['differential','body','return'])
names.extend(suite+'-'+k+'-v1' for suite in ['update','sprite'] for k in ['differential','body','return'])
names.extend('run-'+k+'-v1' for k in ['differential','body','position'])
names.extend('marking-'+suite+'-v1' for suite in ['normal','body','output','returns'])
names.extend('destination-'+suite+'-v1' for suite in ['normal','body','output','returns'])
names.extend('depth-'+suite+'-v1' for suite in ['normal','body','output','returns'])
names.extend('chase-'+suite+'-v1' for suite in ['normal','body','output','returns'])
names.extend('travel-'+suite+'-v1' for suite in ['normal','body','output','returns'])
names.extend('offside-'+suite+'-v1' for suite in ['normal','body','output','returns'])
names.extend('pascal-'+suite+'-v1' for suite in ['normal','body','output'])
names.extend('keyboard-'+suite+'-v1' for suite in ['normal','body','output','returns'])
names.append('prior-pascal-live-observers-v1')
names.extend('text-'+k+'-v1' for k in ['normal','body','output','returns'])
names.append('prior-keyboard-live-observers-v1')
names.append('prior-offside-live-observers-v1')
names.append('prior-travel-live-observers-v1')
names.extend(['prior-chase-live-observers-v1','scoped-write-errors-v1','prior-depth-live-observers-v1','prior-destination-live-observers-v1','prior-live-observers-v1','live-observers-v1','public-cpython-v1.status','public-pypy-v1.status','rust-unit-v1.status','gc-parity-v1','observer-matrix-v2'])
for rnd in range(1,4):names.extend(f'cpu-{arm}-r{rnd}-{version}' for arm in ['baseline','candidate','python','pypy'])
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
for label in ['differential','body','position']:
 r=load('run-'+label+'-v1');assert r['source_unchanged'] and r['captures']==8 and sum(v['total'] for v in r['comparisons'].values())==2096
 assert r['control_scope_verified'] and len(r['write_sites_seen'])==13 and r['guest_calls']==0
 assert r['all_equal']==(label=='differential') and all(r['paths'].values()) and all(r['observer_mutations'].values())
 if label=='differential':assert r['error_comparisons']==2560 and all(r['errors_seen'].values()) and r['branch_comparisons']==160 and all(r['branch_coverage'].values())
 else:assert all(v['equal']==0 for v in r['comparisons'].values())
normal=load('marking-normal-v1');assert normal['all_equal'] and normal['control_scope_verified']
assert all(v==8 for v in normal['captures'].values()) and sum(r['total'] for r in normal['comparisons'].values())==14480
assert normal['error_comparisons']==11200 and len(normal['errors_seen'])==70 and all(normal['errors_seen'].values())
assert normal['branch_comparisons']==1120 and all(normal['branches']['conditions'].values())
assert normal['branches']['slots']==list(range(2,12)) and normal['branches']['holder_results']==normal['branches']['half_results']==[0,1]
assert normal['branches']['zone_results']==[False,True] and len(normal['return_sites_seen'])==13 and len(normal['write_sites_seen'])==27
assert normal['variants']==160 and len(normal['closure_checks'])==5 and all(n==2096 for n in normal['closure_checks'].values())
for suite,total in [('body',10480),('output',6288)]:
 r=load('marking-'+suite+'-v1');assert not r['all_equal'] and r['control_scope_verified'] and r['differences']
 assert sum(row['total'] for row in r['comparisons'].values())==total and all(row['equal']==0 and row['expected_different']==row['total'] for row in r['comparisons'].values())
r=load('marking-returns-v1');assert r['control_scope_verified'] and len(r['return_controls'])==13
assert all(row['total']==160 and row['reached']==row['detected']>0 for row in r['return_controls'].values())
destination=load('destination-normal-v1');assert destination['all_equal'] and destination['control_scope_verified']
assert sum(r['total'] for r in destination['comparisons'].values())==41440 and all(n==8 for n in destination['captures'].values())
assert len(destination['closure_checks'])==15 and all(n==2096 for n in destination['closure_checks'].values())
assert destination['branch_comparisons']==3200 and all(destination['branches'].values())
assert destination['error_comparisons']==44480 and len(destination['errors_seen'])==278 and all(destination['errors_seen'].values())
assert destination['variants']==320
for suite,total in [('body',31440),('output',20960)]:
 r=load('destination-'+suite+'-v1');assert not r['all_equal'] and r['control_scope_verified'] and sum(row['total'] for row in r['comparisons'].values())==total and all(row['equal']==0 for row in r['comparisons'].values())
r=load('destination-returns-v1');assert len(r['return_controls'])==41 and all(row['total']==160 and row['detected']==row['reached']>0 for row in r['return_controls'].values())
for name in ['prior-live-observers-v1','live-observers-v1']:
 r=load(name);assert r['pass_all'] and r['comparisons']==1280 and len(r['scenarios'])==8 and all(row['hits'] and all(row['hits'].values()) and row['effect_witnesses']>0 for row in r['scenarios'].values())
depth=load('depth-normal-v1');assert depth['all_equal'] and depth['control_scope_verified']
assert sum(v['total'] for v in depth['comparisons'].values())==16480 and all(v==8 for v in depth['captures'].values())
assert len(depth['closure_checks'])==5 and all(v==2096 for v in depth['closure_checks'].values())
assert depth['branch_comparisons']==1280 and all(depth['branches'].values())
assert depth['error_comparisons']==19520 and len(depth['errors_seen'])==118 and all(depth['errors_seen'].values())
extra=load('scoped-write-errors-v1');assert extra['pass_all'] and extra['runtime_unchanged'] and extra['source_unchanged'] and extra['comparisons']==640 and len(extra['selectors'])==4
assert all(row['total']==row['equal']==160 and row['reached']==row['legacy_pre_return_witnesses']>0 for row in extra['selectors'].values())
assert len(set(depth['errors_seen'])|{r['root']+'/'+r['selector'] for r in json.loads((e.BASE/'out/T19/proof-plan-v2.json').read_text())['additional_selectors']})==122
assert depth['error_comparisons']+extra['comparisons']==20160
assert depth['variants']==112
for suite,total in [('body',10480),('output',4192)]:
 r=load('depth-'+suite+'-v1');assert r['control_scope_verified'] and not r['all_equal'] and sum(v['total'] for v in r['comparisons'].values())==total and all(v['equal']==0 for v in r['comparisons'].values())
r=load('depth-returns-v1');assert len(r['return_controls'])==23 and all(v['total']==160 and v['reached']==v['detected']>0 for v in r['return_controls'].values())
r=load('prior-destination-live-observers-v1');assert r['pass_all'] and r['comparisons']==1280
chase=load('chase-normal-v1');plan=json.loads((e.BASE/'out/T20/proof-plan-v1.json').read_text());assert chase['all_equal'] and chase['control_scope_verified']
assert sum(v['total'] for v in chase['comparisons'].values())==8288 and all(v==8 for v in chase['captures'].values())
assert len(chase['closure_checks'])==3 and all(v==2096 for v in chase['closure_checks'].values())
assert chase['branch_comparisons']==640 and all(chase['branches'].values()) and chase['variants']==80
assert chase['error_comparisons']==15840 and len(chase['errors_seen'])==99 and all(chase['errors_seen'].values())
assert plan['error_execution_rows']==plan['distinct_error_selectors']==99 and sum(len(v) for v in plan['errors'].values())==99
assert len({root+'/'+r['selector'] for root,rows in plan['errors'].items() for r in rows})==99
for suite,total in [('body',6288),('output',4192)]:
 r=load('chase-'+suite+'-v1');assert r['control_scope_verified'] and not r['all_equal'] and sum(v['total'] for v in r['comparisons'].values())==total and all(v['equal']==0 for v in r['comparisons'].values())
r=load('chase-returns-v1');assert len(r['return_controls'])==5 and all(v['total']==160 and v['reached']==v['detected']>0 for v in r['return_controls'].values())
r=load('prior-depth-live-observers-v1');assert r['pass_all'] and r['comparisons']==1280
travel=load('travel-normal-v1');plan=json.loads((e.BASE/'out/T21/proof-plan-v1.json').read_text());assert travel['all_equal'] and travel['control_scope_verified']
assert sum(v['total'] for v in travel['comparisons'].values())==6192 and all(v==8 for v in travel['captures'].values())
assert len(travel['closure_checks'])==2 and all(v==2096 for v in travel['closure_checks'].values())
assert travel['branch_comparisons']==480 and all(travel['branches'].values()) and travel['variants']==32
assert travel['error_comparisons']==6720 and len(travel['errors_seen'])==42 and all(travel['errors_seen'].values())
assert plan['error_execution_rows']==plan['distinct_error_selectors']==42 and sum(len(v) for v in plan['errors'].values())==42
assert len({root+'/'+r['selector'] for root,rows in plan['errors'].items() for r in rows})==42
for suite,total in [('body',4192),('output',6288)]:
 r=load('travel-'+suite+'-v1');assert r['control_scope_verified'] and not r['all_equal'] and sum(v['total'] for v in r['comparisons'].values())==total and all(v['equal']==0 for v in r['comparisons'].values())
 if suite=='output':
  for control in [157,158,159]:assert sum(v['total'] for key,v in r['comparisons'].items() if key.endswith('/control'+str(control)))==2096
r=load('travel-returns-v1');assert len(r['return_controls'])==1 and all(v['total']==160 and v['reached']==v['detected']>0 for v in r['return_controls'].values())
r=load('prior-chase-live-observers-v1');assert r['pass_all'] and r['comparisons']==1280
offside=load('offside-normal-v1');plan=json.loads((e.BASE/'out/T22/proof-plan-v1.json').read_text());assert offside['all_equal'] and offside['control_scope_verified']
assert sum(v['total'] for v in offside['comparisons'].values())==10288 and all(v==8 for v in offside['captures'].values())
assert len(offside['closure_checks'])==3 and all(v==2096 for v in offside['closure_checks'].values())
assert offside['branch_comparisons']==800 and all(offside['branches'].values()) and offside['variants']==64
assert offside['error_comparisons']==26080 and len(offside['errors_seen'])==163 and all(offside['errors_seen'].values())
assert plan['error_execution_rows']==plan['distinct_error_selectors']==163 and sum(len(v) for v in plan['errors'].values())==163
assert len({root+'/'+r['selector'] for root,rows in plan['errors'].items() for r in rows})==163
for suite,total in [('body',6288),('output',4192)]:
 r=load('offside-'+suite+'-v1');assert r['control_scope_verified'] and not r['all_equal'] and sum(v['total'] for v in r['comparisons'].values())==total and all(v['equal']==0 for v in r['comparisons'].values())
 if suite=='output':
  for control in [164,165]:assert sum(v['total'] for key,v in r['comparisons'].items() if key.endswith('/control'+str(control)))==2096
r=load('offside-returns-v1');assert len(r['return_controls'])==4 and all(v['total']==160 and v['reached']==v['detected']>0 for v in r['return_controls'].values())
r=load('prior-travel-live-observers-v1');assert r['pass_all'] and r['comparisons']==1280
assert offside['all_inventory_helper_scope'] and all(offside['shared_source_calls'].values())
pascal=load('pascal-normal-v1');plan=json.loads((e.BASE/'out/T23/proof-plan-v1.json').read_text());assert pascal['all_equal'] and pascal['control_scope_verified']
assert sum(v['total'] for v in pascal['comparisons'].values())==6288 and all(v==8 for v in pascal['captures'].values())
assert pascal['all_inventory_helper_scope'] and len(pascal['owned_symbols'])==7 and all(pascal['source_owned_calls'].values())
assert len(pascal['closure_checks'])==3 and all(v==2096 for v in pascal['closure_checks'].values())
assert pascal['branch_comparisons']==480 and all(pascal['branches'].values()) and pascal['variants']==48
assert pascal['error_comparisons']==12000 and len(pascal['errors_seen'])==75 and all(pascal['errors_seen'].values())
assert plan['error_execution_rows']==plan['distinct_error_selectors']==75 and sum(len(v) for v in plan['errors'].values())==75
assert len({root+'/'+r['selector'] for root,rows in plan['errors'].items() for r in rows})==75
for suite,total in [('body',6288),('output',25152)]:
 r=load('pascal-'+suite+'-v1');assert r['control_scope_verified'] and not r['all_equal'] and sum(v['total'] for v in r['comparisons'].values())==total and all(v['equal']==0 for v in r['comparisons'].values())
 if suite=='output':
  for control in range(173,185):assert sum(v['total'] for key,v in r['comparisons'].items() if key.endswith('/control'+str(control)))==2096
assert json.loads((e.BASE/'out/T23/inventory-v1.json').read_text())['site_count']==0
r=load('prior-offside-live-observers-v1');assert r['pass_all'] and r['comparisons']==1280
keyboard=load('keyboard-normal-v1');plan=json.loads((e.BASE/'out/T24/proof-plan-v1.json').read_text());assert keyboard['all_equal'] and keyboard['control_scope_verified'] and keyboard['all_inventory_helper_scope']
assert sum(v['total'] for v in keyboard['comparisons'].values())==10384 and len(keyboard['owned_symbols'])==9 and all(keyboard['source_owned_calls'].values())
assert len(keyboard['closure_checks'])==4 and all(v==2096 for v in keyboard['closure_checks'].values())
assert keyboard['branch_comparisons']==800 and all(keyboard['branches'].values()) and keyboard['source_return_sites'] and keyboard['variants']==64
assert keyboard['error_comparisons']==12320 and len(keyboard['errors_seen'])==77 and all(keyboard['errors_seen'].values())
assert plan['error_execution_rows']==plan['distinct_error_selectors']==77 and sum(len(v) for v in plan['errors'].values())==77
assert len({root+'/'+r['selector'] for root,rows in plan['errors'].items() for r in rows})==77
for suite,total in [('body',8384),('output',16768)]:
 r=load('keyboard-'+suite+'-v1');assert r['control_scope_verified'] and not r['all_equal'] and sum(v['total'] for v in r['comparisons'].values())==total and all(v['equal']==0 for v in r['comparisons'].values())
 if suite=='output':
  for control in range(189,197):assert sum(v['total'] for k,v in r['comparisons'].items() if k.endswith('/control'+str(control)))==2096
r=load('keyboard-returns-v1');assert set(r['return_controls'])=={'214B:098A'} and all(v['total']==160 and v['reached']==v['detected']>0 for v in r['return_controls'].values())
r=load('prior-pascal-live-observers-v1');assert r['pass_all'] and r['comparisons']==1280
text=load('text-normal-v1');plan=load('proof-plan-v1');inventory=load('inventory-v2')
assert text['all_equal'] and text['control_scope_verified'] and text['all_inventory_helper_scope']
assert sum(v['total'] for v in text['comparisons'].values())==20576 and all(v==8 for v in text['captures'].values())
assert text['owned_symbols']==inventory['owned_symbols'] and len(text['owned_symbols'])==14 and all(text['source_owned_calls'].values())
assert len(text['closure_checks'])==6 and all(v==2096 for v in text['closure_checks'].values())
assert text['branch_comparisons']==1600 and len(text['branches'])==10 and all(text['branches'].values()) and len(text['source_return_sites'])==8 and text['variants']==192
assert text['error_comparisons']==27360 and len(text['errors_seen'])==171 and all(text['errors_seen'].values())
assert plan['error_execution_rows']==plan['distinct_error_selectors']==171 and sum(len(v) for v in plan['errors'].values())==171
assert len({root+'/'+r['selector'] for root,rows in plan['errors'].items() for r in rows})==171
assert plan['test_source_sha256']==sha(e.BASE/'engine/tests/test_text.py') and plan['inventory_sha256']==sha(out/'inventory-v2.json')
for suite,total in [('body',12576),('output',88032)]:
 r=load('text-'+suite+'-v1');assert r['control_scope_verified'] and not r['all_equal'] and sum(v['total'] for v in r['comparisons'].values())==total and all(v['equal']==0 for v in r['comparisons'].values())
 if suite=='output':
  for control in range(204,246):assert sum(v['total'] for k,v in r['comparisons'].items() if k.endswith('/control'+str(control)))==2096
r=load('text-returns-v1');assert set(r['return_controls'])=={s['ret_to'] for s in inventory['guest_sites']} and len(r['return_controls'])==8 and all(v['total']==160 and v['reached']==v['detected']>0 for v in r['return_controls'].values())
for name in ['live-observers-v1','prior-keyboard-live-observers-v1']:
 r=load(name);assert r['pass_all'] and r['comparisons']==1280 and len(r['scenarios'])==8 and all(v['effect_witnesses']>0 and v['hits'] and all(v['hits'].values()) for v in r['scenarios'].values())
for name in ['public-cpython-v1','public-pypy-v1']:
 assert load(name+'.status')['exit_code']==0
 text=(out/(name+'.log')).read_text();assert 'Ran 94 tests' in text and text.rstrip().endswith('OK')
check=load('check-v1');assert check['state'] and check['exit_code']==0 and set(check['checks'])=={'engine','interactive','goals','knockout'} and all(r['pass'] for r in check['checks'].values())
comparisons=[]
for group in [['taps-python-v1','taps-rust-v1']]+[[f'cpu-{a}-r{r}-{version}' for a in ['baseline','candidate','python','pypy']] for r in range(1,4)]:
 rows=[load(n) for n in group]
 for key in ['oracle','input_state_sha256','events','events_sha256','result_sha256','records_sha256','memory_sha256','stretches']:
  assert all(row[key]==rows[0][key] for row in rows),(group,key)
 comparisons.append(dict(files=group,equal=True))
assert load('taps-python-v1')['taps']==load('taps-rust-v1')['taps']
for name in ['taps-rust-v1']+[f'cpu-{a}-r{r}-{version}' for r in range(1,4) for a in ['baseline','candidate']]:
 assert len(load(name)['native_calls'])==(63 if 'baseline' in name else 69) and sum(load(name)['native_calls'].values())==(2688294 if 'baseline' in name else 2699104)
for name in ['taps-rust-v1']+[f'cpu-candidate-r{r}-{version}' for r in range(1,4)]:assert all(v>0 for v in load(name)['bridge_fast_calls'].values())
for rnd in range(1,4):
 base=load(f'cpu-baseline-r{rnd}-{version}');assert base['bridge_fast_calls'] and all(base['bridge_fast_calls'].values()) and base['arm']=='baseline'
 so=[p for p in base['source_sha256'] if p.endswith('.so') and p.startswith('.cache/T25-baseline/engine/')];assert len(so)==1
perf=load('performance-'+version);assert perf['quiet_complete'] and perf['outputs_equal'] and perf['measurement_complete'] and perf['incremental_port_no_magnitude_minimum']
ratios=[]
for rnd in range(1,4):
 ratio=load(f'cpu-candidate-r{rnd}-{version}')['drive_cpu_s']/load(f'cpu-baseline-r{rnd}-{version}')['drive_cpu_s'];ratios.append(ratio)
 starts=[r for r in perf['starts'] if r['round']==rnd];assert len(starts)==4 and max(r['time'] for r in starts)-min(r['time'] for r in starts)<5 and len({r['cpu'] for r in starts})==4
 quiet=[r for r in perf['quiet_observations'] if r['round']==rnd];assert len(quiet)>=3 and all(max(r['load'][:2])<4 for r in quiet[-3:])
assert statistics.median(ratios)==perf['median_ratio']
for row in perf['rounds']:
 cpu=row['cpu_s'];assert row['baseline_to_pypy']==cpu['baseline']/cpu['pypy'] and row['candidate_to_pypy']==cpu['candidate']/cpu['pypy'] and row['cpython_to_candidate']==cpu['python']/cpu['candidate']
assert perf['median_baseline_to_pypy']==statistics.median(r['baseline_to_pypy'] for r in perf['rounds'])
assert perf['median_candidate_to_pypy']==statistics.median(r['candidate_to_pypy'] for r in perf['rounds'])
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
p=load('profile-after-v1');assert p['equal_to_fresh_state_v2'] and p['total_guest_entries']==3103685 and p['python_guest_entries']==404581
for path,h in load('baseline-snapshot-v1')['source_and_binary_sha256'].items():assert sha(e.BASE/path)==h,path
jobs=[json.loads(x) for x in (out/'jobs-v1.jsonl').read_text().splitlines()];starts=[r for r in jobs if r['event']=='start'];exits=[r for r in jobs if r['event']=='exit']
assert len(starts)==len(exits)==92 and all(r['code']==0 for r in exits) and {r['pid'] for r in starts}=={r['pid'] for r in exits}
for r in starts:
 try:os.killpg(r['pid'],0)
 except ProcessLookupError:pass
 else:raise AssertionError(('canonical producer group still alive',r))
assert load('post-exit-audit-v1')['pass_all'] and load('process-closure-v1')['pass_all']
assert load('freeze-v1')['source_sha256']==e.hashes()
old_manifest=json.loads((e.BASE/'out/T19/supplemental-source-inputs-v2.json').read_text())
for p,h in old_manifest['source_sha256'].items():assert sha(e.BASE/p)==h
assert extra['supplemental_source_sha256']==old_manifest['source_sha256']
assert load('baseline-input-audit-v1')['pass_all']
old_plan=json.loads((e.BASE/'out/T19/proof-plan-v1.json').read_text());assert sum(len(rows) for rows in old_plan['errors'].values())==122
assert len({root+'/'+row['selector'] for root,rows in old_plan['errors'].items() for row in rows})==118
closure=load('process-closure-v1');assert len(closure['groups'])==92+12*len(campaigns) and all(g['empty'] for g in closure['groups'])
for rnd in range(1,4):
 for arm in ['baseline','candidate','python','pypy']:
  r=load(f'cpu-{arm}-r{rnd}-{version}');assert max(r['load_before'][:2])<4 and max(r['load_after'][:2])<4
 trace=[r for r in perf['continuous_load'] if r['round']==rnd];assert trace and all(max(r['load'][:2])<8 for r in trace)
assert len(perf['quiet_quality'])==3 and all(r['all_arm_ends_quiet'] and r['continuous_total_load_below8'] for r in perf['quiet_quality'])
for campaign in campaigns:
 r=load('performance-'+campaign['version']);assert r['measurement_complete'] and r['source_unchanged'] and sha(out/('performance-'+campaign['version']+'.json'))==campaign['sha256']
 if campaign['version']!=version:assert not campaign['accepted'] and not r['quiet_complete']
 for rnd in range(1,4):
  for arm in ['baseline','candidate','python','pypy']:
   row=load(f"cpu-{arm}-r{rnd}-{campaign['version']}");assert row['source_unchanged']
   for path,h in row['source_sha256'].items():assert sha(e.BASE/path)==h
assert load('capture-input-audit-v1')['pass_all']
assert all(q['all_runner_observations_idle'] and q['runner_observations'] and all(r['known'] and not r['busy'] for r in q['runner_observations']) for q in perf['quiet_quality'])
assert all(r['runners']['known'] and not r['runners']['busy'] for rnd in range(1,4) for r in [x for x in perf['quiet_observations'] if x['round']==rnd][-3:])
result=dict(pass_all=True,new_error_comparisons=27360,new_distinct_error_selectors=171,selected_performance_version=version,prior_chase_error_comparisons=15840,prior_depth_error_comparisons=20160,all_writers_finished=True,comparisons=comparisons,attestation=attest,performance_ratios=ratios,median_performance_ratio=statistics.median(ratios),incremental_port_no_magnitude_minimum=True,all_rounds_improve=all(r<1 for r in ratios),
 evidence_sha256={str(p.relative_to(out)):sha(p) for p in sorted(out.rglob('*')) if p.is_file() and p.suffix in ['.json','.jsonl','.log','.txt','.prof'] and not p.name.startswith('validation-')})
e.write(sys.argv[1],result,e.hashes());print('T25 fidelity, complete measurements and closed source/binary/input/evidence gates pass')
