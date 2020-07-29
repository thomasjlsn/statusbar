#!/usr/bin/env python3

from os import chmod, geteuid, path, remove
from socket import AF_UNIX, SOCK_STREAM, socket
from threading import Thread

from lib_pybar.blocks import (backlight, battery, cpu, date, disks, memory,
                              network)
from lib_pybar.core import StatusBar

if geteuid() != 0:
    raise PermissionError


class Server(StatusBar):
    bindpoint = '/tmp/pybar.sock'
    server = socket(AF_UNIX, SOCK_STREAM)

    def __remove_existing_bindpoint(self):
        if path.exists(self.bindpoint):
            remove(self.bindpoint)

    def __drop_permissions(self):
        # Unix domain sockets only need write permission
        chmod(self.bindpoint, 0o222)

    def __accept_connections(self):
        try:
            client, address = self.server.accept()
            client.send(bytes(self.statusbar(), 'utf-8'))
        finally:
            client.close()

    def __start_server(self):
        self.__remove_existing_bindpoint()
        self.server.bind(self.bindpoint)
        self.__drop_permissions()
        self.server.listen(5)

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
