import typing as t
from multiprocessing import Process
from subprocess import Popen

from time import sleep

from .webview_window import open_native_window


def launch(
    title: str,
    url: str,
    copilot_backend: t.Union[Popen, t.Callable] = None,
    wait_url_ready: bool = False,
    **kwargs
) -> None:
    if copilot_backend:
        if isinstance(copilot_backend, Popen):
            proc_back = copilot_backend
        else:
            proc_back = Process(target=copilot_backend, daemon=True)
            proc_back.start()
        
        proc_front = Process(
            target=open_native_window,
            kwargs={
                'title'    : title,
                'url'      : url,
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
            if isinstance(proc_back, Popen):
                if proc_back.poll() is not None:
                    proc_front.terminate()
                    break
            else:
                if not proc_back.is_alive():
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
