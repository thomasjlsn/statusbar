'''Various helper functions.'''

from math import floor, log


def human_readable(size_in_bytes):
    if size_in_bytes == 0:
        return '0B'

    units = ('B', 'K', 'M', 'G', 'T', 'P')

    i = int(floor(log(size_in_bytes, 1024)))
    p = pow(1024, i)
    s = round(size_in_bytes / p, 2)

    return '%s%s' % (s, units[i])


def readint(file):
    '''
    Many files in /sys/* and /proc/* contain single integer values.
    This reduces boilerplate.
    '''
    with open(file, 'r') as f:
        val = int(f.readline())

    return val
