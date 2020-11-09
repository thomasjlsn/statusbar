'''CPU usage in percentage.'''

from lib_pybar.core import Block
from lib_pybar.widgets import label, meter
from psutil import cpu_percent


def percent():
    percent = cpu_percent()
    return label('cpu', meter(percent)) if percent > 20 else None


def main():
    return Block(
        source=percent,
        sleep_ms=1000,
        weight=80,
    )
