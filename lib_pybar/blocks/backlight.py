#!/usr/bin/env python3
"""Backlight level percentage."""

from glob import glob

from lib_pybar.core import Block, RemoveBlock
from lib_pybar.helpers import readint
from lib_pybar.widgets import label, meter

try:
    bl_max = readint(glob('/sys/class/backlight/*/max_brightness')[0])
except (FileNotFoundError, IndexError):
    pass


def backlight_percentage() -> str:
    try:
        bl_now = readint(glob('/sys/class/backlight/*/brightness')[0])
    except FileNotFoundError:
        raise RemoveBlock

    percent = (100 / bl_max) * bl_now

    return label('bl', meter(percent))


def main():
    return Block(
        source=backlight_percentage,
        sleep_ms=500,
        weight=95,
    )
