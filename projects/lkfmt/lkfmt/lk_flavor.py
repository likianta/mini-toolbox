"""
likianta flavored code formatting style.
    - ensure newline at the end of file
    - keep indents on empty lines
    - align dict key-value pairs by colon
    - align variable assignments by equal sign
"""
import re
import typing as t


def keep_indents(code: str) -> str:
    _leading_spaces = re.compile(r'^ *')
    
    def walk() -> t.Iterator[str]:
        lines0 = tuple(code.splitlines())
        lines1 = lines0[1:] + ('',)
        
        for curr_line, next_line in zip(lines0, lines1):
            if not curr_line:
                if next_line:
                    yield '{}{}'.format(
                        _leading_spaces.match(next_line).group(0), curr_line
                    )
                    continue
            yield curr_line
    
    return '\n'.join(walk())


def align_dict_items(code: str) -> str:
    pass


def align_vars_assignments(code: str) -> str:
    pass


def ensure_newline_at_eof(code: str) -> str:
    return code + '\n'
