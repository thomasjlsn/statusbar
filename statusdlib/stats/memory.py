#!/usr/bin/env python3

import psutil
from statusdlib.core.components import Segment
from statusdlib.core.ui import meter

# ==========================================================================
# Memory usage.
# ==========================================================================

def memory_usage():
    """Memory displayed in largest unit."""
    mem = psutil.virtual_memory()._asdict()

    return meter(
        current=mem['used'],
        maximum=mem['total'],
    )


usage = Segment(
    source=memory_usage,
    label='ram',
    sleep_ms=500,
    weight=70,
)
