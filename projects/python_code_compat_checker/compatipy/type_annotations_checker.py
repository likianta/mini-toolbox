import ast
import typing as t


class T:
    _RichText = str
    CheckedInfo = t.Iterator[t.Tuple[ast.AST, _RichText]]


def check_typing_annotations(
        tree: ast.AST,
        future_annotations=False,
        typing_extensions=False
) -> t.Iterator[tuple]:
    
    def _check_py310_new_typings(node: ast.Attribute) -> T.CheckedInfo:
        if node.attr == 'ParamSpec':
            if not typing_extensions:
                yield node, (
                    '[red][b]`ParamSpec`[/] is not available in '
                    'Python 3.9 and lower![/]'
                )
    
    # noinspection PyUnresolvedReferences,PyShadowingBuiltins,PyTypeChecker
    def _check_subscriptable(node: ast.Subscript) -> T.CheckedInfo:
        if isinstance((node1 := node.value), ast.Name):
            if (id := node1.id) in ('dict', 'list', 'set', 'tuple'):
                if node.lineno in weak_warning_linenos:
                    yield node, (
                        f'[red dim][b]`{id}`[/] is not '
                        f'subscriptable! [i](missing future '
                        f'annotations)[/][/]'
                    )
                else:
                    yield node, (
                        f'[red][b]`{id}`[/] is not subscriptable![/]'
                    )
        elif isinstance((node2 := node.slice), ast.Subscript):
            yield from _check_subscriptable(node2)
    
    # noinspection PyUnresolvedReferences
    def _check_union_operator(node: ast.BinOp) -> T.CheckedInfo:
        def _get_plain_literal(node) -> str:
            if isinstance(node, ast.Name):
                return node.id
            elif isinstance(node, ast.Constant):
                return str(node.value)
            else:
                raise ValueError(node)
        
        if isinstance(node.op, ast.BitOr):
            left = _get_plain_literal(node.left)
            right = _get_plain_literal(node.right)
            if left in ('dict', 'list', 'set', 'tuple') or \
                    right in ('dict', 'list', 'set', 'tuple'):
                if node.lineno in weak_warning_linenos:
                    yield node, (
                        '[red dim]union operator: `{} | {}` '
                        '[i](missing future annotations)[/][/]'.format(
                            left, right
                        )
                    )
                else:
                    yield node, (
                        'union operator: `{} | {}`'.format(left, right)
                    )
    
    # -------------------------------------------------------------------------
    
    skipped_linenos = set()
    weak_warning_linenos = set()
    
    for node in ast.walk(tree):  # note: ast.walk is breadth-first.
        # if hasattr(node, 'lineno'):
        #     print(':i', node.lineno, node)
        
        if getattr(node, 'lineno', None) in skipped_linenos:
            if isinstance(node, ast.NamedExpr):
                # noinspection PyTypeChecker
                for subnode in ast.walk(node):
                    if isinstance(subnode, ast.Subscript):
                        yield from _check_subscriptable(subnode)
            continue
        
        if isinstance(node, ast.Attribute):
            yield from _check_py310_new_typings(node)
            continue
        
        if isinstance(node, ast.Subscript):
            yield from _check_subscriptable(node)
            continue
        
        if isinstance(node, ast.BinOp):
            yield from _check_union_operator(node)
            continue
        
        if isinstance(node, (ast.AnnAssign, ast.FunctionDef)):
            if future_annotations:
                for lineno in range(node.lineno, node.end_lineno + 1):
                    skipped_linenos.add(lineno)
            else:
                for lineno in range(node.lineno, node.end_lineno + 1):
                    weak_warning_linenos.add(lineno)
            continue
