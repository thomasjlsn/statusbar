'''
Pybar server.
'''

from os import chmod, getenv, remove
from os.path import exists
from socket import AF_UNIX, SOCK_STREAM, socket
from sys import stderr
from threading import Thread

from lib_pybar import PYBAR_MAX_CONNECTIONS, PYBAR_SOCKET, StatusBar
from lib_pybar.blocks import (backlight, battery, cpu, date, disks, memory,
                              network, pacman, weather)
from lib_pybar.signals import flags


class Server(StatusBar):
    server = socket(AF_UNIX, SOCK_STREAM)

    def __ensure_bindpoint_is_avaiable(self):
        if exists(PYBAR_SOCKET):
            remove(PYBAR_SOCKET)

    def __drop_permissions(self):
        # Unix sockets only need write permission
        chmod(PYBAR_SOCKET, 0o222)

    def __start_server(self):
        self.__ensure_bindpoint_is_avaiable()
        self.server.bind(PYBAR_SOCKET)
        self.__drop_permissions()
        self.server.listen(PYBAR_MAX_CONNECTIONS)

    def __accept_connections(self):
        try:
            client, address = self.server.accept()
            client.send(bytes(self.statusbar(), 'utf-8'))
        finally:
            client.close()

    def run(self):
        stderr.write('starting pybar server\n')
        try:
            self.__start_server()
            while not flags.abort:
                self.__accept_connections()
        finally:
            stderr.write('stopping pybar server\n')
            self.server.close()


def main():
    server = Server()

    threads = {
        Thread(target=thread.run)
        for condition, thread in (
            (True,                                server),
            (getenv('PYBAR_ENABLE_BATTERY',   1), battery.main()),
            (getenv('PYBAR_ENABLE_BACKLIGHT', 0), backlight.main()),
            (getenv('PYBAR_ENABLE_DATE',      1), date.main()),
            (getenv('PYBAR_ENABLE_CPU',       1), cpu.main()),
            (getenv('PYBAR_ENABLE_DISKS',     1), disks.main()),
            (getenv('PYBAR_ENABLE_MEMORY',    1), memory.main()),
            (getenv('PYBAR_ENABLE_NETWORK',   1), network.main()),
            (getenv('PYBAR_ENABLE_PACMAN',    1), pacman.main()),
            (getenv('PYBAR_ENABLE_WEATHER',   1), weather.main()),
        )
        if condition
    }

    try:
        for thread in threads:
            thread.start()
    finally:
        for thread in threads:
            thread.join()
