#!/usr/bin/env python3
"""Check for package updates on Arch based distros."""

from os import popen
from shutil import which
from time import strftime

from lib_pybar.core import Block
from lib_pybar.widgets import label

has_checkupdates = which('checkupdates')


def checkupdates():
    hour = int(strftime('%H'))
    day = strftime('%a').lower()

    night_time = hour not in range(8, 21)
    weekend = day.startswith('s')

    if night_time or weekend:
        return None

    updates = len(popen('checkupdates').readlines())

    if not updates:
        return None

    return label('updates', str(updates))


def main():
    return Block(
        prerequisites=has_checkupdates,
        source=checkupdates,
        sleep_ms=900000,
        weight=98,
    )
