import os
import sys

from argsense import cli
from lk_utils import fs
from lk_utils import loads


@cli.cmd()
def run(target: str, *args, working_dir: str = None, **kwargs) -> None:
    print(target, working_dir, args, kwargs, ':v')
    if target.endswith('.py') and os.path.isfile(target):
        if working_dir is None:
            working_dir = fs.parent(target)
        launch_script(target, working_dir, args)
    else:
        raise Exception


def launch_script(script: str, working_dir: str, args) -> None:
    script = fs.abspath(script)
    print('package name', fs.dirname(working_dir))
    os.chdir(fs.parent(working_dir))
    sys.path.insert(0, fs.parent(working_dir))
    sys.argv = [script, *args]
    code = loads(script, 'plain')
    exec(code, {
        '__package__': fs.dirname(working_dir),
        '__name__'   : '__main__',
        '__file__'   : script,
    })


if __name__ == '__main__':
    # py pyexecutor/pyx/main.py -h
    # py pyexecutor/pyx/main.py ...
    cli.run(run)
