import subprocess as sp

import sys
from lk_utils import fs
from lk_utils.subproc import run_cmd_args


def main(port: int = 2013, *args) -> None:
    try:
        from pyapp_window import launch
    except (ImportError, ModuleNotFoundError) as e:
        print(':v4', '''
            `pyapp-window` dependency is not installed. this is a general
            error that could happen at linux platform.
            for linux user, please follow the instructions below:
            1. check and install core libraries:
                ubuntu 18.04+, debian 10+:
                    sudo apt update
                    sudo apt install pkg-config python3-dev \\
                        libgirepository1.0-dev libcairo2-dev \\
                        gir1.2-webkit2-4.0 libcanberra-gtk3-module
                fedora:
                    sudo dnf install pkg-config python3-devel \\
                    gobject-introspection-devel cairo-gobject-devel \\
                    webkit2gtk3 libcanberra-gtk3
                freebsd:
                    sudo pkg update
                    sudo pkg install gobject-introspection cairo webkit2-gtk3
            2. then pip install:
                pip install http://likianta.pro:2006/pyapp-window/pyapp_window-0.3.0-py3-none-any.whl
        ''')
        raise e
    
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
