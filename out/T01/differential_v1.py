"""T01: each Rust routine against its Python port from the same machine state, many times, in-process.

    PYTHONHASHSEED=0 PYTHONPATH=runtime:<goal2rust>/.venv/lib/python3.12/site-packages \
        python3.12 -B <goal2rust>/out/T01/differential_v1.py --root <clone> --trials N --out <new json>

The machine is E034-03's drive (as drive_receipt_v1.py) stopped after its first 60 events. Each trial restores that
state, randomises the routine's inputs (its argument words, SP down to a 16-bit wrap, the registers and flags, the DS
bytes and the record it reads), then runs the Python port function and the Rust function each from the identical
state, both through `fn(mem, None)` inside a port entry (mem._entries), in four modes: io_tap off/on x a kit write
listener over the stack page off/on. Compared: full memory, every register, the ordered io_tap and listener calls,
and the exception (type and message) if any. Diagnostic only; the receipts are the acceptance."""
import argparse, hashlib, importlib.util, json, random, sys, time
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--root", type=Path, required=True)
ap.add_argument("--trials", type=int, default=500)
ap.add_argument("--seed", type=int, default=1)
ap.add_argument("--mutant", type=int, default=0)
ap.add_argument("--out", type=Path, required=True)
a = ap.parse_args()
out = a.out.open("x")
ROOT = a.root.resolve()
sys.path[:0] = [str(ROOT), str(ROOT / "runtime")]
from original_match import Image, Match, Fixture  # noqa: E402
from original_match.assets import reference_image  # noqa: E402
import goal2rust_engine as engine  # noqa: E402

engine.set_mutant(a.mutant)
m = Match(Image.from_savestate(reference_image(ROOT / ".cache/dl")), Fixture(7, 19, index=9, kind=200), managed=7,
          substitutions=None, engine="port", record_draws=True)
m.timeout_s = 10 ** 6
for i, ev in enumerate(m.events()):
    if ev.kind == "decision":
        m.answer(quick=True) if ev.data["context"] == "half_time" else m.answer()
    if i >= 60:
        break
M, mem = m.m, m.ports.mem
assert type(M).__name__ == "PortMachine"
python_fn = {}
for reg, variant in m.ports.loaded:
    for address, entry in reg.entries.items():
        python_fn[address] = (entry, variant)
DS = mem.DS
SNAP_MEM, SNAP_REGS = bytes(M._memory), dict(M._registers)
SNAP_W = (list(M._writes), M._writes_now, M._writes_span)


class Log:
    def __init__(self):
        self.calls = []

    def io(self, kind, x, y):
        self.calls.append(("io", kind, x, bytes(y) if isinstance(y, (bytes, bytearray)) else y))

    def listen_enter(self, index, address, size, value):
        self.calls.append(("le", index, address, size, value))
        return len(self.calls)

    def listen_leave(self, token):
        self.calls.append(("ll", token))

    def site_enter(self, *x):
        self.calls.append(("se",) + x)

    def site_leave(self, *x):
        self.calls.append(("sl",) + x)


def restore():
    M._memory[:] = SNAP_MEM
    M._registers.clear(); M._registers.update(SNAP_REGS)
    M._writes[:] = SNAP_W[0]; M._writes_now, M._writes_span = SNAP_W[1], SNAP_W[2]
    M.io_tap = M.listen_tap = M.site_tap = None


def nargs(entry):
    return {"0791:045D": 1, "0791:26D7": 3}.get(entry.address, 2)


def make_state(rng, address, far):
    """The trial's inputs, as a list of (linear, bytes) and register values, and the entry SP."""
    pokes = []
    slot = rng.choice([rng.randrange(0, 24), rng.randrange(1, 23), rng.randrange(1, 23)])
    off = (0x80E8 + 0x16 * slot) & 0xFFFF if rng.random() < 0.9 else rng.randrange(0, 0x10000)
    seg = DS if rng.random() < 0.9 else rng.randrange(0, 0x10000)
    rec = bytes(rng.randrange(256) for _ in range(0x16))
    if rng.random() < 0.5:
        rec = rec[:6] + bytes([rng.choice([0, 1, 5, 0xB, 0xC, 0xD, 0x16, 0x17])]) + rec[7:]
    if rng.random() < 0.7:          # a real player index at +0xD
        rec = rec[:0xD] + rng.randrange(0, 40).to_bytes(2, "little") + rec[0xF:]
    pokes.append((seg * 16 + off, rec))
    for o, n in ((0x830B, 1), (0x8319, 1), (0x831B, 2), (0x8302, 1), (0x82F6, 2), (0x80FC, 1)):
        if rng.random() < 0.6:
            v = rng.randrange(1 << (8 * n)) if rng.random() < 0.5 else rng.choice([0, 1, 0xB, 0xC, 0xD, 0xFF])
            pokes.append((DS * 16 + o, v.to_bytes(n, "little")))
    if rng.random() < 0.3:          # the ball word equal to the record's position (2CEC's true case)
        pokes.append((DS * 16 + 0x82F6, rec[0:2]))
    n = nargs(python_fn[address][0])
    if address == "0791:045D":
        words = [rng.choice([0, 1, 12, 13, 0x101, 0xFFFF, rng.randrange(0x10000)])]
    elif address == "0791:26D7":
        words = [off, seg, rng.choice([1, 2, 3, 4, 5, 6, 8, rng.randrange(0, 17), rng.randrange(0x10000)])]
    else:
        words = [off, seg]
    sp = rng.choice([rng.randrange(0x100, 0xFF00) & ~1, rng.randrange(0, 0x30) & ~1, SNAP_REGS["esp"] & 0xFFFF])
    regs = {r: rng.randrange(0x10000) for r in ("eax", "ebx", "ecx", "edx", "esi", "edi", "ebp", "es")}
    regs["eflags"] = rng.randrange(0x10000) | 2
    regs["esp"] = sp
    return pokes, words, sp, regs


def run(fn, state, tapped, listener):
    restore()
    pokes, words, sp, regs, entry_far = state
    for lin, data in pokes:
        M._memory[lin:lin + len(data)] = data
    M._registers.update(regs)
    ss = M._registers["ss"] & 0xFFFF

    base = sp + (4 if entry_far else 2)
    for i, w in enumerate(words):
        lin = ss * 16 + ((base + 2 * i) & 0xFFFF)
        M._memory[lin:lin + 2] = w.to_bytes(2, "little")
    log = Log()
    if listener:
        page = ss * 16 + ((sp - 0x40) & 0xFFFF)
        M.on_write(max(0, page - 0x40), page + 0x80, lambda ad, sz, v: log.calls.append(("w", ad, sz, v, M.pc())))
    if tapped:
        M.io_tap, M.listen_tap = log.io, log
    mem._entries.append((sp, entry_far))
    error = None
    try:
        value = fn(mem, None)
    except Exception as e:      # noqa: BLE001 - compared, not hidden
        value, error = None, f"{type(e).__name__}: {e}"
    finally:
        mem._entries.pop()
        M.io_tap = M.listen_tap = None
    return dict(value=value, error=error, memory=hashlib.sha256(M._memory).hexdigest(), regs=dict(M._registers),
                calls=log.calls)


rng = random.Random(a.seed)
report = dict(root=str(ROOT), trials=a.trials, seed=a.seed, mutant=a.mutant, routines={})
t0 = time.time()
for address, rust in sorted(engine.PORTS.items()):
    entry, variant = python_fn[address]
    assert variant is None and entry.fn is not rust, address
    far = entry.far
    stats = dict(trials=0, equal=0, errors_both=0, differences=[])
    for t in range(a.trials):
        state = make_state(rng, address, far) + (far,)
        for tapped in (False, True):
            for listener in (False, True):
                p = run(entry.fn, state, tapped, listener)
                r = run(rust, state, tapped, listener)
                stats["trials"] += 1
                if p == r:
                    stats["equal"] += 1
                    stats["errors_both"] += p["error"] is not None
                elif len(stats["differences"]) < 5:
                    diff = {k: (repr(p[k])[:300], repr(r[k])[:300]) for k in p if p[k] != r[k]}
                    stats["differences"].append(dict(trial=t, tapped=tapped, listener=listener, diff=diff))
    report["routines"][address] = stats
    print(address, stats["equal"], "/", stats["trials"], "errors(both)", stats["errors_both"], flush=True)
restore()
report["seconds"] = time.time() - t0
report["all_equal"] = all(s["equal"] == s["trials"] for s in report["routines"].values())
json.dump(report, out, indent=1, default=repr); out.close()
print("all equal:", report["all_equal"])
