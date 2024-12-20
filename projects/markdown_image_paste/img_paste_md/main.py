"""
requirements:
    - lk-utils
    - pillow
    - pyperclip
    - qmlease
"""
import os.path

import pyperclip
from PIL import ImageGrab
from lk_utils import fs
from lk_utils import xpath
from lk_utils.time_utils import timestamp
from qmlease import QObject
from qmlease import app
from qmlease import slot


def main() -> None:
    app.set_app_icon(xpath('../python-holo.ico'))
    app.register(Main(), 'main')
    app.run(xpath('qml/Main.qml'))


class Main(QObject):
    doc_root: str
    img_root: str
    
    @property
    def _relpath(self) -> str:
        out = fs.relpath(self.img_root, self.doc_root)
        if not out.startswith(('./', '../')):
            out = './' + out
        return out
    
    @slot(str, result=bool)
    def set_doc_root(self, dirpath: str) -> bool:
        if os.path.isdir(dirpath):
            self.doc_root = dirpath
            return True
        return False
    
    @slot(str, result=bool)
    def set_img_root(self, dirpath: str) -> bool:
        print(dirpath, os.path.isdir(dirpath))
        if os.path.isdir(dirpath):
            self.img_root = dirpath
            return True
        return False
    
    @slot(result=str)
    def dump_image(self) -> str:
        assert self.doc_root and self.img_root
        # grab image from clipboard
        img = ImageGrab.grabclipboard()
        # save image
        # filename = f'{timestamp("ymdhns")}.png'
        filename = f'{timestamp("hns")}.png'
        img.save(f'{self.img_root}/{filename}')
        # copy path to clipboard, in markdown format
        link = '![{}]({}/{})'.format(filename[:-4], self._relpath, filename)
        print(':i', link)
        pyperclip.copy(link)
        # # https://stackoverflow.com/a/9409898/9695911
        # subprocess.check_call(f'echo | set /p nul={link}| clip', shell=True)
        return link


if __name__ == '__main__':
    main()
