#!/usr/bin/env python3

from os import chmod, path, remove, stat
from socket import AF_UNIX, SOCK_STREAM, socket
from stat import S_ISSOCK
from sys import exit
from time import sleep

from statusdlib.args import args
from statusdlib.helpers import make_meter_values, uuid


class SharedData:
    """Data shared between blocks and the statusbar."""
    data = {}


class RemoveBlock(Exception):
    """
    Blocks may raise this from their source function to cleanly remove
    themselves from the statusbar.
    """
    pass


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

    def remove_block(self):
        self.data.pop(self.uuid, None)

    def run(self):
        while True:
            try:
                self.update()
                sleep(self.sleep_ms / 1000)

            except RemoveBlock:
                self.remove_block()
                break

            except Exception as e:
                # Display the error briefly
                self.data[self.uuid] = f'ERROR: "{e}"'
                sleep(10)

                if args.abort:
                    self.data[self.uuid] = None
                    break
                continue


class StatusBar(SharedData):
    def active_blocks(self):
        return [
            block for block in sorted(self.data.keys())
            if self.data[block] is not None
        ]

    def statusbar(self):
        return ''.join([
            f' {str(self.data[block])} ' for block in self.active_blocks()
        ])


class Server(StatusBar):
    bindpoint = '/tmp/statusd.sock'
    server = socket(AF_UNIX, SOCK_STREAM)

    def drop_permissions(self):
        # Unix domain sockets only need write permission
        chmod(self.bindpoint, 0o222)

    def has_existing_bindpoint(self):
        return S_ISSOCK(stat(self.bindpoint).st_mode)

    def remove_existing_bindpoint(self):
        try:
            if path.exists(self.bindpoint) or self.has_existing_bindpoint():
                remove(self.bindpoint)
        except FileNotFoundError:
            pass

    def start_server(self):
        self.remove_existing_bindpoint()
        self.server.bind(self.bindpoint)
        self.drop_permissions()
        self.server.listen(5)

    def accept_connections(self):
        try:
            client, address = self.server.accept()
            client.send(bytes(self.statusbar(), 'utf-8'))
        finally:
            client.close()

    def run(self):
        try:
            self.start_server()
            while True:
                self.accept_connections()
        finally:
            self.server.close()


meter_values = make_meter_values(int(args.width))


def meter(percentage):
    return meter_values[int(percentage)]
