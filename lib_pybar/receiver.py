'''
Recieve and print data from the server.
'''

from socket import AF_UNIX, SOCK_STREAM, socket
from sys import exit, stderr, stdout

from lib_pybar import PYBAR_SOCKET


def main():
    try:
        client = socket(AF_UNIX, SOCK_STREAM)
        client.connect(PYBAR_SOCKET)
        stdout.write(client.recv(1024).decode('utf-8'))
    except ConnectionRefusedError as e:
        stderr.write(f'ConnectionRefusedError: {e}\n')
        exit(1)
    finally:
        client.close()
