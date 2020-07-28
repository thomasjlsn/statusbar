#!/usr/bin/env python3
"""Main entrypoint to pybar."""

from os import geteuid
from sys import exit

from lib_pybar.args import args

if geteuid() != 0:
    # Pybar must be run as root
    exit(1)
else:
    from threading import Thread

    from lib_pybar.components import Server
    from lib_pybar.blocks import (backlight, battery, cpu, date, disks,
                                  memory, network)


def main():
    server = Server()

    threads = (
        Thread(target=thread.run)
        for condition, thread in (
            (True,           server),
            (args.battery,   battery.main()),
            (args.backlight, backlight.main()),
            (args.clock,     date.main()),
            (args.cpu,       cpu.main()),
            (args.disks,     disks.main()),
            (args.mem,       memory.main()),
            (args.net,       network.main()),
        )
        if condition
    )

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
