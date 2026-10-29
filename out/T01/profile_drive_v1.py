"""T01 M2 profile producer: E034-03's straight drive (as drive_receipt_v1.py: Fixture(7,19,index=9,kind=200),
quick answer at half time) on the plain port under cProfile, at the clone given by --root.

    PYTHONHASHSEED=0 python3.12 -B profile_drive_v1.py --root <clone> --out <new .prof> [--summary <new .txt>]

The between-events guard is lifted (cProfile's own cost must not trip it). Diagnostic only: no game byte is
written; the .prof holds function names and timings only."""
import argparse, builtins, cProfile, importlib.util, io, pstats, sys
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--root", type=Path, required=True)
ap.add_argument("--out", type=Path, required=True)
ap.add_argument("--summary", type=Path)
a = ap.parse_args()
ROOT = a.root.resolve()
open(a.out, "x").close()
sys.path[:0] = [str(ROOT), str(ROOT / "runtime")]
from original_match import Image, Match, Fixture  # noqa: E402
from original_match.assets import reference_image  # noqa: E402
spec = importlib.util.spec_from_file_location("boundaries", ROOT / "experiments/E033-original-match-kit/save_boundaries.py")
harness = importlib.util.module_from_spec(spec); spec.loader.exec_module(harness)
m = Match(Image.from_savestate(reference_image(ROOT / ".cache/dl")), Fixture(7, 19, index=9, kind=200), managed=7,
          substitutions=None, engine="port", record_draws=True)
m.timeout_s = 10 ** 6


def policy(match, data):
    match.answer(quick=True) if data["context"] == "half_time" else match.answer()


prof = cProfile.Profile()
prof.enable()
events = harness.drive(m, policy, ())
prof.disable()
prof.dump_stats(str(a.out))
s = io.StringIO()
st = pstats.Stats(prof, stream=s); st.sort_stats("tottime").print_stats(60)
st.sort_stats("cumulative").print_stats(80)
print(len(events), "events", m.result().get("score"), file=s)
calls = m.ports.calls
print("port calls, top 40:", file=s)
for addr, n in sorted(calls.items(), key=lambda kv: -kv[1])[:40]:
    print(f"  {addr} {n}", file=s)
if a.summary:
    with open(a.summary, "x") as f:
        f.write(s.getvalue())
else:
    print(s.getvalue())
