#!/usr/bin/env python3
"""Current battery percentage."""

from glob import glob

from statusdlib.components import Block, meter
from statusdlib.helpers import readint


def battery_source() -> str:
    """Returns current battery percentage"""
    try:
        batteries = glob('/sys/class/power_supply/BAT*')

        if not batteries:
            return None
        else:
            power_levels = []
            for battery in batteries:
                full = readint(f'{battery}/energy_full')
                now = readint(f'{battery}/energy_now')
                power = ((100 / full) * now)
                power_levels.append(power)

        percent = int(sum(power_levels) / len(batteries))

        charging = readint('/sys/class/power_supply/AC/online')

        if charging:
            if percent >= 99:
                return f'{meter(percent)} full'
            return f'{meter(percent)} ++'

        return meter(percent)

    except FileNotFoundError:
        return None


def main():
    return Block(
        source=battery_source,
        label='bat',
        sleep_ms=10000,
        weight=90,
    )
