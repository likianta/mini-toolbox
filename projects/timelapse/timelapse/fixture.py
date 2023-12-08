from contextlib import contextmanager
from functools import wraps
from inspect import currentframe
from time import time

import rich
import rich.table


def timeit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with fixture.timing():
            return func(*args, **kwargs)
    return wrapper


class Fixture:
    records: dict
    
    def __init__(self) -> None:
        self.records = {}
    
    @contextmanager
    def timing(self, label: str = None) -> None:
        if label is None:
            caller_frame = currentframe().f_back
            label = '{}:{}'.format(
                caller_frame.f_code.co_filename,
                caller_frame.f_lineno,
            )
        if label not in self.records:
            self.records[label] = {
                'count'    : 0,
                'accu_time': 0.0,
                'shortest' : 999,
                'longest'  : 0.0,
            }
        
        start = time()
        yield
        end = time()
        
        node = self.records[label]
        duration = end - start
        
        node['count'] += 1
        node['accu_time'] += duration
        if duration < node['shortest']:
            node['shortest'] = duration
        if duration > node['longest']:
            node['longest'] = duration
    
    def report(self) -> None:
        table = rich.table.Table(
            'label',
            'accumulative_time/s',
            'call_count',
            'average_time/ms',
            'shortest/ms',
            'longest/ms',
        )
        table.columns[0].style = 'cyan'
        table.columns[1].style = 'yellow'
        table.columns[2].style = 'magenta'
        table.columns[3].style = 'bold blue'
        table.columns[4].style = 'green'
        table.columns[5].style = 'red'
        for label, data in self.records.items():
            table.add_row(
                label,
                str(round(data['accu_time'], 2)),
                str(data['count']),
                str(round(data['accu_time'] / data['count'] * 1000, 2)),
                str(round(data['shortest'] * 1000, 2)),
                str(round(data['longest'] * 1000, 2)),
            )
        rich.print(table)


fixture = Fixture()
timing = fixture.timing
