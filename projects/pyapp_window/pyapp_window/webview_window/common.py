import re
import subprocess as sp
import typing as t
from urllib.error import URLError
from urllib.request import urlopen

import sys


def get_center_pos(window_size: t.Tuple[int, int]) -> t.Tuple[int, int]:
    if sys.platform == 'darwin':
        w0, h0 = get_screen_size()
        w1, h1 = window_size
        return (w0 - w1) // 2, (h0 - h1) // 2
    else:
        return 100, 100


def get_screen_size() -> t.Tuple[int, int]:
    def via_tkinter() -> t.Tuple[int, int]:
        import tkinter
        root = tkinter.Tk()
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        root.destroy()
        return width, height
    
    def via_system_api() -> t.Tuple[int, int]:
        ret = sp.run(
            'echo $(system_profiler SPDisplaysDataType)',
            text=True,
            shell=True,
            stdout=sp.PIPE,
        )
        m = re.search(r'Resolution: (\d+) x (\d+)', ret.stdout)
        w, h = map(int, m.groups())
        # print(ret, (w, h), ':v')
        return w, h
    
    try:
        return via_system_api()
    except Exception:
        return via_tkinter()


def wait_webpage_ready(url: str, timeout: float = 10) -> None:
    print(':t2s')
    for _ in _wait(timeout, 0.1):
        try:
            if urlopen(url, timeout=1):
                print('webpage ready', ':t2')
                return
        except (TimeoutError, URLError):
            continue
    # raise TimeoutError('url is not accessible', url)


def _wait(timeout: float, interval: float = 1) -> t.Iterator[int]:
    count = int(timeout / interval)
    for i in range(count):
        yield i
        time.sleep(interval)
    raise TimeoutError(f'timeout in {timeout} seconds (with {count} loops)')
