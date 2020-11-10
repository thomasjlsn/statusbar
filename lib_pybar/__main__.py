'''pybar

Pybar is a minimal client / server statusbar for dwm, tmux, etc.

The server should start automatically if you are using systemd. If for any
reason you need to control the server manually, several commands are provided
to let you do so.

CLIENT USAGE:
    pybar

SERVER USAGE:
    pybar <COMMAND>

COMMANDS:
    start
    stop
    pause
    resume


*see the README for example usage.

'''

from functools import partial
from sys import argv, exit, stderr


def main():
    if len(argv) == 1:
        from lib_pybar import receiver

        receiver.main()

    if len(argv) == 2:
        from os import geteuid
        from signal import SIGUSR1
        from lib_pybar import server, signals, send

        if argv[1] in ('-h', '--help', 'help'):
            stderr.write(__doc__)
            exit(1)

        if geteuid() != 0:
            stderr.write('you must be root to control pybar\n')
            exit(1)

        dispatch_table = {
            'start':    server.main,
            '_pacman':  partial(send, SIGUSR1),
            'stop':     partial(send, signals.PYBAR_SIGABRT),
            'resume':   partial(send, signals.PYBAR_SIGCONT),
            'pause':    partial(send, signals.PYBAR_SIGSTOP),
        }

        dispatch_table.get(argv[1], lambda: None)()


if __name__ == '__main__':
    stderr.write(__doc__)
