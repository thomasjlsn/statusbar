#!/usr/bin/env python3
"""Main entrypoint to statusd."""

from statusdlib.core.data import SharedData


def main():
    # Import Components after args are processed. This way, if the user
    # runs --help, it will not require root or try to restart the server.
    from threading import Thread

    from statusdlib.core.components import StatusBar
    from statusdlib.blocks import (backlight, battery, cpu, date, disks,
                                   memory, network)

    targets = set()

    # Main thread
    statusbar = StatusBar()
    targets.add(statusbar)

    # Optional threads
    if SharedData.args.battery:   targets.add(battery.main())
    if SharedData.args.backlight: targets.add(backlight.main())
    if SharedData.args.clock:     targets.add(date.main())
    if SharedData.args.cpu:       targets.add(cpu.main())
    if SharedData.args.disks:     targets.add(disks.main())
    if SharedData.args.mem:       targets.add(memory.main())
    if SharedData.args.net:       targets.add(network.main())

    threads = [Thread(target=thread.run) for thread in targets]

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
