"""
python difflib htmldiff:
    https://testdriven.io/tips/43480c4e-72db-4728-8afd-0b0f4f42d4f4/
"""
import difflib

from argsense import cli
from lk_utils import dumps
from lk_utils import fs
from lk_utils import loads


@cli.cmd()
def main(file_a: str, file_b: str, open_now=False) -> None:
    lines_a = loads(file_a, 'plain').splitlines()
    lines_b = loads(file_b, 'plain').splitlines()
    diff = difflib.HtmlDiff().make_file(
        lines_a, lines_b
    )
    dumps(diff, '{}/diff.html'.format(fs.parent(file_a)))
    if open_now:
        import webbrowser
        webbrowser.open('diff.html')


if __name__ == '__main__':
    cli.run(main)
