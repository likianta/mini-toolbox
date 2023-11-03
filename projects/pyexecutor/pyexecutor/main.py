import os
import sys

import lk_logger
from lk_utils import fs
from lk_utils import loads

lk_logger.update(show_varnames=True)


def run(target: str, *args, working_dir: str = None, **kwargs) -> None:
    if _is_package(target):
        target = f'{target}/__main__.py'
    elif _is_script(target):
        pass
    else:
        raise Exception(target)
    
    if working_dir is None:
        working_dir = fs.parent(target)
    
    launch_script(target, working_dir, args)


def _is_package(path: str) -> bool:
    if (
        os.path.isdir(path)
        and os.path.exists(f'{path}/__init__.py')
        and os.path.exists(f'{path}/__main__.py')
    ):
        return True
    return False


def _is_script(path: str) -> bool:
    if os.path.isfile(path) and path.endswith('.py'): return True
    return False


# def launch_package(package: str, working_dir: str, args: tuple) -> None:
#     launch_script(f'{package}/__main__.py', working_dir, args)


def launch_script(target: str, working_dir: str, args: tuple) -> None:
    target = fs.abspath(target)
    target_dir = fs.parent(target)
    working_dir = fs.abspath(working_dir)
    
    sys.path.insert(0, working_dir)
    sys.path.insert(0, target_dir)
    sys.argv = [target, *args]
    
    os.chdir(working_dir)
    # print(os.getcwd(), sys.path, ':vl')
    code = loads(target, 'plain')
    exec(
        code,
        {
            '__package__': fs.barename(
                fs.relpath(target, working_dir)
            ).replace('/', '.'),
            '__name__': '__main__',
            '__file__': target,
        },
    )
