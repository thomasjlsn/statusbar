#!/usr/bin/env python3
"""Disk usage."""

from os import path, statvfs
from os.path import basename, exists, islink, realpath

from statusdlib.components import Block, meter


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

    label = basename(disk[0]).upper()
    mountpoint = disk[1]

    size, free = size_of(mountpoint)

    return ': '.join([label, meter((100 / size) * (size - free))])


def main():
    return Block(
        source=disk_usage,
        sleep_ms=10000,
        weight=85,
    )
