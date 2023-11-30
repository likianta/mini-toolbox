import typing as t
from multiprocessing import Process
from subprocess import Popen
from threading import Thread


class ProcessWrapper:
    """ a wrapper to provide common interface on Popen, Process, Thread. """
    
    def __init__(self, core: t.Union[Popen, Process, Thread]):
        self._core = core
        # assert self._core.daemon is True
    
    def start(self) -> None:
        self._core.start()
    
    def close(self) -> None:
        if isinstance(self._core, Thread):
            self._core.join()  # FIXME: is this right?
        else:
            self._core.terminate()
    
    def is_alive(self) -> bool:
        if isinstance(self._core, Popen):
            return self._core.poll() is None
        else:
            return self._core.is_alive()
