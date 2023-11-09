"""
why this script?
    since `poetry export` cannot export 'pythonnet>=3.0.0'.
"""
import typing as t
from collections import defaultdict

from argsense import cli
from lk_utils import dumps
from lk_utils import fs
from lk_utils import loads


@cli.cmd()
def main(
    cwd: str = '.',
    file_o: str = None,
    include_dev_group: bool = False,
    only_top_deps: bool = True,
    flatten_top_deps: bool = False,
) -> None:
    """
    kwargs:
        include_dev_group (-d):
        flatten_top_deps:
            FIXME: do not set it true, there is a bug which leaks non-relevant  |
                platform dependencies into the flatten list.
    """
    file_i = f'{cwd}/poetry.lock'
    file_o = file_o or f'{cwd}/requirements.lock'
    
    data_i = loads(file_i, 'toml')
    data_o = [
        '# pip install -r {} {}'.format(
            fs.basename(file_o),
            '--no-deps' if flatten_top_deps else '',
        ).rstrip(),
        '--index-url https://pypi.tuna.tsinghua.edu.cn/simple',
        '',
    ]
    
    info = defaultdict(lambda: {
        'version': '',
        'url'    : '',
        'markers': '',
    })
    
    if only_top_deps:
        top_deps = _get_top_dependencies(
            f'{cwd}/pyproject.toml', include_dev_group
        )
        if flatten_top_deps:
            all_deps = _get_all_dependencies(data_i)
            top_deps = set(_extend_top_dependencies(top_deps, all_deps))
        else:
            top_deps = set(top_deps)
    else:
        top_deps = None
    
    for item in data_i['package']:
        name = _normalize_name(item['name'])
        if top_deps and name not in top_deps:
            continue
        
        info[name]['version'] = item['version']
        if item['source']['type'] == 'legacy':
            if item['source']['reference'] == 'likianta-hosted':
                info[name]['url'] = '{}/{}/{}'.format(
                    item['source']['url'],
                    name,
                    item['files'][0]['file'],
                )
        else:
            info[name]['url'] = item['source']['url']
        
        if 'dependencies' in item:
            for dep_name, dep_spec in item['dependencies'].items():
                dep_name = _normalize_name(dep_name)
                if isinstance(dep_spec, dict) and 'markers' in dep_spec:
                    info[dep_name]['markers'] = dep_spec['markers']
    
    for name in sorted(info.keys()):
        dict_ = info[name]
        print(name, ':i')
        if dict_['version']:
            if dict_['url']:
                line = '{} @ {}'.format(name, dict_['url'])
            else:
                line = '{}=={}'.format(name, dict_['version'])
            if dict_['markers']:
                line += ' ; {}'.format(dict_['markers'])
            data_o.append(line)
        else:
            print(f'skip {name}', ':v3s')
    
    dumps(data_o, file_o, 'plain')
    print('done', fs.relpath(file_o), ':t')


def _get_top_dependencies(
    pyproj_file: str, include_dev_group: bool = False
) -> t.Iterator[str]:
    data = loads(pyproj_file)
    for name in data['tool']['poetry']['dependencies'].keys():
        if name == 'python':
            continue
        yield _normalize_name(name)
    if 'group' in data['tool']['poetry']:
        for key, value in data['tool']['poetry']['group'].items():
            if key == 'dev' and not include_dev_group:
                continue
            for name in value['dependencies'].keys():
                yield _normalize_name(name)


def _get_all_dependencies(locked_data: dict) -> dict:
    out0 = {}
    for item in locked_data['package']:
        name = _normalize_name(item['name'])
        out0[name] = set()
        if 'dependencies' in item:
            for dep_name in item['dependencies'].keys():
                dep_name = _normalize_name(dep_name)
                out0[name].add(dep_name)
    
    def flatten(
        direct_deps: t.Set[str], _recorded: t.Set = None
    ) -> t.Iterator[str]:
        if _recorded is None:
            _recorded = set()
        for dep in direct_deps:
            if dep in _recorded:
                continue
            else:
                yield dep
                _recorded.add(dep)
            # if dep in out0:
            indirect_deps = out0[dep]
            yield from flatten(indirect_deps, _recorded)
    
    out1 = {}
    for k, v in out0.items():
        out1[k] = set(flatten(v))
    return out1


def _extend_top_dependencies(
    top_deps: t.Iterable[str], all_deps: dict
) -> t.Iterator[str]:
    for d in top_deps:
        yield d
        yield from all_deps[d]


def _normalize_name(raw: str) -> str:
    return raw.lower().replace('_', '-').replace('.', '-')
    #   e.g. 'jaraco.classes' -> 'jaraco-classes'


if __name__ == '__main__':
    # pox poetry_extensions/requirements_lock_2.py
    cli.run(main)
