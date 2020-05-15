#!/usr/bin/env python3
"""A client recieving the status bar."""

import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((socket.gethostname(), 8787))

print(client.recv(1024).decode('utf-8'))
