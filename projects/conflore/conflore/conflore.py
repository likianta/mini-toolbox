import atexit
import typing as t
from os.path import exists

from .load_and_dump import dumps
from .load_and_dump import loads


class Conflore:
    _data: dict
    _file: str
    _on_save_callbacks: t.List[t.Callable[[], t.Any]]
    _on_save_callbacks_kv: t.Dict[str, t.Callable[[], t.Any]]
    
    def __init__(
            self,
            file: str,
            default: dict = None,
            auto_save=False,
            **kwargs
    ):
        """
        args:
            file: json, yaml, or pickle file.
        kwargs:
            version_number (int): if number is newer than the one in the file,
                the file will be dropped.
        """
        self._on_save_callbacks = []
        self._data = loads(file) if exists(file) else {}
        self._file = file
        self._on_save_callbacks_kv = {}
        
        if exists(file):
            if v1 := kwargs.get('version_number'):
                v0 = self._data.get('__conflore_version__', 0)
                if v1 > v0:
                    print(':p', f'auto drop config file "{file}" ({v1} > {v0})')
                    self._data = {'__conflore_version__': v1, **(default or {})}
                # else: do nothing
            # else: do nothing
        else:
            self._data['__conflore_version__'] = kwargs.get('version_number', 0)
            if default: self._data.update(default)
        
        if auto_save:
            atexit.register(self.save)
    
    def __getitem__(self, item):
        return self._data[item]
    
    def __iter__(self):
        yield from self._data.items()
    
    @property
    def data(self) -> dict:
        return self._data
    
    def bind(self, key: str, *args):
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
