import ast
import astpretty

from lk_utils import loads


def show_ast(file: str) -> None:
    code: str = loads(file)
    tree = ast.parse(code)
    astpretty.pprint(tree)
    # for node in ast.walk(tree):
    #     print(node)
