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

                if args.abort:
                    self.data[self.uuid] = None
                    break
                continue


class StatusBar(SharedData):
    bindpoint = '/tmp/statusd.sock'
    server = socket(AF_UNIX, SOCK_STREAM)

    def active_blocks(self):
        return [
            k for k in sorted(self.data.keys()) if self.data[k] is not None
        ]

    def bar(self):
        return ''.join([
            f' {str(self.data[block])} ' for block in self.active_blocks()
        ])

    def remove_existing_bindpoint(self):
        path_is_socket = lambda path: S_ISSOCK(stat(path).st_mode)
        try:
            if path.exists(self.bindpoint) or path_is_socket(self.bindpoint):
                remove(self.bindpoint)
        except FileNotFoundError:
            pass

    def run(self):
        self.remove_existing_bindpoint()

        self.server.bind(self.bindpoint)
        # Unix domain sockets only need write permission
        chmod(self.bindpoint, 0o222)
        self.server.listen(5)

        while True:
            try:
                client, address = self.server.accept()
                client.send(bytes(self.bar(), 'utf-8'))
            finally:
                client.close()
        self.server.close()


meter_values = make_meter_values(int(args.width))


def meter(percentage):
    return meter_values[int(percentage)]
