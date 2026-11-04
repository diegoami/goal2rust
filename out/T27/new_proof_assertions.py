"""Accept new strength proofs and preserve the entire prior commentary gate."""
import importlib.util,json
from pathlib import Path
O=Path(__file__).resolve().parent;B=O.parents[1]
def check_new(load):
 inv=json.loads((O/'inventory-v1.json').read_text());plan=load('proof-plan-v1')
 n=load('strength-normal-v1')
 assert n['all_equal'] and n['control_scope_verified'] and n['all_inventory_helper_scope']
 assert sum(v['total'] for v in n['comparisons'].values())==20672
 assert len(n['captures'])==7 and all(v==8 for v in n['captures'].values())
 assert n['owned_code_objects']==inv['owned_code_objects'] and len(n['owned_code_objects'])==27
 assert set(n['source_owned_calls'])==set(inv['owned_code_objects']) and all(n['source_owned_calls'].values())
 assert len(n['closure_checks'])==7 and all(v==2096 for v in n['closure_checks'].values())
 assert n['branch_comparisons']==1600 and sorted(n['branches'])==plan['branch_outcomes'] and all(n['branches'].values())
 assert n['error_comparisons']==plan['error_comparisons'] and len(n['errors_seen'])==plan['error_execution_rows']==plan['distinct_error_selectors'] and all(n['errors_seen'].values())
 assert n['variants']==144
 for suite,total in [('body',14672),('output',102704)]:
  r=load('strength-'+suite+'-v1');assert r['control_scope_verified'] and not r['all_equal']
  assert sum(v['total'] for v in r['comparisons'].values())==total and all(v['equal']==0 for v in r['comparisons'].values())
 r=load('strength-returns-v1');assert set(r['return_controls'])=={s['ret_to'] for s in inv['guest_sites']} and len(r['return_controls'])==12
 assert all(v['total']==160 and v['reached']==v['detected']>0 for v in r['return_controls'].values())
 for name in ['live-observers-v1','prior-commentary-live-observers-v1']:
  r=load(name);assert r['pass_all'] and r['comparisons']==1280 and len(r['scenarios'])==8
  assert all(v['effect_witnesses']>0 and v['hits'] and all(v['hits'].values()) for v in r['scenarios'].values())
 # Execute the preserved prior79 proof assertions while explicitly binding their
 # historical inventory/plan,but use the current campaign's profile/attestation.
 old=(B/'out/T26/new_proof_assertions.py').read_text()
 old=old.replace("O = Path(__file__).resolve().parent","O = Path(__file__).resolve().parent")
 old=old.replace("(O/'inventory-v1.json')","(B/'out/T26/inventory-v1.json')").replace("(O/'proof-plan-v1.json')","(B/'out/T26/proof-plan-v1.json')")
 old=old.replace("['live-observers-v1', 'prior-text-live-observers-v1']","['prior-commentary-live-observers-v1', 'prior-text-live-observers-v1']")
 old=old.replace('== 79','== 86').replace('== 359012','== 340762').replace('== 2744673','== 2762923')
 namespace=dict(__file__=str(O/'new_proof_assertions.py'),B=B)
 exec(compile(old,'preserved-T26-proof-assertions','exec'),namespace)
 namespace['check_new'](load)
