'''A Clock.'''

from os import getenv
from time import strftime

from lib_pybar.core import Block

PYBAR_DATE_FORMAT = getenv('PYBAR_DATE_FORMAT', '%a, %b %d %H:%M')


def time_now():
    return strftime(PYBAR_DATE_FORMAT)


def main():
    return Block(
        source=time_now,
        sleep_ms=1000,
        weight=99,
    )
