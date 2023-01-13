"""
TODO: watchdog
"""
import re
import subprocess
from shutil import move
from sys import platform

import lk_logger
from argsense import cli
from lk_utils import find_files
from lk_utils.time_utils import timestamp

lk_logger.setup(quiet=True, show_funcname=False)


@cli.cmd()
def main(
        dir_i: str,
        dir_o: str,
        post_rename=False,
        add_to_clipboard=False,
        paste_format='![]({name})',
) -> None:
    regex: re.Pattern
    exclusion_list = set()
    
    while True:
        print(':f2d')
        cmd = input('command: ')
        
        match cmd:
            case 'h':  # help
                print('''
                    f: change paste format
                    h: help
                    m: move file
                    q: quit
                    r: set regex pattern
                ''')
            # -----------------------------------------------------------------
            case 'f':  # change paste format
                paste_format = input('set new paste format: ')
            case 'm':  # move
                for f in find_files(dir_i):
                    if f.name in exclusion_list:
                        continue
                    if regex.search(f.name):  # noqa
                        i = f.path
                        if post_rename:
                            suffix = f.name.rsplit('.', 1)[-1]
                            new_name = f'{timestamp("ymdhns")}.{suffix}'
                        else:
                            new_name = f.name
                        o = f'{dir_o}/{new_name}'
                        
                        print(f'move: [red]{f.name}[/] -> [green]{new_name}[/]',
                              ':r')
                        move(i, o)
                        
                        if add_to_clipboard:
                            text = paste_format.format(name=new_name)
                            _add_to_clipboard(text)
                    else:
                        exclusion_list.add(f.name)
            case 'q':  # quit
                print('quit')
                break
            case 'r':  # regex
                regex = re.compile(input('regex: '))
                print(regex)


def _add_to_clipboard(text: str) -> None:
    # https://stackoverflow.com/a/17371323
    if platform == 'darwin':
        subprocess.run(['pbcopy'], text=True, input=text)
    elif platform == 'win32':
        subprocess.run(['clip'], text=True, input=text)
    else:
        subprocess.run(['xclip'], text=True, input=text)
    print(f'added to clipboard: {text}')


if __name__ == '__main__':
    cli.run(main)
