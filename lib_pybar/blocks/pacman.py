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
# state, these dataclasses keep track of their state.
class state:
    init = True

    class pacnew:
        count = 0
        wait = 30
        timestamp = time()

    class orphans:
        count = 0
        wait = 30
        timestamp = time()

    class updates:
        count = 0
        wait = 60 * 30
        timestamp = time()


def checkupdates():
    if flags.clear_updates:
        state.updates.count = 0
        state.updates.timestamp = time()
        flags.clear_updates = False

    if (time() - state.updates.timestamp) > state.updates.wait or state.init:
        hour = int(strftime('%H'))
        day = strftime('%a').lower()

        night_time = hour not in range(8, 21)
        weekend = day.startswith('s')

        if not (night_time or weekend):
            state.updates.timestamp = time()
            stderr.write('checking for system updates\n')
            state.updates.count = len(popen('checkupdates').readlines())

    if flags.do_healthcheck or state.init:
        if (time() - state.pacnew.timestamp) > state.pacnew.wait:
            state.pacnew.timestamp = time()
            state.pacnew.count = len(popen('pacdiff -o').readlines())

        if (time() - state.orphans.timestamp) > state.orphans.wait:
            state.orphans.timestamp = time()
            state.orphans.count = len(popen('pacman -Qdtq').readlines())

        total_conflicts = sum((
            state.pacnew.count,
            state.orphans.count,
        ))

        if total_conflicts == 0:
            # Once conflicts have been resolved, we don't need to notify $USER
            # until the next time they update.
            flags.do_healthcheck = False

    state.init = False

    total_count = sum((
        state.pacnew.count,
        state.orphans.count,
        state.updates.count,
    ))

    if total_count == 0:
        return None

    if state.pacnew.count:
        return label('pacnew', str(state.pacnew.count))

    if state.updates.count:
        return label('updates', str(state.updates.count))

    if state.orphans.count:
        return label('orphans', str(state.orphans.count))


def main():
    return Block(
        prerequisites=has_dependencies,
        source=checkupdates,
        sleep_ms=1000 * 30,
        weight=98,
    )
