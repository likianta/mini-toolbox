"""
chrome in command line:
    help: list all command line options
        https://peter.sh/experiments/chromium-command-line-switches/
"""
import os

from argsense import cli
from lk_utils import run_cmd_args
from lk_utils import xpath


@cli.cmd()
def where_is_chrome() -> str:
    # macos
    path = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    if os.path.exists(path):
        return path
    pass


@cli.cmd()
def launch(
        url: str,
        win_size: tuple[int, int] = None,
        win_pos: tuple[int, int] = None,
        # app_name: str = None,
) -> None:
    print('open url', url)
    win_size = win_size or (800, 600)
    win_pos = win_pos or _get_center_pos(win_size)
    temp_data_dir = xpath("__chrome_app_mode_temp_data__")
    # TODO: more flags
    #   --app-auto-launched
    #   --app-id
    #   --app-shell-host-window-size
    #   --ash-host-window-bounds=100+300-800x600
    #                             x   y   w   h
    #   --auto-accept-camera-and-microphone-capture
    #   --force-dark-mode
    #   --headless
    #   --hide-scrollbars
    #   --install-chrome-app
    #   --no-experiments
    #   --no-startup-window
    #       something like tray mode
    #   --single-process
    #   --start-maximized
    #   --trusted-download-sources
    run_cmd_args(
        where_is_chrome(),
        # ('--window-name', app_name),
        # app_name and '--window-name={}'.format(app_name),
        "--app={}".format(url),
        "--window-size={}".format(",".join(map(str, win_size))),
        "--window-position={}".format(",".join(map(str, win_pos))),
        "--user-data-dir={}".format(temp_data_dir),
        '--ash-no-nudges',  # do not show first-run dialog, if disable this flag,
        #   chrome may occcasionally show `set chrome as default browser`,
        #   `send anonymous feedbacks to google for analysis` in app startup.
        '--no-crash-upload',
        '--no-default-browser-check',
        '--no-first-run',  # do not show "what's new"
        verbose=True,
    )


def _get_center_pos(win_size) -> tuple[int, int]:
    w0, h0 = _get_screen_size()
    w1, h1 = win_size
    return (w0 - w1) // 2, (h0 - h1) // 2


def _get_screen_size() -> tuple[int, int]:
    import tkinter
    root = tkinter.Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.destroy()
    return screen_width, screen_height


if __name__ == "__main__":
    # py chrome_app_mode/app.py -h
    # py chrome_app_mode/app.py where-is-chrome
    # py chrome_app_mode/app.py launch -h
    # py chrome_app_mode/app.py launch localhost:2000
    cli.run()
