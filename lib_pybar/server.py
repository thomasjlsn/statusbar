#!/usr/bin/env python3

from os import chmod, geteuid, remove
from os.path import exists
from socket import AF_UNIX, SOCK_STREAM, socket
from threading import Thread

from lib_pybar.blocks import (backlight, battery, cpu, date, disks, memory,
                              network)
from lib_pybar.core import PYBAR_SOCKET, StatusBar

if geteuid() != 0:
    raise PermissionError


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
        self.server.listen(5)

    def __accept_connections(self):
        try:
            client, address = self.server.accept()
            client.send(bytes(self.statusbar(), 'utf-8'))
        finally:
            client.close()

    def run(self):
        try:
            self.__start_server()
            while True:
                self.__accept_connections()
        finally:
            self.server.close()


def main():
    server = Server()

    threads = {
        Thread(target=thread.run)
        for condition, thread in (
            (True,  server),
            (True,  battery.main()),
            (False, backlight.main()),
            (True,  date.main()),
            (True,  cpu.main()),
            (True,  disks.main()),
            (True,  memory.main()),
            (True,  network.main()),
        )
        if condition
    }

    try:
        for thread in threads:
            thread.start()
    finally:
        for thread in threads:
            thread.join()
