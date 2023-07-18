import os
import sys

import lk_logger
from lk_utils import fs
from lk_utils import loads

lk_logger.update(show_varnames=True)


def run(target: str, *args, working_dir: str = None, **kwargs) -> None:
    if target.endswith('.py') and os.path.isfile(target):
        if working_dir is None:
            working_dir = fs.parent(target)
        working_dir = fs.abspath(working_dir)
        print(target, working_dir, args, kwargs, ':l')
        launch_script(target, working_dir, args)
    else:
        raise Exception


def launch_script(script: str, working_dir: str, args) -> None:
    script = fs.abspath(script)
    print('package name', fs.dirname(working_dir))
    os.chdir(fs.parent(working_dir))
    sys.path.insert(0, fs.parent(working_dir))
    # print(os.getcwd(), sys.path, ':vl')
    sys.argv = [script, *args]
    code = loads(script, 'plain')
    exec(code, {
        '__package__': fs.dirname(working_dir),
        '__name__'   : '__main__',
        '__file__'   : script,
    })
