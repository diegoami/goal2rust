"""T01 Done-when 2: a drive receipt (drive_receipt_v1.py's JSON, which hashes the clone's Python sources) with the
goal2rust side added: this repository's commit, the sha256 of every crate and binding source, the built extension's
sha256, and the run's environment (overrides on or off). Written to a new file.

    python3 compose_receipt_v1.py <raw receipt> <new out> --clone <clone> [--rust]"""
import argparse, hashlib, json, os, platform, subprocess
from pathlib import Path

G2R = Path(__file__).resolve().parents[2]
ap = argparse.ArgumentParser()
ap.add_argument("raw", type=Path)
ap.add_argument("out", type=Path)
ap.add_argument("--clone", type=Path, required=True)
ap.add_argument("--rust", action="store_true")
ap.add_argument("--site", type=Path, default=G2R / ".venv/lib/python3.12/site-packages", help="where the crate's build is installed")
a = ap.parse_args()
receipt = json.loads(a.raw.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()  # noqa: E731
sources = sorted(list((G2R / "engine/src").rglob("*.rs")) + [G2R / "engine/Cargo.toml", G2R / "engine/Cargo.lock",
                 G2R / "engine/pyproject.toml", G2R / "bindings/goal2rust_overrides.py"])
so = sorted((a.site / "goal2rust_engine").glob("*.so"))
git = lambda *c, cwd=G2R: subprocess.run(["git", *c], cwd=cwd, capture_output=True, text=True).stdout.strip()  # noqa: E731
receipt["goal2rust"] = dict(
    rust_routines_on=a.rust, head=git("rev-parse", "HEAD"), dirty=bool(git("status", "--porcelain", "engine", "bindings")),
    clone=str(a.clone), clone_head=git("rev-parse", "HEAD", cwd=a.clone),
    source_sha256={str(p.relative_to(G2R)): sha(p) for p in sources},
    extension_sha256={p.name: sha(p) for p in so},
    overrides=os.environ.get("GOAL2_PORT_OVERRIDES") if a.rust else None,
    machine=dict(node=platform.node(), cpus=os.cpu_count(), load_at_compose=os.getloadavg()))
with a.out.open("x") as f:
    json.dump(receipt, f, indent=2)
print(a.out, receipt["drive_cpu_s"])
