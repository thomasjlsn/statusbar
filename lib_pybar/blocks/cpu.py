#!/usr/bin/env python3
"""CPU usage in percentage."""

from psutil import cpu_percent

from lib_pybar.components import Block, meter


def percent():
    return meter(cpu_percent())


def main():
    return Block(
        source=percent,
        label='cpu',
        sleep_ms=500,
        weight=80,
    )
