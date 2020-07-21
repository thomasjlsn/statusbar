#!/usr/bin/env python3
"""A Server producing the status bar."""

import logging
import os
import socket
import time
from glob import glob
from itertools import cycle
from math import floor, log
from threading import Event, Thread
from time import strftime

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
    Many files in /sys/* and /proc/* contain single integer values.
    This reduces boilerplate.
    """
    with open(file, 'r') as f:
        val = int(f.readline())

    return val


def readstr(file):
    """Counterpart to readint()."""
    with open(file, 'r') as f:
        val = str(f.readline()).strip()

    return val


def uuid():
    """Get a uuid from the kernel."""
    return readstr('/proc/sys/kernel/random/uuid')


def make_meter(meter_width):
    """Assign unicode bars to percentages to make meters."""
    meter = {0: ' ' * meter_width}
    bar_chars = []
    cell_chars = [' ', '▏', '▎', '▍', '▌', '▋', '▊', '▉', '█']
    full = cell_chars[-1]

    fill = ''
    for _ in range(meter_width):
        for char in cell_chars:
            bar = fill + char
            bar_chars.append(bar.ljust(meter_width))
        fill += full

    for percent in range(1, 101):
        end = 0
        for i, char in enumerate(bar_chars):
            start = end
            end = (100 / len(bar_chars)) * i
            if start < percent > end:
                meter[percent] = bar_chars[i]

    return meter


meter = make_meter(10)


def fancy_meter(percentage=None, current=None, maximum=None):
    if percentage is None:
        val = ((100 / maximum) * current)
    else:
        val = percentage

    return meter[int(val)]


def bytes_to_largest_units(size_in_bytes):
    if size_in_bytes == 0:
        return '0B'

    units = ('B', 'K', 'M', 'G', 'T', 'P')

    i = int(floor(log(size_in_bytes, 1024)))
    p = pow(1024, i)
    s = round(size_in_bytes / p, 2)

    return '%s%s' % (s, units[i])


# ==========================================================================

class SharedData:
    data = {}


class Block_Devices:
    disks = cycle([
        line.split()[0] for line in [
            drive.strip() for drive in
            os.popen('df').readlines() if drive.startswith('/dev/sda')
        ]
    ])

    def next(self):
        return(next(self.disks))


class Network:
    interfaces = [d for d in os.listdir('/sys/class/net/') if d != 'lo']
    traffic = (0, 0)


disks = Block_Devices()
network = Network()


class Component(SharedData):
    def __init__(self, source=None, label=None, sleep_ms=1000, weight=0):
        # The function data is recieved from
        self.source = source

        # An optional label for the component
        self.label = label

        # Time in ms to sleep, between 0.5 ... 20 seconds
        self.sleep_ms = max(500, min(20000, sleep_ms))

        # Used to determine order of components
        self.weight = str(weight).zfill(8)

        # Unique key to store data
        self.uuid = f'{self.weight}-{uuid()}'

    def update(self):
        component = self.source()
        if component is not None:
            if self.label is not None:
                self.data[self.uuid] = f'{self.label.upper()}: {component}'
            else:
                self.data[self.uuid] = component

    def sleep(self):
        if laptop_open():
            time.sleep(self.sleep_ms / 1000)
        else:
            # Sleep longer.
            time.sleep((self.sleep_ms * 3) / 1000)

    def run(self):
        while True:
            try:
                self.update()
                self.sleep()

            except Exception as e:
                # Display the error briefly
                self.data[self.uuid] = f'ERROR: "{e}"'
                time.sleep(10)

                # Set data to None, effectively removing the component,
                # allowing the status bar to continue running without it.
                self.data[self.uuid] = None
                break

            finally:
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
#  Main status bar function.
# ==========================================================================

lpad = ' '
rpad = ' '


def make_bar():
    return ''.join([
        ''.join([
            lpad, str(SharedData.data[component]), rpad
        ])
        for component in sorted(SharedData.data.keys())
        if SharedData.data[component] is not None
    ])


status_bar = StatusBar(
    source=make_bar,
    sleep_ms=200,
)


# ==========================================================================
# The individual segments of the status bar.
#
# ==========================================================================
# A Clock.
# ==========================================================================

def time_now():
    return time.strftime('%a, %b %d %H:%M')


clock = Segment(
    source=time_now,
    sleep_ms=250,
    weight=99,
)


# ==========================================================================
# Disk usage.
# ==========================================================================

# def disk_label():
    # if readint('/sys/block/sda/queue/rotational'):
        # return 'hdd'
    # return 'ssd'


def disk_usage():
    disk = disks.next()

    label = f'{disk.split("/")[-1:][0].upper()}: '

    return label + fancy_meter(int(
        os.popen(f'df {disk} --output=pcent').readlines()[1].strip()[:-1]
    ))


disk = Segment(
    source=disk_usage,
    # label=disk_label(),
    sleep_ms=20000,
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
    up = []

    for interface in network.interfaces:
        with open(f'/sys/class/net/{interface}/operstate', 'r') as s:
            if s.readline().strip() == 'up':
                up.append(interface)

    if not up:
        return 'offline'

    if int(strftime('%S')[0]) % 2 == 0:
        return os.popen('ip route get 1.1.1.1').readlines()[0].split()[6]
    return ' '.join(up)


net = Segment(
    source=interfaces,
    label='net',
    sleep_ms=1000,
    weight=10,
)


# ==========================================================================
# Network usage.
# ==========================================================================

def net_usage():
    tx_bytes, rx_bytes = 0, 0

    for interface in network.interfaces:
        tx_bytes += readint(f'/sys/class/net/{interface}/statistics/tx_bytes')
        rx_bytes += readint(f'/sys/class/net/{interface}/statistics/rx_bytes')

    tx_old, rx_old = network.traffic

    tx_rate = (tx_bytes - tx_old)
    rx_rate = (rx_bytes - rx_old)

    network.traffic = (tx_bytes, rx_bytes)

    return ' '.join([
        f'↑ {bytes_to_largest_units(tx_rate)}',
        f'↓ {bytes_to_largest_units(rx_rate)}',
    ])


traffic = Segment(
    source=net_usage,
    sleep_ms=1000,
    weight=5,
)

# ==========================================================================
# Backlight level percentage.
# ==========================================================================

try:
    bl_max = readint(glob('/sys/class/backlight/*/max_brightness')[0])
except (FileNotFoundError, IndexError):
    pass


def backlight_percentage() -> str:
    try:
        bl_now = readint(glob('/sys/class/backlight/*/brightness')[0])
        return fancy_meter(maximum=bl_max, current=bl_now)
    except FileNotFoundError:
        return None


backlight = Segment(
    source=backlight_percentage,
    label='bl',
    sleep_ms=500,
    weight=95,
)


# ==========================================================================
# Current battery percentage.
# ==========================================================================

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
                return f'{fancy_meter(percent)} full'
            return f'{fancy_meter(percent)} ++'

        return fancy_meter(percent)

    except FileNotFoundError:
        return None


battery = Segment(
    source=battery_source,
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
    target_threads += [
        # backlight,
        battery,
        clock,
        cpu,
        disk,
        # net,
        ram,
        traffic,
    ]

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
