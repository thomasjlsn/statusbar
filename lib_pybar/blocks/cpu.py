#!/usr/bin/env python3
"""CPU usage in percentage."""

from lib_pybar.core import Block
from lib_pybar.widgets import label, meter
from psutil import cpu_percent


def percent():
    return label('cpu', meter(cpu_percent()))


def main():
    return Block(
        source=percent,
        sleep_ms=1000,
        weight=80,
    )
