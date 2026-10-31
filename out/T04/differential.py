"""Full native-tree frames from real sealed inputs and authored random/edge states.

Only digests/counts of private captured inputs and outputs are emitted.
"""
import argparse
import hashlib
import json
import random
import sys
import time
import evidence as e


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--mutant', type=int, default=0)
    a = ap.parse_args()
    assert not e.Path(a.out).exists()
    e.verify()
    before = e.hashes()
    e.deny_original()
    from original_match import Match, Fixture
    from original_match.port.engine import PortMachine as Oracle
    from original_match.port.guest import PortFrame
    from goal2rust.machine import PortMachine, BridgeRunner
    sys.path.insert(0, str(e.BASE / 'engine/tests'))
    from test_native_subtree import exercise, ENTRIES
    m = Match(e.image(), Fixture(7, 19, index=9, kind=200), managed=7,
              substitutions=None, engine='port', record_draws=True)
    captures = {ad: [] for ad in ENTRIES}
    originals = {ad: entry.fn for ad, entry in ENTRIES.items()}
    for ad, entry in ENTRIES.items():
        def capture(mem, variant, ad=ad):
            if len(captures[ad]) < 8:
                captures[ad].append((bytes(mem.m._memory), dict(mem.m._registers), mem._entries[-1]))
            return originals[ad](mem, variant)
        entry.fn = capture
    for i, ev in enumerate(m.events()):
        if ev.kind == 'decision':
            m.answer(quick=True) if ev.data['context'] == 'half_time' else m.answer()
        if i >= 60: break
    for ad, entry in ENTRIES.items(): entry.fn = originals[ad]

    def real(cls, root, snap, tapped, listener, pause):
        memory, regs, entry_state = snap
        machine = cls(memory, m.m.load, mutant=a.mutant) if cls is PortMachine else cls(memory, m.m.load)
        machine._registers.clear(); machine._registers.update(regs)
        mem, calls, log = machine.port_memory(), {}, []
        for ad, entry in ENTRIES.items():
            if cls is Oracle:
                def runner(machine, entry=entry):
                    calls[entry.address] = calls.get(entry.address, 0) + 1
                    PortFrame(machine, mem, entry, None).start()
            else: runner = BridgeRunner(entry, None, mem, calls)
            machine.port(ad, runner)
        if tapped: machine.io_tap = lambda *v: log.append(('io', v))
        if listener:
            machine.on_write(0, 0x10ffff, lambda *v: log.append(('w', v, machine.pc())))
        visits = []
        for site in ENTRIES.keys() | {'0791:2968'}:
            def handler(replay, site=site):
                visits.append((site, replay))
                if pause == site and len([x for x in visits if x[0] == site]) == 1: machine.stop('pause')
            machine.at(site, handler)
        sp, _ = entry_state
        ss = regs['ss'] & 65535
        ret_ip = int.from_bytes(memory[ss * 16 + sp:ss * 16 + sp + 2], 'little')
        cs_off = (sp + 2) & 65535
        ret_cs = int.from_bytes(memory[ss * 16 + cs_off:ss * 16 + cs_off + 2], 'little')
        error, suspended = None, []
        try:
            reason = machine.run(ret_cs * 16 + ret_ip, fresh=True)
            if reason == 'pause':
                suspended = [(f.entry.address, f.sp, f.bp, f.ret_lin, f.expect_sp) for f in machine.frames]
                machine.run(ret_cs * 16 + ret_ip)
        except Exception as exc: error = type(exc).__name__, str(exc)
        machine.io_tap = None
        return dict(memory=hashlib.sha256(machine._memory).hexdigest(), regs=dict(machine._registers),
                    calls=calls, log=e.digest(log), visits=visits, error=error,
                    suspended=suspended, entries=list(mem._entries))

    counts, differences = {}, []
    def compare(kind, left, right):
        row = counts.setdefault(kind, dict(total=0, equal=0))
        row['total'] += 1; row['equal'] += left == right
        if left != right and len(differences) < 10:
            differences.append(dict(kind=kind, python=e.digest(left), rust=e.digest(right)))
    for root, snaps in captures.items():
        assert len(snaps) == 8, (root, len(snaps))
        for snap in snaps:
            for tapped in (False, True):
                for listener in (False, True):
                    for pause in (None, '1771:3216', '0791:2968'):
                        compare('real:' + root, real(Oracle, root, snap, tapped, listener, pause),
                                real(PortMachine, root, snap, tapped, listener, pause))
    for case in range(500):
        for root in ENTRIES:
            for tapped in (False, True):
                opts = dict(root=root, tapped=tapped, pause=[None, '1771:3216', '0791:2968'][case % 3])
                compare('random-edge:' + root, exercise(Oracle, case, **opts)[0],
                        exercise(PortMachine, case, mutant=a.mutant, **opts)[0])
    report = dict(mutant=a.mutant, captures={ad: len(v) for ad, v in captures.items()},
                  comparisons=counts, differences=differences,
                  all_equal=all(v['total'] == v['equal'] for v in counts.values()))
    e.write(a.out, report, before)
    print(json.dumps(report), flush=True)
    assert report['all_equal'] == (a.mutant == 0)


if __name__ == '__main__': main()
