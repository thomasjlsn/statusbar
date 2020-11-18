'''A Clock.'''

from time import strftime

from lib_pybar import Block
from lib_pybar.config import config


def time_now():
    return strftime(config.PYBAR_STATUSBAR_DATE_FORMAT).replace('  ', ' ')


def main():
    return Block(
        source=time_now,
        sleep_ms=5000,
        weight=99,
    )
