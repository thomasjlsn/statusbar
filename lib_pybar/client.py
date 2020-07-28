#!/usr/bin/env python3
"""A simple client that recieves data from pybard."""

from socket import AF_UNIX, SOCK_STREAM, socket
from sys import exit, stderr, stdout


def main():
    try:
        client = socket(AF_UNIX, SOCK_STREAM)
        client.connect('/tmp/pybar.sock')
        stdout.write(client.recv(1024).decode('utf-8'))
    except ConnectionRefusedError as e:
        stderr.write(f'{e}\n')
        exit(1)
    finally:
        client.close()
