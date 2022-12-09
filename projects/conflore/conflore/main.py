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
        need_init = default and not os.path.exists(file)
        super().__init__(file)
        if need_init:
            self.update(default)
    
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
