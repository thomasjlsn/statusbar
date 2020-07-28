#!/usr/bin/env python3
"""Main entrypoint to pybar."""

from sys import stderr

from lib_pybar.args import args


def main():
    if args.run:
        try:
            from lib_pybar import server
            server.main()
            exit(0)
        except PermissionError:
            stderr.write('you must be root to start pybar\n')
            exit(1)

    from lib_pybar import client
    exit(client.main())
