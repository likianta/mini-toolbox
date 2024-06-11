from argsense import cli

from .debugger import run_client
from .debugger import run_server

cli.add_cmd(run_server, 'launch-server')
cli.add_cmd(run_client, 'connect-debugger')

if __name__ == '__main__':
    # pox -m remote_ipython connect-debugger <kernel_id>
    cli.run()
