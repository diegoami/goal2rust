"""Native machine's seven bodies AND full frames against the pinned Python oracle.

500 random states x 4 tap/listener modes x body/framed, plus real call inputs
captured in RAM from E034-03's first 60 events. Only hashes/counts in the receipt.
"""
import argparse
import hashlib
import json
import random
import sys
import time
from pathlib import Path

G2R = Path(__file__).resolve().parents[2]
ROOT = G2R / '.cache/goal2-archaeology'
sys.path[:0] = [str(ROOT), str(ROOT / 'runtime'), str(G2R / 'engine/python')]
from original_match import Match, Image, Fixture
import evidence as e
from original_match.port.engine import PortMachine as Oracle
from original_match.port.guest import PortFrame
from goal2rust.machine import PortMachine, BridgeRunner
import goal2rust_engine
import differential_helpers as helpers

ap = argparse.ArgumentParser()
ap.add_argument('--trials', type=int, default=500)
ap.add_argument('--seed', type=int, default=1)
ap.add_argument('--out', type=Path, required=True)
a = ap.parse_args()
out = a.out.open('x')
m = Match(e.image(), Fixture(7,19,index=9,kind=200),
          managed=7, substitutions=None, engine='port', record_draws=True)
python_fn = {ad: (e, v) for reg,v in m.ports.loaded for ad,e in reg.entries.items() if ad in goal2rust_engine.PORTS}
captured = {ad: [] for ad in python_fn}
original = {}
for ad, (entry, _) in python_fn.items():
    fn = original[ad] = entry.fn
    def capture(mem, variant, ad=ad, fn=fn):
        if len(captured[ad]) < 8:
            captured[ad].append((bytes(mem.m._memory), dict(mem.m._registers), mem._entries[-1]))
        return fn(mem, variant)
    entry.fn = capture
for i, ev in enumerate(m.events()):
    if ev.kind == 'decision': m.answer(quick=True) if ev.data['context']=='half_time' else m.answer()
    if i >= 60: break
for ad,(entry,_) in python_fn.items(): entry.fn = original[ad]
SNAP_MEM, SNAP_REGS = bytes(m.m._memory), dict(m.m._registers)
helpers.python_fn, helpers.SNAP_REGS, helpers.DS = python_fn, SNAP_REGS, m.m.DS
machines = [Oracle(SNAP_MEM, m.m.load), PortMachine(SNAP_MEM, m.m.load)]
mems = [machine.port_memory() for machine in machines]


def run(native, address, snapshot, state, tapped, listener, framed):
    M, mem = machines[native], mems[native]
    M.io_tap = M.listen_tap = M.site_tap = None
    M._writes.clear(); M._writes_now = (); M._writes_span = (1,0)
    M._memory[:] = snapshot[0]
    M._registers.clear(); M._registers.update(snapshot[1])
    if state is None:
        sp, far = snapshot[2]
    else:
        pokes, words, sp, regs, far = state
        for lin,data in pokes: M._memory[lin:lin+len(data)] = data
        M._registers.update(regs)
        ss = M._registers['ss'] & 0xffff
        base = sp + (4 if far else 2)
        for i,w in enumerate(words):
            lin = ss*16 + ((base+2*i)&0xffff)
            M._memory[lin:lin+2] = w.to_bytes(2,'little')
    log = helpers.Log()
    if listener:
        # Watch the entire stack segment, including offsets wrapping at zero.
        ss = M._registers['ss'] & 0xffff
        M.on_write(ss*16, ss*16+0xffff, lambda ad,sz,v: log.calls.append(('w',ad,sz,v,M.pc())))
    if tapped: M.io_tap, M.listen_tap = log.io, log
    entry, variant = python_fn[address]
    error, value = None, None
    try:
        if framed:
            if native: BridgeRunner(entry,variant,mem,{})(M)
            else: PortFrame(M,mem,entry,variant).start()
        else:
            mem._entries.append((sp,far))
            try:
                value = M._core.routine(M,mem,address) if native else entry.fn(mem,variant)
            finally: mem._entries.pop()
    except Exception as e: error = f'{type(e).__name__}: {e}'
    M.io_tap = M.listen_tap = None
    return dict(value=value,error=error,memory=hashlib.sha256(M._memory).hexdigest(),regs=dict(M._registers),calls=log.calls)


rng = random.Random(a.seed)
report = dict(trials=a.trials, seed=a.seed, routines={}, captured_counts={k:len(v) for k,v in captured.items()})
t0 = time.monotonic()
for address,(entry,variant) in sorted(python_fn.items()):
    stats = dict(random=0,real=0,equal=0,errors_both=0,differences=[])
    cases = [(None, snap) for snap in captured[address]]
    cases += [(helpers.make_state(rng,address,entry.far)+(entry.far,), (SNAP_MEM,SNAP_REGS,None)) for _ in range(a.trials)]
    for trial,(state,snapshot) in enumerate(cases):
        for tapped in (False,True):
            for listener in (False,True):
                for framed in (False,True):
                    p,r = [run(n,address,snapshot,state,tapped,listener,framed) for n in (0,1)]
                    stats['real' if state is None else 'random'] += 1
                    if p == r:
                        stats['equal'] += 1
                        stats['errors_both'] += p['error'] is not None
                    elif len(stats['differences']) < 5:
                        stats['differences'].append(dict(trial=trial,tapped=tapped,listener=listener,framed=framed,
                            diff={k:[repr(p[k])[:300],repr(r[k])[:300]] for k in p if p[k]!=r[k]}))
    report['routines'][address]=stats
    print(address,stats['equal'],'/',stats['real']+stats['random'],flush=True)
report['all_equal']=all(s['equal']==s['real']+s['random'] for s in report['routines'].values())
report['seconds']=time.monotonic()-t0
report['source_sha256']={str(p.relative_to(G2R)):hashlib.sha256(p.read_bytes()).hexdigest()
    for p in sorted((G2R/'engine/src').glob('*.rs'))+sorted((G2R/'engine/python').rglob('*.py'))+[Path(__file__).resolve(),Path(helpers.__file__)]}
json.dump(report,out,indent=2)
out.close()
sys.exit(0 if report['all_equal'] else 1)
