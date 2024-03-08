import sys
import typing as t

try:
    import toga
except ImportError:
    toga = None

from ..util import wait_webpage_ready


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
    
    # from .webbrowser_impl import App
    # app = App(title, url, size=size, **kwargs)
    # app.mainloop()
    
    if sys.platform == 'linux':
        import webbrowser
        webbrowser.open_new_tab(url)
    else:
        if toga:
            from .toga_impl import App
        else:
            from .webbrowser_impl import App
        app = App(title, url, size=size, **kwargs)
        app.mainloop()
