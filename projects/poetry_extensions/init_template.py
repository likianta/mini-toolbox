import os
import re

import lk_logger
from argsense import cli
from lk_utils import dedent
from lk_utils import fs

lk_logger.setup(quiet=True, show_varnames=True)

template = dedent(
    """
    [project]
    name = "<package_name>"
    version = "0.1.0"
    description = ""
    # readme = "README.md"
    authors = [{ name = "Likianta", email = "likianta@foxmail.com" }]
    packages = [{ include = "<package_name_snakecase>" }]
    requires-python = ">=<pyversion>"
    dynamic = ["dependencies"]
    # license = "MIT"
    
    # [project.urls]
    # homepage = "https://github.com/likianta/<package_name>"
    
    [tool.poetry.dependencies]
    python = "^<pyversion>"
    
    [[tool.poetry.source]]
    name = "tsinghua"
    url = "https://pypi.tuna.tsinghua.edu.cn/simple/"
    priority = "primary"
    
    [[tool.poetry.source]]
    name = "likianta"
    url = "<likianta_source_url>"
    priority = "supplemental"

    [build-system]
    requires = ["poetry-core"]
    build-backend = "poetry.core.masonry.api"
    """
)


@cli
def main(
    target_dir: str,
    package_name: str = None,
    pyversion: str = '3.12',
    custom_source_url: str = 'http://localhost:2131/',
) -> None:
    """
    params:
        pyversion (-v):
        custom_source_url (-u):
            - http://localhost:2131/
            - http://47.102.108.149:2131/
            - http://likianta.top:2131/
    """
    if target_dir is None:
        target_dir = os.getcwd()
    if package_name is None:
        package_name = (
            fs.dirname(target_dir)
            .lower()
            .replace('_', '-')
            .replace(' ', '-')
        )
    assert re.match(r'[-a-z]+', package_name)
    print(package_name, ':v2')
    
    output = (
        template
        .replace('<package_name>', package_name)
        .replace('<package_name_snakecase>', package_name.replace('-', '_'))
        .replace('<pyversion>', pyversion)
        .replace('<likianta_source_url>', custom_source_url)
    )
    fs.dump(output, target_dir + '/pyproject.toml', 'plain')


if __name__ == '__main__':
    # pox projects/poetry_extensions/init_template.py <dir>
    # pox projects/poetry_extensions/init_template.py <dir> -v 3.8
    cli.run(main)
