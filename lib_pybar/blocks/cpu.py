#!/usr/bin/env python3
"""CPU usage in percentage."""

from lib_pybar.core import Block, meter
from psutil import cpu_percent


def percent():
    return meter(cpu_percent())


def main():
    return Block(
        source=percent,
        label='cpu',
        sleep_ms=500,
        weight=80,
    )
