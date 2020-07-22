#!/usr/bin/env python3
"""
The Server is a Component of statusd. It uses unix domain sockets.

The Server combines all the Components in the stats module to form the
statusbar (basically just joining a bunch of strings into one), then
serves it at `/tmp/statusd.sock`.


"""

import logging
import os
from socket import AF_UNIX, SOCK_STREAM, socket
from stat import S_ISSOCK

from statusdlib.core.components import Component
from statusdlib.core.data import SharedData


class Server(Component):
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


statusbar = Server(
    source=make_bar,
    sleep_ms=200,
)
