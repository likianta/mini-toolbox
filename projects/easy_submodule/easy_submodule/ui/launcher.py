import subprocess as sp

import sys
from lk_utils import fs
from lk_utils.subproc import run_cmd_args
from pyapp_window import launch


def main(port: int = 2013, *args) -> None:
    launch(
        'Easy Submodule',
        'http://localhost:{}'.format(port),
        size=(600, 1000),
        copilot_backend=_start_backend(port, *args),
    )


def _start_backend(port: int, *args) -> sp.Popen:
    proc: sp.Popen = run_cmd_args(
        (sys.executable, '-m', 'streamlit', 'run'),
        # ('run', fs.xpath('ui_builder.py')),
        ('--global.developmentMode', 'false'),
        ('--server.headless', 'true'),
        ('--server.port', port),
        (
            fs.xpath('../__main__.py'), 'run-gui',
            # ('--', *args, ('--port', port), '--only-backend'),
            (*args, port, ':true'),
        ),
        blocking=False,
        cwd=fs.xpath('../../'),
        verbose=True,
    )
    return proc
