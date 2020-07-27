#!/usr/bin/env python3

from os import chmod, path, remove, stat
from socket import AF_UNIX, SOCK_STREAM, socket
from stat import S_ISSOCK
from sys import exit
from time import sleep

from statusdlib.args import args
from statusdlib.helpers import laptop_open, make_meter_values, uuid


class SharedData:
    """Data shared between blocks and the statusbar."""
    data = {}


class Block(SharedData):
    def __init__(self, source=None, label=None, sleep_ms=1000, weight=0):
        # The function data is recieved from
        self.source = source

        # An optional label for the block
        self.label = label

        # Time in ms to sleep, between 0.5 ... 20 seconds
        self.sleep_ms = max(500, min(20000, sleep_ms))

        # Used to determine order of components
        self.weight = str(weight).zfill(8)

        # Unique key to store data
        self.uuid = f'{self.weight}-{uuid()}'

    def update(self):
        value = self.source()
        if value is not None:
            if self.label is not None:
                self.data[self.uuid] = f'{self.label.upper()}: {value}'
            else:
                self.data[self.uuid] = value

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
                self.data[self.uuid] = f'ERROR: "{e}"'
                sleep(10)

                # Set data to None, effectively removing the block,
                # allowing the status bar to continue running without it.
                self.data[self.uuid] = None
                break


class StatusBar(SharedData):
    """
    The StatusBar combines all the Blocks in the blocks module to form the
    statusbar (basically just joining a bunch of strings into one), then
    serves it at `/tmp/statusd.sock`.
    """

    bar = ''
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
        self.bar = ''.join([
            f' {str(self.data[key])} '
            for key in sorted(self.data.keys())
            if self.data[key] is not None
        ])

    def run(self):
        try:
            while True:
                client, address = self.server.accept()
                self.update()
                client.send(bytes(self.bar, 'utf-8'))
        finally:
            self.server.close()


meter_values = make_meter_values(int(args.width))


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
