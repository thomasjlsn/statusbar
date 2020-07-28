#!/usr/bin/env python3
"""Memory usage."""

from lib_pybar.components import Block, meter


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

    return meter(
        # memory usage as calculated by `free(1)`
        (100 / mem['MemTotal']) * (
            mem['MemTotal'] - mem['Buffers'] - mem['Cached'] - mem['MemFree']
        )
    )


def main():
    return Block(
        source=memory_usage,
        label='ram',
        sleep_ms=1000,
        weight=70,
    )
