#!/usr/bin/env python3
"""CPU usage in percentage."""

import psutil
from statusdlib.core.components import Segment
from statusdlib.core.ui import meter


def cpu_percent():
    usage = psutil.cpu_percent()

    return meter(usage)


usage = Segment(
    source=cpu_percent,
    label='cpu',
    sleep_ms=250,
    weight=80,
)
