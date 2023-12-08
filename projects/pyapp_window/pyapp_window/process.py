import sys
import typing as t
from multiprocessing import Process
from subprocess import Popen
from threading import Thread

_is_linux = sys.platform == 'linux'


class ProcessWrapper:
    """ a wrapper to provide common interface on Popen, Process, Thread. """
    
    def __init__(self, core: t.Union[Popen, Process, Thread]):
        self._core = core
        # assert self._core.daemon is True
    
    def start(self) -> None:
        if not isinstance(self._core, Popen):
            self._core.start()
    
    def close(self) -> None:
        if isinstance(self._core, Thread):
            self._core.join()  # FIXME: is this right?
        else:
            self._core.terminate()
    
    def is_alive(self) -> bool:
        if _is_linux:
            # FIXME: since linux uses `webbrowser.open` as a workaround instead
            #   of a valid window handle, we cannot check the process status.
            return True
        if isinstance(self._core, Popen):
            return self._core.poll() is None
        else:
            return self._core.is_alive()
