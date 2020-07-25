#!/usr/bin/env python3

from os import chmod, path, remove, stat
from socket import AF_UNIX, SOCK_STREAM, socket
from stat import S_ISSOCK
from sys import exit
from time import sleep

from statusdlib.core.data import SharedData
from statusdlib.helpers import laptop_open, uuid


class Block(SharedData):
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
                self.shared_data[self.uuid] = f'{self.label.upper()}: {component}'
            else:
                self.shared_data[self.uuid] = component

    def sleep(self):
        if laptop_open():
            sleep(self.sleep_ms / 1000)
        else:
            # Sleep longer.
            sleep((self.sleep_ms * 3) / 1000)

    def run(self):
        while True:
            try:
                self.update()
                self.sleep()

            except Exception as e:
                # Display the error briefly
                self.shared_data[self.uuid] = f'ERROR: "{e}"'
                sleep(10)

                # Set data to None, effectively removing the component,
                # allowing the status bar to continue running without it.
                self.shared_data[self.uuid] = None
                break


class StatusBar(SharedData):
    """
    The StatusBar is a Component of statusd. It uses unix domain sockets.

    The StatusBar combines all the Blocks in the blocks module to form the
    statusbar (basically just joining a bunch of strings into one), then
    serves it at `/tmp/statusd.sock`.

    """

    data = ''
    sleep_ms = 200
    uds = '/tmp/statusd.sock'

    # Remove the old socket if there is one
    try:
        is_socket = S_ISSOCK(stat(uds).st_mode)
        if path.exists(uds) or is_socket:
            remove(uds)
    except FileNotFoundError:
        pass
    except PermissionError:
        exit(1)

    server = socket(AF_UNIX, SOCK_STREAM)
    server.bind(uds)
    chmod(uds, 0o722)  # Reduce permissions to minimum needed
    server.listen(5)

    def update(self):
        self.data = ''.join([
        ''.join([
            ' ', str(self.shared_data[component]), ' '
        ])
        for component in sorted(self.shared_data.keys())
        if self.shared_data[component] is not None
    ])

    def run(self):
        try:
            while True:
                client, address = self.server.accept()
                self.update()
                client.send(bytes(self.data, 'utf-8'))
                # if teardown.is_set():
                    # break
        finally:
            self.server.close()


def make_meter_values(meter_width):
    """Assign unicode bars to percentages."""
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


meter_values = make_meter_values(int(SharedData.args.width))


def meter(percentage=None, current=None, maximum=None):
    """
    A Unicode 'meter'.

    A meter needs either:
        * a percentage
        * the current and maximum values

    """
    if percentage is None:
        val = ((100 / maximum) * current)
    else:
        val = percentage

    return meter_values[int(val)]
