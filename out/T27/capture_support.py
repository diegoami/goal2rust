"""Pure pinned-oracle image and denial helpers; no candidate/test imports."""
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
ORACLE = BASE / '.cache/goal2-archaeology'
PIN = '2cbeb36fdd3feb369324aaa88e6e4d2aa3b3d99c'
sys.path[:0] = [str(ORACLE), str(ORACLE / 'runtime')]
TABLES = BASE / '.cache/T07-tables'
STATE = BASE / '.cache/T07-state-v2-v1.json'


def verify():
    assert os.environ.get('PYTHONHASHSEED') == '0'
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ORACLE, text=True).strip() == PIN
    assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=ORACLE, text=True).strip()


def deny_original():
    spec = importlib.util.spec_from_file_location('seal_test', ORACLE / 'tests/test_port_seal.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    exec(module.BOOTSTRAP.split("sys.argv = ['original_match.check']")[0], {})


def image():
    from original_match import Image
    from original_match.port import tables
    return Image.from_state(json.loads(STATE.read_text()), tables.load(TABLES))
