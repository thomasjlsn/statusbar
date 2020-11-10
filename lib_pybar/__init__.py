'''
Core pybar library.
'''

from math import floor, log
from os import getenv, system
from time import sleep
from uuid import uuid4

from lib_pybar.signals import flags

PYBAR_MAX_CONNECTIONS = getenv('PYBAR_MAX_CONNECTIONS', 5)
PYBAR_METER_WIDTH = getenv('PYBAR_METER_WIDTH', 10)
PYBAR_SOCKET = getenv('PYBAR_SOCKET', '/tmp/pybar.sock')


class SharedData:
    '''Data shared between blocks and the statusbar.'''
    data = {}


class Block(SharedData):
    def __init__(self,
                 prerequisites: bool = True,
                 source: callable = None,
                 sleep_ms: int = 1000,
                 weight: int = 0):

        self.prerequisites = prerequisites
        self.source = source
        self.sleep_ms = sleep_ms
        self.weight = str(weight).zfill(8)  # Determines order of blocks
        self.key = f'{self.weight}-{uuid4()}'

    def run(self):
        if not self.prerequisites:
            return

        while not flags.abort:
            try:
                if flags.halt:
                    interruptable_sleep(1_000)
                    continue

                self.data[self.key] = self.source()
                interruptable_sleep(self.sleep_ms)

            except Exception as e:
                # Display the error briefly
                self.data[self.key] = label('error', f'"{e}"')
                interruptable_sleep(10_000)
                self.data.pop(self.key, None)
                break


class StatusBar(SharedData):
    @property
    def active_blocks(self):
        return [
            self.data[block] for block in sorted(self.data.keys())
            if self.data[block] is not None
        ]

    def statusbar(self):
        return ''.join([f' {block} ' for block in self.active_blocks])


def send(signal):
    system(f'kill -{signal} $(pgrep pybar)')


def human_readable(size_in_bytes):
    if size_in_bytes == 0:
        return '0B'

    units = ('B', 'K', 'M', 'G', 'T', 'P')

    i = int(floor(log(size_in_bytes, 1024)))
    p = pow(1024, i)
    s = round(size_in_bytes / p, 2)

    return '%s%s' % (s, units[i])


def interruptable_sleep(ms):
    while not flags.abort:
        if ms > 100:
            ms -= 100
            sleep(.1)
        else:
            sleep(ms / 1000)
            break


def readint(file):
    '''
    Many files in /sys/* and /proc/* contain single integer values.
    This reduces boilerplate.
    '''
    with open(file, 'r') as f:
        val = int(f.readline())

    return val


def label(label_text, string):
    return ': '.join((label_text.upper(), string))


def __make_meter_values(meter_width):
    '''Assign unicode bars to percentages.'''
    bg_char = ' '
    meter = {0: bg_char * meter_width}
    bar_chars = []
    cell_chars = [bg_char, '▏', '▎', '▍', '▌', '▋', '▊', '▉', '█']
    full = cell_chars[-1]

    fill = ''
    for _ in range(meter_width):
        for char in cell_chars:
            bar = fill + char
            bar_chars.append(bar.ljust(meter_width, bg_char))
        fill += full

    for percent in range(1, 101):
        end = 0
        for i, char in enumerate(bar_chars):
            start = end
            end = (100 / len(bar_chars)) * i
            if start < percent > end:
                meter[percent] = bar_chars[i]

    return meter


__meter_values = __make_meter_values(int(PYBAR_METER_WIDTH))


def meter(percentage):
    return __meter_values[int(percentage)]
