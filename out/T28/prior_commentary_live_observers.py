"""Eight live/cached/order witnesses,160 pairs each; no source helper callbacks."""
import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path
import evidence as e
sys.path.insert(0, str(e.BASE/'engine/tests'))
from test_commentary import *

SCENARIOS = ('fill-cached-word-late-DF', 'wrap-own-store-before-pending-pushes',
             'rating-live-SS-parent-code', 'new-record-captured-country-pointer',
             'ring-live-word-cached-indices', 'emitter-live-loop-bound',
             'render-captured-temporary-live-BP', 'render-live-parent-row-after-attribute')
ROOTS = ['214B:0018', '214B:1C86', '0791:1E53', '0791:1C78',
         '0791:1D4A', '0791:1EB5', '0791:1829', '0791:1829']
OLD_AT = {c:c.at for c in (Oracle, PortMachine)}
OLD_WRITE = {c:c.on_write for c in (Oracle, PortMachine)}
ctx = {}


def put(m, at, value, n=1):
    m._memory[at:at+n] = (value & ((1 << (8*n))-1)).to_bytes(n, 'little')


def hit(key):
    ctx['hits'][key] = ctx['hits'].get(key, 0)+1


def at(m, site, fn):
    def wrapped(replay):
        fn(replay)
        r = m._registers
        scenario = ctx['scenario']
        if site == ctx['root'] and not replay:
            ss = r['ss']*16
            old_sp = r['esp'] & 65535
            far = ENTRIES[site].far
            header = 2 if far else 1
            sp = 0xe000
            for i in range(header):
                old = ss+((old_sp+2*i) & 65535)
                put(m, ss+sp+2*i, int.from_bytes(m._memory[old:old+2], 'little'), 2)
            r['esp'] = (r['esp'] & 0xffff0000) | sp
            ctx.update(ss=ss, sp=sp, bp=sp-2, line=sp-2-0x24)
            ds = m.DS*16
            parent = 0x600
            if scenario == SCENARIOS[0]:
                packet = [0x5a17, 9, 0xfffc, 0x5000]
            elif scenario == SCENARIOS[1]:
                packet = [1, 200, 1, sp-6, ss//16]
                put(m, ss+sp-6, 200, 2)
            elif scenario in (SCENARIOS[2], SCENARIOS[3]):
                packet = [parent]
                for k, value in [(4, 1), (6, 2), (8, 1), (10, 0)]:
                    put(m, ss+parent+k, value, 2)
                put(m, ds+0x80ee, 1, 2)
                for k, value, n in [(0, 1, 1), (1, 1, 2), (3, 2, 2), (5, 0, 1)]:
                    put(m, ds+0x7c3e+k, value, n)
            elif scenario == SCENARIOS[4]:
                packet = [1, 1, 1, 0]
                put(m, ds+0x80ee, 0, 2)
            elif scenario == SCENARIOS[5]:
                packet = [1, 1, 1, 0]
            else:
                packet = [33, 1, 1]
                put(m, ds+0x7c3e, 1)
                put(m, ds+0x7c43, 0)
                put(m, ds+0x832e, 7)
            for i, value in enumerate(packet):
                put(m, ss+sp+header*2+2*i, value, 2)
        if scenario == SCENARIOS[5] and site == '0791:1ED0':
            put(m, m.DS*16+0x80ee, 5, 2)
            r['eax'] = (r['eax'] & 0xffff0000) | 1
        if scenario == SCENARIOS[5] and site == '0791:1F21' and ctx['mutate']:
            put(m, ctx['ss']+ctx['bp']-4, 5, 2)
            hit('lower-bound-read-after-draw')
        if scenario == SCENARIOS[6] and site == '0791:1873' and ctx['mutate']:
            alternate = 0xc000
            for k, value in [(0, 0x1234), (4, 33), (6, 5), (8, 1)]:
                put(m, ctx['ss']+alternate+k, value, 2)
            r['ebp'] = (r['ebp'] & 0xffff0000) | alternate
            hit('live-BP-after-copy-captured-old-buffer')
    return OLD_AT[type(m)](m, site, wrapped)


def on_write(m, lo, hi, fn):
    def wrapped(address, n, value):
        fn(address, n, value)
        pc = m.pc()
        if not ctx['mutate']:
            return
        scenario = ctx['scenario']
        r = m._registers
        ds = m.DS*16
        if scenario == SCENARIOS[0] and pc == m.lin('214B:002D'):
            r['eax'] ^= 0xab00
            if not ctx.get('fill_flags_changed'):
                r['eflags'] ^= 0xc00
                ctx['fill_flags_changed'] = True
            hit('cached-word-and-late-flags')
        elif scenario == SCENARIOS[1]:
            if pc == m.lin('214B:1CF8'):
                assert address == ctx['ss']+ctx['sp']-6 and value == 1
                r['eflags'] ^= 0x800
                ctx['wrapped'] = True
                hit('own-store-before-pending-flush')
            elif pc == m.lin('214B:0000') and ctx.get('wrapped'):
                a = ctx['ss']+ctx['sp']-6
                assert int.from_bytes(m._memory[a:a+2], 'little') == 1
                hit('pending-push-overwrites-own-store')
        elif scenario == SCENARIOS[2]:
            if pc == m.lin('0791:1E7B'):
                alternate = 0x30000
                m._memory[alternate:alternate+65536] = m._memory[ctx['ss']:ctx['ss']+65536]
                put(m, alternate+(address-ctx['ss']), value, n)
                put(m, alternate+0x600+4, 2, 2)
                r['ss'] = alternate//16
                hit('SS-changed-after-record-local')
            elif pc == m.lin('0791:1EAB'):
                r['ss'] = ctx['ss']//16
                hit('rating-used-live-parent-code')
        elif scenario == SCENARIOS[3] and pc == m.lin('0791:1CAF'):
            put(m, ds+0xa917, 0x200, 2)
            put(m, ds+0xa919, 0x7000, 2)
            put(m, 0x70200, 0xaaaa, 2)
            put(m, 0x70202, 0xbbbb, 2)
            hit('country-pointer-replaced-after-capture')
        elif scenario == SCENARIOS[4] and pc == m.lin('0791:1DDB'):
            put(m, 0x50100, 0xbeef, 2)
            put(m, ctx['ss']+ctx['bp']+6, 2, 2)
            hit('live-country-word-with-cached-second-index')
        elif scenario == SCENARIOS[7] and pc == m.lin('214B:02E6'):
            put(m, ctx['ss']+ctx['bp']+6, 5, 2)
            hit('parent-row-changed-after-child-attribute')
    return OLD_WRITE[type(m)](m, lo, hi, wrapped)


def run(cls, case, scenario, mutate):
    ctx.clear()
    ctx.update(scenario=scenario, root=ROOTS[SCENARIOS.index(scenario)], mutate=mutate, hits={})
    result, native, _ = exercise(cls, case, root=ctx['root'],
                                 controlled=scenario in (SCENARIOS[5], SCENARIOS[6]))
    assert result['error'] is None, (scenario, case, cls.__name__, result['error'])
    if mutate:
        assert ctx['hits'], (scenario, case)
        if scenario == SCENARIOS[0]:
            values = [row[3] for row in result['log'] if row[0] == 'w' and row[4] == ((0x214b+0x823)*16+0x2d)]
            assert values == [0x1717]*4
            assert result['regs']['eflags'] & 0x400 == 0
        elif scenario == SCENARIOS[1]:
            assert set(ctx['hits']) == {'own-store-before-pending-flush', 'pending-push-overwrites-own-store'}
        elif scenario == SCENARIOS[3]:
            assert result['regs']['eax'] & 255 == 0
        elif scenario == SCENARIOS[4]:
            values = {row[4]:row[3] for row in result['log'] if row[0] == 'w'}
            assert values[(0x791+0x823)*16+0x1ddb] == 1
            assert values[(0x791+0x823)*16+0x1e01] == 0xbeef
        elif scenario == SCENARIOS[5]:
            assert result['calls'].get('0791:1829') == 1
        elif scenario == SCENARIOS[6]:
            packets = [row[2] for row in result['log'] if row[0] == 'abi' and row[1] == '214B:02C8']
            assert len(packets) == 1 and packets[0][3] & 255 == 5 and packets[0][4] == ctx['line']
        elif scenario == SCENARIOS[7]:
            assert result['calls'].get('214B:02C8') == 1
    return result, dict(ctx['hits'])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    parser.add_argument('--development', action='store_true')
    a = parser.parse_args()
    e.verify()
    assert not Path(a.out).exists()
    import goal2rust_engine
    files = sorted((e.BASE/'engine/src').glob('*.rs'))+[Path(__file__), e.BASE/'engine/tests/test_commentary.py']
    files += sorted(Path(goal2rust_engine.__file__).parent.glob('*.so'))
    sha = lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    before = {str(p.relative_to(e.BASE)):sha(p) for p in files} if a.development else e.hashes()
    archive_map = {}
    if a.development:
        archive = e.BASE/'.cache/T26-development-sources'
        for p in files:
            saved = archive/sha(p)
            if not saved.exists():
                with saved.open('xb') as stream:stream.write(p.read_bytes())
            archive_map[str(p.relative_to(e.BASE))] = str(saved.relative_to(e.BASE))
    start = time.monotonic()
    rows = {}
    for cls in (Oracle, PortMachine):
        cls.at, cls.on_write = at, on_write
    try:
        for scenario in SCENARIOS:
            row = rows[scenario] = dict(comparisons=0, effect_witnesses=0, hits={})
            for case in range(160):
                p, ph = run(Oracle, case, scenario, True)
                r, rh = run(PortMachine, case, scenario, True)
                assert p == r and ph == rh, (scenario, case, [k for k in p if p[k] != r[k]])
                base, _ = run(Oracle, case, scenario, False)
                row['comparisons'] += 1
                row['effect_witnesses'] += any(p[key] != base[key] for key in ['memory', 'regs', 'calls'])
                for key, value in ph.items():row['hits'][key] = row['hits'].get(key, 0)+value
            assert row['effect_witnesses'] > 0 and all(row['hits'].values())
            print(scenario, row, flush=True)
    finally:
        for cls in (Oracle, PortMachine):cls.at, cls.on_write = OLD_AT[cls], OLD_WRITE[cls]
    report = dict(pass_all=True, comparisons=1280, scenarios=rows, pid=os.getpid(), pgid=os.getpgrp(),
                  script_sha256=sha(Path(__file__)), wall_s=time.monotonic()-start)
    if a.development:
        assert before == {str(p.relative_to(e.BASE)):sha(p) for p in files}
        report.update(development_only=True, accepted_canonical_evidence=False,
                      executed_source_sha256=before, preserved_source_map=archive_map)
        with Path(a.out).open('x') as stream:json.dump(report, stream, indent=2, sort_keys=True)
    else:
        e.write(a.out, report, before)


if __name__ == '__main__':main()
