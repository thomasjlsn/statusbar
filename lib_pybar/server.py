'''Pybar server.'''

import atexit
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

    piddir = '/run/pybar/'
    pidfile = '/run/pybar/pid'

    def write_pidfile(self):
        if not path.isdir(self.piddir):
            os.makedirs(self.piddir)

        with open(self.pidfile, 'w') as f:
            f.write(str(os.getpid()))

    def remove_pidfile(self):
        sys.stderr.write('deleted server pidfile\n')
        os.remove(self.pidfile)

    def check_if_already_running(self):
        if path.exists(self.pidfile):
            sys.stderr.write('pybar server is already running\n')
            flags.abort = True
            exit(1)

    def start_server(self):
        # Only one instance of the server should be running.
        self.check_if_already_running()
        self.write_pidfile()
        atexit.register(self.remove_pidfile)

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
