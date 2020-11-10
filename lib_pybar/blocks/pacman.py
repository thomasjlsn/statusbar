'''Check for package updates on Arch based distros.'''

from os import popen
from shutil import which
from sys import stderr
from time import strftime, time

from lib_pybar import Block, label
from lib_pybar.signals import flags

has_dependencies = all((
    which('checkupdates'),
    which('pacdiff'),
    which('pacman'),
))


# The pacman block keeps track of multiple things, each with their own
# state, these data classes keep track of their state.

class pkg_state:
    def __init__(self, wait=60):
        self.count = 0
        self.timestamp = time()
        self.wait = wait  # in seconds

    @property
    def due(self):
        return (time() - self.timestamp) > self.wait


class pkgs:
    init = True

    pacnew = pkg_state(30)
    orphans = pkg_state(30)
    updates = pkg_state(60 * 30)


def systemcount(cmd):
    return len(popen(cmd).readlines())


def checkupdates():
    if flags.clear_updates:
        pkgs.updates.count = 0
        pkgs.updates.timestamp = time()
        flags.clear_updates = False

    if pkgs.updates.due or pkgs.init:
        hour = int(strftime('%H'))
        day = strftime('%a').lower()

        night_time = hour not in range(8, 21)
        weekend = day.startswith('s')

        if not (night_time or weekend):
            pkgs.updates.timestamp = time()
            stderr.write('checking for system updates\n')
            pkgs.updates.count = systemcount('checkupdates')

    if flags.do_healthcheck or pkgs.init:
        if pkgs.pacnew.due:
            pkgs.pacnew.timestamp = time()
            pkgs.pacnew.count = systemcount('pacdiff -o')

        if pkgs.orphans.due:
            pkgs.orphans.timestamp = time()
            pkgs.orphans.count = systemcount('pacman -Qdtq')

        total_conflicts = sum((
            pkgs.pacnew.count,
            pkgs.orphans.count,
        ))

        if total_conflicts == 0:
            # Once conflicts have been resolved, we don't need to notify $USER
            # until the next time they update.
            flags.do_healthcheck = False

    pkgs.init = False

    total_count = sum((
        pkgs.pacnew.count,
        pkgs.orphans.count,
        pkgs.updates.count,
    ))

    if total_count == 0:
        return None

    if pkgs.pacnew.count:
        return label('pacnew', str(pkgs.pacnew.count))

    if pkgs.updates.count:
        return label('updates', str(pkgs.updates.count))

    if pkgs.orphans.count:
        return label('orphans', str(pkgs.orphans.count))


def main():
    return Block(
        prerequisites=has_dependencies,
        source=checkupdates,
        sleep_ms=1000 * 30,
        weight=98,
    )
