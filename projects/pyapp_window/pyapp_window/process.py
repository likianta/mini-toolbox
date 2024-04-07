import sys
import typing as t
from multiprocessing import Process
from subprocess import Popen
from threading import Thread

_is_linux = sys.platform == 'linux'


class ProcessWrapper:
    """ a wrapper to provide common interface on Popen, Process, Thread. """
    
    def __init__(self, prog: t.Union[Popen, Process, Thread]) -> None:
        self._prog = prog
        # assert self._prog.daemon is True
        
    @property
    def alive(self) -> bool:
        if _is_linux:
            # FIXME: since linux uses `webbrowser.open` as a workaround instead
            #   of a valid window handle, we cannot check the process status.
            return True
        if isinstance(self._prog, Popen):
            return self._prog.poll() is None
        else:
            return self._prog.is_alive()
    
    def start(self) -> None:
        if not isinstance(self._prog, Popen):
            self._prog.start()
    
    def close(self) -> None:
        if isinstance(self._prog, Thread):
            self._prog.join()  # FIXME: is this right?
        else:
            self._prog.terminate()
