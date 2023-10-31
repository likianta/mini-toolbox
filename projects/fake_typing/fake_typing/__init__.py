"""
usage:
    from fake_typing import register_fake_typing
    if register_fake_type:
        register_fake_type('T')
    else:
        # here you can use relative imports without circular import errors.
        from ..xxx import yyy
        class T:
            ...
"""
from .const import TRUTH_CASE
from .fake import FakeType
from .register import register_fake_type

__version__ = '0.1.1'
