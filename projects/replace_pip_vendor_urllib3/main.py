"""
requirements:
    - lk-logger
    - lk-utils
"""
import lk_logger
import os
import re
from lk_utils import fs
from lk_utils import run_cmd_args
from lk_utils import xpath

lk_logger.setup(quiet=True, show_varnames=True)


def main():
    dir_i = _get_specific_urllib3_dir()
    dir_o = '{}/_vendor/urllib3'.format(_get_current_pip_dir())
    dir_m = f'{dir_o}/_vendor/urllib3.bak'
    
    fs.move(dir_o, dir_m, overwrite=True)
    fs.copy_tree(dir_i, dir_o)
    
    print(':t', 'done')


def _get_specific_urllib3_dir() -> str:
    dir_ = xpath('urllib3')
    if not os.path.exists(dir_):
        run_cmd_args('pip', 'install', 'urllib3==1.25.11',
                     '-t', xpath('.'), verbose=True)
        assert os.path.exists(dir_)
    return dir_


def _get_current_pip_dir() -> str:
    response = run_cmd_args('pip', '-V')
    pip_location = re.search(r'pip [.\d]+ from (.+) \(python [.\d]+\)',
                             response).group(1)
    assert os.path.exists(pip_location)
    return pip_location


if __name__ == '__main__':
    main()
