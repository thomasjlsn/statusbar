'''Check for package updates on Arch based distros.'''

from os import popen
from shutil import which
from time import strftime

from lib_pybar.core import Block
from lib_pybar.widgets import label

has_dependencies = all((
    which('checkupdates'),
    which('pacdiff'),
    which('pacman'),
))


def checkupdates():
    hour = int(strftime('%H'))
    day = strftime('%a').lower()

    night_time = hour not in range(8, 21)
    weekend = day.startswith('s')

    if not (night_time or weekend):
        updates = len(popen('checkupdates').readlines())
    else:
        updates = 0

    conflicts = len(popen('pacdiff -o').readlines())
    orphans = len(popen('pacman -Qdtq').readlines())

    if not any((conflicts, orphans, updates)):
        return None

    if conflicts:
        return label('pacdiff', str(conflicts))

    if updates:
        return label('updates', str(updates))

    if orphans:
        return label('orphans', str(orphans))


def main():
    return Block(
        prerequisites=has_dependencies,
        source=checkupdates,
        sleep_ms=900000,
        weight=98,
    )
