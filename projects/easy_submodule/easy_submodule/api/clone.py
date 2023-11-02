from lk_utils import fs
from lk_utils import run_cmd_args

from ..profile import load_profile


def clone_submodules(profile_path: str) -> None:
    profile = load_profile(profile_path)
    
    # premake paths
    dirs = set(fs.parent(v['path']) for v in profile.values())
    for d in sorted(dirs):
        fs.make_dirs(d)
    
    for name, info in profile.items():
        print('cloning {} to {}'.format(name, fs.relpath(info['path'])),
              ':dv2i2')
        run_cmd_args(
            'git', 'clone', info['url'], info['path'],
            ('-b', info['branch']),
            verbose=True
        )
        
        # https://stackoverflow.com/questions/31462683/git-pull-till-a |
        # -particular-commit
        # https://stackoverflow.com/a/48728993
        if info['commit']:
            run_cmd_args(
                'git', 'reset', '--hard', info['commit'],
                verbose=True, cwd=info['path']
            )
