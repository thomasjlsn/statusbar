'''
Signal definitions for pybar.
'''

import signal
from dataclasses import dataclass
from sys import stderr


@dataclass
class flags:
    abort = False
    clear_updates = True
    do_healthcheck = True
    halt = False


def _post_transaction_hook(*_):
    stderr.write('running post transaction hook\n')
    flags.clear_updates = True
    flags.do_healthcheck = True


def _abort_hook(*_):
    stderr.write('running abort hook\n')
    flags.abort = True


def _stop_hook(*_):
    stderr.write('running stop hook\n')
    flags.halt = True


def _cont_hook(*_):
    stderr.write('running cont hook\n')
    flags.halt = False


@dataclass
class hooks:
    abort = _abort_hook
    cont = _cont_hook
    stop = _stop_hook
    post_transaction = _post_transaction_hook


_realtime_signal_range = range(
    signal.SIGRTMIN,
    signal.SIGRTMAX,
)  # TODO validate me!

PYBAR_SIGABRT = signal.SIGRTMIN + 1
PYBAR_SIGCONT = signal.SIGRTMIN + 2
PYBAR_SIGSTOP = signal.SIGRTMIN + 3

signal.signal(signal.SIGUSR1, hooks.post_transaction)
signal.signal(signal.SIGTERM, hooks.abort)
signal.signal(PYBAR_SIGABRT,  hooks.abort)
signal.signal(PYBAR_SIGCONT,  hooks.cont)
signal.signal(PYBAR_SIGSTOP,  hooks.stop)
