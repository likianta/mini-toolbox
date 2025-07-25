"""
use ast to parse the source code and find all imports.
if imports in pyproject.toml are defined but not used across the source code, -
print them out.
"""
import ast

import lk_logger
from argsense import cli
from lk_utils import fs

lk_logger.update(show_varnames=True)


@cli
def main(
    source_dir: str,
    include_dev_group: bool = False,
    ignored: str = None,
) -> None:
    """
    params:
        include_dev_group (-d):
        ignored (-i):
        
    required:
        <user_project>
        |- <source>         # <- `source_dir`
        |- pyproject.toml
    """
    project_dir = fs.parent(source_dir)
    assert fs.exists(f'{project_dir}/pyproject.toml')
    
    imported_packages = set()  # {pkg_name, ...}
    # {`aaa_bbb`: `ccc-ddd`, ...}
    known_aliases = {
        'code_editor': 'streamlit-code-editor',
        'google'     : 'google-cloud-translate',
        'hid'        : 'hidapi',
        'pil'        : 'pillow',
        'serial'     : 'pyserial',
        'yaml'       : 'pyyaml',
        'zmq'        : 'pyzmq',
    }
    for f in fs.findall_files(source_dir, ".py"):
        print(f.relpath, ':is')
        code = fs.load(f.path)
        try:
            tree = ast.parse(code)
        except TabError as e:
            print(':v6', f.relpath, e)
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top_name = alias.name.split(".")[0].lower()
                    pkg_name = known_aliases.get(
                        top_name, top_name.replace("_", "-")
                    )
                    imported_packages.add(pkg_name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    top_name = node.module.split(".")[0].lower()
                    pkg_name = known_aliases.get(
                        top_name, top_name.replace("_", "-")
                    )
                    imported_packages.add(pkg_name)
    print(':d')
    print(len(imported_packages))
    
    defined_packages = set()
    conf = fs.load(f"{project_dir}/pyproject.toml")
    for x in conf["tool"]["poetry"]["dependencies"]:
        if x == "python":
            continue
        defined_packages.add(x)
    if "group" in conf["tool"]["poetry"]:
        for k, x in conf["tool"]["poetry"]["group"].items():
            if k == 'dev' and not include_dev_group:
                continue
            for y in x["dependencies"]:
                defined_packages.add(y)
    print(len(defined_packages))
    
    ignored = set() if ignored is None else set(ignored.split(','))
    if 'poetry-extensions' in conf['tool']:
        ignored.update(
            conf['tool']['poetry-extensions']['ignore-unused-packages']
        )
    
    flag = 0
    for x in sorted(defined_packages):
        if x not in imported_packages:
            if x not in ignored:
                flag = 1
                print(x, ":iv6")
    if not flag:
        print(':v4', 'satisfying all packages.')


if __name__ == "__main__":
    # pox projects/poetry_extensions/find_unused_dependencies.py <src_dir>
    # pox projects/poetry_extensions/find_unused_dependencies.py <src_dir> :true
    cli.run(main)
