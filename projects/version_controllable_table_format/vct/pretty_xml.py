from xml.dom import minidom

from argsense import cli
from lk_utils import fs


@cli.cmd('one')
def one_file(file_i: str, file_o: str = None, indentation: int = 2) -> None:
    """
    params:
        file_i (-i): input ".xml" file.
        file_o (-o): output ".xml" file, if not given, will overwrite `file_i`.
        indentation (-d): suggest 2 (default) or 4.
    """
    content = fs.load(file_i, 'plain')
    content = minidom.parseString(content).toprettyxml(indent=' ' * indentation)
    fs.dump(content, file_o or file_i)


if __name__ == '__main__':
    # 1. open wps excel program
    # 2. make some content, save as xml table
    # 3. use this script to format the xml file
    #   pox projects/version_controllable_table_format/vct/pretty_xml.py ...
    # 4. git commit
    cli.run()
