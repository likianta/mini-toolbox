import typing as t

from ..util import get_center_pos


class BaseApplication:
    url: str
    _pos: t.Tuple[int, int]
    _size: t.Tuple[int, int]
    
    def __init__(
        self,
        title: str,
        url: str,
        size: t.Tuple[int, int] = (800, 600),
        pos: t.Optional[t.Tuple[int, int]] = None,
        **_
    ) -> None:
        """
        kwargs:
            icon: str = None
            ...
        """
        self.title = title
        self.url = url
        self._pos = pos or get_center_pos(size)
        self._size = size
        
    def start(self) -> None:
        raise NotImplementedError
