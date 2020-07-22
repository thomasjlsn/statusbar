#!/usr/bin/env python3

from glob import glob

from statusdlib.core.components import Segment
from statusdlib.helpers import readint

# ==========================================================================
# Backlight level percentage.
# ==========================================================================

try:
    bl_max = readint(glob('/sys/class/backlight/*/max_brightness')[0])
except (FileNotFoundError, IndexError):
    pass


def backlight_percentage() -> str:
    try:
        bl_now = readint(glob('/sys/class/backlight/*/brightness')[0])
        return meter(maximum=bl_max, current=bl_now)
    except FileNotFoundError:
        return None


backlight = Segment(
    source=backlight_percentage,
    label='bl',
    sleep_ms=500,
    weight=95,
)
