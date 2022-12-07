import sys
from importlib.util import module_from_spec
from importlib.util import spec_from_file_location
from os.path import isfile
from types import ModuleType

from lk_utils.filesniff import basename


def load_module(path: str) -> ModuleType:
    """
    ref: https://blog.csdn.net/Likianta/article/details/126660058
    """
    name = basename(path, False)
    spec = spec_from_file_location(
        name, path if isfile(path) else path + '/__init__.py'
    )
    # print(spec.name, spec.origin)
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module
