#!/usr/bin/env python3
"""Main entrypoint to statusd."""

from os import geteuid
from sys import exit

from statusdlib.args import args

if geteuid() != 0:
    # Statusd must be run as root
    exit(1)
else:
    from threading import Thread

    from statusdlib.components import Server
    from statusdlib.blocks import (backlight, battery, cpu, date, disks,
                                   memory, network)


def main():
    targets = set()

    # Main thread
    server = Server()
    targets.add(server)

    # Optional threads
    if args.battery:   targets.add(battery.main())
    if args.backlight: targets.add(backlight.main())
    if args.clock:     targets.add(date.main())
    if args.cpu:       targets.add(cpu.main())
    if args.disks:     targets.add(disks.main())
    if args.mem:       targets.add(memory.main())
    if args.net:       targets.add(network.main())

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
