#!/usr/bin/env python3
"""A Server producing the status bar."""

import logging
import os
import socket
import time
from glob import glob
from threading import Event, Thread

import psutil

# Kill all threads in the status_bar
teardown = Event()


# ==========================================================================
# Helper functions.
# ==========================================================================

def laptop_open():
    """Check if laptop lid is open."""
    try:
        with open('/proc/acpi/button/lid/LID/state', 'r') as f:
            state = f.readline().split()[1]
        if state.lower() == 'open':
            return True
        return False
    except FileNotFoundError:
        return True


def readint(file):
    """
    Many files in /sys/class/* contain single integer values.
    This reduces boilerplate.
    """
    with open(file, 'r') as f:
        val = int(f.readline())

    return val


# Assign unicode bars to percentages to make meters.
meter = {0: '    '}

# meter_ = [' ', '▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']
meter_ = [
    '▏   ', '▎   ', '▍   ', '▌   ', '▋   ', '▊   ', '▉   ', '█   ',
    '█▏  ', '█▎  ', '█▍  ', '█▌  ', '█▋  ', '█▊  ', '█▉  ', '██  ',
    '██▏ ', '██▎ ', '██▍ ', '██▌ ', '██▋ ', '██▊ ', '██▉ ', '███ ',
    '███▏', '███▎', '███▍', '███▌', '███▋', '███▊', '███▉', '████',
]

for percent in range(1, 101):
    end = 0
    for i, icon in enumerate(meter_):
        start = end
        end = (100 / len(meter_)) * i
        if start < percent > end:
            meter[percent] = meter_[i]


def fancy_meter(percentage=None, current=None, maximum=None):
    if percentage is None:
        val = ((100 / maximum) * current)
    else:
        val = percentage

    return meter[int(val)]


# ==========================================================================
# Data Classes / Globals
# ==========================================================================

seperator = ''
lpad = ' '
rpad = ' '


class SharedData:
    data = {}


# ==========================================================================
# Classes making up the status bar.
# ==========================================================================

class Component(SharedData):
    def __init__(self, source=None, sink=None, label=None,
                 sleep_ms=1000, weight=0):

        # The function data is recieved from
        self.source = source

        # The function data is sent to
        self.sink = sink

        # An optional label for the component
        self.label = label

        # Time in ms to sleep, between 0.5 ... 10 seconds
        self.sleep_ms = max(500, min(10000, sleep_ms))

        # Used to determine order of components
        self.weight = weight

    def update(self):
        component = self.source()
        if component is not None:
            if self.label is not None:
                self.data[self.weight] = f'{self.label.upper()}: {component}'
            else:
                self.data[self.weight] = component

    def out(self):
        if self.sink is not None:
            self.sink(self.data[self.weight])

    def sleep(self):
        if laptop_open():
            time.sleep(self.sleep_ms / 1000)
        else:
            # Sleep longer.
            time.sleep((self.sleep_ms * 3) / 1000)

    def run(self):
        while True:
            self.update()
            self.out()
            self.sleep()
            if teardown.is_set():
                break


class StatusBar(Component):
    """The status bar as a whole. Needs its own unique dataset."""
    data = ''

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((socket.gethostname(), 8787))
    server.listen(5)

    def update(self):
        self.data = self.source()

    def run(self):
        try:
            while True:
                client, address = self.server.accept()
                self.update()
                logging.info(f'connection from: {address}')
                client.send(bytes(self.data, 'utf-8'))
                if teardown.is_set():
                    break
        finally:
            self.server.close()


class Segment(Component):
    """One segment of the status bar."""
    pass


# ==========================================================================
# Various sink funcions for the statusbar.
# ==========================================================================

def dwm(data):
    os.system(f'xsetroot -name "{data}"')


def tmp(data):
    with open('/tmp/status_bar', 'w') as f:
        f.write(data)


# ==========================================================================
#  Main status bar function.
# ==========================================================================

def make_bar():
    return seperator.join([
        ''.join([
            lpad, str(SharedData.data[component]), rpad
        ])
        for component in sorted(SharedData.data.keys())
        if SharedData.data[component] is not None
    ])


status_bar = StatusBar(
    source=make_bar,
    sink=tmp,
    sleep_ms=200,
)


# ==========================================================================
# The individual segments of the status bar.
#
# ==========================================================================
# A Clock.
# ==========================================================================

def time_now():
    return time.strftime('%a %d %H:%M')


clock = Segment(
    source=time_now,
    sleep_ms=250,
    weight=100,
)


# ==========================================================================
# Disk usage.
# ==========================================================================

df_cmd = f'df /dev/sda1 --output=pcent'


def disk_usage():
    return fancy_meter(
        int(os.popen(df_cmd).readlines()[1].strip()[:-1])
    )


disk = Segment(
    source=disk_usage,
    label='sda',
    sleep_ms=10000,
    weight=85,
)


# ==========================================================================
# CPU usage in percentage.
# ==========================================================================

def cpu_percent():
    usage = psutil.cpu_percent()

    return fancy_meter(usage)


cpu = Segment(
    source=cpu_percent,
    label='cpu',
    sleep_ms=250,
    weight=80,
)


# ==========================================================================
# Memory usage.
# ==========================================================================

def memory_usage():
    """Memory displayed in largest unit."""
    mem = psutil.virtual_memory()._asdict()

    return fancy_meter(
        current=mem['used'],
        maximum=mem['total'],
    )


ram = Segment(
    source=memory_usage,
    label='ram',
    sleep_ms=500,
    weight=70,
)


# ==========================================================================
# Active network interfaces
# ==========================================================================

def interfaces():
    """Returns state of network interfaces"""
    interfaces = [d for d in os.listdir('/sys/class/net/') if d != 'lo']
    up = []

    for interface in interfaces:
        with open(f'/sys/class/net/{interface}/operstate', 'r') as s:
            if s.readline().strip() == 'up':
                up.append(interface)

    if not up:
        return 'offline'

    return ' '.join(up)


net = Segment(
    source=interfaces,
    sleep_ms=1000,
    weight=10,
)


# ==========================================================================
# Backlight level percentage.
# ==========================================================================

try:
    bl_max = readint(glob('/sys/class/backlight/*/max_brightness')[0])
except (FileNotFoundError, IndexError):
    pass


def backlight_percentage() -> str:
    return None
    try:
        bl_now = readint(glob('/sys/class/backlight/*/brightness')[0])
        return f'{int((100 / bl_max) * bl_now)}%'
    except FileNotFoundError:
        return None


backlight = Segment(
    source=backlight_percentage,
    label='bl',
    sleep_ms=5000,
    weight=95,
)


# ==========================================================================
# Current battery percentage.
# ==========================================================================

def battery_percentage() -> str:
    """Returns current battery percentage"""
    try:
        batteries = glob('/sys/class/power_supply/BAT*')

        if batteries:
            power_levels = set()
            for battery in batteries:
                full = readint(f'{battery}/energy_full')
                now = readint(f'{battery}/energy_now')
                power = ((100 / full) * now)
                power_levels.add(power)

        percent = int(sum(power_levels) / len(batteries))

        charging = readint('/sys/class/power_supply/AC/online')

        if charging:
            if percent >= 99:
                return f'{fancy_meter(percent)} full'
            return f'{fancy_meter(percent)} ++'

        return fancy_meter(percent)

    except FileNotFoundError:
        return None


battery = Segment(
    source=battery_percentage,
    label='bat',
    sleep_ms=10000,
    weight=90,
)


if __name__ == '__main__':
    # ======================================================================
    # Run the status bar.
    # ======================================================================

    # Main thread, required
    target_threads = [status_bar]

    # Optional threads
    target_threads += [battery, backlight, clock, cpu, disk, net, ram]

    threads = [Thread(target=thread.run) for thread in target_threads]

    try:
        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

    except (EOFError, KeyboardInterrupt):
        teardown.set()

    finally:
        teardown.set()
        for thread in threads:
            thread.join()
