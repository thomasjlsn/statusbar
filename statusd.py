#!/usr/bin/env python3
"""A Server producing the status bar."""

import os
import socket
import logging
import time
from glob import glob
from threading import Event, Thread

import psutil

# Kill all threads in the status_bar
teardown = Event()


# ==========================================================================
# Data Classes.
# ==========================================================================

class Config:
    surround = '  '  # Could be something like '[]', '<>', etc.
    seperator = '|'


class SharedData:
    data = {}


# ==========================================================================
# Classes making up the status bar.
# ==========================================================================

class Component(SharedData):
    def __init__(self, source=None, sink=None, label=None,
                 sleep_ms=1000, weight=0):

        self.source = source      # The function data is recieved from
        self.sink = sink          # The function data is sent to
        self.label = label        # An optional label for the component
        self.sleep_ms = sleep_ms  # Time in ms to sleep
        self.weight = weight      # Used to determine order of components

    def update(self):
        component = self.source()
        if component is not None:
            if self.label is not None:
                self.data[self.weight] = f'{self.label}: {component}'
            else:
                self.data[self.weight] = component

    def out(self):
        if self.sink is not None:
            self.sink(self.data[self.weight])

    def sleep(self):
        time.sleep(self.sleep_ms / 1000)

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
    return Config.seperator.join([
        ''.join([
            Config.surround[0],
            str(SharedData.data[component]),
            Config.surround[1],
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
# ==========================================================================


# ==========================================================================
# Helper functions.
# ==========================================================================

def readint(file):
    """
    Many files in /sys/class/* contain single integer values.
    This reduces boilerplate.
    """
    with open(file, 'r') as f:
        val = int(f.readline())

    return val


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
# CPU usage in percentage.
# ==========================================================================

def cpu_percent():
    usage = psutil.cpu_percent()

    if usage < 1:
        return 'idle'

    return f'{usage:.1f}%'.zfill(5)


cpu = Segment(
    source=cpu_percent,
    label='cpu',
    sleep_ms=500,
    weight=80,
)


# ==========================================================================
# Memory usage.
# ==========================================================================

def memory_usage():
    """Memory displayed in largest unit."""
    mem = psutil.virtual_memory()._asdict()['used']
    units = {
        'K': 1_000,
        'M': 1_000_000,
        'G': 1_000_000_000,
    }

    if mem in range(1_000, 1_000_000):
        return f'{int(mem / units["K"])}K'
    elif mem in range(1_000_000, 1_000_000_000):
        return f'{int(mem / units["M"])}M'
    elif mem in range(1_000_000_000, 1_000_000_000_000):
        return f'{mem / units["G"]:.2f}G'
    return str(mem)


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
    ifs = ''
    ifstate = {'up': '+', 'down': '-'}

    for interface in (d for d in os.listdir('/sys/class/net/') if d != 'lo'):
        with open(f'/sys/class/net/{interface}/operstate', 'r') as s:

            ifs = f'{ifs} {interface[:3]}: {ifstate[s.readline().strip()]}'
    return ifs.strip()


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
except FileNotFoundError:
    pass


def backlight_percentage() -> str:
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

        percent = f'{sum(power_levels) / len(batteries):.2f}'

        charging = readint('/sys/class/power_supply/AC/online')

        if charging:
            return f'{percent}% ++'

        return f'{percent}%'

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
    target_threads += [battery, backlight, clock, cpu, net, ram]

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
