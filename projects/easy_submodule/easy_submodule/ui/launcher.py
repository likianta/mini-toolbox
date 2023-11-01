import multiprocessing as mp
import subprocess as sp
import sys
from time import sleep

from argsense import cli
from lk_utils import fs
from lk_utils.subproc import run_cmd_args
from pyapp_window import open_native_window


@cli.cmd()
def main(port: int = 2013) -> None:
    proc_back = backend(port)
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


# shared object across multiprocessing
# https://docs.python.org/3/library/multiprocessing.html#sharing-state-between \
# -processes
# https://docs.python.org/3/library/array.html#module-array
# _backend_running = mp.Value('B', 0)


def backend(port: int) -> sp.Popen:
    proc: sp.Popen = run_cmd_args(
        (sys.executable, '-m', 'streamlit'),
        ('run', 'easy_submodule/__main__.py', 'run-backend'),
        ('--global.developmentMode', 'false'),
        ('--server.headless', 'true'),
        ('--server.port', str(port)),
        blocking=False,
        cwd=fs.xpath('../../'),
        rich_print=False,
        verbose=True,
    )
    return proc
    
    # _backend_running.value = 1
    # while _backend_running.value:
    #     sleep(0.2)
    # else:
    #     proc.terminate()
    #     print('backend process is killed')


def frontend(port: int) -> None:
    open_native_window(
        'Easy Submodule',
        'http://localhost:{}'.format(port),
        size=(600, 1000)
    )


if __name__ == '__main__':
    # pox easy_submodule/ui/launcher.py
    cli.run(main)