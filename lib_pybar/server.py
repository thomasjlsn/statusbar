'''Pybar server.'''

import os
import sys
from os import path
from socket import AF_UNIX, SOCK_STREAM, socket
from threading import Thread

from lib_pybar import PYBAR_MAX_CONNECTIONS, PYBAR_SOCKET, StatusBar
from lib_pybar.blocks import (backlight, battery, cpu, date, disks, memory,
                              network, pacman, weather)
from lib_pybar.signals import flags


class Server(StatusBar):
    server = socket(AF_UNIX, SOCK_STREAM)

    def start_server(self):
        # Only one instance of the server should be running.

        # NOTE: no more checking if pybar pid exists before starting the
        # server.
        #
        # Apparently, (after an update) systemd does this now (hooray! one
        # more way those cunts are overstepping their bounds!). Trying to do
        # it ourselves causes systemd to lose its mind, and subsequently, my
        # entire system comes grinding to a halt via infinitely spawned
        # pybar processes + never ending stop jobs.
        #
        # THANK YOU SO MUCH, SYSTEMD!

        # Ensure the socket is available.
        if path.exists(PYBAR_SOCKET):
            os.remove(PYBAR_SOCKET)

        self.server.bind(PYBAR_SOCKET)

        # Unix sockets only need write permission.
        os.chmod(PYBAR_SOCKET, 0o222)

    def accept_connections(self):
        try:
            client, address = self.server.accept()
            client.send(bytes(self.statusbar(), 'utf-8'))
        finally:
            client.close()

    def run(self):
        try:
            self.start_server()
            self.server.listen(PYBAR_MAX_CONNECTIONS)

            flags.server_is_running = True

            sys.stderr.write('started pybar server\n')

            while not flags.abort:
                self.accept_connections()

        finally:
            self.server.close()


def main():
    server = Server()

    threads = {
        Thread(target=thread.run)
        for condition, thread in (
            (True,                                   server),
            (os.getenv('PYBAR_ENABLE_BATTERY',   1), battery.main()),
            (os.getenv('PYBAR_ENABLE_BACKLIGHT', 0), backlight.main()),
            (os.getenv('PYBAR_ENABLE_DATE',      1), date.main()),
            (os.getenv('PYBAR_ENABLE_CPU',       1), cpu.main()),
            (os.getenv('PYBAR_ENABLE_DISKS',     1), disks.main()),
            (os.getenv('PYBAR_ENABLE_MEMORY',    1), memory.main()),
            (os.getenv('PYBAR_ENABLE_NETWORK',   1), network.main()),
            (os.getenv('PYBAR_ENABLE_PACMAN',    1), pacman.main()),
            (os.getenv('PYBAR_ENABLE_WEATHER',   1), weather.main()),
        )
        if condition
    }

    try:
        for thread in threads:
            thread.start()
    finally:
        for thread in threads:
            thread.join()
