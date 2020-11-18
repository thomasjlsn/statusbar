'''A Clock.'''

from time import strftime

from lib_pybar import Block
from lib_pybar.config import config

PYBAR_DATE_FORMAT = config['statusbar']['date_format']


def time_now():
    return strftime(PYBAR_DATE_FORMAT).replace('  ', ' ')


def main():
    return Block(
        source=time_now,
        sleep_ms=5000,
        weight=99,
    )
