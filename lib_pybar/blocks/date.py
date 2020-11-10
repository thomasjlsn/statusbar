'''A Clock.'''

from os import getenv
from time import strftime

from lib_pybar import Block

PYBAR_DATE_FORMAT = getenv('PYBAR_DATE_FORMAT', '%a, %b %d %k:%M')


def time_now():
    return strftime(PYBAR_DATE_FORMAT).replace('  ', ' ')


def main():
    return Block(
        source=time_now,
        sleep_ms=5000,
        weight=99,
    )
