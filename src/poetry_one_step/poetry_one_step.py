"""
command: py src/poetry_one_step/poetry_one_step.py ...
"""
import os.path
import re

from argsense import cli
from lk_utils import subproc
from lk_utils import xpath

lk_root = xpath('../../..')


@cli.cmd()
def main(dirname: str) -> None:
    dir_ = f'{lk_root}/{dirname}'
    file = f'{dir_}/pyproject.toml'
    config = open(file, 'r').read()
    version = re.search(r'version = "(.+)"', config).group(1)
    
    package = f'{dirname} {version}'
    print(package, ':v2')
    
    file = f'{dir_}/dist/{dirname.replace("-", "_")}-{version}-py3-none-any.whl'
    if not os.path.exists(file):
        print(f'poetry build {package}')
        os.chdir(dir_)
        subproc.run_cmd_args(
            'poetry', 'build', '-f', 'wheel',
            verbose=True
        )
    
    print(f'pip install {package}')
    subproc.run_cmd_args('pip', 'install', file, verbose=True)
    print('done', ':t')


if __name__ == '__main__':
    cli.run(main)
