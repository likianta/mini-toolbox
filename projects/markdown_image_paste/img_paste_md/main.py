"""
requirements:
    - lk-qtquick-scaffold
    - lk-utils
    - pillow
"""
import subprocess
from os.path import isdir

from PIL import ImageGrab
from lk_qtquick_scaffold import QObject
from lk_qtquick_scaffold import app
from lk_qtquick_scaffold import slot
from lk_utils import normpath
from lk_utils import xpath
from lk_utils.time_utils import timestamp
from qtpy.QtGui import QIcon


class Main(QObject):
    dirpath: str = ''
    
    @slot(str, result=bool)
    def update_assets_dirpath(self, dirpath: str) -> bool:
        self.dirpath = normpath(dirpath)
        print(self.dirpath)
        return isdir(self.dirpath)
    
    @property
    def prefix(self) -> str:
        """
        e.g. 'C:/demo/.assets/xxx' -> '.assets/xxx'
        """
        assert '.assets/' in self.dirpath
        point = self.dirpath.index('.assets/')
        return self.dirpath[point:]
    
    @slot(result=str)
    def dump_image(self) -> str:
        if not self.dirpath:
            print('you have not set the assets dirpath', ':v4s')
            return ''
        if not isdir(self.dirpath):
            print('invalid dirpath!', self.dirpath, ':v4s')
            return ''
        
        # grab image from clipboard
        img = ImageGrab.grabclipboard()
        # save image
        filename = f'{timestamp("ymdhns")}.png'
        img.save(f'{self.dirpath}/{filename}')
        # copy path to clipboard, in markdown format
        link = '![{}]({}/{})'.format(filename[:-4], self.prefix, filename)
        print(':i', link)
        # https://stackoverflow.com/a/9409898/9695911
        subprocess.check_call(f'echo | set /p nul={link}| clip', shell=True)
        return link


app.setWindowIcon(QIcon(xpath('../python-holo.ico')))
app.register(Main(), 'pymain')
app.run(xpath('qml/Main.qml'))
