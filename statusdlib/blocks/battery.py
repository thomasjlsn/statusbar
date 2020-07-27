#!/usr/bin/env python3
"""Current battery percentage."""

from glob import glob

from statusdlib.components import Block, RemoveBlock, meter
from statusdlib.helpers import readint


class Power:
    try:
        batteries = glob('/sys/class/power_supply/BAT*')
    except FileNotFoundError:
        batteries = None

    def power_levels(self):
        for battery in self.batteries:
            full = readint(f'{battery}/energy_full')
            now = readint(f'{battery}/energy_now')
            power = ((100 / full) * now)
            yield power

    def percent(self):
        return int(sum(self.power_levels()) / len(self.batteries))

    def charging(self):
        return readint('/sys/class/power_supply/AC/online')


power = Power()


def battery_source():
    if not power.batteries:
        raise RemoveBlock

    percent = power.percent()

    if power.charging():
        if percent >= 99:
            return f'{meter(percent)} full'
        return f'{meter(percent)} ++'
    return meter(percent)


def main():
    return Block(
        source=battery_source,
        label='bat',
        sleep_ms=20000,
        weight=90,
    )
