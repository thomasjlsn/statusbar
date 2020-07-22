#!/usr/bin/env python3

import logging
import os
import time
from socket import AF_UNIX, SOCK_STREAM, socket
from stat import S_ISSOCK

from statusdlib.helpers import laptop_open, uuid


class SharedData:
    data = {}


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

            # finally:
                # if teardown.is_set():
                    # break


class StatusBar(Component):
    """The status bar as a whole. Needs its own unique dataset."""
    data = ''
    uds = '/tmp/statusd.sock'

    # Remove the old socket if there is one
    try:
        is_socket = S_ISSOCK(os.stat(uds).st_mode)
        if os.path.exists(uds) or is_socket:
            os.remove(uds)
    except FileNotFoundError:
        pass

    server = socket(AF_UNIX, SOCK_STREAM)
    server.bind(uds)
    os.chmod(uds, 0o722)  # Reduce permissions to minimum needed
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
                # if teardown.is_set():
                    # break
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


statusbar = StatusBar(
    source=make_bar,
    sleep_ms=200,
)
