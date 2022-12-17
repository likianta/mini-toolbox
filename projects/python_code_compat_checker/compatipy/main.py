import ast
from posixpath import isfile

from lk_utils import fs

from .type_annotations_checker import check_typing_annotations


def check_py38(path: str) -> None:
    if isfile(path):
        err_count = _check_file(path)
    else:
        err_count = _check_dir(path)
    if err_count:
        print(':r', f'[#e64747][b]{err_count}[/] errors found (see above).[/]')
    else:
        print(':r', '[green]done with no error found.[/]')


def _check_dir(dir_: str) -> int:
    err_count = 0
    for f in fs.findall_files(dir_, '.py'):
        with open(f.path) as fh:
            code = fh.read()
            future_enabled = 'from __future__ import annotations' in code
            collector = tuple(check_typing_annotations(
                ast.parse(code), future_enabled
            ))
        if collector:
            print(':ri0s', f'[red]found [bright_red b]{len(collector)}[/] '
                           f'errors in [magenta]{f.name}[/]:[/]')
            for node, msg in collector:
                report(node, msg, filepath=f.relpath, filename=f.name)
            err_count += len(collector)
        else:
            print(':ri0s', f'[green dim]found no error in [cyan]{f.name}[/][/]')
    return err_count


def _check_file(file: str, _info=None) -> int:
    count = 0
    
    if _info is None:
        _info = {'filepath': file,
                 'filename': fs.filename(file)}
    
    with open(file) as f:
        code = f.read()
        future_enabled = 'from __future__ import annotations' in code
        for node, msg in check_typing_annotations(
                ast.parse(code), future_enabled
        ):
            count += 1
            report(node, msg, **_info)
    return count


# -----------------------------------------------------------------------------

def report(node: ast.AST, msg: str = '', **kwargs):
    print(':ir', '''
        [cyan]path:[/] [magenta]{filepath}[/]
        [cyan]name:[/] [yellow]{filename}[/]
        [cyan]line:[/] [green]\\[[b]{row}[/][dim]:{col}[/]][/]
        [cyan]info:[/] [red]{msg}[/]
    '''.format(
        filepath=kwargs['filepath'],
        filename=kwargs['filename'],
        row=node.lineno,
        col=node.col_offset,
        msg=msg,
    ))
