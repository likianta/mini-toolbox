import typing as t

import toga  # noqa

from .common import get_center_pos


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
        self.url = url
        self._pos = pos or get_center_pos(size)
        self._size = size
        super().__init__(
            formal_name=title,
            app_id='dev.likianta.brilliant',
            icon=icon,
        )
    
    # override
    def startup(self) -> None:
        # noinspection PyTypeChecker
        self.main_window = toga.MainWindow(
            title=self.formal_name,
            size=self._size,
            position=self._pos,
        )
        self._view = toga.WebView(
            url=self.url,
            on_webview_load=lambda _: print('webview loaded', self.url),
        )
        self.main_window.content = self._view
        self.main_window.show()


if __name__ == '__main__':
    # pox pyapp_window/webview_window/toga_impl.py
    open_native_window(
        'WebView Example',
        'https://www.google.com/',
    )
