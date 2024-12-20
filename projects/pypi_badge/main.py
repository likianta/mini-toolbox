from textwrap import dedent

from argsense import cli


@cli.cmd()
def main(package_name: str) -> None:
    print(
        dedent(
            '''
            - [![PyPI version](https://badge.fury.io/py/{0}.svg)] \\
              (https://badge.fury.io/py/{0})
            - [![Downloads](https://static.pepy.tech/badge/{0})] \\
              (https://pepy.tech/project/{0})
            - [![Downloads](https://static.pepy.tech/badge/{0}/month)] \\
              (https://pepy.tech/project/{0})
            '''
            .format(package_name)
        )
        .strip()
        .replace(' \\\n  ', '')
        .replace('- ', '', 1)
        .replace('\n- ', ' ')
    )


if __name__ == '__main__':
    cli.run(main)
