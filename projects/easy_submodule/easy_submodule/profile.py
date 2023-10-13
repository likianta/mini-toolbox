import os.path
import typing as t

from lk_utils import dumps
from lk_utils import fs
from lk_utils import loads


class T:
    ProfileItemRaw = t.TypedDict('ProfileItemRaw', {
        'url'   : str,
        'path'  : str,  # relpath, can be missing
        'branch': str,  # can be missing
        'commit': str,  # can be missing
    }, total=False)
    ProfileItem = t.TypedDict('ProfileItem', {
        'url'   : str,
        'path'  : str,  # abspath
        'branch': str,  # empty means default branch
        'commit': str,  # empty means latest commit
    })
    ProjectName = str
    
    Profile0 = t.Dict[ProjectName, ProfileItemRaw]
    Profile1 = t.Dict[ProjectName, ProfileItem]
    Profile = Profile1


def init_profile(path: str) -> None:
    if os.path.isdir(path):
        file_o = f'{path}/.submodules.yaml'
    else:
        file_o = path
        assert file_o.endswith('.yaml')
    dumps('', file_o, 'plain')


def load_profile(path: str) -> T.Profile:
    data0: t.Dict[str, T.ProfileItemRaw] = loads(path)
    data1: t.Dict[str, T.ProfileItem] = {}
    
    base_dir = fs.parent(path)
    
    def get_path() -> str:
        if 'path' in v:
            assert not os.path.isabs(v['path'])
            return fs.normpath('{}/{}'.format(base_dir, v['path']))
        else:
            return fs.normpath('{}/lib/{}'.format(base_dir, k))
    
    for k, v in data0.items():
        data1[k] = {
            'url'   : v['url'],
            'path'  : get_path(),
            'branch': v.get('branch', ''),
            'commit': v.get('commit', ''),
        }
    
    return data1

# def dump_profile(profile: T.Profile1, path: str) -> None:
#     data = profile.copy()
