import sys
import typing as t

from .common import wait_webpage_ready


def open_native_window(
    title: str,
    url: str,
    size: t.Tuple[int, int] = (800, 600),
    check_url: bool = False,
    # _backend: str = None,
    **kwargs
) -> None:
    if check_url:
        wait_webpage_ready(url)
    
    from .toga_impl import App
    app = App(title, url, size=size, **kwargs)
    app.main_loop()
    
    # """
    # different webview backend for platforms:
    #     darwin: uses toga
    #         pros: lightweight, native
    #         cons:
    #             - fow windows: poetry cannot resolve 'pythonnet' dependency.
    #             - for linux: no binary build, and requires installing libraries
    #                 via `apt install`.
    #     windows: uses pywebview.
    #         cons:
    #             - for macos: pywebview cannot work in poetry virtual
    #                 environment.
    #     linux: uses wxpython.
    #         cons:
    #             - wxpython has large size.
    # """
    # if sys.platform == 'darwin' or sys.platform == 'win32':
    #     from .toga_impl import App
    #     app = App(title, url, size=size, **kwargs)
    #     app.main_loop()
    # elif sys.platform == 'linux':
    #     from .wx_impl import MyFrame, wx
    #     app = wx.App()
    #     MyFrame(title, url, size, **kwargs)
    #     app.MainLoop()
    # elif sys.platform == 'win32':
    #     raise NotImplementedError
    # else:
    #     raise Exception(f'unsupported platform: {sys.platform}')
