import os.path

from lk_utils import normpath
from .lock import get_current_info
from ..profile import load_profile


def main(profile_path: str = '.submodules.yaml', verbose: bool = False) -> bool:
    need_sync = False
    profile = load_profile(profile_path)
    for name, info in profile.items():
        print(name, ':i2')
        branch0, commit0 = get_current_info(info['path'])
        branch1, commit1 = info['branch'], info['commit']
        print({
            'name'      : name,
            'is_symlink': (
                is_symlink := os.path.islink(info['path'])
            ),
            'source'    : (
                is_symlink and
                normpath(os.path.realpath(info['path']))
                or '<as_is>'
            ),
            'is_sync'   : (
                is_sync := (branch0 == branch1 and commit0 == commit1)
            ),
        }, ':l')
        if not is_sync:
            need_sync = True
    
    print('overview', ':dt')
    print(overview, ':l')
    return need_sync
_
