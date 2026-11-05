"""Close accepted T26, its historical epochs and the actual saved comparator."""
import hashlib
import json
from pathlib import Path
import evidence as e

B = e.BASE
O = B/'out/T27'
load = lambda p:json.loads((B/p).read_text())
sha = lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
e.verify()
before = e.hashes()
assert before == load('out/T27/freeze-v1.json')['source_sha256']
assert load('out/T27/process-closure-v1.json')['pass_all']
old = load('out/T26/validation-final-v1.json')
assert old['pass_all'] and len(old['source_sha256']) == 1647 and len(old['evidence_sha256']) == 283
for p, digest in old['source_sha256'].items():assert sha(B/e.accepted_path(p)) == digest, p
for p, digest in old['evidence_sha256'].items():assert sha(B/'out/T26'/p) == digest, p
resume = load('out/T25/resume-source-inputs-v2.json')
assert len(resume['source_sha256']) == 6 and len(resume['input_sha256']) == 121
for key in ['source_sha256', 'input_sha256']:
    for p, digest in resume[key].items():assert sha(B/p) == digest, p
merged = load('.cache/T26-merged-binding-audit-v1.json')
assert merged['pass_all'] and merged['identical_tree'] and merged['groups_stopped'] == 109
assert merged['merged_sha'] == 'd2f5a194e921f69b5492f19a4c3bbda85725b3d3'
assert merged['controller_stopped']
baseline = load('out/T27/baseline-snapshot-v1.json')
assert len(baseline['source_and_binary_sha256']) == len(baseline['source_map']) == 79
assert baseline['preserved_before_build'] and baseline['revision'] == merged['merged_sha']
assert baseline['accepted_merged_audit_sha256'] == sha(B/'.cache/T26-merged-binding-audit-v1.json')
for p, digest in baseline['source_and_binary_sha256'].items():assert sha(B/p) == digest, p
for original, saved in baseline['source_map'].items():
    assert saved in baseline['source_and_binary_sha256']
    if original in old['source_sha256']:
        assert baseline['source_and_binary_sha256'][saved] == old['source_sha256'][original]
archives = []
for stage in range(7, 28):
    for path in sorted((B/f'out/T{stage:02}').glob('artifact-archive-v*.json')):
        for row in json.loads(path.read_text())['artifacts']:
            assert sha(B/row['archive']) == row['sha256']
            if stage == 27:
                assert sha(B/row['original']) == row['sha256']
                assert row['public_preflight_sha256'] == sha(O/f"public-{row['interpreter']}-preflight-v2.log")
            archives.append(row['archive'])
assert len(archives) == 44
diagnostics = {}
for version in ['v1', 'v2']:
    rejected = load(f'out/T27/rejected-preparation-{version}.json')
    assert not rejected['accepted'] and rejected['no_final_build_or_canonical_started']
    for name, digest in rejected['receipts_sha256'].items():assert sha(O/name) == digest, name
    for original, digest in rejected['live_source_sha256'].items():
        assert sha(B/rejected['live_source_map'][original]) == digest, original
    for original, digest in rejected['preparation_source_sha256'].items():
        assert sha(B/rejected['preparation_preserved_source_map'][original]) == digest, original
failed = load('out/T27/rejected-preparation-v3.json')
assert not failed['accepted'] and failed['no_archive_freeze_or_canonical_started']
assert failed['failed_code'] == -9 and failed['completed_successful_groups'] == 4
for name, digest in failed['receipts_sha256'].items():assert sha(O/name) == digest, name
for name, digest in failed['source_sha256'].items():assert sha(B/failed['preserved_source_map'][name]) == digest, name
for row in failed['artifacts']:assert sha(B/row['archive']) == row['sha256']
for name in ['development-probe-v1.json', 'live-development-v3.json']:
    report = load('out/T27/'+name)
    assert report['development_only'] and not report['accepted_canonical_evidence']
    for p, digest in report['executed_source_sha256'].items():
        assert sha(B/report['preserved_source_map'][p]) == digest, (name, p)
    diagnostics[name] = len(report['executed_source_sha256'])
profile = load('out/T27/profile-after-v1.json')
for name in ['taps-python-v1', 'taps-rust-v1']:
    receipt = load('out/T27/'+name+'.json')
    assert all(profile['observed'][key] == receipt[key] for key in profile['observed'])
assert 'out/T26/taps-rust-v1.json' in before
selection = load('out/T27/performance-selection-v1.json')
new = set(load('out/T27/inventory-v1.json')['bodies'])
for rnd in range(1, 4):
    base = load(f"out/T27/cpu-baseline-r{rnd}-{selection['selected_version']}.json")
    candidate = load(f"out/T27/cpu-candidate-r{rnd}-{selection['selected_version']}.json")
    assert base['arm'] == 'baseline' and candidate['arm'] == 'candidate'
    assert len(base['native_calls']) == 79 and not (new & set(base['native_calls']))
    assert len(candidate['native_calls']) == 86 and new <= set(candidate['native_calls'])
e.write(O/'baseline-input-audit-v1.json', dict(pass_all=True, accepted_T26_primary=1647,
        accepted_T26_evidence=283, accepted_T25_resume_sources=6, accepted_T25_resume_inputs=121,
        accepted_T26_merged_audit_verified=True, baseline_files=79, archive_bindings=44,
        preserved_development_bindings=diagnostics, profile_matches_fresh_receipts=True,
        native_presence_before_after=True, script_sha256=sha(Path(__file__))), before)
print('Accepted1647+283/resume6+121,baseline79,all44 artifacts and archived diagnostics verified')
