#!/usr/bin/env python3
"""A client recieving the status bar."""

from socket import AF_UNIX, SOCK_STREAM, socket
from sys import stderr, stdout

try:
    client = socket(AF_UNIX, SOCK_STREAM)
    client.connect('/tmp/statusd.sock')
    stdout.write(client.recv(1024).decode('utf-8'))
except ConnectionRefusedError:
    stderr.write('server is not running\n')
finally:
    client.close()
