from argsense import cli

from .main import run as _run


def run() -> None:
    cli.add_cmd(_run)
    cli.run(_run)
