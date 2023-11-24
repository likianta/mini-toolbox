import os

import lk_logger
from argsense import cli
from lk_utils import dumps
from lk_utils import fs
from lk_utils.textwrap import dedent

lk_logger.setup(quiet=True, show_varnames=True)

template = dedent("""
    [tool.poetry]
    name = "$project_name_kebabcase"
    version = "0.1.0"
    description = ""
    authors = ["likianta <likianta@foxmail.com>"]
    # readme = "README.md"
    packages = [{ include = "$project_name_snakecase" }]
    
    [tool.poetry.dependencies]
    python = "^3.11"
    
    [[tool.poetry.source]]
    name = "tsinghua"
    url = "https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple/"
    priority = "default"
    
    [[tool.poetry.source]]
    name = "likianta-hosted"
    url = "http://likianta.pro:2006/"
    priority = "supplemental"

    [build-system]
    requires = ["poetry-core"]
    build-backend = "poetry.core.masonry.api"
""")


@cli.cmd()
def main(target_dir: str = None, package_name: str = None) -> None:
    if target_dir is None:
        target_dir = os.getcwd()
    
    project_name = fs.dirname(target_dir)
    assert project_name == (
        package_name.lower().replace('_', '-').replace(' ', '-')
    ), ('project name must be a kebab-case string!', project_name)
    
    if package_name is None:
        package_name = project_name.replace('-', '_')
    
    print(target_dir, project_name, package_name, ':lv2')
    
    output = (
        template
        .replace('$project_name_kebabcase', project_name)
        .replace('$project_name_snakecase', package_name)
    )
    dumps(output, target_dir + '/pyproject.toml')


if __name__ == '__main__':
    # pox poetry_extensions/init_template.py
    cli.run(main)
