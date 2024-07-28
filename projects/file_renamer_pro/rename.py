import hashlib
import re

from argsense import cli
from lk_utils import fs
from lk_utils.time_utils import get_mtime


@cli.cmd()
def main(dir_i: str) -> None:
    for f in tuple(fs.find_files(dir_i)):
        if re.match(r'^\d{8}-\d{6}-[0-9a-f]{8}\.\w+$', f.name):
            continue
        i = f.path
        o = '{}/{}.{}'.format(dir_i, _get_uid(f.path), f.ext)
        _print_change(f.name, o.rsplit('/', 1)[1])
        fs.move(i, o)


@cli.cmd()
def all_upper_case(dir_i: str) -> None:
    for f in tuple(fs.find_files(dir_i)):
        if f.name.isupper():
            continue
        i = f.path
        o = '{}/{}.{}'.format(dir_i, f.stem.upper(), f.ext)
        _print_change(f.name, o.rsplit('/', 1)[1])
        fs.move(i, o + '.tmp')
        fs.move(o + '.tmp', o)


def _get_uid(file: str) -> str:
    # return format: '<ymd>-<hns>-<md5_in_8_chars>'
    return '{}-{}'.format(
        get_mtime(file, 'ymd-hns'),
        hashlib.md5(fs.load(file, 'binary')).hexdigest()[::4]
    )


def _print_change(old: str, new: str) -> None:
    print(':rpi', '[red]{}[/] -> [green]{}'.format(old, new))


if __name__ == '__main__':
    # pox projects/file_renamer_pro/rename.py main <dir_i>
    # pox projects/file_renamer_pro/rename.py all-upper-case <dir_i>
    cli.run()
