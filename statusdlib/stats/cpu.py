#!/usr/bin/env python3

import psutil
from statusdlib.core.components import Segment
from statusdlib.core.ui import meter

# ==========================================================================
# CPU usage in percentage.
# ==========================================================================

def cpu_percent():
    usage = psutil.cpu_percent()

    return meter(usage)


usage = Segment(
    source=cpu_percent,
    label='cpu',
    sleep_ms=250,
    weight=80,
)
