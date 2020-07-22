#!/usr/bin/env python3
"""Memory usage."""

from statusdlib.core.components import Component
from statusdlib.core.ui import meter


def memory_usage():
    with open('/proc/meminfo', 'r') as f:
        meminfo = [l.strip() for l in f.readlines()]

    mem = {}

    for i in meminfo:
        try:
            key, val, _ = i.split()
            key = key[:-1]
        except ValueError:
            try:
                key, _ = i.split()
                key = key[:-1]
                val = 0
            except ValueError:
                continue
        try:
            mem[key] = int(val)
        except TypeError:
            continue

    return meter(
        # memory usage as calculated by `free(1)`
        current=(mem['MemTotal'] - mem['MemFree'] - mem['Buffers'] - mem['Cached']),
        maximum=mem['MemTotal'],
    )


usage = Component(
    source=memory_usage,
    label='ram',
    sleep_ms=500,
    weight=70,
)
