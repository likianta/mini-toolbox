from typing import Any


class FakeTyping:
    def __getattr__(self, item):
        return Any
    
    # def __getitem__(self, item):
    #     return self
