"""
reference:
    https://github.com/likianta/brilliant-ui/blob/master/brilliant/application -
        /debug.py
    https://github.com/albertz/background-zmq-ipython/blob/master/kernel.py
"""

if 1:
    import os
    import typing as t
    from contextlib import contextmanager
    from os import getpid
    
    import lk_logger
    from lk_utils import new_thread
    from lk_utils.textwrap import dedent
    from rich.markdown import Markdown

if 2:  # import ipykernal related stuff
    # ignore some warning from ipython kernel.
    os.environ['PYDEVD_DISABLE_FILE_VALIDATION'] = '1'
    
    
    @contextmanager
    def _suppress_kernel_warning() -> None:
        # lk_logger.mute()  # TEST
        yield
        lk_logger.unmute()
    
    
    with _suppress_kernel_warning():
        # from IPython import embed_kernel
        from IPython.core.autocall import ZMQExitAutocall
        from ipykernel.embed import embed_kernel
        from ipykernel.kernelapp import IPKernelApp
        from ipykernel.zmqshell import ZMQInteractiveShell
        from jupyter_console.app import ZMQTerminalIPythonApp
        from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

__all__ = [
    'KernelWrapper',
    'run_client',
    'run_server',
]


# -----------------------------------------------------------------------------


class KernelWrapper:
    _callback: t.Optional[t.Callable]
    _pid: str
    
    def __init__(self, callback: t.Callable = None):
        self._callback = callback
    
    @property
    def app(self) -> IPKernelApp:
        return IPKernelApp.instance()
    
    @property
    def kernel_id(self) -> str:
        return self._pid
    
    # @new_thread()
    def start(self, user_ns: dict) -> None:
        self._pid = str(getpid())
        print(
            '\nto connect to this kernel, use:\n',
            '    [cyan]python -m [yellow]remote_ipython[/] connect-debugger '
            '[cyan]{}[/][/]'.format(self._pid),
            ':r',
        )
        
        with _suppress_kernel_warning():
            """
            suppress warning from `IPKernelApp.init_signal`, because we do \
            want to do this in a subthread.
            """
            embed_kernel(local_ns=user_ns)
        
        # after
        print(':r', '[red dim]kernel exited[/]')
        if self._callback:
            self._callback()
    
    @new_thread()
    def async_start(self, user_ns: dict) -> None:
        self.start(user_ns)
    
    def close(self) -> None:
        self.app.close()


def run_server(
    user_ns: dict = None, callback: t.Callable = None, new_thread: bool = False
) -> KernelWrapper:
    print('start ipython kernel', ':v2d')
    print(
        ':r1',
        Markdown(_help := dedent('''
            # how to use libmdio-mini's debug mode

            when you start the debug mode, a kernel id is shown in console.

            you can open a new terminal, use the kernel id to connect via
            `remote_ipython connect-debugger` command:

            ```sh
            py -m remote_ipython connect-debugger <kernel_id>
            ```

            ## exit debug mode

            to disconnect kernel but not terminate it:

            ```py
            leave()
            ```

            you can reconnect to it by same kernel id at anytime then.

            to disconnect and totaly terminate the debugger:

            ```py
            exit()  # or `quit()`
            ```
        ''')),
    )
    
    def _leave() -> None:
        sh = ZMQInteractiveShell.instance()
        exiter = ZMQExitAutocall(ip=sh)
        exiter(keep_kernel=True)
    
    kernel = KernelWrapper(callback=callback)
    user_ns = {
        'README'        : _help,
        'leave'         : _leave,
        'print'         : lk_logger.bprint,
        **(user_ns or {}),
    }
    if new_thread:
        kernel.async_start(user_ns)
        from time import sleep
        sleep(2)
    else:
        kernel.start(user_ns)
    return kernel


def run_client(kernel_id: str) -> None:
    lk_logger.unload()
    
    instance = ZMQTerminalIPythonApp.instance()
    instance.initialize(
        argv=['console', '--existing', kernel_id],
    )
    # fix no prompt
    # https://blog.csdn.net/Likianta/article/details/131486249
    instance.shell.pt_cli.auto_suggest = AutoSuggestFromHistory()
    instance.start()  # blocking
    
    lk_logger.setup(quiet=True)
