"""Additive post-writer binding of the profile's historical reference receipt."""
import hashlib
import json
import subprocess
from pathlib import Path
import evidence as e

B = e.BASE
O = B / 'out/T24'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads((B / p).read_text())
e.verify()
before = e.hashes()
assert before == load('out/T24/freeze-v1.json')['source_sha256']
assert load('out/T24/process-closure-v1.json')['pass_all']
manifest_path = O / 'supplemental-source-inputs-v1.json'
manifest = json.loads(manifest_path.read_text())
assert manifest['primary_freeze_sha256'] == sha(O / 'freeze-v1.json')
assert set(manifest['source_sha256']) == {'out/T24/profile_reference_audit.py'}
assert set(manifest['input_sha256']) == {
    'out/T21/taps-rust-v1.json', 'out/T24/profile-after-v1.json',
    'out/T24/taps-python-v1.json', 'out/T24/taps-rust-v1.json',
}
for key in ['source_sha256', 'input_sha256']:
    for p, h in manifest[key].items():
        assert sha(B / p) == h, p
historical = 'out/T21/taps-rust-v1.json'
accepted = manifest['accepted_main']
assert accepted == '42c06a71398fb930ad6c1f9104c5398cccbf1481'
blob = subprocess.check_output(['git', 'show', accepted + ':' + historical], cwd=B)
assert hashlib.sha256(blob).hexdigest() == sha(B / historical)
old = load('out/T21/validation-final-v1.json')
assert old['pass_all'] and old['evidence_sha256']['taps-rust-v1.json'] == sha(B / historical)
assert 'out/T21/validation-final-v1.json' in before
profile = load('out/T24/profile-after-v1.json')
reference = load('out/T24/taps-python-v1.json')
candidate = load('out/T24/taps-rust-v1.json')
assert profile['source_unchanged'] and profile['equal_to_fresh_state_v2']
assert profile['source_sha256'] == before
assert all(profile['observed'][k] == reference[k] == candidate[k] for k in profile['observed'])
assert profile['native_calls'] == candidate['native_calls']
assert sum(profile['native_calls'].values()) == 2688294
assert profile['python_guest_entries'] == 415391 and profile['total_guest_entries'] == 3103685
report = dict(
    pass_all=True, additive_only=True, no_runtime_or_primary_source_change=True,
    primary_freeze_sha256=manifest['primary_freeze_sha256'],
    source_manifest_sha256=sha(manifest_path),
    supplemental_source_sha256=manifest['source_sha256'],
    supplemental_input_sha256=manifest['input_sha256'],
    historical_reference=historical, accepted_main=accepted,
    historical_reference_matches_accepted_tree=True,
    historical_reference_matches_T21_evidence_ledger=True,
    profile_matches_fresh_python_and_rust=True,
    observed_fields=sorted(profile['observed']),
)
e.write(O / 'profile-reference-audit-v1.json', report, before)
print('Historical profile reference and fresh Python/Rust outputs independently bound and equal')
