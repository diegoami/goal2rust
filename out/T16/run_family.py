"""Append-only ALL from records; use a fresh attestation folder for each invocation."""
import argparse
import json
import os
import subprocess
import sys
import evidence as common

ap = argparse.ArgumentParser()
ap.add_argument('--out', required=True)
ap.add_argument('--attest', required=True)
a = ap.parse_args()
common.verify()
before = common.hashes()
env = dict(os.environ, GOAL2RUST_T16='1', GOAL2RUST_T16_ATTEST=a.attest,
           PYTHONPATH=os.pathsep.join([str(common.BASE / 'out/T16'), str(common.BASE / 'engine/python'), str(common.ORACLE / 'runtime')]))
command = [sys.executable, '-B', 'experiments/E036-match-port/family.py', '--family', 'ALL',
           '--engine', 'port', '--no-unicorn', '--from-records', '--tables', str(common.TABLES),
           '--workers', '2', '--cache', str(common.ORACLE / '.cache/dl'), '--out', str(common.BASE / a.out)]
code = subprocess.call(command, cwd=common.ORACLE, env=env)
common.write(common.BASE / (a.attest + '-invocation.json'),
             dict(command=command, exit_code=code, candidate=a.out, attestation=a.attest), before)
assert code == 0
