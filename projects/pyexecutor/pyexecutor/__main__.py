from argsense import cli

from .main import launch_script
from .main import run

cli.add_cmd(run)
cli.add_cmd(launch_script)

if __name__ == '__main__':
    # py -m pyx -h
    cli.run(run)
