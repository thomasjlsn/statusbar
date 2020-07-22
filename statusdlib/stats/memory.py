#!/usr/bin/env python3
"""Memory usage."""

from psutil import virtual_memory
from statusdlib.core.components import Component
from statusdlib.core.ui import meter


def memory_usage():
    """Memory displayed in largest unit."""
    mem = virtual_memory()._asdict()

    return meter(
        current=mem['used'],
        maximum=mem['total'],
    )


usage = Component(
    source=memory_usage,
    label='ram',
    sleep_ms=500,
    weight=70,
)
