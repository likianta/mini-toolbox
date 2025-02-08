import os.path
import re
from argsense import cli
from lk_utils import fs
from lk_utils import timestamp


@cli.cmd()
def delete_image_files(md_file: str) -> None:
    md_dir = fs.parent(md_file)
    fs.make_dir(del_dir := fs.xpath('deleted/{}'.format(timestamp('ymd-hns'))))
    content = fs.load(md_file)
    
    count = 0
    for m in re.finditer(r'!\[.*?]\((.*?)\)', content):
        print(':i', m.group(0))
        possible_path = m.group(1)
        if possible_path.startswith('http'):
            continue
        if os.path.isabs(possible_path):
            path = possible_path
        else:
            if fs.exists(x := fs.normpath(
                '{}/{}'.format(md_dir, possible_path.removeprefix('./'))
            )):
                path = x
            else:
                print(':v6', 'invalid path "{}" in "{}"'.format(x, m.group(0)))
                continue
        fs.move(path, del_dir + '/' + fs.basename(path))
        count += 1
        
    if count:
        print(':v1t', 'delete {} files, see "{}"'.format(count, del_dir))
    else:
        print(':v7', 'there is no image file to delete')
        fs.remove(del_dir)


if __name__ == '__main__':
    # pox -m projects.markdown_image_cleaner -h
    cli.run(delete_image_files)
