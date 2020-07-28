#!/usr/bin/env python3
"""A Clock."""

from time import strftime

from lib_pybar.core import Block


def time_now():
    return strftime('%a, %b %d %H:%M')


def main():
    return Block(
        source=time_now,
        sleep_ms=1000,
        weight=99,
    )
