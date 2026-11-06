"""Retain every T26 commentary assertion against the combined T28 campaign."""
import json
from pathlib import Path


def check_new(load):
    O = Path(__file__).resolve().parent
    inventory = json.loads((O.parent/'T26/inventory-v1.json').read_text())
    plan = json.loads((O.parent/'T26/proof-plan-v1.json').read_text())
    normal = load('commentary-normal-v1')
    assert normal['all_equal'] and normal['control_scope_verified'] and normal['all_inventory_helper_scope']
    assert sum(row['total'] for row in normal['comparisons'].values()) == 30960
    assert len(normal['captures']) == 10 and all(n == 8 for n in normal['captures'].values())
    assert normal['owned_code_objects'] == inventory['owned_code_objects'] and len(normal['owned_code_objects']) == 31
    assert set(normal['source_owned_calls']) == set(inventory['owned_code_objects']) and all(normal['source_owned_calls'].values())
    assert len(normal['closure_checks']) == 10 and all(n == 2096 for n in normal['closure_checks'].values())
    assert normal['branch_comparisons'] == 2400 and len(normal['branches']) == 65 and all(normal['branches'].values())
    assert sorted(normal['branches']) == plan['branch_outcomes']
    assert normal['error_comparisons'] == plan['error_comparisons'] == 147360
    assert len(normal['errors_seen']) == plan['error_execution_rows'] == plan['distinct_error_selectors'] == 921
    assert all(normal['errors_seen'].values()) and normal['variants'] == 224
    for suite, total in [('body', 20960), ('output', 146720)]:
        report = load('commentary-'+suite+'-v1')
        assert report['control_scope_verified'] and not report['all_equal']
        assert sum(row['total'] for row in report['comparisons'].values()) == total
        assert all(row['equal'] == 0 for row in report['comparisons'].values())
    returns = load('commentary-returns-v1')
    assert set(returns['return_controls']) == {site['ret_to'] for site in inventory['guest_sites']}
    assert len(returns['return_controls']) == 25
    assert all(row['total'] == 160 and row['reached'] == row['detected'] > 0 for row in returns['return_controls'].values())
    for name in ['prior-commentary-live-observers-v1', 'prior-text-live-observers-v1']:
        report = load(name)
        assert report['pass_all'] and report['comparisons'] == 1280 and len(report['scenarios']) == 8
        assert all(row['effect_witnesses'] > 0 and row['hits'] and all(row['hits'].values()) for row in report['scenarios'].values())
    profile = load('profile-after-v1')
    assert len(profile['routines']) == 422 and sum(row['native_entries'] > 0 for row in profile['routines'].values()) == 87
    assert profile['total_guest_entries'] == 3103685 and profile['python_guest_entries'] == 305039
    assert sum(profile['native_calls'].values()) == 2798646
    for label in ['check', 'family-ALL']:
        attestations = [json.loads(p.read_text()) for p in (O/f'attest-{label}-v1').glob('*.json')]
        reached = {address for row in attestations for address, count in row['native_calls'].items() if count > 0}
        assert len(reached) == 87 and set(inventory['bodies']) <= reached
