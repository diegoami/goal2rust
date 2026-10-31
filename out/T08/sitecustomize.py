"""Opt-in child-process backend attestation; never patches the pinned oracle."""
import os
if os.environ.get('GOAL2RUST_T08') == '1':
    import atexit
    import hashlib
    import json
    import sys
    import evidence as common
    common.verify()
    common.select('rust')
    from original_match import Match
    original_init, original_load = Match.__init__, Match.load.__func__
    identities = []
    finalizer = None
    reported = False

    def remember(match):
        global finalizer
        assert type(match.m).__module__ == 'goal2rust.machine'
        identities.append(match.m._core)
        if finalizer is None:
            from multiprocessing.util import Finalize
            finalizer = Finalize(None, receipt, exitpriority=0)

    def init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        remember(self)

    def load(cls, *args, **kwargs):
        match = original_load(cls, *args, **kwargs)
        remember(match)
        return match

    Match.__init__, Match.load = init, classmethod(load)

    def receipt():
        global reported
        if reported: return
        reported = True
        calls = {}
        fast_calls = {}
        for core in {id(core): core for core in identities}.values():
            for address, count in core.native_calls.items(): calls[address] = calls.get(address, 0) + count
        for core in {id(core): core for core in identities}.values():
            for name, count in getattr(core, 'bridge_fast_calls', {}).items(): fast_calls[name] = fast_calls.get(name, 0) + count
        folder = common.BASE / os.environ['GOAL2RUST_T08_ATTEST']
        folder.mkdir(parents=True, exist_ok=True)
        value = dict(pid=os.getpid(), argv=sys.argv, oracle=common.PIN,
                     machines=len({id(core) for core in identities}), backend='rust', native_calls=calls, bridge_fast_calls=fast_calls)
        with (folder / f'{os.getpid()}.json').open('x') as f: json.dump(value, f, indent=2)
    atexit.register(receipt)
