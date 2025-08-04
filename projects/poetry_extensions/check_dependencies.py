import ast
import lk_logger
from argsense import cli
from lk_utils import fs

lk_logger.update(show_varnames=True)


@cli
def main(
    source_dir: str,
    include_dev_group: bool = False,
    ignored: str = None,
    tkinter_is_installed: bool = True,
) -> None:
    """
    find out "unused" and "missing" dependencies by going through the source -
    code.
    how does it work?
        we use ast to parse the source code and find out all imports.
        if imports found but not listed in pyproject.toml, it reports -
        "missing"; on the other hand it reports "unused".
    
    params:
        include_dev_group (-d):
        ignored (-i):
        tkinter_is_installed (-t):
        
    required:
        <user_project>
        |- <source>         # <- `source_dir`
        |- pyproject.toml
    """
    project_dir = fs.parent(source_dir)
    assert fs.exist(f'{project_dir}/pyproject.toml')
    
    imported_packages = set()  # {pkg_name, ...}, names are in kebab-case.
    known_aliases = {  # {imported_name: package_name, ...}
        'code_editor': 'streamlit-code-editor',
        'google'     : 'google-cloud-translate',
        'hid'        : 'hidapi',
        'pil'        : 'pillow',
        'serial'     : 'pyserial',
        'yaml'       : 'pyyaml',
        'zmq'        : 'pyzmq',
    }
    for f in fs.findall_files(source_dir, ".py"):
        print(f.relpath, ':is')
        code = fs.load(f.path)
        try:
            tree = ast.parse(code)
        except TabError as e:
            print(':v6', f.relpath, e)
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top_name = alias.name.split(".")[0].lower()
                    pkg_name = known_aliases.get(
                        top_name, top_name.lower().replace("_", "-")
                    )
                    imported_packages.add(pkg_name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    top_name = node.module.split(".")[0].lower()
                    pkg_name = known_aliases.get(
                        top_name, top_name.lower().replace("_", "-")
                    )
                    imported_packages.add(pkg_name)
    print(':d')
    print(len(imported_packages))
    
    defined_packages = set()
    conf = fs.load(f"{project_dir}/pyproject.toml")
    for x in conf["tool"]["poetry"]["dependencies"]:
        if x == "python":
            continue
        defined_packages.add(x)
    if "group" in conf["tool"]["poetry"]:
        for k, x in conf["tool"]["poetry"]["group"].items():
            if k == 'dev' and not include_dev_group:
                continue
            for y in x["dependencies"]:
                defined_packages.add(y)
    print(len(defined_packages))
    
    ignored = set() if ignored is None else set(ignored.split(','))
    if 'poetry-extensions' in conf['tool']:
        ignored.update(
            conf['tool']['poetry-extensions']['ignore-unused-packages']
        )
    
    unused = []
    for x in sorted(defined_packages):
        if x not in imported_packages:
            if x not in ignored:
                unused.append(x)
                print(x, ":iv6")
    print(unused, ':lv6')
    
    missing = []
    std_names = (
        # ref: `[prj] python-tree-shaking : /tree_shaking/module.py :
        # ModuleInspector : __init__ : known_stdlib_module_names`.
        '__future__',
        '_abc', '_aix_support', '_ast', '_asyncio',
        '_bisect', '_blake2', '_bootsubprocess', '_bz2',
        '_codecs', '_codecs_cn', '_codecs_hk', '_codecs_iso2022', '_codecs_jp',
        '_codecs_kr', '_codecs_tw', '_collections', '_collections_abc',
        '_compat_pickle', '_compression', '_contextvars', '_crypt', '_csv',
        '_ctypes', '_curses', '_curses_panel',
        '_datetime', '_dbm', '_decimal',
        '_elementtree',
        '_frozen_importlib', '_frozen_importlib_external', '_functools',
        '_gdbm',
        '_hashlib', '_heapq',
        '_imp', '_io',
        '_json',
        '_locale', '_lsprof', '_lzma',
        '_markupbase', '_md5', '_msi', '_multibytecodec', '_multiprocessing',
        '_opcode', '_operator', '_osx_support', '_overlapped',
        '_pickle', '_posixshmem', '_posixsubprocess', '_py_abc', '_pydecimal',
        '_pyio',
        '_queue',
        '_random',
        '_sha1', '_sha256', '_sha3', '_sha512', '_signal', '_sitebuiltins',
        '_socket', '_sqlite3', '_sre', '_ssl', '_stat', '_statistics',
        '_string', '_strptime', '_struct', '_symtable',
        '_thread', '_threading_local', '_tkinter', '_tracemalloc',
        '_uuid',
        '_warnings', '_weakref', '_weakrefset', '_winapi',
        '_zoneinfo',
        'abc', 'aifc', 'antigravity', 'argparse', 'array', 'ast', 'asynchat',
        'asyncio', 'asyncore', 'atexit', 'audioop',
        'base64', 'bdb', 'binascii', 'binhex', 'bisect', 'builtins', 'bz2',
        'cProfile', 'calendar', 'cgi', 'cgitb', 'chunk', 'cmath', 'cmd', 'code',
        'codecs', 'codeop', 'collections', 'colorsys', 'compileall',
        'concurrent', 'configparser', 'contextlib', 'contextvars', 'copy',
        'copyreg', 'crypt', 'csv', 'ctypes', 'curses',
        'dataclasses', 'datetime', 'dbm', 'decimal', 'difflib', 'dis',
        'distutils', 'doctest',
        'email', 'encodings', 'ensurepip', 'enum', 'errno',
        'faulthandler', 'fcntl', 'filecmp', 'fileinput', 'fnmatch', 'fractions',
        'ftplib', 'functools',
        'gc', 'genericpath', 'getopt', 'getpass', 'gettext', 'glob', 'graphlib',
        'grp', 'gzip',
        'hashlib', 'heapq', 'hmac', 'html', 'http',
        'idlelib', 'imaplib', 'imghdr', 'imp', 'importlib', 'inspect', 'io',
        'ipaddress', 'itertools',
        'json',
        'keyword',
        'lib2to3', 'linecache', 'locale', 'logging', 'lzma',
        'mailbox', 'mailcap', 'marshal', 'math', 'mimetypes', 'mmap',
        'modulefinder', 'msilib', 'msvcrt', 'multiprocessing',
        'netrc', 'nis', 'nntplib', 'nt', 'ntpath', 'nturl2path', 'numbers',
        'opcode', 'operator', 'optparse', 'os', 'ossaudiodev',
        'pathlib', 'pdb', 'pickle', 'pickletools', 'pipes', 'pkgutil',
        'platform', 'plistlib', 'poplib', 'posix', 'posixpath', 'pprint',
        'profile', 'pstats', 'pty', 'pwd', 'py_compile', 'pyclbr', 'pydoc',
        'pydoc_data', 'pyexpat',
        'queue', 'quopri',
        'random', 're', 'readline', 'reprlib', 'resource', 'rlcompleter',
        'runpy', 'sched',
        'secrets', 'select', 'selectors', 'shelve', 'shlex', 'shutil', 'signal',
        'site', 'smtpd', 'smtplib', 'sndhdr', 'socket', 'socketserver', 'spwd',
        'sqlite3', 'sre_compile', 'sre_constants', 'sre_parse', 'ssl', 'stat',
        'statistics', 'string', 'stringprep', 'struct', 'subprocess', 'sunau',
        'symtable', 'sys', 'sysconfig', 'syslog',
        'tabnanny', 'tarfile', 'telnetlib', 'tempfile', 'termios', 'textwrap',
        'this', 'threading', 'time', 'timeit', 'token', 'tokenize', 'tomllib',
        'trace', 'traceback', 'tracemalloc', 'tty', 'turtle', 'turtledemo',
        'types', 'typing',
        'unicodedata', 'unittest', 'urllib', 'uu', 'uuid',
        'venv',
        'warnings', 'wave', 'weakref', 'webbrowser', 'winreg', 'winsound',
        'wsgiref',
        'xdrlib', 'xml', 'xmlrpc',
        'zipapp', 'zipfile', 'zipimport', 'zlib',
    )
    if tkinter_is_installed:
        std_names += ('tkinter',)
    for x in sorted(imported_packages):
        if x.replace('-', '_') not in std_names:
            missing.append(x)
    print(missing, ':lv8')


if __name__ == "__main__":
    # pox projects/poetry_extensions/check_dependencies.py <src_dir>
    cli.run(main)
