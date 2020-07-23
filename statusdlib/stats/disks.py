#!/usr/bin/env python3
"""Disk usage."""

from os import popen

from statusdlib.core.components import Component
from statusdlib.core.ui import meter


class Block_Devices:
    def disks(self):
        return [
            line.split()[0] for line in [
                drive.strip() for drive in
                popen('df').readlines() if drive.startswith('/dev/sd')
            ]
        ]

    seen = set()

    def next(self):
        while True:
            for disk in self.disks():
                if disk not in self.seen:
                    self.seen.add(disk)
                    return disk
            self.seen = set()


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
