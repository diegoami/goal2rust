"""T01: two drive receipts (drive_receipt_v1.py) compared on what Done-when 1 names: events, result, full memory and,
for taps receipts, the ordered tap hash and every tap count. Exit 0 when equal.

    python3 compare_receipts.py <before.json> <after.json>"""
import json, sys

a, b = (json.load(open(p)) for p in sys.argv[1:3])
keys = ["events", "events_sha256", "score", "draws", "result_sha256", "memory_sha256", "stretches"]
if a["mode"] == "taps" or b["mode"] == "taps":
    keys.append("taps")
bad = [k for k in keys if a.get(k) != b.get(k)]
for k in keys:
    print(f"{'EQUAL' if k not in bad else 'DIFF '} {k}: {json.dumps(a.get(k))[:90]}" + ("" if k not in bad else f" vs {json.dumps(b.get(k))[:90]}"))
print(f"cpu {a['drive_cpu_s']:.1f} s -> {b['drive_cpu_s']:.1f} s ({a['drive_cpu_s'] / b['drive_cpu_s']:.3f}x); "
      f"heads {a['head'][:8]} -> {b['head'][:8]}")
sys.exit(1 if bad else 0)
