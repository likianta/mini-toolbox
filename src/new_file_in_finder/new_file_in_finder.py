from os.path import exists

from argsense import cli
from lk_utils import fs


@cli.cmd()
def main(root_dir: str):
    uid_2_path = {}
    
    def walk(dir_: str, parent_level: str) -> None:
        for i, d in enumerate(fs.find_dirs(dir_), 1):
            if d.name == '.assets':
                continue
            level = (parent_level + '-' + str(i)).lstrip('-')
            uid_2_path[level] = d.path
            walk(d.path, level)
    
    def show() -> None:
        for level in sorted(uid_2_path):
            path = uid_2_path[level]
            print('[red]\\[{}][/] {} [dim]({})[/]'.format(
                level, fs.dirname(path), fs.relpath(path, root_dir)
            ), ':rs2')
    
    walk(root_dir, '')
    show()
    
    print(':df2')
    
    while True:
        cmd = input('input `uid; name` to make a file in the dir: ')
        match cmd:
            case 'x':  # exit
                break
            case 'h':  # help
                uid_2_path.clear()
                walk(root_dir, '')
                show()
                print(':sf2')
            case _:  # make file
                try:
                    uid, name = cmd.split('; ', 1)
                    path = uid_2_path[uid] + '/' + name
                    if not exists(path):
                        open(path, 'w').close()
                    else:
                        print('[dim]file already exists[/]', ':r')
                    print('done', path)
                except Exception as e:
                    print(':v3', e)
                    continue


if __name__ == '__main__':
    cli.run(main)
