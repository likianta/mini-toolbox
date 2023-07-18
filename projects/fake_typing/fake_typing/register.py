from inspect import currentframe
from typing import Any

from .fake import FakeType


def register_fake_type(name='T') -> Any:
    last_frame = currentframe().f_back
    out = last_frame.f_globals[name] = FakeType()
    return out
