#!/usr/bin/env python3
"""A Clock."""

from time import strftime

from statusdlib.core.components import Component


def time_now():
    return strftime('%a, %b %d %H:%M')


clock = Component(
    source=time_now,
    sleep_ms=250,
    weight=99,
)
