"""Public state/tables API through Rust, using entirely authored synthetic data."""
import os
import subprocess
import sys
import unittest


CASE = r'''
import base64, hashlib, json, sys, zlib
from original_match import Image, Fixture
from original_match.port.tables import Tables, TablesError, DS_INIT
from goal2rust import Match

ds = bytes(DS_INIT)
code = b'authored test table'
tables = Tables(ds, [(0x100, code)], dict(ds=hashlib.sha256(ds).hexdigest(),
                                       code_data=hashlib.sha256(code).hexdigest()))
image = Image.__new__(Image)
image.header, image.memory, image.load = bytes(0x78), bytearray(0x110000), 0x823
image.DS, image.tables = image.load + 0x2581, None
tables.place(image.memory, image.load)
for field, seg in [(0xA91B, 0x4000), (0xA917, 0x5000), (0xA923, 0x6000),
                   (0xA91F, 0x7000), (0xA92B, 0x8000)]:
    at = image.DS * 16 + field
    image.memory[at:at+4] = b'\x00\x00' + seg.to_bytes(2, 'little')
image.memory[0x60028:0x6002A] = (10).to_bytes(2, 'little')
state = image.state(tables)

mode = sys.argv[1]
if mode == 'invalid':
    for bad, exception in [(dict(state, schema='wrong'), ValueError),
                           (dict(state, tables_sha256={}), TablesError)]:
        try: Image.from_state(bad, tables)
        except exception: pass
        else: raise AssertionError('invalid state accepted')
    raw = bytearray(zlib.decompress(base64.b64decode(state['memory'])))
    raw[image.load * 16 + 1] = 1
    bad = dict(state, memory=base64.b64encode(zlib.compress(raw)).decode())
    try: Image.from_state(bad, tables)
    except ValueError: pass
    else: raise AssertionError('module bytes accepted')
else:
    sealed = Image.from_state(state, tables)
    match = Match(sealed, Fixture(7, 19, index=9, kind=200), managed=7)
    assert type(match.m).__module__ == 'goal2rust.machine'
    after = match.records_after()
    restored = Image.from_state(after, tables)
    assert restored.state() == after
    assert match.m.read(0x80040, 8) == b'\xfe\x00\xc8\x00\x07\x00\x13\x00'
    if mode == 'replay':
        loaded = Match.load(match.save())
        assert type(loaded.m).__module__ == 'goal2rust.machine'
        assert loaded.records_after(tables) == after
        assert loaded.m.snapshot() == match.m.snapshot()
        assert loaded.save() == match.save()
print('PASS', mode)
'''


class SealedAPITests(unittest.TestCase):
    def test_state_records_and_checkpoint_through_rust(self):
        for mode in ('invalid', 'records', 'replay'):
            with self.subTest(mode=mode):
                run = subprocess.run([sys.executable, '-B', '-c', CASE, mode],
                                     env=dict(os.environ, PYTHONHASHSEED='0'),
                                     text=True, capture_output=True, timeout=30)
                self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
                self.assertIn('PASS ' + mode, run.stdout)


if __name__ == '__main__':
    unittest.main()
