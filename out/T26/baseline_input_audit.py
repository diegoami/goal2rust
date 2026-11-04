"""Close accepted T25, all historical inputs, archived diagnostics and comparator."""
import hashlib
import json
from pathlib import Path
import evidence as e

B = e.BASE
O = B/'out/T26'
load = lambda p:json.loads((B/p).read_text())
sha = lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
e.verify()
before = e.hashes()
assert before == load('out/T26/freeze-v1.json')['source_sha256']
assert load('out/T26/process-closure-v1.json')['pass_all']
old = load('out/T25/validation-final-v2.json')
assert old['pass_all'] and len(old['source_sha256']) == 1083 and len(old['evidence_sha256']) == 277
for p, digest in old['source_sha256'].items():assert sha(B/e.accepted_path(p)) == digest, p
for p, digest in old['evidence_sha256'].items():assert sha(B/'out/T25'/p) == digest, p
resume = load('out/T25/resume-source-inputs-v2.json')
assert len(resume['source_sha256']) == 6 and len(resume['input_sha256']) == 121
for key in ['source_sha256', 'input_sha256']:
    for p, digest in resume[key].items():assert sha(B/p) == digest
    assert old['resume_'+key] == resume[key]
merged = load('.cache/T25-merged-binding-audit-v1.json')
assert merged['pass_all'] and merged['identical_tree'] and merged['groups_stopped'] == 105
assert merged['merged_sha'] == 'd300f988a343124969d870625aaa5c2c0a75e8d0'
assert len(merged['controllers_stopped']) == 3
baseline = load('out/T26/baseline-snapshot-v1.json')
assert len(baseline['source_and_binary_sha256']) == 77 and baseline['preserved_before_build']
assert baseline['accepted_merged_audit_sha256'] == sha(B/'.cache/T25-merged-binding-audit-v1.json')
for p, digest in baseline['source_and_binary_sha256'].items():assert sha(B/p) == digest
archives = []
for stage in range(7, 27):
    for path in sorted((B/f'out/T{stage:02}').glob('artifact-archive-v*.json')):
        for row in json.loads(path.read_text())['artifacts']:
            assert sha(B/row['archive']) == row['sha256']
            if stage == 26:
                assert sha(B/row['original']) == row['sha256']
                assert row['public_preflight_sha256'] == sha(O/f"public-{row['interpreter']}-preflight-v1.log")
            archives.append(row['archive'])
assert len(archives) == 42
diagnostics = {}
for name in ['development-probe-v1.json', 'live-development-v1.json', 'live-development-v2.json']:
    report = load('out/T26/'+name)
    assert report['development_only'] and not report['accepted_canonical_evidence']
    for p, digest in report['executed_source_sha256'].items():
        assert sha(B/report['preserved_source_map'][p]) == digest, (name, p)
    diagnostics[name] = len(report['executed_source_sha256'])
rejected = load('out/T26/rejected-live-development-v1.json')
assert not rejected['accepted'] and sha(B/rejected['receipt']) == rejected['receipt_sha256']
assert sha(O/'live-development-v1.log') == rejected['log_sha256']
profile = load('out/T26/profile-after-v1.json')
for name in ['taps-python-v1', 'taps-rust-v1']:
    receipt = load('out/T26/'+name+'.json')
    assert all(profile['observed'][key] == receipt[key] for key in profile['observed'])
assert 'out/T25/taps-rust-v1.json' in before
selection = load('out/T26/performance-selection-v1.json')
new = set(load('out/T26/inventory-v1.json')['bodies'])
for rnd in range(1, 4):
    base = load(f"out/T26/cpu-baseline-r{rnd}-{selection['selected_version']}.json")
    candidate = load(f"out/T26/cpu-candidate-r{rnd}-{selection['selected_version']}.json")
    assert base['arm'] == 'baseline' and candidate['arm'] == 'candidate'
    assert len(base['native_calls']) == 69 and not (new & set(base['native_calls']))
    assert len(candidate['native_calls']) == 79 and new <= set(candidate['native_calls'])
e.write(O/'baseline-input-audit-v1.json', dict(pass_all=True, accepted_T25_primary=1083,
        accepted_T25_evidence=277, accepted_T25_resume_sources=6, accepted_T25_resume_inputs=121,
        accepted_T25_merged_audit_verified=True, baseline_files=77, archive_bindings=42,
        preserved_development_bindings=diagnostics, profile_matches_fresh_receipts=True,
        native_presence_before_after=True, script_sha256=sha(Path(__file__))), before)
print('Accepted1083+277/resume6+121,baseline77,all42 artifacts and archived diagnostics verified')
