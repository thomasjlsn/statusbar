#!/usr/bin/env python3
"""A simple client that recieves data from pybard."""

from socket import AF_UNIX, SOCK_STREAM, socket
from sys import stderr, stdout


def main():
    try:
        client = socket(AF_UNIX, SOCK_STREAM)
        client.connect('/tmp/pybar.sock')
        stdout.write(client.recv(1024).decode('utf-8'))
        return 0
    except ConnectionRefusedError:
        stderr.write('server is not running\n')
        return 1
    finally:
        client.close()
