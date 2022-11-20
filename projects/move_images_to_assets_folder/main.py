import subprocess

from argsense import cli
from lk_utils import fs


@cli.cmd()
def main(dir_i: str, dir_o: str) -> None:
    dir_i, dir_o = map(fs.normpath, (dir_i, dir_o))
    print(dir_i)
    print(dir_o)
    print(':f2s')
    
    dirname_o = fs.dirname(dir_o)
    images = []
    
    while True:
        cmd = input('press enter to continue, or "x" to exit: ')
        if cmd == 'x':
            print(':t', 'exit')
            break
        
        for f in fs.find_files(dir_i):
            file_i = f.path
            file_o = f'{dir_o}/{f.name}'
            md_link = f'![{f.name_stem}](.assets/{dirname_o}/{f.name})'
            fs.move(file_i, file_o)
            print(md_link, ':i')
            images.append(md_link)
        
        if images:
            _copy_2_clipboard('\n'.join(images))
            images.clear()
        else:
            print(':vs', 'no image found')
        
        print(':i0sf2')


def _copy_2_clipboard(text: str) -> None:
    """
    https://stackoverflow.com/questions/11063458/python-script-to-copy-text-to
    -clipboard
    """
    subprocess.check_call('echo {}|clip'.format(text), shell=True)


if __name__ == '__main__':
    cli.run(main)
