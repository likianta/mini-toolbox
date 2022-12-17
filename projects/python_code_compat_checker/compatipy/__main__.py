import ast

import astpretty
from argsense import cli

from .main import check_py38
from .main import check_typing_annotations
from .play import show_ast

cli.add_cmd(check_py38)
cli.add_cmd(show_ast)


@cli.cmd()
def check_subscript(file_i: str):
    with open(file_i, 'r') as f:
        code = f.read()
        if 'from __future__ import annotations' in code:
            future_enabled = True
        else:
            future_enabled = False
        tree = ast.parse(code)
        check_typing_annotations(tree, future_enabled)


@cli.cmd()
def ast_dump(file_i: str, file_o: str = None) -> None:
    fileobj_i = open(file_i, 'r')
    fileobj_o = open(file_o, 'w') if file_o else None
    
    tree = ast.parse(fileobj_i.read())
    dump = astpretty.pformat(tree)
    print(dump)
    
    fileobj_i.close()
    if file_o:
        fileobj_o.write(dump)
        fileobj_o.close()


if __name__ == '__main__':
    cli.run()
