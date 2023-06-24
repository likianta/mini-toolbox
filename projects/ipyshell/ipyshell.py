import os
import sys
from importlib import reload as reload_module
from importlib.util import module_from_spec
from importlib.util import spec_from_file_location
from types import ModuleType

from lk_logger import start_ipython
from lk_utils import fs


class Paths:
    home = 'C:/Likianta'
    
    workspace = f'{home}/workspace'
    
    argsense = f'{workspace}/dev_master_likianta/argsense-cli'
    dps = depsland = f'{workspace}/dev_master_likianta/depsland'
    lk_logger = f'{workspace}/dev_master_likianta/lk-logger'
    lk_utils = f'{workspace}/dev_master_likianta/lk-utils'
    playground = f'{workspace}/playground'
    
    def list(self):
        for k, v in self.__dict__.items():
            if k.startswith('_'):
                continue
            if k in ('list',):
                continue
            print(f'{k}: {v}')


ch = os.chdir
exists = os.path.exists
p = Paths()


def find_module(path: str) -> ModuleType:
    """
    ref: https://blog.csdn.net/Likianta/article/details/126660058
    """
    name = fs.basename(path, False)
    spec = spec_from_file_location(name, path)
    # print(spec.name, spec.origin)
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


# -----------------------------------------------------------------------------

ns = {
    'ch'           : ch,
    'exists'       : exists,
    'find_module'  : find_module,
    'fs'           : fs,
    'os'           : os,
    'p'            : p,
    'reload_module': reload_module,
    'sys'          : sys,
}
ns['show_ns'] = lambda: print(ns, ':l')
# py ipyshell.py
start_ipython(ns)
