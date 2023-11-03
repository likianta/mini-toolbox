import multiprocessing as mp
import subprocess as sp
import sys
from time import sleep

from lk_utils import fs
from lk_utils.subproc import run_cmd_args
from pyapp_window import open_native_window


def main(port: int = 2013, *args) -> None:
    proc_back = backend(port, *args)
    assert proc_back
    # proc_back = mp.Process(target=backend, kwargs={'port': port}, daemon=True)
    # proc_back.start()
    proc_front = mp.Process(target=frontend, kwargs={'port': port}, daemon=True)
    proc_front.start()
    
    while True:
        if not proc_front.is_alive():
            # _backend_running.value = 0
            proc_back.terminate()
            break
        # if not proc_back.is_alive():
        #     proc_front.terminate()
        #     break
        if proc_back.poll() is not None:
            proc_front.terminate()
            break
        sleep(1)
    
    print('exit program')


def backend(port: int, *args) -> sp.Popen:
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


def frontend(port: int) -> None:
    open_native_window(
        'Easy Submodule',
        'http://localhost:{}'.format(port),
        size=(600, 1000)
    )
