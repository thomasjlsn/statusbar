#!/usr/bin/env python3
"""Various helper functions."""

from math import floor, log


def laptop_open():
    """Check if laptop lid is open."""
    try:
        with open('/proc/acpi/button/lid/LID/state', 'r') as f:
            state = f.readline().split()[1]
        if state.lower() == 'open':
            return True
        return False
    except FileNotFoundError:
        return True


def bytes_to_largest_units(size_in_bytes):
    if size_in_bytes == 0:
        return '0B'

    units = ('B', 'K', 'M', 'G', 'T', 'P')

    i = int(floor(log(size_in_bytes, 1024)))
    p = pow(1024, i)
    s = round(size_in_bytes / p, 2)

    return '%s%s' % (s, units[i])


def readint(file):
    """
    Many files in /sys/* and /proc/* contain single integer values.
    This reduces boilerplate.
    """
    with open(file, 'r') as f:
        val = int(f.readline())

    return val


def readstr(file):
    """Counterpart to readint()."""
    with open(file, 'r') as f:
        val = str(f.readline()).strip()

    return val


def uuid():
    """Get a uuid from the kernel."""
    return readstr('/proc/sys/kernel/random/uuid')
