#!/usr/bin/env python3
"""A Server producing the status bar."""

from threading import Event, Thread

from statusdlib.core.components import Segment, statusbar
from statusdlib.core.ui import meter
from statusdlib.helpers import (bytes_to_largest_units, laptop_open, readint,
                                readstr, uuid)
from statusdlib.stats import (backlight, battery, cpu, date, disks, memory,
                              network)

# Kill all threads in the statusbar
teardown = Event()


def main():
    # Main thread
    target_threads = [statusbar]

    # Optional threads
    target_threads += [
        # backlight.level,
        battery.life,
        date.clock,
        cpu.usage,
        disks.usage,
        # network.operstate,
        memory.usage,
        network.usage,
    ]

    threads = [Thread(target=thread.run) for thread in target_threads]

    try:
        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

    except (EOFError, KeyboardInterrupt):
        teardown.set()

    finally:
        teardown.set()
        for thread in threads:
            thread.join()
