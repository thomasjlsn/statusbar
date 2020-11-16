'''Signal definitions for pybar.'''

import signal
from sys import stderr


def _post_transaction_hook(*_):
    stderr.write('running post transaction hook\n')
    flags.clear_updates = True
    flags.do_healthcheck = True


def _abort_hook(*_):
    stderr.write('running abort hook\n')
    flags.abort = True


def _pause_hook(*_):
    stderr.write('running pause hook\n')
    flags.halt = True


def _resume_hook(*_):
    stderr.write('running resume hook\n')
    flags.halt = False


class flags:
    abort = False
    clear_updates = True
    do_healthcheck = True
    halt = False
    server_is_running = False


class hooks:
    abort = _abort_hook
    resume = _resume_hook
    pause = _pause_hook
    post_transaction = _post_transaction_hook


_realtime_signal_range = range(
    signal.SIGRTMIN,
    signal.SIGRTMAX,
)  # TODO validate me!

PYBAR_SIGABRT = signal.SIGRTMIN + 1
PYBAR_SIGCONT = signal.SIGRTMIN + 2
PYBAR_SIGSTOP = signal.SIGRTMIN + 3

signal.signal(signal.SIGUSR1, hooks.post_transaction)
signal.signal(PYBAR_SIGABRT,  hooks.abort)
signal.signal(PYBAR_SIGCONT,  hooks.resume)
signal.signal(PYBAR_SIGSTOP,  hooks.pause)
