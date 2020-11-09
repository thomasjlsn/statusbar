'''Main entrypoint to pybar.'''

from sys import argv, exit, stderr


def main():
    if len(argv) == 2 and argv[1] == 'run':
        try:
            from lib_pybar import server
            server.main()
            exit(0)
        except PermissionError:
            stderr.write('you must be root to start pybar\n')
            exit(1)

    from lib_pybar import client
    client.main()
