#!/usr/bin/env python3
"""Backlight level percentage."""

from glob import glob

from statusdlib.components import Block, meter
from statusdlib.helpers import readint

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


def main():
    return Block(
        source=backlight_percentage,
        label='bl',
        sleep_ms=500,
        weight=95,
    )
