"""T07 public schema-v2/retained-table contract, authored data only."""
import os,subprocess,sys,unittest
from test_sealed_api import CASE
PREFIX=CASE.split('mode = sys.argv[1]')[0]
TEST=PREFIX+r'''
from original_match.port.tables import MODULE_SIZE
mode=sys.argv[1]
module=image.load*16
image.memory[module+0x103]^=1
image.memory[image.DS*16+0x10]=0xaa
state=image.state(tables)
if mode=='overlay':
    assert state.get('code_data')==[[0x103,image.memory[module+0x103]]]
    assert state['schema']=='original_match.state/2'
    sealed=Image.from_state(state,tables)
    assert sealed.memory==image.memory
    assert sealed.state()==state
    match=Match(sealed,Fixture(7,19,index=9,kind=200),managed=7)
    assert type(match.m).__module__=='goal2rust.machine'
    assert match.m.read(module+0x103,1)==bytes([image.memory[module+0x103]])
    assert match.records_after()['code_data']==state['code_data']
elif mode=='invalid':
    # The previous schema is refused, rather than silently losing its code-data overlay.
    bad=dict(state,schema='original_match.state/1')
    try:Image.from_state(bad,tables)
    except ValueError:pass
    else:raise AssertionError('legacy schema accepted')
    for key,off,outside in [('initialised',0,DS_INIT),('code_data',0x100,0x200)]:
        for entries in [None,{},'bad', [None], [[]], [[off]], [[off,1,2]],
                        [[True,1]], [[off,False]], [['0',1]], [[off,'1']],
                        [[off,1.0]], [[-1,1]], [[outside,1]], [[off,-1]], [[off,256]], [(off,1)]]:
            bad=dict(state,**{key:entries})
            try:Image.from_state(bad,tables)
            except ValueError as exc:assert key in str(exc)
            else:raise AssertionError((key,'malformed entry accepted'))
        bad=dict(state);del bad[key]
        try:Image.from_state(bad,tables)
        except ValueError as exc:assert key in str(exc)
        else:raise AssertionError('missing list accepted')
else:
    match=Match(Image.from_state(state,tables),Fixture(7,19,index=9,kind=200),managed=7)
    saved=match.save();loaded=Match.load(saved)
    assert type(loaded.m).__module__=='goal2rust.machine'
    assert loaded.records_after()==match.records_after()
    assert loaded.m.snapshot()==match.m.snapshot()
    assert loaded.save()==saved
    n=int.from_bytes(saved[4:8],'little');record=json.loads(saved[8:8+n])
    record['tables']['sha256']['ds']='0'*64
    head=json.dumps(record).encode()
    try:Match.load(saved[:4]+len(head).to_bytes(4,'little')+head+saved[8+n:])
    except ValueError as exc:assert 'recorded digests' in str(exc)
    else:raise AssertionError('tampered checkpoint tables accepted')
print('PASS',mode)
'''

class StateV2Tests(unittest.TestCase):
    def run_mode(self,mode):
        p=subprocess.run([sys.executable,'-B','-c',TEST,mode],env=dict(os.environ,PYTHONHASHSEED='0'),text=True,capture_output=True,timeout=30)
        self.assertEqual(p.returncode,0,p.stdout+p.stderr);self.assertIn('PASS '+mode,p.stdout)
    def test_relocated_code_data_and_rust_records(self):self.run_mode('overlay')
    def test_entry_types_ranges_and_legacy_refusal(self):self.run_mode('invalid')
    def test_checkpoint_retains_tables_and_checks_digests(self):self.run_mode('checkpoint')

if __name__=='__main__':unittest.main()
