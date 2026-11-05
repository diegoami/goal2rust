"""Close accepted T27, its historical epochs and the actual saved comparator."""
import hashlib
import json
from pathlib import Path
import evidence as e

B = e.BASE
O = B/'out/T28'
load = lambda p:json.loads((B/p).read_text())
sha = lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
e.verify()
before = e.hashes()
assert before == load('out/T28/freeze-v1.json')['source_sha256']
assert load('out/T28/process-closure-v1.json')['pass_all']
old = load('out/T27/validation-final-v1.json')
assert old['pass_all'] and len(old['source_sha256']) == 2378 and len(old['evidence_sha256']) == 320
for p, digest in old['source_sha256'].items():assert sha(B/e.accepted_path(p)) == digest, p
for p, digest in old['evidence_sha256'].items():assert sha(B/'out/T27'/p) == digest, p
resume = load('out/T25/resume-source-inputs-v2.json')
assert len(resume['source_sha256']) == 6 and len(resume['input_sha256']) == 121
for key in ['source_sha256', 'input_sha256']:
    for p, digest in resume[key].items():assert sha(B/p) == digest, p
merged = load('.cache/T27-merged-binding-audit-v1.json')
assert merged['pass_all'] and merged['identical_tree'] and merged['groups_stopped'] == 114
assert merged['merged_sha'] == 'cfdd296175a5ce7bf873d18fe41d02cddd1e53bc'
assert merged['controller_stopped']
baseline = load('out/T28/baseline-snapshot-v1.json')
assert len(baseline['source_and_binary_sha256']) == len(baseline['source_map']) == 82
assert baseline['preserved_before_build'] and baseline['revision'] == merged['merged_sha']
assert baseline['accepted_merged_audit_sha256'] == sha(B/'.cache/T27-merged-binding-audit-v1.json')
for p, digest in baseline['source_and_binary_sha256'].items():assert sha(B/p) == digest, p
for original, saved in baseline['source_map'].items():
    assert saved in baseline['source_and_binary_sha256']
    if original in old['source_sha256']:
        assert baseline['source_and_binary_sha256'][saved] == old['source_sha256'][original]
archives = []
for stage in range(7, 29):
    for path in sorted((B/f'out/T{stage:02}').glob('artifact-archive-v*.json')):
        for row in json.loads(path.read_text())['artifacts']:
            assert sha(B/row['archive']) == row['sha256']
            if stage == 28:
                assert sha(B/row['original']) == row['sha256']
                assert row['public_preflight_sha256'] == sha(O/f"public-{row['interpreter']}-preflight-v1.log")
            archives.append(row['archive'])
assert len(archives) == 46
diagnostics = {}
for version in ['v1', 'v2']:
    rejected=load(f'out/T28/rejected-live-development-{version}.json')
    assert not rejected['accepted'] and rejected['no_canonical_started']
    assert sha(O/f'live-development-{version}.log')==rejected['log_sha256']
    for name,digest in rejected['executed_source_sha256'].items():assert sha(B/rejected['preserved_source_map'][name])==digest,name
for name in ['development-probe-v1.json', 'live-development-v3.json']:
    report = load('out/T28/'+name)
    assert report['development_only'] and not report['accepted_canonical_evidence']
    for p, digest in report['executed_source_sha256'].items():
        assert sha(B/report['preserved_source_map'][p]) == digest, (name, p)
    diagnostics[name] = len(report['executed_source_sha256'])
profile = load('out/T28/profile-after-v1.json')
for name in ['taps-python-v1', 'taps-rust-v1']:
    receipt = load('out/T28/'+name+'.json')
    assert all(profile['observed'][key] == receipt[key] for key in profile['observed'])
assert 'out/T26/taps-rust-v1.json' in before
selection = load('out/T28/performance-selection-v1.json')
new = set(load('out/T28/inventory-v1.json')['bodies'])
for rnd in range(1, 4):
    base = load(f"out/T28/cpu-baseline-r{rnd}-{selection['selected_version']}.json")
    candidate = load(f"out/T28/cpu-candidate-r{rnd}-{selection['selected_version']}.json")
    assert base['arm'] == 'baseline' and candidate['arm'] == 'candidate'
    assert len(base['native_calls']) == 86 and not (new & set(base['native_calls']))
    assert len(candidate['native_calls']) == 87 and new <= set(candidate['native_calls'])
e.write(O/'baseline-input-audit-v1.json', dict(pass_all=True, accepted_T27_primary=2378,
        accepted_T27_evidence=320, accepted_T25_resume_sources=6, accepted_T25_resume_inputs=121,
        accepted_T27_merged_audit_verified=True, baseline_files=82, archive_bindings=46,
        preserved_development_bindings=diagnostics, profile_matches_fresh_receipts=True,
        native_presence_before_after=True, script_sha256=sha(Path(__file__))), before)
print('Accepted2378+320/resume6+121,baseline82,all46 artifacts and archived diagnostics verified')
