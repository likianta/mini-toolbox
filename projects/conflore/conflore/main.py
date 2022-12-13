import os
import typing as t

from hot_shelve import FlatShelve


class Conflore(FlatShelve):
    """ simple and good config management tool. """
    
    def __init__(self, path: str, default: dict = None):
        self._default = default or {}
        if os.path.exists(path):
            assert os.path.isdir(path)
        else:
            os.mkdir(path)
        file = f'{path}/__main__.db'
        need_init = default and not os.listdir(path)
        super().__init__(file)
        if need_init:
            self.update(default)
        self._before_close = set()
    
    def __getitem__(self, key: str):
        previous_key, current_key = self._rsplit_key(key)
        node, key_chain = self._locate_node(previous_key)
        return self._get_node(
            node,
            key_chain,
            current_key,
            default=self._get_default(key)
        )
    
    def _get_default(self, key: str) -> t.Union[t.Any, KeyError]:
        node = self._default
        for part in key.split('.'):
            if part in node:
                node = node[part]
            else:
                return KeyError
        return node
    
    def on_close(self, func: t.Callable) -> None:
        self._before_close.add(func)
    
    def close(self) -> None:
        for i, func in enumerate(self._before_close):
            try:
                func()
            except Exception as e:
                print(':v4', 'error in saving config on closed', i, func, e)
                continue
        self._before_close.clear()
        super().close()
