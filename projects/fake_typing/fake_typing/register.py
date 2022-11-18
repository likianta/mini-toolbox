from inspect import currentframe

from .fake import FakeTyping


def register_fake_typing(name='T'):
    last_frame = currentframe().f_back
    last_frame.f_globals[name] = FakeTyping()
