if __package__ is None:
    __package__ = 'easy_submodule'

import os.path

from argsense import cli
from lk_utils import fs

from . import ui
from .check import check_submodules
from .clone import clone_submodules
from .lock import lock_submodules
from .profile import init_profile
from .pull import pull_submodules


@cli.cmd()
def init(path: str = '.') -> None:
    init_profile(_normpath(path))


@cli.cmd()
def clone(path: str = '.') -> None:
    clone_submodules(_normpath(path))


@cli.cmd()
def check(path: str = '.') -> None:
    check_submodules(_normpath(path))


@cli.cmd()
def lock(path: str = '.') -> None:
    lock_submodules(_normpath(path))


@cli.cmd()
def pull(path: str = '.') -> None:
    pull_submodules(_normpath(path))


@cli.cmd()
def run_gui(
    cwd: str = '', port: int = 2013, _only_backend: bool = False
) -> None:
    if cwd: cwd = fs.abspath(cwd)
    # ui.run_app(port)
    if not _only_backend:
        ui.run_app(port, ('--cwd', cwd))
    else:
        ui.setup_ui(_default_input=cwd)


def _normpath(file_or_dir: str) -> str:
    if file_or_dir == '.' or os.path.isdir(file_or_dir):
        return '{}/.submodules.yaml'.format(file_or_dir)
    else:
        return file_or_dir


if __name__ == '__main__':
    # pox -m easy_submodule run-gui
    cli.run()
