import os

from hot_shelve import FlatShelve


class Conflore(FlatShelve):
    """ simple and good config management tool. """
    
    def __init__(self, path: str, init_data: dict = None):
        if os.path.exists(path):
            assert os.path.isdir(path)
        else:
            os.mkdir(path)
        file = f'{path}/__main__.db'
        need_init = init_data and not os.path.exists(file)
        super().__init__(file)
        if need_init:
            self.update(init_data)
