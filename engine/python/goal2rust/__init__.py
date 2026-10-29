"""goal2rust: a Rust machine behind goal2-archaeology's per-event Match API."""
from .machine import install
from original_match import Match as _KitMatch


class Match(_KitMatch):
    """The kit's advance/events, answer, save/load API over the Rust machine."""
    def __init__(self, *args, **kwargs):
        install()
        kwargs['engine'] = 'port'
        super().__init__(*args, **kwargs)

    @classmethod
    def load(cls, *args, **kwargs):
        install()
        return super().load(*args, **kwargs)

__all__ = ['Match', 'install']
