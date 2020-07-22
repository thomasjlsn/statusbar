#!/usr/bin/env python3
"""
The StatusBar is a Component of statusd. It uses unix domain sockets.

The StatusBar combines all the Components in the stats module to form the
statusbar (basically just joining a bunch of strings into one), then
serves it at `/tmp/statusd.sock`.


"""

from os import chmod, path, remove, stat
from socket import AF_UNIX, SOCK_STREAM, socket
from stat import S_ISSOCK
from sys import exit

from statusdlib.core.components import Component


class StatusBar(Component):
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


statusbar = StatusBar()
