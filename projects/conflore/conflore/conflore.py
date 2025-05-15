import atexit
import typing as t
from os.path import exists

from .io import dumps
from .io import loads


class Conflore:
    _data: dict
    _file: str
    _on_save_callbacks: t.List[t.Callable[[], t.Any]]
    _on_save_callbacks_kv: t.Dict[str, t.Callable[[], t.Any]]
    
    def __init__(
        self,
        file: str,
        default: dict = None,
        *,
        auto_save: bool = False,
        version: int = 0,
    ) -> None:
        """
        params:
            file: json, yaml, or pickle file.
            version: if number is different with the one in the file, file will
                be dropped.
        """
        self._on_save_callbacks = []
        self._file = file
        self._on_save_callbacks_kv = {}
        
        if exists(file):
            self._data = loads(file)
            if version:
                v0, v1 = self._data.get('__conflore_version__', 0), version
                if v1 != v0:
                    print(
                        'auto drop last config file "{}": {} -> {}'
                        .format(file, v0, v1), ':r2p'
                    )
                    self._data = {'__conflore_version__': v1, **(default or {})}
        else:
            self._data = {'__conflore_version__': version, **(default or {})}
        
        if auto_save:
            atexit.register(self.save)
    
    def __getitem__(self, item) -> t.Any:
        return self._data[item]
    
    def __iter__(self) -> t.Iterator:
        yield from self._data.items()
    
    @property
    def data(self) -> dict:
        return self._data
    
    def bind(self, key: str, *args) -> None:
        """
        args:
            key: a dot-separated string.
            *args: assert len(args) in (1, 2)
                if len(args) == 1:
                    callback: a callable that takes no argument.
                if len(args) == 2:
                    object, str attr
        """
        assert len(args) in (1, 2)
        if len(args) == 1:
            self._on_save_callbacks_kv[key] = args[0]
        else:
            obj, attr = args
            self._on_save_callbacks_kv[key] = lambda: getattr(obj, attr)
    
    def on_save(self, func: t.Callable[[], t.Any]) -> None:
        self._on_save_callbacks.append(func)
    
    def save(self, file: str = None) -> None:
        self._auto_save()
        dumps(self._data, file or self._file)
    
    def _auto_save(self) -> None:
        def get_node() -> t.Tuple[t.Optional[dict], str]:
            # return: tuple[node, last_key]
            if '.' not in key_chain:
                key = key_chain
                return self._data, key
            
            node = self._data
            keys = key_chain.split('.')
            for key in keys[:-1]:
                node = node[key]
            return node, keys[-1]
        
        for key_chain, callback in self._on_save_callbacks_kv.items():
            node, key = get_node()
            node[key] = callback()
        
        for callback in self._on_save_callbacks:
            try:
                callback()
            except Exception as e:
                print(':lv4', e)
