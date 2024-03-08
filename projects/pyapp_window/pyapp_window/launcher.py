import typing as t
from multiprocessing import Process
from subprocess import Popen
from threading import Thread

from time import sleep

from .process import ProcessWrapper
from .webview_window import open_native_window


def launch(
    title: str,
    url: str,
    copilot_backend: t.Union[
        Popen, Process, Thread, t.Callable[[], t.Any]
    ] = None,
    wait_url_ready: bool = False,
    **kwargs
) -> None:
    if copilot_backend:
        proc_back = ProcessWrapper(
            copilot_backend
            if isinstance(copilot_backend, (Popen, Process, Thread))
            else Process(target=copilot_backend, daemon=True)
        )
        proc_back.start()
        
        proc_front = ProcessWrapper(
            Process(
                target=open_native_window,
                kwargs={
                    'title'    : title,
                    'url'      : url,
                    'check_url': wait_url_ready,
                    **kwargs
                },
                daemon=True
            )
        )
        proc_front.start()
        
        while True:
            if not proc_front.is_alive():
                proc_back.close()
                break
            if not proc_back.is_alive():
                proc_front.close()
                break
            sleep(1)
    else:
        open_native_window(title=title, url=url, **kwargs)
    
    print('exit program')
