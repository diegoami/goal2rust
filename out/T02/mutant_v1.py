"""Positive control: corrupt a pushed guest-call return IP in the Rust machine.

Run one full-memory/tap machine differential; keep counts/hashes and the error,
never raw guest memory. Nonzero if the mutation escapes the differential.
"""
import hashlib
import json
import os
import sys
from pathlib import Path

G2R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(G2R/'engine/tests'),str(G2R/'engine/python'),str(G2R/'.cache/goal2-archaeology/runtime')]
from test_machine import MachineTests, Oracle, PortMachine

out=Path(sys.argv[1]).open('x')
test=MachineTests()
os.environ['GOAL2RUST_MACHINE_MUTANT']='0'
expected=test.run_case(Oracle,sp=0,tapped=True,stop=True)
os.environ['GOAL2RUST_MACHINE_MUTANT']='1'
try:
    actual=test.run_case(PortMachine,sp=0,tapped=True,stop=True)
except Exception as e:
    caught=True
    error=f'{type(e).__name__}: {e}'
else:
    caught=actual!=expected
    error=None
report=dict(mutant='guest-call saved return IP incremented by one',caught=caught,
            check='synthetic full-frame machine differential (near/far returns, memory, registers, ordered taps)',
            error=error, oracle_memory_sha256=hashlib.sha256(expected[0]['memory']).hexdigest(),
            oracle_tap_calls=len(expected[1]),
            source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [G2R/'engine/src/machine.rs',Path(__file__).resolve()]})
json.dump(report,out,indent=2)
out.close()
print(json.dumps(report))
sys.exit(0 if caught else 1)
