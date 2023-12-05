import shutil
import subprocess as sp
import typing as t
import webbrowser

import sys

from .common import get_center_pos


class App:
    
    def __init__(
        self,
        title: str,
        url: str,
        *,
        size: t.Tuple[int, int] = (800, 600),
        pos: t.Optional[t.Tuple[int, int]] = None,
        icon: str = None,
    ) -> None:
        self.title = title
        self.url = url
        self._favicon = icon  # TODO
        self._pos = pos or get_center_pos(size)
        self._size = size
    
    def mainloop(self) -> None:
        if exe := find_executable():
            proc = sp.Popen(
                (
                    exe,
                    '--app={}'.format(self.url),
                    '--window-size={}'.format(','.join(map(str, self._size))),
                    '--window-position={}'.format(','.join(map(str, self._pos))),
                    '--ash-no-nudges',
                    '--no-crash-upload',
                    '--no-default-browser-check',
                    '--no-first-run',  # don't show "what's new"
                ),
                close_fds=True,
                start_new_session=True,
            )
            if proc.poll() is None:  # means worked
                return
        # fallback to standlib webbrowser
        webbrowser.open_new_tab(self.url)


def find_executable() -> t.Optional[str]:
    """
    ref: https://github.com/mhils/native_web_app/blob/master/native_web_app.py
    """
    is_win = sys.platform == 'win32'
    # noinspection PyTypeChecker
    possible_names: t.Iterator[str] = filter(None, (
        sys.platform == 'darwin' and
        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        sys.platform == 'win32' and 'msedge',
        'chrome',
        'google-chrome',
        'google-chrome-stable',
        'chromium',
        'chromium-browser',
    ))
    for name in possible_names:
        if x := shutil.which(name):
            return x
        if is_win and (x := _find_in_registry(name)):
            return x
    return None


def _find_in_registry(browser_name: str) -> t.Optional[str]:
    import winreg  # this only available on windows
    try:
        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths',
                0,
                winreg.KEY_READ
            ) as key:
                return winreg.QueryValue(key, browser_name + '.exe')
        except FileNotFoundError:
            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths',
                0,
                winreg.KEY_READ
            ) as key:
                return winreg.QueryValue(key, browser_name + '.exe')
    except OSError:
        return None
