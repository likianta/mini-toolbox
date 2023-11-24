import typing as t

from lk_utils import dumps
from lk_utils import fs
from lk_utils import loads
from toml import dumps as tdumps  # pip install toml

from .profile import load_profile


def merge_deps(
    root: str,
    include_dev_group: bool = False,
    _skip_recorded_names: t.Tuple[str, ...] = (),
    _prefix: str = '',
    _dump: bool = True,
) -> dict:
    all_subproj_deps = {}
    root_name = fs.dirname(root)
    if _prefix == '':
        _prefix = root_name
    
    if fs.exists(x := f'{root}/.submodules.yaml'):
        for name, info in load_profile(x).items():
            if name in _skip_recorded_names:
                continue
            all_subproj_deps[name] = get_subproj_deps(
                info['path'], include_dev_group, prefix=_prefix
            )
            # print(':v', 'dive into recursive loop', f'{_prefix}/{name}')
            all_subproj_deps.update(
                merge_deps(
                    root=info['path'],
                    include_dev_group=include_dev_group,
                    _skip_recorded_names=(
                        _skip_recorded_names + tuple(all_subproj_deps.keys())
                    ),
                    _prefix=f'{_prefix}/{name}',
                    _dump=False,
                )
            )
    
    if _dump:
        temp = {'tool': {'poetry': {'group': (groups := {})}}}
        for name, deps in all_subproj_deps.items():
            groups[name] = {'dependencies': deps}
        _add_content_to_pyproj_file(
            tdumps(temp),
            f'{root}/pyproject.toml'
        )
    
    return all_subproj_deps


def get_subproj_deps(
    root: str, include_dev_group: bool = False, prefix: str = ''
) -> dict:
    conf_i = loads(f'{root}/pyproject.toml')
    out = {}
    subproj_name = fs.dirname(root)
    
    print(':v2si', f'{prefix}/{subproj_name}')
    for k, v in conf_i['tool']['poetry']['dependencies'].items():
        if k == 'python': continue
        out[k] = v
    
    if 'group' in conf_i['tool']['poetry']:
        for group_name, dict_ in conf_i['tool']['poetry']['group'].items():
            if group_name == 'dev' and not include_dev_group: continue
            print(f'{prefix}/{subproj_name}:{group_name}', ':ivs')
            out.update(dict_['dependencies'])
    
    return out


def _add_content_to_pyproj_file(additional_content: str, file: str) -> None:
    content_i: str = loads(file, ftype='plain')
    if '# --- auto gen' in content_i:
        content_i = content_i[:content_i.index('# --- auto gen')]
    content_o = '{}\n\n# --- auto gen\n\n{}'.format(
        content_i.rstrip(), additional_content.lstrip()
    )
    dumps(content_o, file, ftype='plain')
