#!/usr/bin/env python3
"""Memory usage."""

from lib_pybar.core import Block
from lib_pybar.widgets import label, meter


def memory_usage():
    with open('/proc/meminfo', 'r') as f:
        meminfo = [line.strip() for line in f.readlines()]

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

    # memory usage as calculated by `free(1)`
    percent = (100 / mem['MemTotal']) * (
        mem['MemTotal'] - mem['Buffers'] - mem['Cached'] - mem['MemFree']
    )

    return label('ram', meter(percent)) if percent > 20 else None


def main():
    return Block(
        source=memory_usage,
        sleep_ms=1000,
        weight=70,
    )
