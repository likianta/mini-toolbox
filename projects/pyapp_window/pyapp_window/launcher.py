from multiprocessing import Process
from subprocess import Popen
from time import sleep

from .native_window import open_native_window


def launch(
    title: str,
    url: str,
    copilot_backend: Popen = None,
    wait_url_ready: bool = False,
    **kwargs
) -> None:
    if copilot_backend:
        proc_back = copilot_backend
        proc_front = Process(
            target=open_native_window,
            kwargs={
                'title': title,
                'url'  : url,
                'check_url': wait_url_ready,
                **kwargs
            },
            daemon=True
        )
        proc_front.start()
        
        while True:
            if not proc_front.is_alive():
                proc_back.terminate()
                break
            if proc_back.poll() is not None:
                proc_front.terminate()
                break
            sleep(1)
    else:
        open_native_window(
            title=title,
            url=url,
            **kwargs
        )
    
    print('exit program')
