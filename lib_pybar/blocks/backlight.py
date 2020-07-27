#!/usr/bin/env python3
"""Backlight level percentage."""

from glob import glob

from lib_pybar.components import Block, RemoveBlock, meter
from lib_pybar.helpers import readint

try:
    bl_max = readint(glob('/sys/class/backlight/*/max_brightness')[0])
except (FileNotFoundError, IndexError):
    pass


def backlight_percentage() -> str:
    try:
        bl_now = readint(glob('/sys/class/backlight/*/brightness')[0])
    except FileNotFoundError:
        raise RemoveBlock
    return meter((100 / bl_max) * bl_now)


def main():
    return Block(
        source=backlight_percentage,
        label='bl',
        sleep_ms=500,
        weight=95,
    )
