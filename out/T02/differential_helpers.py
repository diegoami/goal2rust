"""T01 random-state generator and ordered log, retained verbatim for T02."""
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
