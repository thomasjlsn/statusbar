'''Backlight level percentage.'''

from glob import glob

from lib_pybar import Block, label, meter, readint

try:
    bl_max = readint(glob('/sys/class/backlight/*/max_brightness')[0])
    has_backlight_info = True
except (FileNotFoundError, IndexError):
    has_backlight_info = False


def backlight_percentage() -> str:
    bl_now = readint(glob('/sys/class/backlight/*/brightness')[0])

    percent = (100 / bl_max) * bl_now

    return label('bl', meter(percent))


def main():
    return Block(
        prerequisite=has_backlight_info,
        source=backlight_percentage,
        sleep_ms=500,
        weight=95,
    )
