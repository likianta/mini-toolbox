import typing as t

from lk_utils import dumps
from lk_utils import fs
from lk_utils import run_cmd_args

from .profile import T
from .profile import load_profile


def lock_submodules(profile_path: str) -> None:
    data0: T.Profile0 = load_profile(profile_path)
    data1: T.Profile1 = {}
    
    base_dir = fs.parent(profile_path)
    
    for k, v in data0.items():
        branch, commit = get_current_info(v['path'])
        data1[k] = {
            'url'   : v['url'],
            'path'  : fs.relpath(v['path'], base_dir),
            'branch': branch,
            'commit': commit,
        }
    
    dumps(data1, profile_path)


def get_current_info(working_dir: str) -> t.Tuple[str, str]:
    # get git branch & commit info
    # https://stackoverflow.com/questions/949314/how-do-i-get-the-hash-for |
    # -the-current-commit-in-git
    branch: str = run_cmd_args('git', 'branch', '--show', cwd=working_dir)
    commit: str = run_cmd_args('git', 'rev-parse', 'HEAD', cwd=working_dir)
    # commit: str = run_cmd_args('git', 'rev-parse', '--short', 'HEAD')
    return branch, commit
