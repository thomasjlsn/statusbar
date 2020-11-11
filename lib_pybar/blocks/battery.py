'''Current battery percentage.'''

from glob import glob

from lib_pybar import Block, label, meter, readint


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

has_batteries = power.batteries not in (None, [])


def battery_source():
    percent = power.percent()

    if power.charging():
        if percent >= 99:
            state = 'full'
        state = '++'
        return ' '.join((label('bat', meter(percent)), state))

    return label('bat', meter(percent))


def main():
    return Block(
        prerequisite=has_batteries,
        source=battery_source,
        sleep_ms=20000,
        weight=90,
    )
