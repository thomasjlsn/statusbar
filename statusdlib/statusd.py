#!/usr/bin/env python3
"""Main entrypoint to statusd."""

from statusdlib.core.data import SharedData


def main():
    # Import Components after args are processed. This way, if the user
    # runs --help, it will not require root or try to restart the server.
    from threading import Thread

    from statusdlib.core.server import statusbar
    from statusdlib.stats import (backlight, battery, cpu, date, disks,
            memory, network)

    # Main thread
    target_threads = [statusbar]

    # Optional threads
    if SharedData.args.battery:   target_threads += [battery.life]
    if SharedData.args.backlight: target_threads += [backlight.level]
    if SharedData.args.clock:     target_threads += [date.clock]
    if SharedData.args.cpu:       target_threads += [cpu.usage]
    if SharedData.args.disks:     target_threads += [disks.usage]
    if SharedData.args.mem:       target_threads += [memory.usage]
    if SharedData.args.net:       target_threads += [network.usage]

    threads = [
        Thread(target=thread.run)
        for thread in target_threads
    ]

    try:
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        return 0

    except KeyboardInterrupt:
        return 1

    finally:
        for thread in threads:
            thread.join()
