import sys
from argsense import cli

from .main import fmt

cli.add_cmd(fmt)


def _exec() -> None:
    """
    poetry build to be executable script.
    """
    fmt(sys.argv[1])


if __name__ == '__main__':
    # pox -m lkfmt -h
    # pox -m lkfmt $file
    cli.run(fmt)
