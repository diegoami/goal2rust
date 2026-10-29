"""Opt-in test-process selection; also loaded by family.py's spawned workers."""
import os
if os.environ.get('GOAL2RUST_MACHINE') == '1':
    from goal2rust import install
    install()
