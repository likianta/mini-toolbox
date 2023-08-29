"""
watchdog ref: https://dev.to/stokry/monitor-files-for-changes-with-python-1npj
"""
import os.path
import typing as t
from time import sleep

from lk_utils import fs
from lk_utils import new_thread
from pysignal import Signal
from watchdog.events import FileModifiedEvent
from watchdog.events import FileSystemEventHandler

# https://github.com/gorakhargosh/watchdog/issues/93#issuecomment-547677667
# # from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver as Observer


class T:
    Checker = t.Callable[[str, bool], bool]
    #   Callable[[path, is_dir], is_target]
    Call = t.Union[
        t.Callable[[], t.Any],
        t.Callable[[str], t.Any],
        t.Callable[[str, str], t.Any],
    ]
    
    Dirpath = str
    #   patterns:
    #       'aaa/bbb': only this dir
    #       'aaa/bbb/*': same as above
    #       'aaa/bbb/*0': same as above (seldomly used)
    #       'aaa/bbb/*1': this dir and its direct children dirs
    #       'aaa/bbb/*2': this dir and its direct children and grandchildren
    #       'aaa/bbb/*3': ...
    #       'aaa/bbb/*4': ...
    #       'aaa/bbb/*5': ...
    #       'aaa/bbb/**': this dir and all its descandants
    Entrances = t.Iterable[Dirpath]
    
    Rule = t.TypedDict(
        'Rule',
        {
            'paths': t.Union[t.Iterable[str], Checker],
            'call' : Call,  # noqa
        },
    )


def watch_file_changes(
    *rules: T.Rule,
    entrances: T.Entrances = None,
    exclude_dot_dirs: bool = True,
) -> None:
    if entrances is None:
        entrances = ((os.getcwd(), False),)
    else:
        entrances = _collect_dirs(entrances, exclude_dot_dirs)
    
    observer = Observer()
    handler = FilesListener(*rules)
    
    for entrance, recursive in entrances:
        print(':i2sp', 'add to watch', entrance + (recursive and '/*' or ''))
        observer.schedule(handler, entrance, recursive=recursive)
    
    _start_polling(observer)


def _collect_dirs(
    entrances: T.Entrances,
    exclude_dot_dirs: bool = True,
) -> t.Iterator[t.Tuple[str, bool]]:  # ((path, recursive), ...)
    def recurse(node: str, level: int, max_depth: int) -> t.Iterator[str]:
        if level > max_depth: return
        for d in fs.find_dirs(node):
            if exclude_dot_dirs and d.name.startswith('.'):
                continue
            yield d.path
            yield from recurse(d.path, level + 1, max_depth)
    
    for root in entrances:
        if root.endswith('/**'):
            yield root.rstrip('/*'), True
        elif root.rstrip('0123456789').endswith('/*'):
            if root.endswith(('/*', '/*0')):
                yield root.rstrip('/*0'), False
                return
            root, max_depth = root.rsplit('*', 1)
            max_depth = int(max_depth)  # 1, 2, 3, ...
            yield root, False
            yield from (
                (x, False) for x in recurse(root, level=1, max_depth=max_depth)
            )
        else:
            yield root, False


class FilesListener(FileSystemEventHandler):
    def __init__(self, *rules: T.Rule) -> None:
        super().__init__()
        
        self._file_2_call = {}
        self._dir_2_call = {}
        self._checkers = []
        
        for rule in rules:
            if isinstance(rule['paths'], t.Callable):
                self._checkers.append(
                    _CheckAndCall(rule['paths'], rule['call'])
                )
            else:
                for path in rule['paths']:
                    call = Signal()
                    call.bind(rule['call'])
                    if os.path.isfile(path):
                        self._file_2_call[fs.abspath(path)] = call
                    elif os.path.isdir(path):
                        self._dir_2_call[fs.abspath(path) + '/'] = call
                    else:  # not exist or symlink
                        raise Exception(f'invalid path: {path}')
        
        self._dirs = set(self._dir_2_call.keys())
        self._files = set(self._file_2_call.keys())
    
    def on_modified(self, event: FileModifiedEvent) -> None:
        # print(event.src_path, event.key, event.event_type, event.is_directory)
        if event.src_path.endswith('~'):
            # e.g. '/path/to/file.py~'
            return
        src_path = fs.normpath(event.src_path)
        print(src_path, os.path.getmtime(src_path), ':v')
        if event.is_directory:
            for d in self._dirs:
                if src_path.startswith(d):
                    self._dir_2_call[d].emit(d.rstrip('/'), src_path)
                    break
        else:
            if src_path in self._files:
                self._file_2_call[src_path].emit(src_path)
        for checker in self._checkers:
            checker(src_path, event.is_directory)


class _CheckAndCall:
    def __init__(self, checker: T.Checker, call: T.Call):
        self._checker = checker
        self._call = call
    
    def __call__(self, path: str, is_dir: bool) -> None:
        if self._checker(path, is_dir):
            self._call(path)


@new_thread()
def _start_polling(observer: Observer) -> None:
    print('start file watcher. you can press `ctrl + c` to stop it.', ':p2')
    observer.start()
    try:
        while True:
            sleep(0.5)
    except KeyboardInterrupt:
        observer.stop()
        print('watchdog stopped')
    finally:
        observer.join()
