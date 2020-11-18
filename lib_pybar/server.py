'''Pybar server.'''

import os
import sys
from os import path
from socket import AF_UNIX, SOCK_STREAM, socket
from threading import Thread

from lib_pybar import StatusBar
from lib_pybar.blocks import (backlight, battery, cpu, date, disks, memory,
                              network, pacman, weather)
from lib_pybar.config import config
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
        if path.exists(config.PYBAR_SERVER_SOCKET):
            os.remove(config.PYBAR_SERVER_SOCKET)

        self.server.bind(config.PYBAR_SERVER_SOCKET)

        # Unix sockets only need write permission.
        os.chmod(config.PYBAR_SERVER_SOCKET, 0o222)

    def accept_connections(self):
        try:
            current_status = self.statusbar()

            if len(current_status) > config.PYBAR_SERVER_MTU:
                current_status = current_status[:-config.PYBAR_SERVER_MTU]

            client, _ = self.server.accept()
            client.send(bytes(current_status, config.PYBAR_SERVER_ENCODING))

        finally:
            client.close()

    def run(self):
        try:
            self.start_server()
            self.server.listen(config.PYBAR_SERVER_MAX_CONNECTIONS)

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
            (True,                          server),
            (True,                          date.main()),
            (config.PYBAR_BLOCKS_BATTERY,   battery.main()),
            (config.PYBAR_BLOCKS_BACKLIGHT, backlight.main()),
            (config.PYBAR_BLOCKS_CPU,       cpu.main()),
            (config.PYBAR_BLOCKS_DISKS,     disks.main()),
            (config.PYBAR_BLOCKS_MEMORY,    memory.main()),
            (config.PYBAR_BLOCKS_NETWORK,   network.main()),
            (config.PYBAR_BLOCKS_PACMAN,    pacman.main()),
            (config.PYBAR_BLOCKS_WEATHER,   weather.main()),
        )
        if condition
    }

    try:
        for thread in threads:
            thread.start()
    finally:
        for thread in threads:
            thread.join()
