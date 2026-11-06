"""New receiver assertions,with the entire prior strength/commentary gate."""
import json
from pathlib import Path
O=Path(__file__).resolve().parent
def check_new(load):
 inv=json.loads((O/'inventory-v1.json').read_text());plan=load('proof-plan-v1');r=load('receiver-normal-v1')
 assert r['all_equal'] and r['control_scope_verified'] and r['all_inventory_helper_scope']
 assert sum(v['total'] for v in r['comparisons'].values())==4096
 assert r['captures']=={'0791:533B':8} and r['owned_code_objects']==inv['owned_code_objects']
 assert len(inv['owned_code_objects'])==6
 for name in ['source_owned_calls','outside_native_owned_calls','nondefault_owned_calls']:
  assert set(r[name])==set(inv['owned_code_objects']) and all(r[name].values())
 assert r['closure_checks']=={'0791:533B':2096}
 assert r['branch_comparisons']==320 and sorted(r['branches'])==plan['branch_outcomes'] and all(r['branches'].values())
 assert r['error_comparisons']==plan['error_comparisons']==3520
 assert len(r['errors_seen'])==plan['distinct_error_selectors']==22 and all(r['errors_seen'].values())
 assert r['variants']==64
 for suite,count in [('body',2096),('output',14672)]:
  r=load('receiver-'+suite+'-v1');assert r['control_scope_verified'] and not r['all_equal']
  assert sum(v['total'] for v in r['comparisons'].values())==count and all(v['equal']==0 for v in r['comparisons'].values())
 r=load('receiver-returns-v1');assert set(r['return_controls'])=={'0791:5367'}
 assert all(v['total']==160 and v['reached']==v['detected']>0 for v in r['return_controls'].values())
 r=load('live-observers-v1');assert r['pass_all'] and r['comparisons']==640 and len(r['scenarios'])==4
 assert all(v['comparisons']==v['effect_witnesses']==160 and v['hits'] and all(v['hits'].values()) for v in r['scenarios'].values())
 profile=load('profile-after-v1');assert len(profile['native_calls'])==87 and profile['native_calls']['0791:533B']==35723
 assert sum(profile['native_calls'].values())==2798646 and profile['python_guest_entries']==305039
 for label in ['check','family-ALL']:
  receipts=[json.loads(p.read_text()) for p in (O/f'attest-{label}-v1').glob('*.json')]
  reached={ad for receipt in receipts for ad,count in receipt['native_calls'].items() if count>0}
  assert len(reached)==87 and '0791:533B' in reached
 from prior_strength_assertions import check_new as check_prior
 check_prior(load)
