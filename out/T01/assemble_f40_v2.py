"""T01: the 40-match F40 candidate family-F40-rust-v2.jsonl, assembled byte for byte from two runs of the same
family.py command with the Rust routines (hook clone ce1d0256): the 37 completed records of family-F40-rust-v1.jsonl
and the 3 reruns (family-F40-rust-v1-rerun.jsonl) of the matches v1 recorded as over the 300 s wall-time limit under
foreign load. No line is changed; the output is a new file."""
import json
RERUN = "family-F40-rust-v1-rerun.jsonl"
v1 = open("family-F40-rust-v1.jsonl").read().splitlines()
rr = open(RERUN).read().splitlines()
rerun_ids = {json.loads(l)["id"] for l in rr}
kept = [l for l in v1 if json.loads(l)["id"] not in rerun_ids]
assert len(kept) == 37 and len(rr) == 3 and rerun_ids == {"F40/edit-b4d2", "F40/edit-d00d", "F40/edit-face"}
with open("family-F40-rust-v2.jsonl", "x") as f:
    f.write("\n".join(kept + rr) + "\n")
print(len(kept) + len(rr), "records")
