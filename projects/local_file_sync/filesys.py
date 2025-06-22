import ftplib
import hashlib
import io
import json
import os
import re
import typing as t
from datetime import datetime
from lk_utils import fs
from time import time


class T:
    Path = str
    Time = int
    SnapshotData = t.Dict[Path, Time]  # {relpath: modified_time, ...}
    SnapshotItem = t.TypedDict('SnapshotItem', {
        'version': str,  # `<hash>-<time>`
        'data'   : SnapshotData,
    })
    SnapshotFull = t.TypedDict('SnapshotFull', {
        'base'   : SnapshotItem,
        'current': SnapshotItem,
    })


class BaseFileSystem:
    def __init__(self, root: T.Path) -> None:
        self.root = root
        self.snapshot_file = f'{root}/snapshot.json'
    
    def load_snapshot(self) -> T.SnapshotFull:
        return self.load(self.snapshot_file)
    
    def update_snapshot(self, data: T.SnapshotData) -> None:
        full: T.SnapshotFull
        if self.exist(self.snapshot_file):
            full = self.load_snapshot()
            full['current']['version'] = '{}-{}'.format(
                self._hash_snapshot(data), int(time())
            )
            full['current']['data'] = data
            self.dump(full, self.snapshot_file)
        else:
            self.rebuild_snapshot(data)
        
    def rebuild_snapshot(self, data: T.SnapshotData) -> None:
        full = {
            'base'   : (x := {
                'version': '{}-{}'.format(
                    self._hash_snapshot(data), int(time())
                ),
                'data'   : data,
            }),
            'current': x
        }
        self.dump(full, self.snapshot_file)
    
    # -------------------------------------------------------------------------
    
    def dump(self, data: t.Any, file: T.Path) -> None:
        raise NotImplementedError
    
    def exist(self, path: T.Path) -> bool:
        raise NotImplementedError
    
    def findall_files(self) -> t.Iterable[t.Tuple[T.Path, int]]:
        raise NotImplementedError
    
    def load(self, file: T.Path) -> t.Any:
        raise NotImplementedError
    
    def make_dirs(self, dirpath: T.Path) -> None:
        raise NotImplementedError
    
    def remove(self, file: T.Path) -> None:
        raise NotImplementedError
    
    @staticmethod
    def _hash_snapshot(data: T.SnapshotData) -> str:
        return hashlib.md5(
            json.dumps(data, sort_keys=True).encode()
            #                ~~~~~~~~~~~~~~ recursively sort.
            #   the order of keys affects hash result. since -
            #   `FtpFileSystem.findall_files` has a random order, we need to -
            #   sort them.
        ).hexdigest()


class LocalFileSystem(BaseFileSystem):
    def __init__(self, root: T.Path) -> None:
        super().__init__(fs.abspath(root))
    
    def dump(self, data: t.Any, file: T.Path, binary: bool = False) -> None:
        fs.dump(data, file, type='binary' if binary else 'auto')
        
    def exist(self, path: T.Path) -> bool:
        return fs.exist(path)
    
    def findall_files(self) -> t.Iterator[t.Tuple[T.Path, int]]:
        for f in fs.findall_files(self.root):
            yield f.path, fs.filetime(f.path)
    
    def load(self, file: T.Path, binary: bool = False) -> t.Any:
        return fs.load(file, type='binary' if binary else 'auto')
    
    def make_dirs(self, dirpath: T.Path) -> None:
        assert dirpath.startswith(self.root)
        if not fs.exist(dirpath):
            fs.make_dirs(dirpath)
    
    def remove(self, file: T.Path) -> None:
        fs.remove_file(file)


class FtpFileSystem(BaseFileSystem):
    def __init__(self, url: str) -> None:
        a, b, c, d = url.split('/', 3)
        assert a == 'ftp:' and b == '' and d.startswith('Likianta/')
        e, f = c.rsplit(':', 1)
        host, port, root = e, int(f), f'/{d}'
        
        super().__init__(root)
        
        self._ftp = ftplib.FTP()
        self._ftp.connect(host, port)
        self._ftp.login()
        self._ftp.cwd(root)
    
    def load_snapshot(self) -> T.SnapshotFull:
        data_bytes = self.load(self.snapshot_file)
        return json.loads(data_bytes)
    
    def download_file(
        self, file_i: T.Path, file_o: T.Path, mtime: int = None
    ) -> None:
        data = self.load(file_i)
        fs.dump(data, file_o, 'binary')
        if mtime is None:
            raise NotImplementedError
        os.utime(file_o, (mtime, mtime))
    
    def dump(self, data: t.Any, file: T.Path) -> None:
        # file = self._normpath(file)
        
        if isinstance(data, bytes):
            data_bytes = data
        elif isinstance(data, dict):
            text = json.dumps(data, indent=2, ensure_ascii=False)
            data_bytes = text.encode('utf-8')
        else:
            raise NotImplementedError
        
        with io.BytesIO(data_bytes) as f:
            self._ftp.storbinary(f'STOR {file}', f)
            #   note: we don't need to quote `file` even it has -
            #   whitespaces. i.e. 'STOR 01 02.txt' is legal.
            #   besides, 'STOR "01 02.txt"' will report an error.
    
    def exist(self, path: T.Path) -> bool:
        # path = self._normpath(path)
        a, b = path.rsplit('/', 1)
        if b[0] == '.':
            for f, _ in self._find_hidden_paths(a):
                if f.endswith('/' + b):
                    return True
        else:
            for name in self._ftp.nlst(a):
                if name == b:
                    return True
        return False
    
    def findall_files(self) -> t.Iterator[t.Tuple[T.Path, int]]:
        def recursive_find(dir: T.Path) -> t.Iterator[
            t.Tuple[str, t.Optional[dict]]
        ]:
            subdirs = []
            # FIXME: ftp.msld doesn't show hidden files.
            for name, info in self._ftp.mlsd(dir):
                if info['type'] == 'file':
                    yield f'{dir}/{name}', info
                elif info['type'] == 'dir':
                    subdirs.append(f'{dir}/{name}')
                    # yield from self.findall_files(f'{dir}/{name}')
                else:
                    raise Exception(dir, name, info)
            for path, type in self._find_hidden_paths(dir):
                if type == 'dir':
                    subdirs.append(path)
                else:
                    yield path, None
            for subdir in subdirs:
                yield from recursive_find(subdir)
        
        def get_modify_time_of_hidden_file(file: T.Path) -> int:
            file_i = file
            a, b = file.rsplit('/', 1)
            file_o = f'{a}/__{b}'
            # print(':v', '{} -> {}'.format(file_i, file_o))
            self._ftp.rename(file_i, file_o)
            for name, info in self._ftp.mlsd(fs.parent(file)):
                if name == f'__{b}':
                    self._ftp.rename(file_o, file_i)
                    return self._time_str_2_int(info['modify'])
            else:
                self._ftp.rename(file_o, file_i)
                raise Exception(file)
        
        hidden_files = []
        for file, info in recursive_find(self.root):
            if info is None:
                hidden_files.append(file)
            else:
                yield file, self._time_str_2_int(info['modify'])
        for file in hidden_files:
            print(file, ':v6i')
            yield file, get_modify_time_of_hidden_file(file)
    
    def load(self, file: T.Path) -> bytes:
        with io.BytesIO() as f:
            self._ftp.retrbinary(f'RETR {file}', f.write)
            f.seek(0)
            return f.read()
    
    def make_dirs(self, dirpath: T.Path, precheck: bool = True) -> None:
        assert dirpath.startswith(self.root)
        if not precheck or not self.exist(dirpath):
            self._ftp.mkd(dirpath)
    
    make_dir = make_dirs
    
    def remove(self, file: T.Path) -> None:
        self._ftp.delete(file)
    
    def upload_file(
        self, file_i: T.Path, file_o: T.Path, mtime: int = None
    ) -> None:
        # this method similar to `self.dump`, but keeps origin file's modify -
        # time for target.
        with open(file_i, 'rb') as f:
            self._ftp.storbinary(f'STOR {file_o}', f)
        self._ftp.sendcmd('MFMT {} {}'.format(
            self._time_int_2_str(mtime or fs.filetime(file_i)), file_o
        ))
    
    # noinspection PyTypeChecker
    def _find_hidden_paths(self, dir: T.Path) -> t.Iterator[
        t.Tuple[T.Path, t.Literal['dir', 'file']]
    ]:
        ls: t.List[str] = []
        self._ftp.retrlines('LIST -a {}'.format(dir), ls.append)
        pattern = re.compile(
            r'([-d])rwx?-+ +'
            r'0 user group +'
            r'\d+ '  # size
            r'\w+ +\d+ +(?:\d\d:\d\d|\d{4}) '  # time
            r'(.+)'  # name
        )
        for line in ls:
            assert (m := pattern.match(line)), line
            a, b = m.groups()
            if b[0] == '.':
                yield f'{dir}/{b}', 'dir' if a == 'd' else 'file'
    
    # def _normpath(self, path: T.Path) -> T.Path:
    #     if path == '.':
    #         return self.root
    #     elif path.startswith(('./', '../')):
    #         return fs.normpath('{}/{}'.format(self.root, path))
    #     else:
    #         return path
    
    @staticmethod
    def _time_int_2_str(mtime: int) -> str:
        dt = datetime.fromtimestamp(mtime)
        return dt.strftime('%Y%m%d%H%M%S')
    
    @staticmethod
    def _time_str_2_int(mtime: str) -> int:
        """
        mtime: e.g. '20250619064438.504'
        """
        dt = datetime(
            *map(int, (
                mtime[0:4],
                mtime[4:6],
                mtime[6:8],
                mtime[8:10],
                mtime[10:12],
                mtime[12:14],
            ))
        )
        return int(dt.timestamp())
