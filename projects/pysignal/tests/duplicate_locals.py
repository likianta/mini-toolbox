from pprint import pprint
from random import randint

from pysignal import signal

a = signal()
f = signal()


@a
def b():
    pass


def c():
    @a
    def d():
        pass
    
    # print(d.__qualname__)
    
    e = randint(0, 100)
    print(e)
    
    @f
    def g():
        nonlocal e
        e += 1
        print(e)
    
    f.emit()
    print('final', f'{e = }')


c()
c()

pprint(a._funcs)  # noqa

# pox tests/duplicate_locals.py
