'''Recieve and print data from the server.'''

from socket import AF_UNIX, SOCK_STREAM, socket
from sys import stderr, stdout

from lib_pybar.config import config


def main():
    try:
        client = socket(AF_UNIX, SOCK_STREAM)
        client.connect(config.PYBAR_SERVER_SOCKET)
        stdout.write(client.recv(config.PYBAR_SERVER_MTU).decode('utf-8'))
    except ConnectionRefusedError as e:
        stderr.write(f'ConnectionRefusedError: {e}\n')
        exit(1)
    finally:
        client.close()
