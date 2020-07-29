#!/usr/bin/env python3
"""Disk usage."""

from os import statvfs
from os.path import basename, exists, islink, realpath

from lib_pybar.core import Block
from lib_pybar.widgets import label, meter


class Block_Devices:
    mntfile = '/proc/mounts'
    if exists(mntfile):
        if islink(mntfile):
            mntfile = realpath(mntfile)

    def mounted(self):
        with open(self.mntfile) as mnt:
            return [dev.strip() for dev in mnt.readlines()]

    def disks(self):
        """Returns list of lists containing [disk, mountpoint]."""
        return [
            dev.split()[0:2] for dev in
            self.mounted() if dev.startswith('/dev/sd')
        ]

    seen = set()

    def next(self):
        while True:
            for disk in self.disks():
                if disk[0] not in self.seen:
                    self.seen.add(disk[0])
                    return disk
            self.seen = set()


disks = Block_Devices()


def size_of(mountpoint):
    stats = statvfs(mountpoint)
    block_size = stats.f_frsize
    total_size = stats.f_blocks
    free_size = stats.f_bfree
    return (total_size * block_size,
            free_size * block_size)


def disk_usage():
    disk = disks.next()

    device_name = basename(disk[0])
    mountpoint = disk[1]

    size, free = size_of(mountpoint)
    percent = (100 / size) * (size - free)

    return label(device_name, meter(percent))


def main():
    return Block(
        source=disk_usage,
        sleep_ms=10000,
        weight=85,
    )
