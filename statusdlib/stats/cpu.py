#!/usr/bin/env python3
"""CPU usage in percentage."""

from psutil import cpu_percent
from statusdlib.core.components import Component
from statusdlib.core.ui import meter


def percent():
    return meter(cpu_percent())


usage = Component(
    source=percent,
    label='cpu',
    sleep_ms=250,
    weight=80,
)
