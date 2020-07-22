#!/usr/bin/env python3
"""Disk usage."""

from itertools import cycle
from os import popen

from statusdlib.core.components import Component
from statusdlib.core.ui import meter


class Block_Devices:
    disks = cycle([
        line.split()[0] for line in [
            drive.strip() for drive in
            popen('df').readlines() if drive.startswith('/dev/sda')
        ]
    ])

    def next(self):
        return(next(self.disks))


disks = Block_Devices()


def disk_usage():
    disk = disks.next()

    label = f'{disk.split("/")[-1:][0].upper()}: '

    return label + meter(int(
        popen(f'df {disk} --output=pcent').readlines()[1].strip()[:-1]
    ))


usage = Component(
    source=disk_usage,
    sleep_ms=20000,
    weight=85,
)
