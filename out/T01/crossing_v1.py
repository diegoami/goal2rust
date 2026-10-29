"""T01: the per-call cost of each translated routine in Python and in Rust, of the Python/Rust crossing alone, and of
the port machinery around every call (PortFrame: entry, return), in-process on E034-03's drive state after 60 events.

    PYTHONHASHSEED=0 PYTHONPATH=runtime:<goal2rust>/.venv/lib/python3.12/site-packages \
        python3.12 -B <goal2rust>/out/T01/crossing_v1.py --root <clone> --out <new json>

Untapped, as the cpu receipts run. Each figure is the best of --repeat timings of --n calls (ns per call)."""
import argparse, importlib.util, json, sys, time
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--root", type=Path, required=True)
ap.add_argument("--n", type=int, default=50000)
ap.add_argument("--repeat", type=int, default=5)
ap.add_argument("--out", type=Path, required=True)
a = ap.parse_args()
out = a.out.open("x")
ROOT = a.root.resolve()
sys.path[:0] = [str(ROOT), str(ROOT / "runtime")]
from original_match import Image, Match, Fixture  # noqa: E402
from original_match.assets import reference_image  # noqa: E402
from original_match.port.guest import PortFrame  # noqa: E402
import goal2rust_engine as engine  # noqa: E402

m = Match(Image.from_savestate(reference_image(ROOT / ".cache/dl")), Fixture(7, 19, index=9, kind=200), managed=7,
          substitutions=None, engine="port", record_draws=True)
m.timeout_s = 10 ** 6
for i, ev in enumerate(m.events()):
    if ev.kind == "decision":
        m.answer(quick=True) if ev.data["context"] == "half_time" else m.answer()
    if i >= 60:
        break
M, mem = m.m, m.ports.mem
entries = {}
for reg, variant in m.ports.loaded:
    for address, entry in reg.entries.items():
        entries[address] = entry
DS = mem.DS
SS = M._registers["ss"] & 0xFFFF
SP = 0x8000
REC = 0x80E8 + 0x16 * 5
ARGS = {"0791:045D": [12], "0791:26D7": [REC, DS, 3]}
SNAP_MEM, SNAP_REGS = bytes(M._memory), dict(M._registers)


def setup(entry):
    M._memory[:] = SNAP_MEM
    M._registers.clear(); M._registers.update(SNAP_REGS)
    M._registers["esp"] = SP
    words = ARGS.get(entry.address, [REC, DS])
    base = SP + (4 if entry.far else 2)
    for i, w in enumerate(words):
        lin = SS * 16 + base + 2 * i
        M._memory[lin:lin + 2] = w.to_bytes(2, "little")
    M._memory[SS * 16 + SP:SS * 16 + SP + 4] = (0x1234).to_bytes(2, "little") + (M.load + 0x791).to_bytes(2, "little")


def best(fn):
    times = []
    for _ in range(a.repeat):
        t = time.perf_counter_ns(); fn(); times.append(time.perf_counter_ns() - t)
    return min(times) / a.n


def bare(entry, fn):
    """fn(mem, None) inside a port entry, the registers put back each call (SP walks otherwise)."""
    setup(entry)
    regs, snap, n = M._registers, dict(M._registers), a.n
    mem._entries.append((SP, entry.far))

    def loop():
        for _ in range(n):
            fn(mem, None)
            regs.update(snap)
    try:
        return best(loop)
    finally:
        mem._entries.pop()


def framed(entry, fn):
    """The whole port call as the dispatcher makes it (PortFrame.start: _in_frame, fn, _finish's register writes and
    return_from), the registers put back each call."""
    setup(entry)
    import copy
    e = copy.copy(entry); e.fn = fn
    regs, snap, n = M._registers, dict(M._registers), a.n

    def loop():
        for _ in range(n):
            PortFrame(M, mem, e, None).start()
            regs.update(snap)
    return best(loop)


def restore_only():
    regs, snap, n = M._registers, dict(M._registers), a.n

    def loop():
        for _ in range(n):
            regs.update(snap)
    return best(loop)


report = dict(root=str(ROOT), n=a.n, repeat=a.repeat, unit="ns per call", routines={})
setup(entries["0791:2B51"])
report["restore_registers_ns"] = restore_only()
py_noop = lambda mem, variant: None  # noqa: E731
e0 = entries["0791:2B51"]
report["bare_python_noop_ns"] = bare(e0, py_noop)
report["bare_rust_noop_ns"] = bare(e0, engine.noop)
report["bare_rust_crossing_ns"] = bare(e0, engine.crossing)
report["framed_python_noop_ns"] = framed(e0, py_noop)
report["framed_rust_crossing_ns"] = framed(e0, engine.crossing)
for address, rust in sorted(engine.PORTS.items()):
    entry = entries[address]
    r = dict(bare_python_ns=bare(entry, entry.fn), bare_rust_ns=bare(entry, rust),
             framed_python_ns=framed(entry, entry.fn), framed_rust_ns=framed(entry, rust))
    rr = report["restore_registers_ns"]
    r["bare_speedup"] = (r["bare_python_ns"] - rr) / (r["bare_rust_ns"] - rr)
    r["framed_speedup"] = (r["framed_python_ns"] - rr) / (r["framed_rust_ns"] - rr)
    report["routines"][address] = r
    print(address, {k: round(v, 1) for k, v in r.items()}, flush=True)
json.dump(report, out, indent=1); out.close()
print({k: round(v, 1) for k, v in report.items() if k.endswith("_ns")})
