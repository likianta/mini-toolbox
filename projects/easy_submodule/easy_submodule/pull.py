from lk_utils import run_cmd_args

from .lock import get_current_info
from .profile import load_profile


def pull_submodules(profile_path: str) -> None:
    """
    this is similar to `.clone` but does `git pull` instead of `git clone`.
    
    https://stackoverflow.com/questions/31462683/git-pull-till-a-particular |
    -commit
    """
    profile = load_profile(profile_path)
    for k, v in profile.items():
        curr_branch, curr_commit = get_current_info(v['path'])
        new_branch, new_commit = v['branch'], v['commit']
        if curr_branch != new_branch:
            run_cmd_args(
                'git', 'checkout', new_branch, verbose=True, cwd=v['path']
            )
        if curr_commit != new_commit:
            run_cmd_args(
                'git', 'fetch', verbose=True, cwd=v['path']
            )
            run_cmd_args(
                'git', 'merge', new_commit, verbose=True, cwd=v['path']
            )
