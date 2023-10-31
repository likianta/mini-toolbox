import re
import subprocess as sp
import sys
import typing as t

import toga


def open_native_window(
    title: str,
    url: str,
    size: t.Tuple[int, int] = (800, 600),
    **kwargs
) -> None:
    app = App(title, url, size=size, **kwargs)
    app.main_loop()  # blocking until window closed.


class App(toga.App):
    url: str
    _pos: t.Tuple[int, int]
    _size: t.Tuple[int, int]
    _view: toga.WebView
    
    def __init__(
        self,
        title: str,
        url: str,
        *,
        size: t.Tuple[int, int] = (800, 600),
        pos: t.Optional[t.Tuple[int, int]] = None,
        icon: str = None,
    ) -> None:
        super().__init__(
            formal_name=title,
            app_id='dev.likianta.brilliant',
            icon=icon,
        )
        self.url = url
        self._pos = pos or get_center_pos(size)
        self._size = size
    
    # override
    def startup(self) -> None:
        # noinspection PyTypeChecker
        self.main_window = toga.MainWindow(
            title=self.name,
            size=self._size,
            position=self._pos,
        )
        # self._wait_webpage_ready(self.url)
        self._view = toga.WebView(
            url=self.url,
            on_webview_load=lambda _: print('webview loaded', ':t2v'),
        )
        self.main_window.content = self._view
        self.main_window.show()
    
    # @staticmethod
    # def _wait_webpage_ready(url: str, timeout: float = 3) -> None:
    #     print(':t2s')
    #     for _ in wait(timeout, 0.2):
    #         try:
    #             if urlopen(url, timeout=1):
    #                 print('webpage ready', ':t2')
    #                 return
    #         except Exception:
    #             continue
    #     raise TimeoutError('timeout waiting streamlit service ready')


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
        print(ret, (w, h), ':v')
        return w, h
    
    try:
        return via_system_api()
    except Exception:
        return via_tkinter()


if __name__ == '__main__':
    # pox brilliant/application/opener/native_window_2.py
    open_native_window(
        'WebView Example',
        'https://www.google.com/',
    )
